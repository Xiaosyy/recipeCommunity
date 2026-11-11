from typing import Any, Iterable

from .database import get_connection


class ParameterizedRepository:
    """Small base that centralizes parameterized cursor access."""

    def execute(self, sql: str, parameters: Iterable[Any] = ()) -> list[dict[str, Any]]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(sql, tuple(parameters))
            if cursor.with_rows:
                return cursor.fetchall()
            connection.commit()
            return []
        finally:
            cursor.close()
