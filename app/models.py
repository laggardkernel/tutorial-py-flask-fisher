#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from base64 import b64encode, b64decode
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (
    BadData,
    SignatureExpired,
    TimedJSONWebSignatureSerializer as Serializer,
)
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import func
from app import db, login_manager
from app.utils import is_isbn_or_key, YuShuBook


class Base(db.Model):
    __abstract__ = True  # No table creation
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # soft deletion
    is_deleted = db.Column(db.SmallInteger, nullable=False, default=0)

    def set_attrs(self, attrs_dict):
        """Helper to fill form data into model instance quickly"""
        for key, value in attrs_dict.items():
            # pass self.__class__ to hasattr to avoid write-only @property
            if hasattr(self.__class__, key) and key != "id":
                setattr(self, key, value)

    def delete(self):
        self.is_deleted = 1


class Book(Base):
    # TODO: cache YushuBook into Book Model
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
    def get_user_wishes(cls, user_id):
        wishes = (
            Wish.query.filter_by(recipient_id=user_id, fulfilled=False)
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
        if not isinstance(isbn_list, (str, set)):
            isbn_list = [isbn_list]
        count_list = (
            db.session.query(Gift.isbn, func.count(Gift.id))
            .filter(Gift.given == False, Gift.isbn.in_(isbn_list), Gift.is_deleted == 0)
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
        # 每次查询，不是很经济，
        # 为以后做缓存、存储坐准备，此处声明为 property
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
    def get_user_gifts(cls, user_id):
        gifts = (
            Gift.query.filter_by(sender_id=user_id, given=False)
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
            .filter(
                Wish.fulfilled == False, Wish.isbn.in_(isbn_list), Wish.is_deleted == 0
            )
            .group_by(Wish.isbn)
            .all()
        )
        # return dict to embed description for each item
        # 这里只给出isbn与数量对应关系，简化查询，isbn信息转化为书籍对象在视图中完成
        count_list = [{"isbn": _[0], "count": _[1]} for _ in count_list]
        return count_list

    def do_own_gift(self, user_id):
        return True if self.sender_id == user_id else False


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

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expires_in=expiration)
        r = s.dumps({"reset": self.id}).decode("utf-8")
        # add email address info into token
        r = self.email + ":" + r
        r = b64encode(r.encode("utf-8")).decode("utf-8")
        return r

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        # TODO: feedback detail err to user
        except SignatureExpired:
            # raise ValidationError("The CSRF token has expired.")
            return False
        except BadData:
            # raise ValidationError("The CSRF token is invalid.")
            return False
        if data.get("reset") != self.id:
            return False
        self.password = new_password
        # commit change in the view
        db.session.add(self)
        return True

    def check_before_save_to_list(self, isbn):
        """check validity of isbn number"""
        if is_isbn_or_key(isbn) != "isbn":
            return False
        # check existence of the book
        # 这里也不是很经济，每次入库前都要请求一次接口判断isbn是否有效
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

    def can_request_float(self):
        # check number of beans
        if self.beans < 1:
            return False
        # permit requesting two books after sending one book
        given_count = Gift.query.filter_by(sender_id=self.id, given=True).count()
        received_count = Float.query.filter_by(
            requester_id=self.id, status=FloatStatus.Accepted
        ).count()
        return True if received_count // 2 <= given_count else False

    @property
    def summary(self):
        r = dict(
            name=self.name,
            beans=self.beans,
            email=self.email,
            sent_received="{}/{}".format(self.sent_counter, self.received_counter),
        )
        return r


@login_manager.user_loader
def load_user(user_id):
    """load user into current_user"""
    return User.query.get(int(user_id))


class FloatStatus(Enum):
    Pending = 1
    Accepted = 2
    Refused = 3
    Withdrew = 4
    Finished = 5

    @classmethod
    def status_str(cls, status, key):
        if isinstance(status, int):
            status = FloatStatus(status)
        key_map = {
            cls.Pending: {"requester": "等待对方确认", "giver": "等待你确认"},
            cls.Accepted: {"requester": "对方接受请求", "giver": "你已接受"},
            cls.Refused: {"requester": "对方拒绝请求", "giver": "你已拒绝"},
            cls.Withdrew: {"requester": "对方撤销请求", "giver": "你已撤销请求"},
            cls.Finished: {"requester": "对方已完成赠送", "giver": "你已完成赠送"},
        }
        return key_map[status][key]


class Float(Base):
    __tablename__ = "floats"
    id = db.Column(db.Integer, primary_key=True)
    # recipient info
    name = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(200))
    phone = db.Column(db.String(20), nullable=False)
    # book info
    isbn = db.Column(db.String(13))
    book_title = db.Column(db.String(50))
    book_author = db.Column(db.String(30))
    book_img = db.Column(db.String(140))

    gift_id = db.Column(db.Integer, nullable=False)
    # define requester and giver info directly but not with relationship
    # to keep history data
    # requester
    requester_id = db.Column(db.Integer, nullable=False)
    requester_name = db.Column(db.String(24))
    # giver
    giver_id = db.Column(db.Integer, nullable=False)
    giver_name = db.Column(db.String(24))
    # float status
    transaction_status = db.Column(db.SmallInteger, default=1, nullable=False)

    @property
    def status(self):
        return FloatStatus(self.transaction_status)

    @status.setter
    def status(self, value):
        if isinstance(value, FloatStatus):
            value = value.value
        self.transaction_status = value
