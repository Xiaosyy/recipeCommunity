from werkzeug.security import generate_password_hash

from recipeshare.auth.service import (
    AuthenticationError,
    AuthenticationService,
    EmailNotVerifiedError,
)


class FakeUserRepository:
    def __init__(self):
        self.created = None
        self.verification = None
        self.user = {
            "id": 1,
            "username": "chef_alice",
            "email": "alice@example.com",
            "password_hash": generate_password_hash("correct-password", method="scrypt"),
            "status": "active",
            "role": "user",
        }

    def find_by_login(self, value):
        return self.user

    def find_by_id(self, user_id):
        return self.user

    def create(self, username, email, password_hash):
        self.created = {"id": 1, "username": username, "email": email, "password_hash": password_hash, "role": "user", "status": "active"}
        return self.created

    def update_password(self, user_id, password_hash):
        self.user["password_hash"] = password_hash

    def create_email_verification(self, user_id, email, otp_hash, expiry_seconds=60):
        self.verification = {
            "id": 10,
            "user_id": user_id,
            "email": email,
            "otp_hash": otp_hash,
            "attempts": 0,
            "is_expired": 0,
            "verified_at": None,
            "expiry_seconds": expiry_seconds,
        }
        return self.verification

    def latest_email_verification(self, user_id):
        return self.verification

    def increment_verification_attempts(self, verification_id):
        self.verification["attempts"] += 1
        return self.verification["attempts"]

    def mark_email_verified(self, user_id, verification_id):
        self.verification["verified_at"] = "2026-11-09 20:00:00"
        self.user["email_verified_at"] = "2026-11-09 20:00:00"
        return self.user


def test_registration_validation():
    service = AuthenticationService(FakeUserRepository())
    try:
        service.register("x", "not-an-email", "short", "different")
        assert False, "Invalid registration should fail"
    except AuthenticationError as error:
        assert error.args[0]["username"]
        assert error.args[0]["email"]


def test_authenticate_accepts_valid_password():
    service = AuthenticationService(FakeUserRepository())
    user = service.authenticate("chef_alice", "correct-password")
    assert user["id"] == 1


def test_registration_creates_user():
    repository = FakeUserRepository()
    service = AuthenticationService(repository)
    user = service.register("new_chef", "new@example.com", "GoodPass1!", "GoodPass1!")
    assert user["username"] == "new_chef"


def test_password_complexity_requirements():
    assert "At least 8 characters." in AuthenticationService.validate_password_strength("Ab1!xy")
    assert "Uppercase and lowercase letters." in AuthenticationService.validate_password_strength("alllower1!")
    assert "Uppercase and lowercase letters." in AuthenticationService.validate_password_strength("ALLUPPER1!")
    assert "Contains numbers." in AuthenticationService.validate_password_strength("NoNumber!Pass")
    assert "Contains special characters." in AuthenticationService.validate_password_strength("NoSpecial123")
    assert AuthenticationService.validate_password_strength("GoodPass1!") == []


def test_issue_and_verify_email_otp():
    repository = FakeUserRepository()
    service = AuthenticationService(repository)
    otp_result = service.issue_email_otp(1, "alice@example.com", "chef_alice")
    assert len(otp_result["otp_code"]) == 6
    assert otp_result["otp_code"].isdigit()
    verified_user = service.verify_email_otp(1, otp_result["otp_code"])
    assert verified_user["email_verified_at"] is not None


def test_verify_email_otp_rejects_wrong_code_and_tracks_attempts():
    repository = FakeUserRepository()
    service = AuthenticationService(repository)
    otp_result = service.issue_email_otp(1, "alice@example.com", "chef_alice")
    wrong_code = "000000" if otp_result["otp_code"] != "000000" else "999999"
    try:
        service.verify_email_otp(1, wrong_code)
        assert False, "Wrong OTP should fail"
    except AuthenticationError as error:
        assert "Invalid verification code" in str(error)
        assert repository.verification["attempts"] == 1


def test_authenticate_requires_verified_email_when_field_present():
    repository = FakeUserRepository()
    repository.user["email_verified_at"] = None
    service = AuthenticationService(repository)
    try:
        service.authenticate("chef_alice", "correct-password")
        assert False, "Unverified user should not authenticate directly"
    except EmailNotVerifiedError as error:
        assert error.user["id"] == 1


def test_request_password_reset_and_reset_password():
    repository = FakeUserRepository()
    service = AuthenticationService(repository)
    user, otp_result = service.request_password_reset("chef_alice")
    assert user["id"] == 1
    assert len(otp_result["otp_code"]) == 6
    updated_user = service.reset_password(1, "NewPass123!", "NewPass123!")
    assert updated_user["id"] == 1
    authenticated = service.authenticate("chef_alice", "NewPass123!")
    assert authenticated["id"] == 1

