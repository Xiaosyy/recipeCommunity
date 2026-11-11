import os

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from recipeshare.shared.decorators import login_required
from .service import (
    AuthenticationError,
    AuthenticationService,
    AuthorizationError,
    EmailNotVerifiedError,
)


auth_blueprint = Blueprint("auth", __name__, url_prefix="")


def establish_session(user: dict) -> None:
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["user_role"] = user["role"]
    session.permanent = True


def establish_pending_verification(user: dict, otp_result: dict) -> None:
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("user_role", None)
    session.pop("dev_otp_preview", None)
    session["pending_verification_user_id"] = user["id"]
    session["pending_verification_email"] = user["email"]
    session["pending_verification_username"] = user["username"]
    session["pending_verification_masked_email"] = otp_result.get(
        "masked_email", AuthenticationService.mask_email(user["email"])
    )
    session["pending_verification_expires_seconds"] = otp_result.get("expires_seconds", 60)
    session["pending_verification_smtp_sent"] = bool(otp_result.get("sent_via_smtp"))
    session["pending_verification_smtp_error"] = otp_result.get("smtp_error", "")
    session["pending_verification_otp_code"] = otp_result.get("otp_code", "")
    session.modified = True


def establish_pending_password_reset(user: dict, otp_result: dict) -> None:
    session.pop("pending_reset_otp_verified", None)
    session["pending_reset_user_id"] = user["id"]
    session["pending_reset_email"] = user["email"]
    session["pending_reset_username"] = user.get("username", "")
    session["pending_reset_masked_email"] = otp_result.get(
        "masked_email", AuthenticationService.mask_email(user["email"])
    )
    session["pending_reset_expires_seconds"] = otp_result.get("expires_seconds", 60)
    session["pending_reset_otp_code"] = otp_result.get("otp_code", "")
    session.modified = True


def clear_pending_password_reset() -> None:
    for key in (
        "pending_reset_user_id",
        "pending_reset_email",
        "pending_reset_username",
        "pending_reset_masked_email",
        "pending_reset_expires_seconds",
        "pending_reset_otp_verified",
        "pending_reset_otp_code",
    ):
        session.pop(key, None)
    session.modified = True


def reset_verify_context(error: str = "") -> dict:
    expires_seconds = session.get("pending_reset_expires_seconds", 60)
    pending_user_id = session.get("pending_reset_user_id")
    if pending_user_id:
        try:
            latest = AuthenticationService().repository.latest_email_verification(int(pending_user_id))
            if latest and "remaining_seconds" in latest and latest["remaining_seconds"] is not None:
                expires_seconds = int(latest["remaining_seconds"])
        except Exception:
            pass
    reset_email = (session.get("pending_reset_email", "") or "").strip().lower()
    device_gmail = (request.cookies.get("device_gmail_account") or "").strip().lower()
    is_device_gmail_logged_in = bool(
        device_gmail and reset_email and device_gmail == reset_email and reset_email.endswith("@gmail.com")
    )
    return {
        "email": session.get("pending_reset_email", ""),
        "masked_email": session.get("pending_reset_masked_email", ""),
        "expires_seconds": expires_seconds,
        "otp_code": session.get("pending_reset_otp_code", ""),
        "is_device_gmail_logged_in": is_device_gmail_logged_in,
        "error": error,
    }


def extract_otp_from_request() -> str:
    combined = (request.form.get("otp_code") or "").strip()
    if combined:
        return combined
    digits = [request.form.get(f"otp_{index}", "").strip() for index in range(1, 7)]
    return "".join(digits)


def verify_email_context(error: str = "") -> dict:
    expires_seconds = session.get("pending_verification_expires_seconds", 60)
    pending_user_id = session.get("pending_verification_user_id")
    if pending_user_id:
        try:
            latest = AuthenticationService().repository.latest_email_verification(int(pending_user_id))
            if latest and "remaining_seconds" in latest and latest["remaining_seconds"] is not None:
                expires_seconds = int(latest["remaining_seconds"])
        except Exception:
            pass
    verify_email = (session.get("pending_verification_email", "") or "").strip().lower()
    device_gmail = (request.cookies.get("device_gmail_account") or "").strip().lower()
    is_device_gmail_logged_in = bool(
        device_gmail and verify_email and device_gmail == verify_email and verify_email.endswith("@gmail.com")
    )
    return {
        "email": session.get("pending_verification_email", ""),
        "masked_email": session.get("pending_verification_masked_email", ""),
        "expires_seconds": expires_seconds,
        "smtp_sent": session.get("pending_verification_smtp_sent", True),
        "smtp_error": session.get("pending_verification_smtp_error", ""),
        "smtp_user": os.getenv("SMTP_USER", "").strip() or session.get("pending_verification_email", ""),
        "otp_code": session.get("pending_verification_otp_code", ""),
        "is_device_gmail_logged_in": is_device_gmail_logged_in,
        "error": error,
    }


def role_landing_url(role: str) -> str:
    return url_for("home.user_home")


@auth_blueprint.get("/login")
def login_page():
    if session.get("user_id"):
        return redirect(role_landing_url(session.get("user_role", "user")))
    return render_template("auth/login.html")


@auth_blueprint.post("/login")
def login():
    service = AuthenticationService()
    try:
        user = service.authenticate(request.form.get("email_or_username", ""), request.form.get("password", ""))
    except EmailNotVerifiedError as error:
        otp_result = service.issue_email_otp(
            error.user["id"], error.user["email"], error.user.get("username", "")
        )
        establish_pending_verification(error.user, otp_result)
        flash(f"A 6-digit verification code has been sent to {error.user['email']}.", "success")
        return redirect(url_for("auth.verify_email_page"))
    except (AuthenticationError, AuthorizationError) as error:
        flash(str(error), "error")
        return render_template("auth/login.html", email_or_username=request.form.get("email_or_username", "")), 401
    session.pop("pending_verification_otp_code", None)
    establish_session(user)
    session.modified = True
    flash("Welcome back!", "success")
    return redirect(role_landing_url(user["role"]))


@auth_blueprint.get("/register")
def register_page():
    if session.get("user_id"):
        return redirect(role_landing_url(session.get("user_role", "user")))
    return render_template("auth/register.html")


@auth_blueprint.post("/register")
def register():
    service = AuthenticationService()
    try:
        user = service.register(
            request.form.get("username", ""), request.form.get("email", ""),
            request.form.get("password", ""), request.form.get("password_confirmation", "")
        )
    except AuthenticationError as error:
        details = error.args[0]
        if isinstance(details, dict):
            return render_template("auth/register.html", values=request.form, errors=details), 422
        flash(details, "error")
        return render_template("auth/register.html", values=request.form), 422
    otp_result = service.issue_email_otp(user["id"], user["email"], user.get("username", ""))
    establish_pending_verification(user, otp_result)
    flash("Account created! Enter the 6-digit OTP verification code sent to your email.", "success")
    return redirect(url_for("auth.verify_email_page"))


@auth_blueprint.get("/verify-email")
def verify_email_page():
    if session.get("user_id"):
        return redirect(role_landing_url(session.get("user_role", "user")))
    if not session.get("pending_verification_user_id"):
        flash("Please register or log in to verify your email.", "error")
        return redirect(url_for("auth.login_page"))
    return render_template("auth/verify_email.html", **verify_email_context())


@auth_blueprint.post("/verify-email")
def verify_email():
    pending_user_id = session.get("pending_verification_user_id")
    if not pending_user_id:
        flash("Your verification session expired. Please log in again.", "error")
        return redirect(url_for("auth.login_page"))

    service = AuthenticationService()
    otp_code = extract_otp_from_request()
    try:
        user = service.verify_email_otp(pending_user_id, otp_code)
    except AuthenticationError as error:
        return render_template("auth/verify_email.html", **verify_email_context(error=str(error))), 422

    session.pop("pending_verification_otp_code", None)
    establish_session(user)
    session.modified = True
    flash(f"✓ Account verified! Confirmed {user['email']} is a real verified user. Welcome to RecipeShare!", "success")
    return redirect(role_landing_url(user["role"]))


@auth_blueprint.post("/verify-email/resend")
def resend_verification_otp():
    pending_user_id = session.get("pending_verification_user_id")
    if not pending_user_id:
        flash("Please register or log in to request a verification code.", "error")
        return redirect(url_for("auth.login_page"))

    user_stub = {
        "id": pending_user_id,
        "email": session.get("pending_verification_email", ""),
        "username": session.get("pending_verification_username", ""),
    }
    otp_result = AuthenticationService().issue_email_otp(
        user_stub["id"], user_stub["email"], user_stub["username"]
    )
    establish_pending_verification(user_stub, otp_result)
    flash(f"A new 6-digit verification code has been sent to {user_stub['email']}.", "success")
    return redirect(url_for("auth.verify_email_page"))


@auth_blueprint.get("/forgot-password")
def forgot_password_page():
    if session.get("user_id"):
        return redirect(role_landing_url(session.get("user_role", "user")))
    return render_template("auth/forgot_password.html", email_or_username="", errors={})


@auth_blueprint.post("/forgot-password")
def forgot_password():
    if session.get("user_id"):
        return redirect(role_landing_url(session.get("user_role", "user")))
    email_or_username = request.form.get("email_or_username", "")
    service = AuthenticationService()
    try:
        user, otp_result = service.request_password_reset(email_or_username)
    except AuthenticationError as error:
        return (
            render_template(
                "auth/forgot_password.html",
                email_or_username=email_or_username,
                errors={"email_or_username": str(error)},
            ),
            422,
        )
    establish_pending_password_reset(user, otp_result)
    flash(f"A 6-digit password reset code has been sent to {user['email']}.", "success")
    return redirect(url_for("auth.verify_reset_otp_page"))


@auth_blueprint.get("/reset-password/verify")
def verify_reset_otp_page():
    if session.get("user_id"):
        return redirect(role_landing_url(session.get("user_role", "user")))
    if not session.get("pending_reset_user_id"):
        flash("Enter your email or username first to receive a password reset OTP.", "error")
        return redirect(url_for("auth.forgot_password_page"))
    return render_template("auth/forgot_password_verify.html", **reset_verify_context())


@auth_blueprint.post("/reset-password/verify")
def verify_reset_otp():
    pending_user_id = session.get("pending_reset_user_id")
    if not pending_user_id:
        flash("Your password reset session expired. Please request a new code.", "error")
        return redirect(url_for("auth.forgot_password_page"))

    service = AuthenticationService()
    otp_code = extract_otp_from_request()
    try:
        user = service.verify_email_otp(int(pending_user_id), otp_code)
    except AuthenticationError as error:
        return render_template("auth/forgot_password_verify.html", **reset_verify_context(error=str(error))), 422

    session.pop("pending_reset_otp_code", None)
    session["pending_reset_otp_verified"] = True
    session.modified = True
    flash(f"✓ OTP verified! Confirmed {user['email']} — you may now set your new password.", "success")
    return redirect(url_for("auth.reset_password_page"))


@auth_blueprint.post("/reset-password/resend")
def resend_reset_otp():
    pending_user_id = session.get("pending_reset_user_id")
    if not pending_user_id:
        flash("Enter your email or username to request a password reset code.", "error")
        return redirect(url_for("auth.forgot_password_page"))

    user_stub = {
        "id": int(pending_user_id),
        "email": session.get("pending_reset_email", ""),
        "username": session.get("pending_reset_username", ""),
    }
    otp_result = AuthenticationService().issue_email_otp(
        user_stub["id"], user_stub["email"], user_stub["username"], purpose="password_reset"
    )
    establish_pending_password_reset(user_stub, otp_result)
    flash(f"A new 6-digit password reset code has been sent to {user_stub['email']}.", "success")
    return redirect(url_for("auth.verify_reset_otp_page"))


@auth_blueprint.get("/reset-password")
def reset_password_page():
    if session.get("user_id"):
        return redirect(role_landing_url(session.get("user_role", "user")))
    if not session.get("pending_reset_user_id"):
        flash("Enter your email or username first to reset your password.", "error")
        return redirect(url_for("auth.forgot_password_page"))
    if not session.get("pending_reset_otp_verified"):
        flash("Please verify the 6-digit OTP sent to your email first.", "error")
        return redirect(url_for("auth.verify_reset_otp_page"))
    return render_template(
        "auth/reset_password.html",
        email=session.get("pending_reset_email", ""),
        errors={},
    )


@auth_blueprint.post("/reset-password")
def reset_password():
    pending_user_id = session.get("pending_reset_user_id")
    if not pending_user_id:
        flash("Your password reset session expired. Please request a new code.", "error")
        return redirect(url_for("auth.forgot_password_page"))
    if not session.get("pending_reset_otp_verified"):
        flash("Please verify the 6-digit OTP sent to your email first.", "error")
        return redirect(url_for("auth.verify_reset_otp_page"))

    service = AuthenticationService()
    try:
        service.reset_password(
            int(pending_user_id),
            request.form.get("password", ""),
            request.form.get("password_confirmation", ""),
        )
    except AuthenticationError as error:
        details = error.args[0]
        if isinstance(details, dict):
            return (
                render_template(
                    "auth/reset_password.html",
                    email=session.get("pending_reset_email", ""),
                    errors=details,
                ),
                422,
            )
        flash(str(details), "error")
        return (
            render_template(
                "auth/reset_password.html",
                email=session.get("pending_reset_email", ""),
                errors={},
            ),
            422,
        )

    clear_pending_password_reset()
    flash("✓ Password updated! You can now log in with your new password.", "success")
    return redirect(url_for("auth.login_page"))


@auth_blueprint.post("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home.index"))


@auth_blueprint.post("/password/change")
@login_required
def change_password():
    try:
        AuthenticationService().change_password(
            session["user_id"], request.form.get("current_password", ""),
            request.form.get("new_password", ""), request.form.get("new_password_confirmation", "")
        )
    except (AuthenticationError, AuthorizationError) as error:
        flash(str(error), "error")
        return redirect(request.referrer or url_for("home.user_home"))
    flash("Password updated.", "success")
    return redirect(url_for("home.user_home"))
