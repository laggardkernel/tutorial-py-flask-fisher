#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base64 import b64decode
from werkzeug.urls import url_parse
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .forms import (
    RegistrationForm,
    LoginForm,
    PasswordResetRequestForm,
    PasswordResetForm,
)
from app import db
from app.models import User
from app.email import send_mail
from ..web.errors import page_not_found
from . import auth


# TODO: hook to check login status before request,
#       redirect user to index page if it's authenticated


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with db.auto_commit():
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
        flash("注册成功，请登录")
        return redirect(url_for(".login"))
    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # force redirect to the home page if the "next" url is not safe
            next = request.args.get("next")
            if (
                not next
                or url_parse(next).netloc != ""
                or url_parse(next).path != "/login"
            ):
                next = url_for("web.index")
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
    if not current_user.is_anonymous:
        flash("Reset password is for user who forgot the password.")
        return redirect(url_for("web.index"))
    # EmailForm is only used for validation, not in rendering
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.generate_reset_token()
            send_mail(
                user.email, "重置密码", "email/reset_password", user=user, token=token
            )
            flash("密码重置邮件已发送，注意查收")
            return redirect(url_for("auth.login"))
        else:
            flash("邮件地址无效")
    return render_template("auth/forget_password_request.html", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    if not current_user.is_anonymous:
        flash("Reset password is for user who forgot the password.")
        return redirect(url_for("web.index"))
    try:
        email, token = b64decode(token).decode("utf-8").split(":")
    except Exception as e:
        # TODO: support custom err msg in API's err handler
        return page_not_found(msg="invalid token")
    form = PasswordResetForm()
    # form.email.data = email
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user and user.reset_password(token, form.password.data):
            db.session.commit()
            flash("密码已经更新")
            return redirect(url_for("auth.login"))
        else:
            flash("密码重置链接无效或者链接已过期")
            return redirect(url_for("web.index"))
    return render_template("auth/forget_password.html", form=form)
