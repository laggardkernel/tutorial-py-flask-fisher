#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from . import auth
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm
from .utils import get_redirect_target
from app.models import User
from app import db


# TODO: hook to check login status before request,
#       redirect user to index page if it's authenticated


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        with db.auto_commit():
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
        flash("注册成功，请登录")
        return redirect(url_for(".login"))
    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        # TODO: remove debugging print
        # print(user)
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # force redirect to the home page if the "next" url is not safe
            next = get_redirect_target() or url_for("web.index")
            return redirect(next)
        else:
            flash("账户或密码错误")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.index"))


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    pass


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    pass
