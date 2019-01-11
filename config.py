#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

base_dir = os.path.dirname(os.path.abspath(__file__))


class Config(object):
    """
    Store different configs in separate classes
    """

    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-gue55"

    # SQLALCHEMY_DATABASE_URI = os.environ.get(
    #     "DATABASE_URL"
    # ) or "sqlite:///" + os.path.join(base_dir, "app.db")
    # sqlite doesn't support DROP COLUMN, ALTER COLUMN, ADD CONSTRAINT
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # disable signal of db changes

    # Use FlaskForm to fill form instance with request.form automatically,
    # but disable csrf cause lacking corresponding field in the html pages
    WTF_CSRF_ENABLED = False

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.qq.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # default recipient, email for admin
    FISHER_ADMIN = os.environ.get("FISHER_ADMIN")
    FISHER_MAIL_SUBJECT_PREFIX = "[Fisher]"
    FISHER_MAIL_SENDER = "Fisher Admin <%s>" % MAIL_USERNAME

    # log into stdout for heroku
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT")

    RESULTS_PER_PAGE = 15
    BEANS_UPLOAD_PER_BOOK = 0.5
    BOOK_RECENT_COUNT = 30

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URL")
        or "mysql+pymysql://fisher:fisher@localhost/fisher"
    )

    # TODO: start python smtp server in development
    #       run smptd in an sub-process in the background
    # MAIL_SERVER = "localhost"
    # MAIL_PORT = 8025
    # def init_app(app):
    #     from app.email import LoggingSMTPServer
    #
    #     smtpd = LoggingSMTPServer(("localhost", 8025), None)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(base_dir, "data-test.sqlite")

    # disable csrf protection during test to avoid extraction of token
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(base_dir, "datat.sqlite")

    # TODO: move logging here?


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
