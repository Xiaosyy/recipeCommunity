import re

from recipeshare.shared.database import get_connection


class AdminRepository:
    def users(self) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT u.id, u.username, u.email, u.status, u.created_at, r.name AS role_name, "
                "COUNT(DISTINCT recipes.id) AS recipe_count "
                "FROM users u JOIN roles r ON r.id = u.role_id "
                "LEFT JOIN recipes ON recipes.author_id = u.id "
                "GROUP BY u.id, u.username, u.email, u.status, u.created_at, r.name "
                "ORDER BY u.created_at DESC"
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def set_user_status(self, user_id: int, status: str, actor_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE users SET status = %s WHERE id = %s", (status, user_id))
            cursor.execute("INSERT INTO audit_logs (actor_id, action, target_type, target_id, note) VALUES (%s,%s,%s,%s,%s)", (actor_id, "update_user_status", "user", user_id, f"Status changed to {status}"))
            connection.commit()
        finally:
            cursor.close()

    def set_user_role(self, user_id: int, role_name: str, actor_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE users SET role_id = (SELECT id FROM roles WHERE name = %s) WHERE id = %s", (role_name, user_id))
            cursor.execute("INSERT INTO audit_logs (actor_id, action, target_type, target_id, note) VALUES (%s,%s,%s,%s,%s)", (actor_id, "update_user_role", "user", user_id, f"Role changed to {role_name}"))
            connection.commit()
        finally:
            cursor.close()

    def delete_user_permanently(self, user_id: int, actor_id: int) -> dict:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
            target_user = cursor.fetchone()
            if not target_user:
                raise ValueError("User not found.")

            # 1. Reassign audit_logs where target user was actor so foreign key RESTRICT doesn't block
            cursor.execute("UPDATE audit_logs SET actor_id = %s WHERE actor_id = %s", (actor_id, user_id))

            # 2. Clean reports created by target user or referencing their content
            cursor.execute("DELETE FROM reports WHERE reporter_id = %s", (user_id,))
            cursor.execute(
                "DELETE FROM reports WHERE (target_type = 'recipe' AND target_id IN (SELECT id FROM recipes WHERE author_id = %s)) "
                "OR (target_type = 'comment' AND target_id IN (SELECT id FROM comments WHERE author_id = %s))",
                (user_id, user_id),
            )

            # 3. Clean community posts authored by target user
            cursor.execute("DELETE FROM community_posts WHERE author_id = %s", (user_id,))

            # 4. Clean comments authored by target user
            cursor.execute("DELETE FROM comments WHERE author_id = %s", (user_id,))

            # 5. Delete all recipes authored by target user
            # (cascades to recipe_images, recipe_ingredients, likes, ratings, favorites, comments on those recipes)
            cursor.execute("DELETE FROM recipes WHERE author_id = %s", (user_id,))

            # 6. Delete user account
            # (cascades to user_profiles, user_follows, notifications, likes, favorites, ratings, email_verifications)
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

            # 7. Record audit log for permanent deletion
            cursor.execute(
                "INSERT INTO audit_logs (actor_id, action, target_type, target_id, note) VALUES (%s, %s, %s, %s, %s)",
                (
                    actor_id,
                    "delete_user_permanently",
                    "user",
                    user_id,
                    f"Permanently deleted user @{target_user['username']} ({target_user['email']})",
                ),
            )
            connection.commit()
            return target_user
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    def categories(self) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT c.*, COUNT(r.id) AS recipe_count FROM categories c LEFT JOIN recipes r ON r.category_id = c.id GROUP BY c.id ORDER BY c.name")
            return cursor.fetchall()
        finally:
            cursor.close()

    def save_category(self, category_id: int | None, name: str, description: str, active: bool, actor_id: int) -> None:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        connection = get_connection()
        cursor = connection.cursor()
        try:
            if category_id:
                cursor.execute("UPDATE categories SET name=%s, slug=%s, description=%s, is_active=%s WHERE id=%s", (name, slug, description, active, category_id))
                action = "update_category"
            else:
                cursor.execute("INSERT INTO categories (name, slug, description, is_active) VALUES (%s,%s,%s,%s)", (name, slug, description, active))
                category_id = cursor.lastrowid
                action = "create_category"
            cursor.execute("INSERT INTO audit_logs (actor_id, action, target_type, target_id, note) VALUES (%s,%s,%s,%s,%s)", (actor_id, action, "category", category_id, name))
            connection.commit()
        finally:
            cursor.close()

    def delete_category(self, category_id: int, actor_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE recipes SET category_id=NULL WHERE category_id=%s", (category_id,))
            cursor.execute("DELETE FROM categories WHERE id=%s", (category_id,))
            cursor.execute("INSERT INTO audit_logs (actor_id, action, target_type, target_id, note) VALUES (%s,%s,%s,%s,%s)", (actor_id, "delete_category", "category", category_id, "Category deleted"))
            connection.commit()
        finally:
            cursor.close()

    def reports(self) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT rp.*, reporter.username AS reporter_name FROM reports rp JOIN users reporter ON reporter.id = rp.reporter_id ORDER BY FIELD(rp.status,'open','resolved','dismissed'), rp.created_at DESC")
            return cursor.fetchall()
        finally:
            cursor.close()

    def resolve_report(self, report_id: int, status: str, actor_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE reports SET status=%s WHERE id=%s", (status, report_id))
            cursor.execute("INSERT INTO audit_logs (actor_id, action, target_type, target_id, note) VALUES (%s,%s,%s,%s,%s)", (actor_id, "update_report", "report", report_id, f"Report marked {status}"))
            connection.commit()
        finally:
            cursor.close()

    def recipes(self) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT r.id,r.title,r.slug,r.status,r.view_count,r.created_at,r.updated_at,r.published_at,c.name AS category_name,u.username AS author_name,COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id=r.id ORDER BY ri.is_primary DESC, ri.id LIMIT 1),'') AS image_path FROM recipes r LEFT JOIN categories c ON c.id=r.category_id LEFT JOIN users u ON u.id=r.author_id ORDER BY r.created_at DESC, r.id DESC")
            return cursor.fetchall()
        finally:
            cursor.close()

    def set_recipe_status(self, recipe_id: int, status: str, actor_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE recipes SET status=%s, published_at=CASE WHEN %s='published' AND published_at IS NULL THEN NOW() ELSE published_at END WHERE id=%s", (status, status, recipe_id))
            cursor.execute("INSERT INTO audit_logs (actor_id, action, target_type, target_id, note) VALUES (%s,%s,%s,%s,%s)", (actor_id, "update_recipe_status", "recipe", recipe_id, f"Status changed to {status}"))
            connection.commit()
        finally:
            cursor.close()

    def activity(self) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT a.*, u.username AS actor_name, r.name AS actor_role FROM audit_logs a JOIN users u ON u.id=a.actor_id JOIN roles r ON r.id=u.role_id ORDER BY a.created_at DESC LIMIT 100")
            return cursor.fetchall()
        finally:
            cursor.close()

    def notifications(self, user_id: int) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 100", (user_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    def settings(self) -> dict:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT setting_key, setting_value FROM system_settings")
            values = {row["setting_key"]: row["setting_value"] for row in cursor.fetchall()}
            return {
                "community_name": values.get("community_name", "RecipeShare Community"),
                "community_description": values.get("community_description", "Share and discover delicious recipes with our community!"),
                "timezone": values.get("timezone", "Asia/Manila"),
                "community_logo": values.get("community_logo", ""),
                "new_recipe_notifications": values.get("new_recipe_notifications", "1") == "1",
                "new_user_notifications": values.get("new_user_notifications", "1") == "1",
                "community_notifications": values.get("community_notifications", "1") == "1",
                "allow_public_sharing": values.get("allow_public_sharing", "1") == "1",
                "require_recipe_approval": values.get("require_recipe_approval", "0") == "1",
            }
        finally:
            cursor.close()

    def save_settings(self, settings: dict[str, str], actor_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            for key, value in settings.items():
                cursor.execute("INSERT INTO system_settings (setting_key, setting_value) VALUES (%s,%s) ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value)", (key, value))
            cursor.execute("INSERT INTO audit_logs (actor_id, action, target_type, target_id, note) VALUES (%s,%s,%s,%s,%s)", (actor_id, "update_system_settings", "system", 0, "System settings updated"))
            connection.commit()
        finally:
            cursor.close()

    def system_overview(self) -> dict:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COUNT(*) AS user_count FROM users")
            users = cursor.fetchone()["user_count"]
            cursor.execute("SELECT COUNT(*) AS recipe_count FROM recipes")
            recipes = cursor.fetchone()["recipe_count"]
            cursor.execute("SELECT COUNT(*) AS report_count FROM reports WHERE status='open'")
            reports = cursor.fetchone()["report_count"]
            return {"user_count": users, "recipe_count": recipes, "open_report_count": reports}
        finally:
            cursor.close()
