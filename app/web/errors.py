#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify
from . import web

# app_errorhandler is global for all routes/views
@web.app_errorhandler(404)
def page_not_found(msg="not found"):
    """error handler with content negotiation support"""
    # TODO: separate mimetype check and json resp generation
    if (
        "application/json" in request.accept_mimetypes
        and "text/html" not in request.accept_mimetypes
    ):
        response = jsonify({"error": msg})
        response.status_code = 404
        return response
    return render_template("404.html"), 404
