#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from flask import current_app


def is_isbn_or_key(word):
    # isbn13, numbers
    # isbn10: numbers with '-'
    isbn_or_key = "key"
    if len(word) == 13 and word.isdigit():
        isbn_or_key = "isbn"
    short_word = word.replace("-", "")
    if "-" in word and len(short_word) == 10 and short_word.isdigit:
        isbn_or_key = "isbn"
    return isbn_or_key


class HTTP:
    @staticmethod
    def get(url, return_json=True):
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            return {} if return_json else ""
        return r.json() if return_json else r.text


class YuShuBook:
    isbn_url = "http://t.yushu.im/v2/book/isbn/{}"
    keyword_url = "http://t.yushu.im/v2/book/search?q={}&count={}&start={}"

    @classmethod
    def search_by_isbn(cls, isbn):
        url = cls.isbn_url.format(isbn)
        r = HTTP.get(url)
        return r

    @classmethod
    def search_by_keyword(cls, q, page=1):
        url = cls.keyword_url.format(
            q, current_app.config["RESULTS_PER_PAGE"], cls.calc_start(page)
        )
        r = HTTP.get(url)
        return r

    @staticmethod
    def calc_start(page):
        return (page - 1) * current_app.config["RESULTS_PER_PAGE"]
