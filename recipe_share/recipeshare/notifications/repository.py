import json

from recipeshare.shared.database import get_connection


class NotificationRepository:
    def create(self, user_id: int, notification_type: str, payload: dict) -> int:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO notifications (user_id, type, payload) VALUES (%s, %s, %s)",
                (user_id, notification_type, json.dumps(payload)),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    def unread_count(self, user_id: int) -> int:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = %s AND read_at IS NULL", (user_id,))
            return int(cursor.fetchone()[0])
        finally:
            cursor.close()

    def list_for_user(self, user_id: int, limit: int = 20) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, type, payload, read_at, created_at FROM notifications "
                "WHERE user_id = %s ORDER BY created_at DESC, id DESC LIMIT %s",
                (user_id, limit),
            )
            notifications = cursor.fetchall()
            for notification in notifications:
                if isinstance(notification.get("payload"), str):
                    notification["payload"] = json.loads(notification["payload"])
            return notifications
        finally:
            cursor.close()

    def mark_all_read(self, user_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE notifications SET read_at = NOW() WHERE user_id = %s AND read_at IS NULL", (user_id,))
            connection.commit()
        finally:
            cursor.close()

