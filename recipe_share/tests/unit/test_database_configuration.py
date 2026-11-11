from unittest.mock import patch

from recipeshare.shared.database import get_connection


def test_database_connection_uses_application_config(app):
    app.config.update(MYSQL_HOST="db.local", MYSQL_PORT=3307, MYSQL_USER="recipe", MYSQL_PASSWORD="secret", MYSQL_DATABASE="recipe_db")
    with app.app_context(), patch("recipeshare.shared.database.mysql.connector.connect") as connect:
        connect.return_value.is_closed.return_value = False
        get_connection()
        connect.assert_called_once_with(
            host="db.local",
            port=3307,
            user="recipe",
            password="secret",
            database="recipe_db",
            autocommit=False,
        )
