#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import Form, StringField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp


class SearchForm(Form):
    q = StringField(validators=[DataRequired(), Length(min=1, max=30)])
    page = IntegerField(validators=[NumberRange(min=1, max=99)], default=1)


class FloatForm(FlaskForm):
    name = StringField(
        "收件人姓名",
        validators=[DataRequired(), Length(min=2, max=20, message="收件人姓名长度2~20")],
    )
    phone = StringField("联系电话", validators=[DataRequired(), Regexp("^1\d{10}$")])
    message = StringField("留言")
    address = StringField("邮寄地址", validators=[DataRequired(), Length(min=8, max=100)])
