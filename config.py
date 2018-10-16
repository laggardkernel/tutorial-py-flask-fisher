#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

basedir = os.path.dirname(os.path.abspath(__file__))


class Config(object):
    """
    Store different configs in separate classes
    """

    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-gue55"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # disable signal of db changes
    # log into stdout for heroku
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT")
    RESULTS_PER_PAGE = 15

    BEANS_UPLOAD_PER_BOOK = 0.5
