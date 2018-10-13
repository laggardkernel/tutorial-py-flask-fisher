#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

basedir = os.path.dirname(os.path.abspath(__file__))


class Config(object):
    """
    Store different configs in separate classes
    """

    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-gue55"
    # log into stdout for heroku
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT")
