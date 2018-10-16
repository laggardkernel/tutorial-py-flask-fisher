#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from flask import flash, jsonify, request, render_template
from . import bp
from .forms import SearchFrom
from .utils import is_isbn_or_key, YuShuBook
from app.view_models import BookViewModel, BookCollection


@bp.route("/book/search")
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


@bp.route("/book/<isbn>")
def book_detail(isbn):
    yushu_book = YuShuBook()
    yushu_book.search_by_isbn(isbn)
    book = BookViewModel(yushu_book.first)
    return render_template("book_detail.html", book=book, wishes=[], gifts=[])


@bp.route("/index")
def index():
    pass


@bp.route("/gifts")
def my_gifts():
    pass


@bp.route("/wish")
def my_wish():
    pass


@bp.route("/pending")
def pending():
    pass


@bp.route("/save-to-wish")
def save_to_wish():
    pass


@bp.route("/send-drift")
def send_drift():
    pass


@bp.route("/satisfy-wish")
def satisfy_wish():
    pass