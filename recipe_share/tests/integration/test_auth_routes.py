from unittest.mock import patch


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create Account" in response.data


def test_register_validation(client):
    response = client.post("/register", data={"username": "x", "email": "invalid", "password": "short", "password_confirmation": "different"})
    assert response.status_code == 422
    assert b"Use 3 to 30" in response.data


def test_logout_requires_login(client):
    response = client.post("/logout")
    assert response.status_code == 401


def test_login_session(client):
    user = {"id": 7, "username": "chef", "email": "chef@example.com", "password_hash": "hash", "role": "user", "status": "active"}
    with patch("recipeshare.auth.routes.AuthenticationService.authenticate", return_value=user):
        response = client.post("/login", data={"email_or_username": "chef", "password": "secret-password"})
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["user_id"] == 7
        assert session["user_role"] == "user"
    assert response.headers["Location"].endswith("/home")


def test_admin_login_uses_administrator_landing(client):
    user = {"id": 8, "username": "admin", "email": "admin@example.com", "password_hash": "hash", "role": "admin", "status": "active"}
    with patch("recipeshare.auth.routes.AuthenticationService.authenticate", return_value=user):
        response = client.post("/login", data={"email_or_username": "admin", "password": "secret-password"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/home")
    with client.session_transaction() as session:
        assert session["user_role"] == "admin"


def test_non_admin_cannot_open_administrator_dashboard(client):
    with client.session_transaction() as session:
        session["user_id"] = 7
        session["username"] = "chef"
        session["user_role"] = "user"
    response = client.get("/admin/dashboard")
    assert response.status_code == 403


def test_admin_dashboard_path_redirects_from_user_dashboard(client):
    with client.session_transaction() as session:
        session["user_id"] = 8
        session["username"] = "admin"
        session["user_role"] = "admin"
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/dashboard")


def test_authenticated_root_redirects_by_role(client):
    with client.session_transaction() as session:
        session["user_id"] = 7
        session["username"] = "chef"
        session["user_role"] = "user"
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/home")


def test_register_redirects_to_verify_email_with_otp(client):
    created_user = {"id": 15, "username": "otp_chef", "email": "otp@example.com", "role": "user", "status": "active"}
    otp_payload = {"otp_code": "482910", "sent_via_smtp": True, "expires_seconds": 60, "masked_email": "o*p@example.com"}
    with (
        patch("recipeshare.auth.routes.AuthenticationService.register", return_value=created_user),
        patch("recipeshare.auth.routes.AuthenticationService.issue_email_otp", return_value=otp_payload),
    ):
        response = client.post(
            "/register",
            data={
                "username": "otp_chef",
                "email": "otp@example.com",
                "password": "secret-password",
                "password_confirmation": "secret-password",
            },
        )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/verify-email")
    with client.session_transaction() as session:
        assert session.get("pending_verification_user_id") == 15
        assert session.get("pending_verification_expires_seconds") == 60
        assert "dev_otp_preview" not in session


def test_verify_email_page_and_submission(client):
    with client.session_transaction() as session:
        session["pending_verification_user_id"] = 15
        session["pending_verification_email"] = "otp@example.com"
        session["pending_verification_username"] = "otp_chef"
        session["pending_verification_masked_email"] = "o*p@example.com"
        session["pending_verification_expires_seconds"] = 60

    page_response = client.get("/verify-email")
    assert page_response.status_code == 200
    assert b"Verify Your Email" in page_response.data
    assert b"60s" in page_response.data
    assert b"LOCAL PREVIEW OTP" not in page_response.data

    verified_user = {"id": 15, "username": "otp_chef", "email": "otp@example.com", "role": "user", "status": "active"}
    with patch("recipeshare.auth.routes.AuthenticationService.verify_email_otp", return_value=verified_user):
        post_response = client.post(
            "/verify-email",
            data={"otp_1": "4", "otp_2": "8", "otp_3": "2", "otp_4": "9", "otp_5": "1", "otp_6": "0"},
        )
    assert post_response.status_code == 302
    assert post_response.headers["Location"].endswith("/home")
    with client.session_transaction() as session:
        assert session["user_id"] == 15
        assert "pending_verification_user_id" not in session


def test_forgot_password_otp_and_reset_flow(client):
    get_forgot = client.get("/forgot-password")
    assert get_forgot.status_code == 200
    assert b"Forgot Password?" in get_forgot.data

    user = {"id": 13, "username": "precious_cas", "email": "prcscsy@gmail.com", "role": "user", "status": "active"}
    otp_payload = {"otp_code": "654321", "sent_via_smtp": True, "expires_seconds": 60, "masked_email": "p*****y@gmail.com"}
    with patch("recipeshare.auth.routes.AuthenticationService.request_password_reset", return_value=(user, otp_payload)):
        post_forgot = client.post("/forgot-password", data={"email_or_username": "prcscsy@gmail.com"})
    assert post_forgot.status_code == 302
    assert post_forgot.headers["Location"].endswith("/reset-password/verify")

    verify_page = client.get("/reset-password/verify")
    assert verify_page.status_code == 200
    assert b"Verify Reset Code" in verify_page.data
    assert b"RecipeShare Community" in verify_page.data

    with patch("recipeshare.auth.routes.AuthenticationService.verify_email_otp", return_value=user):
        post_verify = client.post(
            "/reset-password/verify",
            data={"otp_1": "6", "otp_2": "5", "otp_3": "4", "otp_4": "3", "otp_5": "2", "otp_6": "1"},
        )
    assert post_verify.status_code == 302
    assert post_verify.headers["Location"].endswith("/reset-password")

    reset_page = client.get("/reset-password")
    assert reset_page.status_code == 200
    assert b"Create New Password" in reset_page.data
    assert b"Password Strength" in reset_page.data

    with patch("recipeshare.auth.routes.AuthenticationService.reset_password", return_value=user):
        post_reset = client.post(
            "/reset-password",
            data={"password": "NewPass123!", "password_confirmation": "NewPass123!"},
        )
    assert post_reset.status_code == 302
    assert post_reset.headers["Location"].endswith("/login")
    with client.session_transaction() as session:
        assert "pending_reset_user_id" not in session
        assert "pending_reset_otp_verified" not in session


def test_author_can_edit_own_recipe_and_others_forbidden(client):
    sample_recipe = {
        "id": 42,
        "author_id": 13,
        "author_name": "yap",
        "author_avatar": None,
        "category_id": 12,
        "category_name": "Filipino",
        "location_id": 1,
        "location_name": "Philippines",
        "title": "Sinigang na Baboy",
        "slug": "sinigang-na-baboy",
        "description": "A traditional Filipino sour soup made with tender pork.",
        "servings": 6,
        "prep_minutes": 15,
        "cook_minutes": 60,
        "status": "published",
        "view_count": 10,
        "average_rating": 0.0,
        "review_count": 0,
        "like_count": 0,
        "save_count": 0,
        "is_liked": 0,
        "is_saved": 0,
        "user_rating": 0,
        "is_following": 0,
        "image_path": "/static/uploads/recipes/sample.jpg",
        "video_path": None,
        "media_mime_type": "image/jpeg",
        "ingredients": [{"name": "Pork belly", "quantity": 1.0, "unit": "kg"}],
        "steps": ["Prepare the ingredients", "Boil the pork", "Add aromatics"],
    }

    with client.session_transaction() as session:
        session["user_id"] = 13
        session["username"] = "yap"
        session["user_role"] = "user"

    with (
        patch("recipeshare.home.routes.HomeService.recipe_detail", return_value=sample_recipe),
        patch("recipeshare.home.routes.HomeRepository.increment_view"),
        patch("recipeshare.home.routes.HomeRepository.active_categories", return_value=[{"id": 12, "name": "Filipino"}]),
        patch("recipeshare.home.routes.LocationRecipeService.locations", return_value=[{"id": 1, "name": "Philippines"}]),
        patch("recipeshare.home.routes.HomeRepository.update_recipe") as mock_update,
    ):
        detail_resp = client.get("/recipes/sinigang-na-baboy")
        assert detail_resp.status_code == 200
        assert b"Edit Recipe" in detail_resp.data
        assert b"Delete Recipe" in detail_resp.data

        edit_page = client.get("/recipes/sinigang-na-baboy/edit")
        assert edit_page.status_code == 200
        assert b"Edit Recipe" in edit_page.data
        assert b"Sinigang na Baboy" in edit_page.data

        update_resp = client.post(
            "/recipes/sinigang-na-baboy/edit",
            data={
                "title": "Sinigang na Baboy Updated",
                "description": "Updated description",
                "category_id": "12",
                "location_id": "1",
                "prep_minutes": "15",
                "cook_minutes": "60",
                "servings": "6",
                "ingredient_name": ["Pork belly"],
                "ingredient_quantity": ["1"],
                "ingredient_unit": ["kg"],
                "instructions": "1. Wash pork\n2. Simmer broth",
                "status": "published",
            },
        )
        assert update_resp.status_code == 302
        assert update_resp.headers["Location"].endswith("/recipes/sinigang-na-baboy")
        assert mock_update.called

    # Non-owner should not see Edit Recipe and should receive 403 on /edit
    with client.session_transaction() as session:
        session["user_id"] = 99
        session["username"] = "other_user"
        session["user_role"] = "user"

    with (
        patch("recipeshare.home.routes.HomeService.recipe_detail", return_value=sample_recipe),
        patch("recipeshare.home.routes.HomeRepository.increment_view"),
    ):
        other_detail = client.get("/recipes/sinigang-na-baboy")
        assert other_detail.status_code == 200
        assert b"Edit Recipe" not in other_detail.data

        forbidden_edit = client.get("/recipes/sinigang-na-baboy/edit")
        assert forbidden_edit.status_code == 403


def test_otp_notifications_toast_and_in_app(client, app):
    with app.app_context():
        from recipeshare.auth.service import AuthenticationService
        from recipeshare.notifications.repository import NotificationRepository

        service = AuthenticationService()
        unique_username = "otp_test_chef"
        unique_email = "otp_test_chef@example.com"

        # 1. Clean up old user if exists
        existing = service.repository.find_by_login(unique_email)
        if existing:
            from recipeshare.shared.database import get_connection
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id = %s", (existing["id"],))
            conn.commit()
            cur.close()

        # 2. Register user to trigger OTP issue and OTP notification
        reg_resp = client.post(
            "/register",
            data={
                "username": unique_username,
                "email": unique_email,
                "password": "Password123!",
                "password_confirmation": "Password123!",
                "agreement": "on",
            },
            follow_redirects=True,
        )
        assert reg_resp.status_code == 200
        html = reg_resp.get_data(as_text=True)

        # 3. Verify device Gmail banner is present and initial state gates the notification
        assert "device-gmail-banner" in html
        assert "Gmail Not Logged In on this Device" in html
        assert "data-otp-toast" in html
        assert "Auto-fill Verification Code" in html
        # Initially hidden until Gmail is active on this device
        assert 'style="display: none;"' in html

        # 4. Verify in-app notification record exists in database
        user = service.repository.find_by_login(unique_email)
        assert user is not None
        notifications = NotificationRepository().list_for_user(user["id"])
        otp_notifications = [n for n in notifications if n["type"] == "otp_sent"]
        assert len(otp_notifications) > 0, "Expected an otp_sent notification record"
        assert "verification" in otp_notifications[0]["payload"]["title"].lower()

        # 5. Verify that when device has Gmail logged in, notification is actively displayed
        gmail_user_email = "otp_device_chef@gmail.com"
        with client.session_transaction() as sess:
            sess["pending_verification_email"] = gmail_user_email
            sess["pending_verification_otp_code"] = "654321"
        client.set_cookie("device_gmail_account", gmail_user_email)
        synced_resp = client.get("/verify-email")
        synced_html = synced_resp.get_data(as_text=True)
        assert "Gmail Active on this Device" in synced_html
        assert "Auto-fill Verification Code" in synced_html

        # 6. Verify password reset also respects device Gmail sync
        client.set_cookie("device_gmail_account", "")
        reset_resp = client.post(
            "/forgot-password",
            data={"email_or_username": unique_email},
            follow_redirects=True,
        )
        assert reset_resp.status_code == 200
        reset_html = reset_resp.get_data(as_text=True)
        assert "device-gmail-banner" in reset_html
        assert "Auto-fill Verification Code" in reset_html



