#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Blueprint

auth = Blueprint("auth", __name__)

from . import routes
