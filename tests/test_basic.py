#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from app import create_app, db
from app.models import Book
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
