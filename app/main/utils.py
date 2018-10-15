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

    def __init__(self):
        self.total = 0
        self.books = []

    def search_by_isbn(self, isbn):
        url = self.isbn_url.format(isbn)
        r = HTTP.get(url)
        # TODO: cache the result into db. lookup before cache.
        self.__fill_single(r)

    def __fill_single(self, data):
        if data:
            self.total = 1
            self.books.append(data)

    def __fill_collection(self, data):
        if data:
            if data:
                # don't forget the pagination
                self.total = data["total"]
                self.books = data["books"]

    def search_by_keyword(self, q, page=1):
        url = self.keyword_url.format(
            q, current_app.config["RESULTS_PER_PAGE"], self.calc_start(page)
        )
        r = HTTP.get(url)
        self.__fill_collection(r)

    def calc_start(self, page):
        return (page - 1) * current_app.config["RESULTS_PER_PAGE"]
