#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from . import auth
from werkzeug.urls import url_parse
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .forms import RegistrationForm, LoginForm, PasswordResetRequestForm
from app.models import User
from app import db
from app.email import send_mail


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
        user = User.query.filter_by(email=email).first_or_404()
        if user:
            send_mail(
                user.email,
                "重置密码",
                "email/reset_password",
                user=user,
                token="test-token",
            )
            flash("密码重置邮件已发送，注意查收")
        else:
            flash("邮件地址无效")
    return render_template("auth/forget_password_request.html", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    pass
