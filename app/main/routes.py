#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from flask import jsonify, request
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
        return json.dumps(books, default=lambda o: o.__dict__)
    else:
        return jsonify(form.errors)
