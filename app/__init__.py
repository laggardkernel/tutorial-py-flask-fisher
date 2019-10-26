#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from config import config


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            # jump out and execute db statements, which is equivalent to
            # running db statements under current context
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if "is_deleted" not in kwargs:
            kwargs["is_deleted"] = 0
        return super().filter_by(**kwargs)


db = SQLAlchemy(query_class=Query)

login_manager = LoginManager()
login_manager.session_protection = "strong"  # delete non-fresh session
login_manager.login_view = "auth.login"
login_manager.login_message = "请先登录"
login_manager.login_message_category = "info"
mail = Mail()
cache = Cache()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    cache.init_app(app)

    from app.web import web as web_bp
    from app.auth import auth as auth_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)

    if not app.debug and not app.testing:
        # TODO: mail log to admin
        if app.config["LOG_TO_STDOUT"]:
            # for heroku
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists("logs"):
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


# import models for db migration
from app import models
