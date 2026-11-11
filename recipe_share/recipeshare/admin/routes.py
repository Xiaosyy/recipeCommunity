from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from recipeshare.dashboard.service import DashboardService
from recipeshare.shared.decorators import role_required
from .service import AdminService


admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.get("/dashboard")
@role_required("admin")
def dashboard():
    return render_template(
        "dashboard/index.html",
        layout="app",
        **DashboardService().get_dashboard_data(),
    )


ADMIN_MODULES = {
    "users": "User management",
    "reports": "Reports and moderation",
    "content": "Content moderation",
    "categories": "Category management",
    "activity": "Audit activity",
    "notifications": "Notifications",
    "settings": "System settings",
    "system": "System health",
}


def _admin_module(module: str, title: str):
    service = AdminService()
    context = {"layout": "app", "module": module, "module_title": title, "module_icon": "settings"}
    if module == "users":
        context["rows"] = service.users()
    elif module == "categories":
        context["rows"] = service.categories()
    elif module == "reports":
        context["rows"] = service.reports()
    elif module == "content":
        context["rows"] = service.recipes()
    elif module == "activity":
        context["rows"] = service.activity()
    elif module == "notifications":
        context["rows"] = service.notifications(session["user_id"])
    elif module == "system":
        context["system"] = service.system_overview()
    return render_template("admin/modules.html", **context)


for _path, _title in ADMIN_MODULES.items():
    if _path in {"settings", "system", "categories"}:
        def _redirect_module(title=_title):
            return redirect(url_for("admin.dashboard"))
        _redirect_module.__name__ = f"admin_{_path}"
        admin_blueprint.add_url_rule("/" + _path, endpoint=_redirect_module.__name__, view_func=role_required("admin")(_redirect_module), methods=["GET"])
        continue
    def _module(path=_path, title=_title):
        return _admin_module(path, title)
    _module.__name__ = "admin_" + _path.replace("-", "_")
    admin_blueview_func = role_required("admin")(_module)
    admin_blueprint.add_url_rule("/" + _path, endpoint=_module.__name__, view_func=admin_blueview_func, methods=["GET"])


@admin_blueprint.post("/settings/save")
@role_required("admin")
def save_settings():
    values = {"community_name": request.form.get("community_name", ""), "community_description": request.form.get("community_description", ""), "timezone": request.form.get("timezone", "Asia/Manila")}
    logo = request.files.get("community_logo")
    if logo and logo.filename:
        allowed_extensions = {"png", "jpg", "jpeg", "webp"}
        extension = logo.filename.rsplit(".", 1)[-1].lower() if "." in logo.filename else ""
        logo.seek(0, 2)
        logo_size = logo.tell()
        logo.seek(0)
        signature = logo.read(12)
        logo.seek(0)
        valid_signature = signature.startswith(b"\x89PNG\r\n\x1a\n") or signature.startswith(b"\xff\xd8\xff") or signature.startswith(b"RIFF") and signature[8:12] == b"WEBP"
        if extension not in allowed_extensions or not valid_signature or logo_size > 2 * 1024 * 1024:
            flash("Logo must be a valid PNG, JPG, or WEBP image no larger than 2 MB.", "error")
            return redirect(url_for("admin.admin_settings"))
        upload_directory = Path(current_app.root_path) / "static" / "uploads" / "logos"
        upload_directory.mkdir(parents=True, exist_ok=True)
        logo_filename = f"{uuid4().hex}.{extension}"
        logo.save(upload_directory / logo_filename)
        values["community_logo"] = logo_filename
    try:
        AdminService().save_settings(values, session["user_id"])
        flash("System settings saved.", "success")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("admin.admin_settings"))


@admin_blueprint.post("/users/status")
@role_required("admin")
def update_user_status():
    try:
        AdminService().set_user_status(int(request.form["user_id"]), request.form["status"], session["user_id"])
        flash("User status updated.", "success")
    except (KeyError, TypeError, ValueError):
        flash("Unable to update user status.", "error")
    return redirect(url_for("admin.admin_users"))


@admin_blueprint.post("/users/role")
@role_required("admin")
def update_user_role():
    try:
        AdminService().set_user_role(int(request.form["user_id"]), request.form["role"], session["user_id"])
        flash("User role updated.", "success")
    except (KeyError, TypeError, ValueError):
        flash("Unable to update user role.", "error")
    return redirect(url_for("admin.admin_users"))


@admin_blueprint.post("/users/delete")
@role_required("admin")
def delete_user_permanently():
    try:
        user_id = int(request.form["user_id"])
        deleted = AdminService().delete_user_permanently(user_id, session["user_id"])
        flash(f"User @{deleted['username']} ({deleted['email']}) was permanently deleted.", "success")
    except KeyError:
        flash("User ID is required.", "error")
    except ValueError as error:
        flash(str(error), "error")
    except Exception as error:
        flash(f"Unable to delete user: {error}", "error")
    return redirect(url_for("admin.admin_users"))


@admin_blueprint.post("/categories/save")
@role_required("admin")
def save_category():
    try:
        category_id = request.form.get("category_id")
        active = request.form.get("active") == "1" or request.form.get("active") == "on"
        AdminService().save_category(int(category_id) if category_id else None, request.form["name"], request.form.get("description", ""), active, session["user_id"])
        flash("Category saved.", "success")
    except (KeyError, TypeError, ValueError):
        flash("Unable to save category.", "error")
    return redirect(url_for("admin.admin_categories"))


@admin_blueprint.post("/categories/delete")
@role_required("admin")
def delete_category():
    try:
        AdminService().delete_category(int(request.form["category_id"]), session["user_id"])
        flash("Category deleted.", "success")
    except (KeyError, TypeError, ValueError):
        flash("Unable to delete category.", "error")
    return redirect(url_for("admin.admin_categories"))


@admin_blueprint.post("/reports/status")
@role_required("admin")
def update_report_status():
    try:
        AdminService().resolve_report(int(request.form["report_id"]), request.form["status"], session["user_id"])
        flash("Report updated.", "success")
    except (KeyError, TypeError, ValueError):
        flash("Unable to update report.", "error")
    return redirect(url_for("admin.admin_reports"))


@admin_blueprint.post("/content/status")
@role_required("admin")
def update_content_status():
    try:
        AdminService().set_recipe_status(int(request.form["recipe_id"]), request.form["status"], session["user_id"])
        flash("Recipe status updated.", "success")
    except (KeyError, TypeError, ValueError):
        flash("Unable to update recipe status.", "error")
    return redirect(url_for("admin.admin_content"))
