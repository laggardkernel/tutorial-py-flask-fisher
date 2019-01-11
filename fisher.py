#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from app import create_app, db
from app.models import Book, Gift, Wish, User
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
    return {"db": db, "Book": Book, "Gift": Gift, "Wish": Wish, "User": User}
