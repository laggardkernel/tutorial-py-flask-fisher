#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, make_response

app = Flask(__name__)
app.config.from_object('config')


@app.route('/hello')
def hello():
    headers = {'Content-Type': 'text/plain'}
    r = make_response('<html></html>', 404)
    r.headers = headers
    return r


# app.add_url_rule('/hello', view_func=hello)

app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=81)
