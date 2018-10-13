#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)


# @app.route('/hello')
def hello():
    return 'Hello, world'


app.add_url_rule('/hello', view_func=hello)

app.run(host='0.0.0.0', port=81)
