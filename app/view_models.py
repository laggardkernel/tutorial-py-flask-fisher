#!/usr/bin/env python3
# -*- coding: utf-8 -*-


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


class MyTransactions(object):
    def __init__(self, gift_list, count_list):
        self.transactions = []
        self.__transaction_list = gift_list
        self.__count_list = count_list
        self.__parse()

    def __parse(self):
        for gift in self.__transaction_list:
            my_gift = self.__match_count(gift)
            self.transactions.append(my_gift)

    def __match_count(self, gift):
        count = 0
        for _ in self.__count_list:
            if gift.isbn == _["isbn"]:
                count = _["count"]
                break
        r = {"id": gift.id, "book": BookViewModel(gift.book), "count": count}
        return r
