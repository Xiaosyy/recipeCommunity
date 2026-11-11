import pytest
from unittest.mock import patch
from recipeshare.admin.service import AdminService
from recipeshare.shared.database import get_connection


def test_non_admin_cannot_delete_users(client):
    # Ordinary user session
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["user_role"] = "user"
        session["user_name"] = "testuser"

    response = client.post("/admin/users/delete", data={"user_id": 2}, follow_redirects=True)
    # Role required returns 403 forbidden for non-admin
    assert response.status_code == 403


def test_admin_cannot_delete_self(client, app):
    with app.app_context():
        # Admin user session
        with client.session_transaction() as session:
            session["user_id"] = 7 # recipe_admin
            session["user_role"] = "admin"
            session["user_name"] = "recipe_admin"

        response = client.post("/admin/users/delete", data={"user_id": 7}, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "cannot delete your own account" in html.lower()


def test_admin_delete_user_permanently(client, app):
    with app.app_context():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Create a dummy test user to be deleted
        cursor.execute("DELETE FROM users WHERE username = 'to_delete_user'")
        conn.commit()

        cursor.execute(
            "INSERT INTO users (role_id, username, email, password_hash, status) VALUES (1, 'to_delete_user', 'to_delete@example.com', 'dummy_hash', 'active')"
        )
        dummy_user_id = cursor.lastrowid
        conn.commit()

        # Add profile
        cursor.execute("INSERT INTO user_profiles (user_id, display_name, bio) VALUES (%s, 'To Delete', 'Test bio')", (dummy_user_id,))
        # Add a recipe authored by this user
        cursor.execute(
            "INSERT INTO recipes (author_id, category_id, title, slug, description, instructions, status) "
            "VALUES (%s, 1, 'Dummy Delete Dish', 'dummy-delete-dish-unique', 'test description for delete', '[\"Step 1. Prepare ingredients.\", \"Step 2. Cook thoroughly.\"]', 'published')",
            (dummy_user_id,)
        )
        dummy_recipe_id = cursor.lastrowid
        conn.commit()

        # Verify user and recipe exist before deletion
        cursor.execute("SELECT id FROM users WHERE id = %s", (dummy_user_id,))
        assert cursor.fetchone() is not None
        cursor.execute("SELECT id FROM recipes WHERE id = %s", (dummy_recipe_id,))
        assert cursor.fetchone() is not None

        # 2. Admin performs permanent deletion
        with client.session_transaction() as session:
            session["user_id"] = 7 # recipe_admin
            session["user_role"] = "admin"
            session["user_name"] = "recipe_admin"

        response = client.post("/admin/users/delete", data={"user_id": dummy_user_id}, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "permanently deleted" in html.lower()

        # 3. Verify user and cascading records are completely gone from DB
        cursor.execute("SELECT id FROM users WHERE id = %s", (dummy_user_id,))
        assert cursor.fetchone() is None

        cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = %s", (dummy_user_id,))
        assert cursor.fetchone() is None

        cursor.execute("SELECT id FROM recipes WHERE id = %s", (dummy_recipe_id,))
        assert cursor.fetchone() is None

        # 4. Verify audit log entry exists
        cursor.execute(
            "SELECT action, target_type, target_id FROM audit_logs WHERE action = 'delete_user_permanently' AND target_id = %s",
            (dummy_user_id,)
        )
        audit = cursor.fetchone()
        assert audit is not None
        assert audit["action"] == "delete_user_permanently"

        cursor.close()
