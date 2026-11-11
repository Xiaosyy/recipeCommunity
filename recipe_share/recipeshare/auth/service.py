from email.message import EmailMessage
from email.utils import formataddr
import logging
import os
from pathlib import Path
import re
import secrets
import smtplib
import socket
import ssl

from dotenv import load_dotenv, set_key
from werkzeug.security import check_password_hash, generate_password_hash

from recipeshare.shared.exceptions import DuplicateRecordError, RecordNotFoundError
from .repository import UserRepository


ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"
STATIC_IMAGES_DIR = Path(__file__).resolve().parents[1] / "static" / "images"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,30}$")
OTP_PATTERN = re.compile(r"^\d{6}$")
DEFAULT_OTP_EXPIRY_SECONDS = 60
DEFAULT_OTP_MAX_ATTEMPTS = 5

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class EmailNotVerifiedError(AuthenticationError):
    def __init__(self, message: str, user: dict) -> None:
        super().__init__(message)
        self.user = user


class AuthenticationService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    def register(self, username: str, email: str, password: str, password_confirmation: str) -> dict:
        errors = self._registration_errors(username, email, password, password_confirmation)
        if errors:
            raise AuthenticationError(errors)
        try:
            user = self.repository.create(
                username.strip(), email.strip().lower(), generate_password_hash(password, method="scrypt")
            )
        except DuplicateRecordError as error:
            raise AuthenticationError({"username": ["Username or email already exists."]}) from error
        if user is None:
            raise RecordNotFoundError("Created user could not be loaded")
        return user

    def authenticate(self, email_or_username: str, password: str) -> dict:
        user = self.repository.find_by_login(email_or_username.strip())
        if user is None or not check_password_hash(user["password_hash"], password):
            raise AuthenticationError("Invalid email/username or password.")
        if user["status"] != "active":
            raise AuthorizationError("This account is not active.")
        if "email_verified_at" in user and user["email_verified_at"] is None:
            raise EmailNotVerifiedError(
                "Please verify your email address with the 6-digit OTP code before logging in.",
                user,
            )
        return user

    def issue_email_otp(
        self,
        user_id: int,
        email: str,
        username: str = "",
        expiry_seconds: int | None = None,
        purpose: str = "verification",
    ) -> dict:
        normalized_email = email.strip().lower()
        ttl_seconds = expiry_seconds or int(os.getenv("OTP_EXPIRY_SECONDS", str(DEFAULT_OTP_EXPIRY_SECONDS)))
        otp_code = self.generate_otp_code()
        otp_hash = generate_password_hash(otp_code, method="scrypt")
        sent_via_smtp, smtp_error = self._send_otp_email(
            recipient_email=normalized_email,
            username=username or normalized_email,
            otp_code=otp_code,
            expiry_seconds=ttl_seconds,
            purpose=purpose,
        )
        self.repository.create_email_verification(
            user_id=user_id,
            email=normalized_email,
            otp_hash=otp_hash,
            expiry_seconds=ttl_seconds,
        )
        try:
            from recipeshare.notifications.repository import NotificationRepository
            purpose_label = "Password reset" if purpose == "password_reset" else "Email verification"
            NotificationRepository().create(
                user_id,
                "otp_sent",
                {
                    "title": f"{purpose_label} Code Sent",
                    "message": f"A 6-digit verification code was sent to {normalized_email}.",
                    "email": normalized_email,
                    "purpose": purpose,
                    "expires_seconds": ttl_seconds,
                },
            )
        except Exception as notify_err:
            logger.debug("Could not record OTP notification: %s", notify_err)
        return {
            "otp_code": otp_code,
            "sent_via_smtp": sent_via_smtp,
            "smtp_error": smtp_error,
            "expires_seconds": ttl_seconds,
            "masked_email": self.mask_email(normalized_email),
        }

    def verify_email_otp(self, user_id: int, otp_code: str, max_attempts: int | None = None) -> dict:
        cleaned_code = "".join(str(otp_code or "").split())
        if not OTP_PATTERN.fullmatch(cleaned_code):
            raise AuthenticationError("Enter a valid 6-digit verification code.")

        allowed_attempts = max_attempts or int(os.getenv("OTP_MAX_ATTEMPTS", str(DEFAULT_OTP_MAX_ATTEMPTS)))
        if hasattr(self.repository, "active_email_verifications"):
            records = self.repository.active_email_verifications(user_id)
        else:
            latest = self.repository.latest_email_verification(user_id)
            records = [latest] if latest else []

        if not records:
            raise AuthenticationError("No active verification code found. Please request a new code.")

        record = records[0]
        if record.get("is_expired"):
            raise AuthenticationError("This verification code has expired. Please request a new code.")
        if int(record.get("attempts", 0)) >= allowed_attempts:
            raise AuthenticationError("Too many invalid attempts. Please request a new verification code.")

        matched_record = None
        for candidate in records:
            if candidate and not candidate.get("is_expired") and int(candidate.get("attempts", 0)) < allowed_attempts:
                if check_password_hash(candidate["otp_hash"], cleaned_code):
                    matched_record = candidate
                    break

        if matched_record is None:
            attempts = self.repository.increment_verification_attempts(record["id"])
            remaining = max(0, allowed_attempts - attempts)
            if remaining == 0:
                raise AuthenticationError("Too many invalid attempts. Please request a new verification code.")
            suffix = "attempt" if remaining == 1 else "attempts"
            raise AuthenticationError(f"Invalid verification code. {remaining} {suffix} remaining.")

        verified_user = self.repository.mark_email_verified(user_id, matched_record["id"])
        if verified_user is None:
            raise RecordNotFoundError("User could not be loaded after email verification")
        try:
            from recipeshare.notifications.repository import NotificationRepository
            NotificationRepository().create(
                user_id,
                "account_verified",
                {
                    "title": "Account Email Verified",
                    "message": "Your email address has been successfully verified. Welcome to RecipeShare!",
                    "email": verified_user.get("email", ""),
                },
            )
        except Exception as notify_err:
            logger.debug("Could not record verification notification: %s", notify_err)
        return verified_user

    def change_password(self, user_id: int, current_password: str, new_password: str, confirmation: str) -> None:
        user = self.repository.find_by_id(user_id)
        current = self.repository.find_by_login(user["email"])
        if current is None or not check_password_hash(current["password_hash"], current_password):
            raise AuthenticationError("Current password is incorrect.")
        password_errors = self.validate_password_strength(new_password)
        if password_errors or new_password != confirmation:
            if new_password != confirmation:
                password_errors.append("Passwords do not match.")
            raise AuthenticationError(" ".join(password_errors))
        self.repository.update_password(user_id, generate_password_hash(new_password, method="scrypt"))

    def request_password_reset(self, email_or_username: str) -> tuple[dict, dict]:
        cleaned = (email_or_username or "").strip()
        if not cleaned:
            raise AuthenticationError("Please enter your email address or username.")
        user = self.repository.find_by_login(cleaned)
        if user is None:
            raise AuthenticationError("No account found with that email or username.")
        if user.get("status") != "active":
            raise AuthorizationError("This account is not active.")
        otp_result = self.issue_email_otp(
            user_id=user["id"],
            email=user["email"],
            username=user.get("username", ""),
            purpose="password_reset",
        )
        return user, otp_result

    def reset_password(self, user_id: int, new_password: str, confirmation: str) -> dict:
        errors: dict[str, list[str]] = {}
        password_issues = self.validate_password_strength(new_password or "")
        if password_issues:
            errors["password"] = password_issues
        if (new_password or "") != (confirmation or ""):
            errors.setdefault("password_confirmation", []).append("Passwords do not match.")
        if errors:
            raise AuthenticationError(errors)

        self.repository.update_password(user_id, generate_password_hash(new_password, method="scrypt"))
        user = self.repository.find_by_id(user_id)
        if user is None:
            raise RecordNotFoundError("User not found")
        return user

    @staticmethod
    def generate_otp_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def mask_email(email: str) -> str:
        cleaned = (email or "").strip()
        if "@" not in cleaned:
            return cleaned
        local, domain = cleaned.split("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "*" * max(1, len(local) - 1) if local else "*"
        else:
            masked_local = f"{local[0]}{'*' * min(4, len(local) - 2)}{local[-1]}"
        return f"{masked_local}@{domain}"

    @staticmethod
    def save_gmail_smtp_credentials(smtp_user: str, smtp_password: str) -> None:
        cleaned_user = smtp_user.strip().lower()
        cleaned_password = smtp_password.replace(" ", "").strip()
        if not EMAIL_PATTERN.fullmatch(cleaned_user) or not cleaned_password:
            raise AuthenticationError("Enter a valid Gmail address and 16-character Google App Password.")
        set_key(str(ENV_FILE_PATH), "SMTP_HOST", "smtp.gmail.com", quote_mode="never")
        set_key(str(ENV_FILE_PATH), "SMTP_PORT", "587", quote_mode="never")
        set_key(str(ENV_FILE_PATH), "SMTP_USE_TLS", "true", quote_mode="never")
        set_key(str(ENV_FILE_PATH), "SMTP_USER", cleaned_user, quote_mode="never")
        set_key(str(ENV_FILE_PATH), "SMTP_PASSWORD", cleaned_password, quote_mode="never")
        set_key(str(ENV_FILE_PATH), "SMTP_FROM_EMAIL", cleaned_user, quote_mode="never")
        os.environ["SMTP_HOST"] = "smtp.gmail.com"
        os.environ["SMTP_PORT"] = "587"
        os.environ["SMTP_USE_TLS"] = "true"
        os.environ["SMTP_USER"] = cleaned_user
        os.environ["SMTP_PASSWORD"] = cleaned_password
        os.environ["SMTP_FROM_EMAIL"] = cleaned_user

    @staticmethod
    def _send_otp_email(
        recipient_email: str,
        username: str,
        otp_code: str,
        expiry_seconds: int,
        purpose: str = "verification",
    ) -> tuple[bool, str]:
        load_dotenv(ENV_FILE_PATH, override=True)
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip() or "smtp.gmail.com"
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "").strip()
        smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "").strip()
        smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        smtp_from = os.getenv("SMTP_FROM_EMAIL", "").strip() or smtp_user or "noreply@recipeshare.local"

        if not smtp_user or not smtp_password:
            msg = "Gmail sender credentials (SMTP_USER and 16-character Google App Password) are not set yet."
            logger.warning("%s OTP for %s is %s (expires in %s seconds).", msg, recipient_email, otp_code, expiry_seconds)
            return False, msg

        if os.getenv("PYTEST_CURRENT_TEST"):
            return True, ""

        from_address = smtp_from
        if "@" in smtp_from:
            local_part, domain_part = smtp_from.split("@", 1)
            if domain_part.lower() == "gmail.com" and "+" not in local_part:
                from_address = f"{local_part}+recipeshare@{domain_part}"

        is_reset = purpose == "password_reset"
        subject_label = "password reset code" if is_reset else "verification code"
        badge_label = "Official System Security • Password Reset" if is_reset else "Official System Security • Email Verification"
        heading_label = "Reset Your RecipeShare Password" if is_reset else "Verify Your Email Address"
        body_prompt = (
            "Enter the 6-digit password reset code below on RecipeShare Community to confirm your identity and set a new password:"
            if is_reset
            else "Enter the 6-digit verification code below on RecipeShare Community to confirm that you are the real owner of this email address:"
        )

        message = EmailMessage()
        message["Subject"] = f"{otp_code} is your RecipeShare Community {subject_label}"
        message["From"] = formataddr(("RecipeShare Community", from_address))
        message["To"] = recipient_email
        message.set_content(
            f"RecipeShare Community — {heading_label}\n\n"
            f"Hi {username},\n\n"
            f"Your RecipeShare Community 6-digit {subject_label} is: {otp_code}\n\n"
            f"This code will expire in {expiry_seconds} seconds.\n"
            f"If you did not request this code, you can safely ignore this email.\n"
        )
        message.add_alternative(
            f"""\
            <html>
              <body style="margin: 0; font-family: 'Segoe UI', Arial, sans-serif; background: #eef2ed; padding: 28px 16px; color: #1f2d27;">
                <div style="max-width: 480px; margin: 0 auto; background: #ffffff; border-radius: 14px; overflow: hidden; border: 1px solid #d9e1dd; box-shadow: 0 8px 24px rgba(13, 56, 45, 0.08);">
                  <div style="background: #0d382d; padding: 18px 24px; display: flex; align-items: center;">
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="width: 100%;">
                      <tr>
                        <td style="width: 52px; vertical-align: middle;">
                          <img src="cid:recipeshare_avatar" alt="RecipeShare Community" width="44" height="44" style="display: block; width: 44px; height: 44px; border-radius: 50%; background: #ffffff; border: 2px solid #ffffff; object-fit: cover;">
                        </td>
                        <td style="vertical-align: middle; padding-left: 10px;">
                          <div style="font-size: 16px; font-weight: 700; color: #ffffff; line-height: 1.2;">RecipeShare Community</div>
                          <div style="font-size: 12px; color: #b7d7c8; margin-top: 2px;">{badge_label}</div>
                        </td>
                      </tr>
                    </table>
                  </div>
                  <div style="padding: 28px 32px 32px;">
                    <div style="text-align: center; margin-bottom: 18px;">
                      <img src="cid:recipeshare_logo" alt="RecipeShare Community Logo" width="160" style="display: inline-block; max-width: 160px; height: auto;">
                    </div>
                    <h2 style="margin: 0 0 12px; color: #0d382d; text-align: center; font-size: 21px;">{heading_label}</h2>
                    <p style="margin: 0 0 8px; font-size: 14px; line-height: 1.5;">Hi <strong>{username}</strong>,</p>
                    <p style="margin: 0 0 20px; font-size: 14px; line-height: 1.5; color: #40524a;">
                      {body_prompt}
                    </p>
                    <div style="margin: 20px 0; padding: 18px 16px; background: #f0f9f4; border: 1.5px solid #b7e1cd; border-radius: 10px; text-align: center; font-size: 30px; font-weight: 800; letter-spacing: 8px; color: #177252;">
                      {otp_code}
                    </div>
                    <p style="margin: 0; font-size: 13px; color: #66756e; text-align: center;">
                      This verification code expires in <strong>{expiry_seconds} seconds</strong>.
                    </p>
                  </div>
                </div>
              </body>
            </html>
            """,
            subtype="html",
        )

        html_part = message.get_body(preferencelist=("html",))
        if html_part is not None:
            avatar_path = STATIC_IMAGES_DIR / "recipeshare-favicon.png"
            logo_path = STATIC_IMAGES_DIR / "recipeshare-logo.png"
            if avatar_path.exists():
                html_part.add_related(
                    avatar_path.read_bytes(),
                    maintype="image",
                    subtype="png",
                    cid="<recipeshare_avatar>",
                    filename="recipeshare-profile.png",
                )
            if logo_path.exists():
                html_part.add_related(
                    logo_path.read_bytes(),
                    maintype="image",
                    subtype="png",
                    cid="<recipeshare_logo>",
                    filename="recipeshare-logo.png",
                )

        server = None
        try:
            connect_host = smtp_host
            try:
                addr_info = socket.getaddrinfo(smtp_host, smtp_port, socket.AF_INET, socket.SOCK_STREAM)
                if addr_info:
                    connect_host = addr_info[0][4][0]
            except OSError:
                connect_host = smtp_host

            if smtp_port == 465:
                tls_context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(connect_host, smtp_port, local_hostname="localhost", timeout=4, context=tls_context)
                server._host = smtp_host
                server.ehlo()
            else:
                server = smtplib.SMTP(connect_host, smtp_port, local_hostname="localhost", timeout=4)
                server._host = smtp_host
                server.ehlo()
                if smtp_use_tls:
                    tls_context = ssl.create_default_context()
                    server.starttls(context=tls_context)
                    server.ehlo()

            if "auth" in server.esmtp_features:
                server.esmtp_features["auth"] = "PLAIN"
            server.login(smtp_user, smtp_password)
            server.send_message(message)
            try:
                server.quit()
            except Exception:
                pass
            return True, ""
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected) as error:
            err_msg = (
                f"Gmail rejected SMTP_PASSWORD for {smtp_user} (SMTP 535). "
                "Google blocks regular Gmail passwords on smtp.gmail.com — please generate a 16-letter "
                "Google App Password at https://myaccount.google.com/apppasswords and set it as SMTP_PASSWORD in .env."
            )
            logger.error("SMTP authentication failed for %s: %s (OTP for %s: %s)", smtp_user, error, recipient_email, otp_code)
            return False, err_msg
        except Exception as error:
            err_msg = f"Could not deliver email via {smtp_host}: {error}"
            logger.error("Failed to send OTP email to %s via %s: %s (OTP: %s)", recipient_email, smtp_host, error, otp_code)
            return False, err_msg
        finally:
            if server is not None:
                try:
                    server.close()
                except Exception:
                    pass

    @staticmethod
    def validate_password_strength(password: str) -> list[str]:
        issues: list[str] = []
        if len(password) < 8:
            issues.append("At least 8 characters.")
        if not (re.search(r"[A-Z]", password) and re.search(r"[a-z]", password)):
            issues.append("Uppercase and lowercase letters.")
        if not re.search(r"\d", password):
            issues.append("Contains numbers.")
        if not re.search(r"[^A-Za-z0-9\s]", password):
            issues.append("Contains special characters.")
        return issues

    @classmethod
    def _registration_errors(cls, username: str, email: str, password: str, confirmation: str) -> dict[str, list[str]]:
        errors: dict[str, list[str]] = {}
        username = username.strip()
        email = email.strip()
        if not USERNAME_PATTERN.fullmatch(username):
            errors.setdefault("username", []).append("Use 3 to 30 letters, numbers, or underscores.")
        if not EMAIL_PATTERN.fullmatch(email):
            errors.setdefault("email", []).append("Enter a valid email address.")
        password_issues = cls.validate_password_strength(password)
        if password_issues:
            errors.setdefault("password", []).extend(password_issues)
        if password != confirmation:
            errors.setdefault("password_confirmation", []).append("Passwords do not match.")
        return errors
