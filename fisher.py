#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv

# load .env manually, cause auto loading only works with command "flask"
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

import click
from app import create_app, db
from app.models import Book, Gift, Wish, User, FloatStatus, Float
from flask_migrate import Migrate

# `os.getenv` is just a wrapper for `os.environ.get`
app = create_app(os.getenv("FISHER_CONFIG", "default"))
# init Migrate, and the db sub-command is integrated into flask automatically
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    """
    Add additional context into flask shell
    :return:
    """
    return {
        "db": db,
        "Book": Book,
        "Gift": Gift,
        "Wish": Wish,
        "User": User,
        "FloatStatus": FloatStatus,
        "Float": Float,
    }


@app.cli.command()
@click.argument("address", default="localhost:8025")
def smtpd(address):
    """
    SMTP server printing email content as str into stdout

    default address: localhost:8025
    """
    import asyncore
    from app.email import DebuggingSMTPServer

    address, port = address.split(":")
    if port:
        port = int(port)
    else:
        port = 8025

    smtpd = DebuggingSMTPServer((address, port), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass
