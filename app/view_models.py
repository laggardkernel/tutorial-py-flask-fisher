#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class BookViewModel(object):
    @classmethod
    def package_single(cls, data, keyword):
        r = {"books": [], "total": 0, "keyword": keyword}
        if data:
            r["total"] = 1
            r["books"] = [cls.__cut_book_data(data)]
        return r

    @classmethod
    def package_collection(cls, data, keyword):
        r = {"books": [], "total": 0, "keyword": keyword}
        if data:
            # don't forget the pagination
            r["total"] = data["total"]
            r["books"] = [cls.__cut_book_data(item) for item in data["books"]]
        return r

    @classmethod
    def __cut_book_data(cls, data):
        book = {
            "title": data["title"],
            "publisher": data["publisher"],
            "pages": data["pages"] or "",
            "author": "/".join(data["author"]),
            "price": data["price"],
            "summary": data["summary"] or "",
            "image": data["image"],
        }
        return book
