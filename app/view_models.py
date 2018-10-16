#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class BookViewModel(object):
    def __init__(self, book):
        self.title = book["title"]
        self.publisher = book["publisher"]
        self.pages = book["pages"] or ""
        self.author = "/".join(book["author"])
        self.price = book["price"]
        self.summary = book["summary"] or ""
        self.image = book["image"]
        self.isbn = book["isbn"]

    @property
    def intro(self):
        intro = filter(
            lambda x: True if x else False, [self.author, self.publisher, self.price]
        )
        return " / ".join(intro)


class BookCollection(object):
    def __init__(self):
        self.total = 0
        self.books = []
        self.keyword = ""

    def fill(self, yushu_book, keyword):
        self.total = yushu_book.total
        self.keyword = keyword
        self.books = [BookViewModel(book) for book in yushu_book.books]
