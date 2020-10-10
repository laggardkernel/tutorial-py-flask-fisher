#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import flash, request, render_template, current_app, redirect, url_for
from flask_login import login_required, current_user
from . import web
from .forms import SearchForm, FloatForm
from app.utils import is_isbn_or_key, YuShuBook
from app import db
from app.models import User, Gift, Wish, Float
from app.view_models import (
    BookViewModel,
    BookCollection,
    Transaction,
    MyTransactions,
    FloatStatus,
    FloatCollection,
)
from app.email import send_mail


@web.route("/book/search")
def search():
    """
    q/isbn:
    :return:
    """
    form = SearchForm(request.args)
    books = BookCollection()
    if form.validate():
        q = form.q.data.strip()
        page = form.page.data
        isbn_or_key = is_isbn_or_key(q)
        yushu_book = YuShuBook()

        if isbn_or_key == "isbn":
            yushu_book.search_by_isbn(q)
        else:
            yushu_book.search_by_keyword(q, page)

        books.fill(yushu_book, q)
        # return jsonify(books)
        # return json.dumps(books, default=lambda o: o.__dict__)
    else:
        # return jsonify(form.errors)
        flash("搜索的关键字不符合要求，请重新输入关键字")
    # return render_template()
    return render_template("search_result.html", books=books)


@web.route("/book/<isbn>")
def book_detail(isbn):
    in_gift_list, in_wish_list = False, False

    # get book's detail data
    yushu_book = YuShuBook()
    yushu_book.search_by_isbn(isbn)
    book = BookViewModel(yushu_book.first)

    if current_user.is_authenticated:
        if Gift.query.filter_by(
            sender_id=current_user.id, isbn=isbn, given=False
        ).first():
            in_gift_list = True
        if Wish.query.filter_by(
            recipient_id=current_user.id, isbn=isbn, fulfilled=False
        ).first():
            in_wish_list = True

    # TODO: Gift，Wish还没带有书籍信息，会进行隐式API查询
    # sender, recipient 关系 backref 默认为 select，无疑增加了数据库查询
    gifts_available = Gift.query.filter_by(isbn=isbn, given=False).all()
    wishes_available = Wish.query.filter_by(isbn=isbn, fulfilled=False).all()

    gifts_transactions = Transaction(gifts_available, user_ref="sender")
    wish_transactions = Transaction(wishes_available, user_ref="recipient")

    return render_template(
        "book_detail.html",
        book=book,
        wishes=wish_transactions,
        gifts=gifts_transactions,
        in_gift_list=in_gift_list,
        in_wish_list=in_wish_list,
    )


@web.route("/")
def index():
    recent_gifts = Gift.recent()
    books = [BookViewModel(gift.book) for gift in recent_gifts]
    return render_template("index.html", books=books)


@web.route("/gift/mine")
@login_required
def my_gifts():
    id_ = current_user.id
    # books offered by me, 返回的gift只是存储了isbn
    gifts = Gift.get_user_gifts(id_)
    isbn_list = [gift.isbn for gift in gifts]
    # how many want the book
    count_list = Gift.get_wish_counts(isbn_list)
    # 由于数据库 in 查询输入与输出没有严格对应关系，在 MyTransactions 中需要将
    # gifts 与 count_list 中isbn对应
    view_model = MyTransactions(gifts, count_list)
    return render_template("my_gifts.html", gifts=view_model.transactions)


@web.route("/gift/<isbn>")
@login_required
def save_to_gifts(isbn):
    if current_user.check_before_save_to_list(isbn=isbn):
        # Use transaction to make the 2 steps atomic
        with db.auto_commit():
            gift = Gift(sender=current_user._get_current_object(), isbn=isbn)
            current_user.beans += current_app.config["BEANS_UPLOAD_PER_BOOK"]
            db.session.add(gift)
        flash("本书已添加至您的赠送清单中")
    else:
        flash("本书已存在于您的赠送清单或心愿清单中！")
    return redirect(url_for(".book_detail", isbn=isbn))


@web.route("/wish/mine")
@login_required
def my_wishes():
    id_ = current_user.id
    wishes = Wish.get_user_wishes(id_)
    isbn_list = [_.isbn for _ in wishes]
    # how many people want for each book in the isbn list
    count_list = Wish.get_gift_counts(isbn_list)
    # reuse MyTransactions as MyWishes view model
    view_model = MyTransactions(wishes, count_list)
    return render_template("my_wishes.html", wishes=view_model.transactions)


@web.route("/wish/book/<isbn>")
def save_to_wish(isbn):
    # 判断书籍isbn是否有效，同时防止用户钻洞子自己送书给自己
    if current_user.check_before_save_to_list(isbn=isbn):
        with db.auto_commit():
            wish = Wish(recipient=current_user._get_current_object(), isbn=isbn)
            db.session.add(wish)
        flash("本书已添加至您的心愿清单中")
    else:
        flash("本书已存在于您的赠送清单或心愿清单中！")
    return redirect(url_for(".book_detail", isbn=isbn))


@web.route("/float/<int:gift_id>", methods=["GET", "POST"])
@login_required
def request_float(gift_id):
    gift = Gift.query.get_or_404(gift_id)
    if gift.do_own_gift(current_user.id):
        flash("请勿向自己所要书籍")
        return redirect(url_for("web.book_detail", isbn=gift.isbn))
    # beans not enough, or not sending enough books
    if not current_user.can_request_float():
        return render_template("float_error.html", beans=current_user.beans)

    form = FloatForm()
    if form.validate_on_submit():
        # fill form data into Float instance
        with db.auto_commit():
            float = Float()
            form.populate_obj(float)

            # 拷贝当前用户、书籍信息，避免某些数据，
            # 避免用户数据变动后不能正确反映此时信息
            float.gift_id = gift.id
            float.requester_id = current_user.id
            float.requester_name = current_user.name
            float.giver_id = gift.sender_id
            float.giver_name = gift.sender.name

            # 通过BookViewModel处理数据，获得我们所需要的字段
            book = BookViewModel(gift.book)
            float.isbn = book.isbn
            float.book_title = book.title
            float.book_author = book.author
            float.book_img = book.image

            current_user.beans -= current_app.config["BEANS_REQUEST_PER_BOOK"]

            db.session.add(float)
            send_mail(
                gift.sender.email,
                "书籍索取请求",
                "email/request_gift",
                requester=current_user,
                gift=gift,
            )
        # TODO: redirect to float list page
    # 给出书籍拥有者姓名、邮件信息，发送、接受图书数量，可以作为信誉指标展示
    context = {"giver": gift.sender.summary, "beans": current_user.beans, "form": form}
    return render_template("float_request.html", **context)


@web.route("/transactions")
@login_required
def transactions():
    # 展示当前用户正在发送或者正在请求的书籍信息
    floats = (
        Float.query.filter(
            (Float.requester_id == current_user.id)
            | (Float.giver_id == current_user.id)
        )
        .order_by(Float.created_time.desc())
        .all()
    )
    data = []
    if floats:
        data = FloatCollection(floats, current_user.id).data
    return render_template("transactions.html", floats=data)


@web.route("/float/<int:id>/withdraw")
@login_required
def withdraw_float(id):
    """撤销向对方索取书籍"""
    with db.auto_commit():
        item = Float.query.filter_by(request_id=current_user.id, id=id).first_or_404()
        item.status = FloatStatus.Withdrew
        # 拿回自己的豆子
        current_user.beans += current_app.config["BEANS_REQUEST_PER_BOOK"]
    return redirect(url_for("web.transactions"))


@web.route("/float/<int:id>/refuse")
@login_required
def refuse_float(id):
    """拒绝对方请求"""
    with db.auto_commit():
        item = Float.query.filter_by(giver_id=current_user.id, id=id).first_or_404()
        item.status = FloatStatus.Refused
        # 把对方预付的豆子从系统中退还
        item.requester.beans += current_app.config["BEANS_REQUEST_PER_BOOK"]
    return redirect(url_for("web.transactions"))


@web.route("/float/<int:id>/mail")
@login_required
def mail_float(id):
    with db.auto_commit():
        item = Float.query.filter_by(giver_id=current_user.id, id=id).first_or_404()
        # TODO: accept
        item.status = FloatStatus.Finished
        # 完整一次赠送，为赠送者加豆子
        current_user.beans += current_app.config["BEANS_REQUEST_PER_BOOK"]
        # update gift and wish status
        # TODO: 将Gift，Wish对象与Float对象连接，避免此处查询。
        # 但这又违背了交易历史为不可变对象的原则。有待考虑
        gift = Gift.query.get_or_404(item.gift_id)
        gift.given = True
        Wish.query.filter_by(
            isbn=item.isbn, recipient_id=item.requester_id, fulfilled=False
        ).update({Wish.fulfilled: True})
    return redirect(url_for("web.transactions"))


@web.route("/gift/<int:id>/withdraw")
def withdraw_gift(id):
    gift = Gift.query.filter_by(id=id, given=False).first_or_404()
    # cancel action if the gift is in transaction
    float = Float.query.filter_by(gift_id=id, status=FloatStatus.Pending).first()
    if float:
        flash("当前礼物出于交易状态，请先完成交易")
    else:
        with db.auto_commit():
            current_user.beans -= current_app.config["BEANS_UPLOAD_PER_BOOK"]
            gift.delete()
    return redirect(url_for("web.my_gifts"))


# @web.route("/wish/<int:id>/withdraw")
@web.route("/wish/<isbn>/withdraw")
def withdraw_wish(isbn):
    # wish = Wish.query.filter_by(id=id, fulfilled=False).first_or_404()
    wish = Wish.query.filter_by(isbn=isbn, fulfilled=False).first_or_404()
    with db.auto_commit():
        wish.delete()
    return redirect(url_for("web.my_wishes"))


@web.route("/wish/<id>/fulfill")
def fulfill_wish(id):
    # 与float交易对应，float交易为索要者主动请求，此处为拥有者主动赠送
    # 实际仍需要索要者填写表单，生成Float交易
    wish = Wish.query.get_or_404(id)
    gift = Gift.query.filter_by(
        sender_id=current_user.id, isbn=wish.isbn, given=False
    ).first()
    if not gift:
        flash("您还未上传书籍！")
    else:
        send_mail(
            wish.recipient.email, "书籍赠送提醒", "email/fulfill_wish", wish=wish, gift=gift
        )
        flash("赠送请求邮件已经发送")
    return redirect(url_for("web.book_detail", isbn=wish.isbn))


@web.route("/user/<int:id>")
def user_center(id):
    user = User.query.get_or_404(id)
    user = user.summary
    return render_template("user_center.html", user=user)
