#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.models import FloatStatus


class BookViewModel(object):
    def __init__(self, book):
        # filter the keys we don't wanna
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


# Note: Transaction 并非真正交易，只是用于给书籍详情页面下显示当前想要此书，以及用于闲置此书的人
#   MyTransactions, FloatCollection 才是真正交易
class Transaction(object):
    # TODO: 这里起名有些问题，有时间再改
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
        # [{"isbn": value, "count": value}, {}, {}]
        self.__count_list = count_list
        self.__parse()

    def __parse(self):
        for gift in self.__transaction_list:
            # in 查询返回无需，通过isbn对应gift对象与count数量
            my_gift = self.__match_count(gift)
            self.transactions.append(my_gift)

    def __match_count(self, gift):
        count = 0
        for _ in self.__count_list:
            if gift.isbn == _["isbn"]:
                count = _["count"]
                break
        # gift.book 实际为property装饰的函数，依次向API查询获取图书信息
        r = {"id": gift.id, "book": BookViewModel(gift.book), "count": count}
        return r


class FloatCollection(object):
    def __init__(self, floats, user_id):
        self.data = []  # 字典的列表
        self.__parse(floats, user_id)

    def __parse(self, floats, user_id):
        for item in floats:
            temp = FloatModel(item, user_id)
            self.data.append(temp.data)


class FloatModel(object):
    def __init__(self, float, user_id):
        self.data = []
        self.data = self.__parse(float, user_id)

    @staticmethod
    def requester_or_giver(float, user_id):
        if float.requester_id == user_id:
            identity = "requester"
        else:
            identity = "giver"
        return identity

    def __parse(self, float, user_id):
        # 不同于 Gift.book，Float 实例已经记录了真正的图书信息
        # 此处数据整理时没有隐式向API发起请求。
        identity = self.requester_or_giver(float, user_id)
        status_str = FloatStatus.status_str(float.status, identity)
        r = {
            "id": float.id,
            "book_title": float.book_title,
            "book_author": float.book_author,
            "book_img": float.book_img,
            "date": float.created_time,
            "message": float.message,
            "address": float.address,
            "name": float.name,
            "phone": float.phone,
            "status": float.status,
            "status_str": status_str,
            "identity": identity,
            "operator": float.requester_name
            if identity != "requester"
            else float.giver_name,
        }
        return r
