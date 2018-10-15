#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint

bp = Blueprint("web", __name__)

from app.web import routes
