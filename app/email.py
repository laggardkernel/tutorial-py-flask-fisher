#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

from app import mail
from flask import render_template, current_app
from flask_mail import Message


def send_mail(to, subject, template, **kw):
    app = current_app._get_current_object()
    msg = Message(
        app.config["FISHER_MAIL_SUBJECT_PREFIX"] + " " + subject,
        sender=app.config["FISHER_MAIL_SENDER"],
        recipients=[to],
    )
    msg.html = render_template(template + ".html", **kw)
    mail.send(msg)
