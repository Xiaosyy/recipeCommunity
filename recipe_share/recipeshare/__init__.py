import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, session

ENV_FILE_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE_PATH, override=True)

from config.settings import load_config
from .extensions import csrf, register_error_handlers
from .home.routes import home_blueprint
from .auth.routes import auth_blueprint
from .admin.routes import admin_blueprint
from .ui import ui_blueprint


def create_app(config_object=None):
    """Create and configure the RecipeShare application."""
    load_dotenv(ENV_FILE_PATH, override=True)
    app = Flask(__name__)

    app.config.from_object(load_config())
    if config_object:
        if isinstance(config_object, dict):
            app.config.from_mapping(config_object)
        else:
            app.config.from_object(config_object)

    csrf.init_app(app)
    register_error_handlers(app)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(ui_blueprint)

    @app.context_processor
    def community_branding():
        try:
            from .admin.service import AdminService
            settings = AdminService().settings()
            logo = settings.get("community_logo")
            branding = {"community_logo_url": app.url_for("static", filename=f"uploads/logos/{logo}") if logo else app.url_for("static", filename="images/recipeshare-favicon.png")}
            if session.get("user_id"):
                from .auth.repository import UserRepository
                avatar = UserRepository().profile_data(session["user_id"])["profile"].get("avatar_path")
                branding["current_user_avatar_url"] = avatar or ""
                from .notifications.repository import NotificationRepository
                branding["notification_unread_count"] = NotificationRepository().unread_count(session["user_id"])
            return branding
        except Exception:
            return {"community_logo_url": app.url_for("static", filename="images/recipeshare-favicon.png"), "current_user_avatar_url": ""}

    return app
