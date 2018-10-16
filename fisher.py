#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Book, Gift, User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    Add additional context into flask shell
    :return:
    """
    return {"db": db, "Book": Book, "Gift": Gift, "User": User}
