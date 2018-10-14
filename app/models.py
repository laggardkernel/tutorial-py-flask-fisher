#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from app import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(30), default="无名")
    binding = db.Column(db.String(20))
    publisher = db.Column(db.String(50))
    price = db.Column(db.String(20))
    pages = db.Column(db.Integer)
    pubdate = db.Column(db.String(20))
    isbn = db.Column(db.String(15), nullable=False, unique=True)
    summary = db.Column(db.String(1000))
    image = db.Column(db.String(50))

    def __repr__(self):
        return "<Book {}>".format(self.title)
