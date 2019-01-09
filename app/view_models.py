#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple


class BookViewModel(object):
    def __init__(self, book):
        self.title = book["title"]
        self.publisher = book["publisher"]
        self.pages = book["pages"] or ""  # or .get("page", "")
        self.author = "/".join(book["author"])
        self.price = book["price"]
        self.summary = book["summary"] or ""
        self.image = book["image"]
        self.isbn = book["isbn"]
        self.pubdate = book["pubdate"]
        self.binding = book["binding"]

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


class Transaction(object):
    def __init__(self, goods, user_ref="sender"):
        self.total = 0
        self.transactions = []
        self.__parse(goods, user_ref=user_ref)

    def __parse(self, goods, user_ref):
        self.total = len(goods)
        self.transactions = [self.__map2trade(_, user_ref) for _ in goods]

    def __map2trade(self, single, user_ref):
        return dict(
            username=getattr(single, user_ref).name,
            time=single.created_time,
            id=single.id,
        )


MyGift = namedtuple("MyGift", ["id", "book", "count"])


class MyGifts(object):
    def __init__(self, gift_list, wish_count_list):
        self.gifts = []
        self.__gift_list = gift_list
        self.__wish_count_list = wish_count_list
        self.__parse()

    def __parse(self):
        for gift in self.__gift_list:
            my_gift = self.__match_count(gift)
            self.gifts.append(my_gift)

    def __match_count(self, gift):
        count = 0
        for wish_count in self.__wish_count_list:
            if gift.isbn == wish_count["isbn"]:
                count = wish_count["count"]
                break
        my_gift = MyGift(gift.id, BookViewModel(gift.book), count)
        return my_gift
