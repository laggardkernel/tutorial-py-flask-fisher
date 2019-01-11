#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et

from smtpd import SMTPServer, DebuggingServer
from threading import Thread
from app import mail
from flask import render_template, current_app
from flask_mail import Message


class DebuggingSMTPServer(DebuggingServer):
    """Custom debugging SMTP server printing content in str"""

    def _print_message_content(self, peer, data):
        inheaders = 1
        lines = data.splitlines()
        for line in lines:
            # headers first
            if inheaders and not line:
                peerheader = "X-Peer: " + peer[0]
                print(peerheader)
                inheaders = 0
            if isinstance(data, bytes):
                line = repr(line.decode("utf-8"))
            print(line)


class LoggingSMTPServer(SMTPServer):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        import logging

        self.logger = logging.getLogger("flask.app")

    def _log_message_content(self, peer, data):
        inheaders = 1
        lines = data.splitlines()
        for line in lines:
            # headers first
            if inheaders and not line:
                peerheader = "X-Peer: " + peer[0]
                self.logger.info(peerheader)
                inheaders = 0
            if isinstance(data, bytes):
                line = repr(line.decode("utf-8"))
            self.logger.info(line)

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        self.logger.info("---------- MESSAGE FOLLOWS ----------")
        if kwargs:
            if kwargs.get("mail_options"):
                self.logger.info("mail options: %s" % kwargs["mail_options"])
            if kwargs.get("rcpt_options"):
                self.logger.info("rcpt options: %s\n" % kwargs["rcpt_options"])
        self._log_message_content(peer, data)
        self.logger.info("------------ END MESSAGE ------------")


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            # TODO: handler mail exception
            pass


def send_mail(to, subject, template, **kw):
    app = current_app._get_current_object()
    msg = Message(
        app.config["FISHER_MAIL_SUBJECT_PREFIX"] + " " + subject,
        sender=app.config["FISHER_MAIL_SENDER"],
        recipients=[to],
    )
    msg.html = render_template(template + ".html", **kw)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
