#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import flash, request, render_template, current_app, redirect, url_for
from flask_login import login_required, current_user
from . import web
from .forms import SearchFrom
from app.utils import is_isbn_or_key, YuShuBook
from app import db
from app.models import Gift, Wish
from app.view_models import BookViewModel, BookCollection, Transaction, MyTransactions


@web.route("/book/search")
def search():
    """
    q/isbn:
    :return:
    """
    form = SearchFrom(request.args)
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

    gifts_in_trade = Gift.query.filter_by(isbn=isbn, given=False).all()
    wishes_in_trade = Wish.query.filter_by(isbn=isbn, fulfilled=False).all()

    gifts_transactions = Transaction(gifts_in_trade, user_ref="sender")
    wish_transactions = Transaction(wishes_in_trade, user_ref="recipient")

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
    gifts = Gift.get_user_gifts(id_)
    isbn_list = [gift.isbn for gift in gifts]
    count_list = Gift.get_wish_counts(isbn_list)
    view_model = MyTransactions(gifts, count_list)
    return render_template("my_gifts.html", gifts=view_model.transactions)


@web.route("/gift/book/<isbn>")
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
    count_list = Wish.get_gift_counts(isbn_list)
    # reuse MyTransactions as MyWishes view model
    view_model = MyTransactions(wishes, count_list)
    return render_template("my_wishes.html", wishes=view_model.transactions)


@web.route("/wish/book/<isbn>")
def save_to_wish(isbn):
    if current_user.check_before_save_to_list(isbn=isbn):
        with db.auto_commit():
            wish = Wish(recipient=current_user._get_current_object(), isbn=isbn)
            db.session.add(wish)
        flash("本书已添加至您的心愿清单中")
    else:
        flash("本书已存在于您的赠送清单或心愿清单中！")
    return redirect(url_for(".book_detail", isbn=isbn))


@web.route("/gift/redraw")
def redraw_from_gifts():
    pass


@web.route("/wish/redraw")
def redraw_from_wishes():
    pass


@web.route("/user")
def user_center():
    pass


@web.route("/pending")
def pending():
    pass


@web.route("/send-drift")
def send_drift():
    pass


@web.route("/satisfy-wish")
def satisfy_wish():
    pass
