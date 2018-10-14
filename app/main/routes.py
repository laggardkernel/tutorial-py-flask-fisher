#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import jsonify, request
from . import bp
from .forms import SearchFrom
from .utils import is_isbn_or_key, YuShuBook
from app.view_models import BookViewModel


@bp.route("/book/search")
def search():
    """
    q/isbn:
    :return:
    """
    form = SearchFrom(request.args)
    if form.validate():
        q = form.q.data.strip()
        page = form.page.data
        isbn_or_key = is_isbn_or_key(q)
        print(isbn_or_key)
        if isbn_or_key == "isbn":
            result = YuShuBook.search_by_isbn(q)
            result = BookViewModel.package_single(result, q)
        else:
            result = YuShuBook.search_by_keyword(q, page)
            result = BookViewModel.package_collection(result, q)
        return jsonify(result)
    else:
        return jsonify(form.errors)
