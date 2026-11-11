import mysql.connector

from recipeshare.shared.database import get_connection
from recipeshare.shared.exceptions import DuplicateRecordError, RecordNotFoundError


class UserRepository:
    def find_by_login(self, value: str) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT u.id, u.username, u.email, u.password_hash, u.status, u.email_verified_at, r.name AS role "
                "FROM users u JOIN roles r ON r.id = u.role_id "
                "WHERE u.email = %s OR u.username = %s LIMIT 1",
                (value, value),
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def find_by_identity(self, value: str) -> dict | None:
        return self.find_by_login(value)

    def find_by_id(self, user_id: int) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT u.id, u.username, u.email, u.status, u.email_verified_at, r.name AS role "
                "FROM users u JOIN roles r ON r.id = u.role_id WHERE u.id = %s",
                (user_id,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def follower_count(self, user_id: int) -> int:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COUNT(*) AS count FROM user_follows WHERE following_id = %s", (user_id,))
            row = cursor.fetchone()
            return row["count"] if row else 0
        finally:
            cursor.close()

    def following_count(self, user_id: int) -> int:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COUNT(*) AS count FROM user_follows WHERE follower_id = %s", (user_id,))
            row = cursor.fetchone()
            return row["count"] if row else 0
        finally:
            cursor.close()

    def is_following(self, follower_id: int, following_id: int) -> bool:
        if not follower_id or not following_id or follower_id == following_id:
            return False
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT 1 FROM user_follows WHERE follower_id = %s AND following_id = %s LIMIT 1", (follower_id, following_id))
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    def profile_data(self, user_id: int, viewer_id: int | None = None) -> dict:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT u.id, u.username, u.email, u.created_at, r.name AS role, "
                "COALESCE(p.display_name, u.username) AS display_name, p.bio, p.avatar_path, l.name AS location_name "
                "FROM users u JOIN roles r ON r.id=u.role_id "
                "LEFT JOIN user_profiles p ON p.user_id=u.id "
                "LEFT JOIN locations l ON l.id=p.location_id WHERE u.id=%s",
                (user_id,),
            )
            profile = cursor.fetchone() or {}
            cursor.execute("SELECT COUNT(*) AS count FROM recipes WHERE author_id=%s AND status='published'", (user_id,))
            recipe_count = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) AS count FROM favorites WHERE user_id=%s", (user_id,))
            saved_count = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) AS count FROM user_follows WHERE following_id=%s", (user_id,))
            follower_count = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) AS count FROM user_follows WHERE follower_id=%s", (user_id,))
            following_count = cursor.fetchone()["count"]
            cursor.execute(
                "SELECT COUNT(*) AS count FROM likes lk JOIN recipes r ON r.id=lk.recipe_id WHERE lk.user_id=%s AND r.status='published'",
                (user_id,),
            )
            like_count = cursor.fetchone()["count"]
            cursor.execute(
                "SELECT COUNT(*) AS count FROM likes lk JOIN recipes r ON r.id=lk.recipe_id WHERE r.author_id=%s",
                (user_id,),
            )
            likes_received_count = cursor.fetchone()["count"]

            draft_count = 0
            draft_recipes_preview = []
            if viewer_id and viewer_id == user_id:
                cursor.execute("SELECT COUNT(*) AS count FROM recipes WHERE author_id=%s AND status='draft'", (user_id,))
                draft_count = cursor.fetchone()["count"]
                cursor.execute(
                    "SELECT r.id, r.title, r.slug, r.status, r.updated_at, "
                    "COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id=r.id ORDER BY ri.is_primary DESC, ri.id LIMIT 1),'') AS image_path "
                    "FROM recipes r WHERE r.author_id=%s AND r.status='draft' ORDER BY r.updated_at DESC LIMIT 4",
                    (user_id,),
                )
                draft_recipes_preview = cursor.fetchall()

            is_following = False
            if viewer_id and viewer_id != user_id:
                cursor.execute("SELECT 1 FROM user_follows WHERE follower_id=%s AND following_id=%s LIMIT 1", (viewer_id, user_id))
                is_following = cursor.fetchone() is not None

            cursor.execute(
                "SELECT r.id, r.title, r.slug, COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id=r.id ORDER BY ri.is_primary DESC, ri.id LIMIT 1),'') AS image_path "
                "FROM recipes r WHERE r.author_id=%s AND r.status='published' ORDER BY r.created_at DESC, r.id DESC LIMIT 6",
                (user_id,),
            )
            recipes = cursor.fetchall()
            cursor.execute(
                "SELECT r.id, r.title, r.slug, COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id=r.id ORDER BY ri.is_primary DESC, ri.id LIMIT 1),'') AS image_path "
                "FROM recipes r JOIN favorites f ON f.recipe_id=r.id WHERE f.user_id=%s ORDER BY f.created_at DESC LIMIT 6",
                (user_id,),
            )
            favorites = cursor.fetchall()
            return {
                "profile": profile,
                "recipe_count": recipe_count,
                "draft_count": draft_count,
                "draft_recipes_preview": draft_recipes_preview,
                "saved_count": saved_count,
                "follower_count": follower_count,
                "following_count": following_count,
                "like_count": like_count,
                "likes_received_count": likes_received_count,
                "is_following": is_following,
                "is_owner": bool(viewer_id and viewer_id == user_id),
                "recipes": recipes,
                "favorites": favorites,
            }
        finally:
            cursor.close()

    def authored_recipes(self, user_id: int) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.id,r.title,r.slug,r.status,r.created_at, "
                "COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id=r.id ORDER BY ri.is_primary DESC,ri.id LIMIT 1),'') AS image_path, "
                "COALESCE((SELECT COUNT(*) FROM likes lk WHERE lk.recipe_id=r.id),0) AS like_count "
                "FROM recipes r WHERE r.author_id=%s ORDER BY r.created_at DESC",
                (user_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def draft_recipes(self, user_id: int) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.id, r.title, r.slug, r.status, r.created_at, r.updated_at, "
                "COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id=r.id ORDER BY ri.is_primary DESC, ri.id LIMIT 1),'') AS image_path, "
                "COALESCE((SELECT COUNT(*) FROM likes lk WHERE lk.recipe_id=r.id),0) AS like_count "
                "FROM recipes r WHERE r.author_id=%s AND r.status='draft' "
                "ORDER BY r.updated_at DESC, r.created_at DESC",
                (user_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def authored_posts(self, user_id: int) -> list[dict]:
        return self.authored_recipes(user_id)

    def saved_recipes(self, user_id: int) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.id,r.title,r.slug,r.status,f.created_at, "
                "COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id=r.id ORDER BY ri.is_primary DESC,ri.id LIMIT 1),'') AS image_path, "
                "COALESCE((SELECT COUNT(*) FROM likes lk WHERE lk.recipe_id=r.id),0) AS like_count "
                "FROM favorites f JOIN recipes r ON r.id=f.recipe_id WHERE f.user_id=%s ORDER BY f.created_at DESC",
                (user_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def followers(self, user_id: int, viewer_id: int | None = None) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT u.id, u.username, u.email, COALESCE(p.display_name, u.username) AS display_name, "
                "p.bio, p.avatar_path, "
                "(SELECT COUNT(*) FROM user_follows WHERE following_id = u.id) AS follower_count, "
                "(SELECT COUNT(*) FROM recipes WHERE author_id = u.id AND status = 'published') AS recipe_count, "
                "EXISTS(SELECT 1 FROM user_follows WHERE follower_id = %s AND following_id = u.id) AS is_following "
                "FROM user_follows uf "
                "JOIN users u ON u.id = uf.follower_id "
                "LEFT JOIN user_profiles p ON p.user_id = u.id "
                "WHERE uf.following_id = %s "
                "ORDER BY uf.created_at DESC",
                (viewer_id or 0, user_id),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def following(self, user_id: int, viewer_id: int | None = None) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT u.id, u.username, u.email, COALESCE(p.display_name, u.username) AS display_name, "
                "p.bio, p.avatar_path, "
                "(SELECT COUNT(*) FROM user_follows WHERE following_id = u.id) AS follower_count, "
                "(SELECT COUNT(*) FROM recipes WHERE author_id = u.id AND status = 'published') AS recipe_count, "
                "EXISTS(SELECT 1 FROM user_follows WHERE follower_id = %s AND following_id = u.id) AS is_following "
                "FROM user_follows uf "
                "JOIN users u ON u.id = uf.following_id "
                "LEFT JOIN user_profiles p ON p.user_id = u.id "
                "WHERE uf.follower_id = %s "
                "ORDER BY uf.created_at DESC",
                (viewer_id or 0, user_id),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def liked_recipes(self, user_id: int) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.id, r.title, r.slug, r.status, lk.created_at, "
                "COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id ORDER BY ri.is_primary DESC, ri.id LIMIT 1), '') AS image_path, "
                "COALESCE((SELECT COUNT(*) FROM likes l WHERE l.recipe_id = r.id), 0) AS like_count, "
                "COALESCE(p.display_name, u.username) AS author_name, "
                "u.username AS author_username "
                "FROM likes lk "
                "JOIN recipes r ON r.id = lk.recipe_id "
                "JOIN users u ON u.id = r.author_id "
                "LEFT JOIN user_profiles p ON p.user_id = u.id "
                "WHERE lk.user_id = %s AND r.status = 'published' "
                "ORDER BY lk.created_at DESC",
                (user_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def save_profile(self, user_id: int, display_name: str, bio: str, location_id: int | None = None) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO user_profiles (user_id, display_name, bio, location_id) VALUES (%s,%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE display_name=VALUES(display_name), bio=VALUES(bio), location_id=VALUES(location_id)",
                (user_id, display_name, bio, location_id),
            )
            connection.commit()
        finally:
            cursor.close()

    def save_avatar(self, user_id: int, avatar_path: str) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1 FROM user_profiles WHERE user_id=%s", (user_id,))
            if cursor.fetchone():
                cursor.execute("UPDATE user_profiles SET avatar_path=%s WHERE user_id=%s", (avatar_path, user_id))
            else:
                cursor.execute("SELECT username FROM users WHERE id=%s", (user_id,))
                username = cursor.fetchone()[0]
                cursor.execute("INSERT INTO user_profiles (user_id, display_name, avatar_path) VALUES (%s,%s,%s)", (user_id, username, avatar_path))
            connection.commit()
        finally:
            cursor.close()

    def create(self, username: str, email: str, password_hash: str) -> dict:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM roles WHERE name = 'user'")
            role = cursor.fetchone()
            if role is None:
                raise RecordNotFoundError("The user role is not configured")
            cursor.execute(
                "INSERT INTO users (role_id, username, email, password_hash) VALUES (%s, %s, %s, %s)",
                (role["id"], username, email, password_hash),
            )
            connection.commit()
            return self.find_by_id(cursor.lastrowid)
        except mysql.connector.IntegrityError as error:
            connection.rollback()
            cursor.execute(
                "SELECT id, email_verified_at FROM users WHERE email = %s OR username = %s",
                (email, username),
            )
            existing_rows = cursor.fetchall()
            if len(existing_rows) == 1 and existing_rows[0]["email_verified_at"] is None:
                unverified_id = existing_rows[0]["id"]
                cursor.execute(
                    "UPDATE users SET username = %s, email = %s, password_hash = %s WHERE id = %s AND email_verified_at IS NULL",
                    (username, email, password_hash, unverified_id),
                )
                connection.commit()
                return self.find_by_id(unverified_id)
            raise DuplicateRecordError("Username or email already exists") from error
        finally:
            cursor.close()

    def update_password(self, user_id: int, password_hash: str) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
            if cursor.rowcount != 1:
                raise RecordNotFoundError("User not found")
            connection.commit()
        finally:
            cursor.close()

    def create_email_verification(self, user_id: int, email: str, otp_hash: str, expiry_seconds: int = 60) -> dict:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "INSERT INTO email_verifications (user_id, email, otp_hash, attempts, expires_at) "
                "VALUES (%s, %s, %s, 0, TIMESTAMPADD(SECOND, %s, CURRENT_TIMESTAMP))",
                (user_id, email, otp_hash, expiry_seconds),
            )
            verification_id = cursor.lastrowid
            connection.commit()
            cursor.execute(
                "SELECT id, user_id, email, attempts, expires_at, verified_at, created_at "
                "FROM email_verifications WHERE id = %s",
                (verification_id,),
            )
            return cursor.fetchone() or {}
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    def active_email_verifications(self, user_id: int) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, user_id, email, otp_hash, attempts, expires_at, verified_at, "
                "(expires_at <= CURRENT_TIMESTAMP) AS is_expired, "
                "GREATEST(0, TIMESTAMPDIFF(SECOND, CURRENT_TIMESTAMP, expires_at)) AS remaining_seconds "
                "FROM email_verifications "
                "WHERE user_id = %s AND verified_at IS NULL "
                "ORDER BY id DESC LIMIT 5",
                (user_id,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def latest_email_verification(self, user_id: int) -> dict | None:
        rows = self.active_email_verifications(user_id)
        return rows[0] if rows else None

    def increment_verification_attempts(self, verification_id: int) -> int:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "UPDATE email_verifications SET attempts = attempts + 1 WHERE id = %s",
                (verification_id,),
            )
            connection.commit()
            cursor.execute("SELECT attempts FROM email_verifications WHERE id = %s", (verification_id,))
            row = cursor.fetchone()
            return int(row["attempts"]) if row else 0
        finally:
            cursor.close()

    def mark_email_verified(self, user_id: int, verification_id: int) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "UPDATE email_verifications SET verified_at = CURRENT_TIMESTAMP WHERE id = %s AND user_id = %s",
                (verification_id, user_id),
            )
            cursor.execute(
                "UPDATE email_verifications SET expires_at = CURRENT_TIMESTAMP "
                "WHERE user_id = %s AND id != %s AND verified_at IS NULL AND expires_at > CURRENT_TIMESTAMP",
                (user_id, verification_id),
            )
            cursor.execute(
                "UPDATE users SET email_verified_at = CURRENT_TIMESTAMP WHERE id = %s",
                (user_id,),
            )
            connection.commit()
            return self.find_by_id(user_id)
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
