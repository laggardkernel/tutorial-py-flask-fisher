#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import jsonify
from . import bp
from app.utils import is_isbn_or_key, YuShuBook


@bp.route("/book/search/<q>")
def search(q):
    """
    q/isbn:
    page
    :return:
    """
    isbn_or_key = is_isbn_or_key(q)
    print(isbn_or_key)
    if isbn_or_key == "isbn":
        result = YuShuBook.search_by_isbn(q)
    else:
        result = YuShuBook.search_by_keyword(q)
    return jsonify(result)
