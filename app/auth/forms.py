#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models import User


class LoginForm(Form):
    # Why don't inherit from FlaskForm with crsf_token
    email = StringField("Email", validators=[DataRequired(), Length(8, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in", default=True)
    # submit = SubmitField("Log In")


class RegistrationForm(Form):
    email = StringField("Email", validators=[DataRequired(), Length(8, 64), Email()])
    name = StringField("Name", validators=[DataRequired(), Length(2, 24)])
    password = PasswordField("Password", validators=[DataRequired()])
    # submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email is already registered!")

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError("Nickname is already used!")
