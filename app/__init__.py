#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        # TODO: mail log to admin
        if app.config["LOG_TO_STDOUT"]:
            # for heroku
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists("log"):
                os.mkdir("logs")
            # size limit 10k, number limit 10
            file_handler = RotatingFileHandler(
                "logs/fisher.log", maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d"
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Fisher startup")
    return app
