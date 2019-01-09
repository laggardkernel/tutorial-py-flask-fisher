#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import func
from app import db, login_manager
from app.utils import is_isbn_or_key, YuShuBook


class Base(db.Model):
    __abstract__ = True  # No table creation
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    # soft deletion
    status = db.Column(db.SmallInteger, default=1)

    def set_attrs(self, attrs_dict):
        """Helper to fill form data into model instance quickly"""
        for key, value in attrs_dict.items():
            # pass self.__class__ to hasattr to avoid write-only @property
            if hasattr(self.__class__, key) and key != "id":
                setattr(self, key, value)


class Book(Base):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(30), default="无名")
    # 装订类型
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


class Wish(Base):
    __tablename__ = "wishes"
    id = db.Column(db.Integer, primary_key=True)
    fulfilled = db.Column(db.Boolean, default=False)
    isbn = db.Column(db.String(15), nullable=False)

    # sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    @staticmethod
    def check_before_create(isbn):
        pass

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        # return raw data, view model
        return yushu_book.first

    @classmethod
    def get_user_wishes(cls, uid):
        wishes = (
            Wish.query.filter_by(id=uid, fulfilled=False)
            .order_by(Wish.created_time.desc())
            .all()
        )
        return wishes

    @classmethod
    def get_gift_counts(cls, isbn_list):
        """
        Query corresponding Gift according isbn in the list
        :param isbn_list:
        :return: number of wishes corresponding to item in list
        """
        count_list = (
            db.session.query(Gift.isbn, func.count(Gift.id))
            .filter(Gift.given == False, Gift.isbn.in_(isbn_list), Gift.status == 1)
            .group_by(Gift.isbn)
            .all()
        )
        # return dict to embed description for each item
        count_list = [{"isbn": _[0], "count": _[1]} for _ in count_list]
        return count_list


class Gift(Base):
    __tablename__ = "gifts"
    id = db.Column(db.Integer, primary_key=True)
    given = db.Column(db.Boolean, default=False)
    isbn = db.Column(db.String(15), nullable=False)

    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return "<Gift {}>".format(self.isbn)

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        # return raw data, view model
        return yushu_book.first

    @classmethod
    def recent(cls):
        # remove ONLY_FULL_GROUP_BY in sql-mode in MySQL
        gifts = (
            Gift.query.filter_by(given=False)
            .group_by(Gift.isbn)
            .order_by(Gift.created_time.desc())
            .limit(current_app.config["BOOK_RECENT_COUNT"])
            .distinct(Gift.isbn)
            .all()
        )
        return gifts

    @classmethod
    def get_user_gifts(cls, uid):
        gifts = (
            Gift.query.filter_by(id=uid, given=False)
            .order_by(Gift.created_time.desc())
            .all()
        )
        return gifts

    @classmethod
    def get_wish_counts(cls, isbn_list):
        """
        Query corresponding Wish according isbn in the list
        :param isbn_list:
        :return: number of gifts corresponding to item in list
        """
        count_list = (
            db.session.query(Wish.isbn, func.count(Wish.id))
            .filter(Wish.fulfilled == False, Wish.isbn.in_(isbn_list), Wish.status == 1)
            .group_by(Wish.isbn)
            .all()
        )
        # return dict to embed description for each item
        count_list = [{"isbn": _[0], "count": _[1]} for _ in count_list]
        return count_list


class User(Base, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24), unique=True)
    phone = db.Column(db.String(18), unique=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    beans = db.Column(db.Float, default=0)
    sent_counter = db.Column(db.Integer, default=0)
    received_counter = db.Column(db.Integer, default=0)
    wx_open_id = db.Column(db.String(50))
    wx_name = db.Column(db.String(32))
    password_hash = db.Column(db.String(128))

    # given_gifts = db.relationship("Gift", backref="sender", lazy="dynamic")
    # received_gifts = db.relationship("Gift", backref="recipient", lazy="dynamic")

    # gifts given by current user
    gifts = db.relationship(
        "Gift",
        foreign_keys=[Gift.sender_id],
        backref=db.backref("sender"),
        lazy="dynamic",
    )

    # wishes of current user
    wishes = db.relationship(
        "Wish",
        foreign_keys=[Wish.recipient_id],
        backref=db.backref("recipient"),
        lazy="dynamic",
    )

    def __repr__(self):
        return "<User {}: {}>".format(self.id, self.name)

    @property
    def password(self):
        raise AttributeError("password is a write-only attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_before_save_to_list(self, isbn):
        """check validity of isbn number"""
        if is_isbn_or_key(isbn) != "isbn":
            return False
        # check existence of the book
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(isbn)
        if not yushu_book.first:
            return False
        # 不允许用户同时成为同一本书的赠送者和索要者
        gift_in_progress = Gift.query.filter_by(
            sender_id=self.id, isbn=isbn, given=False
        ).first()
        wish_in_progress = Wish.query.filter_by(
            recipient_id=self.id, isbn=isbn, fulfilled=False
        ).first()
        if not gift_in_progress and not wish_in_progress:
            return True
        else:
            return False


@login_manager.user_loader
def load_user(user_id):
    """load user into current_user"""
    return User.query.get(int(user_id))
