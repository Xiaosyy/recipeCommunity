from contextlib import contextmanager
from typing import Iterator

import mysql.connector
from flask import current_app, g


@contextmanager
def database_connection():
    connection = mysql.connector.connect(
        host=current_app.config["MYSQL_HOST"],
        port=current_app.config["MYSQL_PORT"],
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        database=current_app.config["MYSQL_DATABASE"],
        autocommit=False,
    )
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@contextmanager
def cursor(dictionary=True):
    with database_connection() as connection:
        cursor_object = connection.cursor(dictionary=dictionary)
        try:
            yield cursor_object
        finally:
            cursor_object.close()


def get_connection():
    connection = getattr(g, "database_connection", None)
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(
            host=current_app.config["MYSQL_HOST"],
            port=current_app.config["MYSQL_PORT"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DATABASE"],
            autocommit=False,
        )
        g.database_connection = connection
    return connection


def close_database_connection():
    connection = getattr(g, "database_connection", None)
    if connection is not None and connection.is_connected():
        connection.close()
