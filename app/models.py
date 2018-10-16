#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from app import db


class Base(db.Model):
    __abstract__ = True # No table creation
    # soft deletion
    status = db.Column(db.SmallInteger, default=1)


class Book(Base):
    __tablename__ = "books"
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


class User(Base):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24), nullable=False)
    phone = db.Column(db.String(18), unique=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    beans = db.Column(db.Float, default=0)
    sent_counter = db.Column(db.Integer, default=0)
    received_counter = db.Column(db.Integer, default=0)
    wx_open_id = db.Column(db.String(50))
    wx_name = db.Column(db.String(32))

    given_gifts = db.relationship("Gift", backref="sender", lazy="dynamic")
    received_gifts = db.relationship("Gift", backref="recipient", lazy="dynamic")

    def __repr__(self):
        return "<User {}: {}>".format(self.id, self.name)


class Gift(Base):
    __tablename__ = "gifts"
    id = db.Column(db.Integer, primary_key=True)
    sent = db.Column(db.Boolean, default=False)
    isbn = db.Column(db.String(15), nullable=False)

    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
