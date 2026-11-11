from flask import Blueprint, abort, jsonify, render_template, request, session

from recipeshare.dashboard.service import DashboardService
from recipeshare.home.service import HomeService
from recipeshare.location.service import LocationRecipeService
from recipeshare.home.repository import HomeRepository
from recipeshare.admin.service import AdminService
from recipeshare.auth.repository import UserRepository
from recipeshare.notifications.repository import NotificationRepository


ui_blueprint = Blueprint("ui_api", __name__, url_prefix="/api/v1/ui")


def require_recipe_action():
    user_id = session.get("user_id")
    if user_id is None:
        return None, (jsonify({"error": {"code": "UNAUTHORIZED", "message": "Please log in."}}), 401)
    data = request.get_json(silent=True) or {}
    slug = data.get("slug")
    recipe = HomeService().recipe_detail(slug, user_id) if slug else None
    if recipe is None:
        return None, (jsonify({"error": {"code": "NOT_FOUND", "message": "Recipe not found."}}), 404)
    return (user_id, recipe, data), None


@ui_blueprint.post("/recipe-actions/like")
def recipe_like():
    payload, error = require_recipe_action()
    if error:
        return error
    user_id, recipe, _ = payload
    active = HomeRepository().toggle_like(recipe["id"], user_id)
    if active and user_id != recipe["author_id"]:
        NotificationRepository().create(
            recipe["author_id"],
            "recipe_liked",
            {
                "actor_id": user_id,
                "actor_name": session.get("username", "A member"),
                "recipe_id": recipe["id"],
                "recipe_title": recipe["title"],
                "recipe_slug": recipe["slug"],
            },
        )
    counts = HomeRepository().interaction_counts(recipe["id"])
    return jsonify({"active": active, **counts})


@ui_blueprint.post("/recipe-actions/save")
def recipe_save():
    payload, error = require_recipe_action()
    if error:
        return error
    user_id, recipe, _ = payload
    active = HomeRepository().toggle_favorite(recipe["id"], user_id)
    if active and user_id != recipe["author_id"]:
        NotificationRepository().create(
            recipe["author_id"],
            "recipe_saved",
            {
                "actor_id": user_id,
                "actor_name": session.get("username", "A member"),
                "recipe_id": recipe["id"],
                "recipe_title": recipe["title"],
                "recipe_slug": recipe["slug"],
            },
        )
    counts = HomeRepository().interaction_counts(recipe["id"])
    return jsonify({"active": active, **counts})


@ui_blueprint.post("/recipe-actions/follow")
def recipe_follow():
    payload, error = require_recipe_action()
    if error:
        return error
    user_id, recipe, _ = payload
    if user_id == recipe["author_id"]:
        return jsonify({"error": {"code": "VALIDATION", "message": "You cannot follow your own account."}}), 422
    active = HomeRepository().toggle_follow(recipe["author_id"], user_id)
    if active:
        NotificationRepository().create(
            recipe["author_id"],
            "user_followed",
            {
                "message": f"{session.get('username', 'A community member')} started following you.",
                "actor_id": user_id,
                "actor_name": session.get("username", "A community member"),
                "recipe_slug": recipe["slug"],
                "recipe_title": recipe.get("title", ""),
            },
        )
    follower_count = UserRepository().follower_count(recipe["author_id"])
    return jsonify({
        "active": active,
        "author_id": recipe["author_id"],
        "author_name": recipe.get("author_name"),
        "follower_count": follower_count,
    })


@ui_blueprint.post("/users/<int:target_user_id>/follow")
def user_follow_by_id(target_user_id: int):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Please log in to follow chefs."}}), 401
    if user_id == target_user_id:
        return jsonify({"error": {"code": "VALIDATION", "message": "You cannot follow your own account."}}), 422
    target_user = UserRepository().find_by_id(target_user_id)
    if not target_user:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Chef not found."}}), 404

    active = HomeRepository().toggle_follow(target_user_id, user_id)
    if active:
        NotificationRepository().create(
            target_user_id,
            "user_followed",
            {
                "message": f"{session.get('username', 'A member')} started following you.",
                "actor_id": user_id,
                "actor_name": session.get("username", "A member"),
            },
        )
    follower_count = UserRepository().follower_count(target_user_id)
    following_count = UserRepository().following_count(user_id)
    return jsonify({
        "active": active,
        "target_user_id": target_user_id,
        "follower_count": follower_count,
        "following_count": following_count,
    })


@ui_blueprint.post("/users/<username>/follow")
def user_follow_by_username(username: str):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": {"code": "UNAUTHORIZED", "message": "Please log in to follow chefs."}}), 401
    target_user = UserRepository().find_by_identity(username)
    if not target_user:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Chef not found."}}), 404
    return user_follow_by_id(target_user["id"])


@ui_blueprint.get("/dashboard-stats")
def dashboard_stats():
    period = request.args.get("period", "all").strip().lower()
    if period not in {"week", "month", "all"}:
        period = "all"
    data = DashboardService().get_dashboard_data(user_id=None, period=period)
    if session.get("user_id"):
        data["user_metrics"] = DashboardService().repository.metrics(session.get("user_id"))
    response = jsonify(data)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@ui_blueprint.post("/recipe-actions/rate")
def recipe_rate():
    payload, error = require_recipe_action()
    if error:
        return error
    user_id, recipe, data = payload
    try:
        score = int(data.get("rating"))
    except (TypeError, ValueError):
        return jsonify({"error": {"code": "VALIDATION", "message": "Rating must be from 1 to 5."}}), 422
    if score < 1 or score > 5:
        return jsonify({"error": {"code": "VALIDATION", "message": "Rating must be from 1 to 5."}}), 422
    repository = HomeRepository()
    repository.set_rating(recipe["id"], user_id, score)
    return jsonify({"active": True, "user_rating": score, **repository.interaction_counts(recipe["id"])})


@ui_blueprint.get("/profile-statistics")
def profile_statistics():
    if session.get("user_id") is None:
        abort(401)
    data = UserRepository().profile_data(session["user_id"])
    response = jsonify({"recipe_count": data["recipe_count"], "follower_count": data["follower_count"], "like_count": data["like_count"]})
    response.headers["Cache-Control"] = "no-store"
    return response


@ui_blueprint.get("/notifications")
def notifications():
    user_id = session.get("user_id")
    if user_id is None:
        abort(401)
    repository = NotificationRepository()
    return jsonify({
        "unread_count": repository.unread_count(user_id),
        "items": repository.list_for_user(user_id),
    })


@ui_blueprint.post("/notifications/read")
def read_notifications():
    user_id = session.get("user_id")
    if user_id is None:
        abort(401)
    NotificationRepository().mark_all_read(user_id)
    return jsonify({"unread_count": 0})


@ui_blueprint.post("/locations/generate")
def api_generate_location_recipe():
    payload = request.get_json(silent=True) or {}
    location_id = int(payload.get("location_id") or 1)
    service = LocationRecipeService()
    raw_loc = service.repository.location_by_id(location_id)
    if not raw_loc:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Location not found"}}), 404
    existing_count = int(raw_loc.get("recipe_count") or 0)
    recipe_id = service.generate_recipe_for_location(raw_loc, existing_count=existing_count)
    return jsonify({
        "ok": True,
        "recipe_id": recipe_id,
        "location_id": location_id,
        "location_name": raw_loc["name"],
    })


@ui_blueprint.get("/navigation")
def navigation():
    return jsonify({
        "navigation": [
            {"id": "dashboard", "label": "Dashboard", "path": "/dashboard", "icon": "dashboard"},
            {"id": "recipes", "label": "Recipes", "path": "/recipes", "icon": "recipe"},
            {"id": "create-recipe", "label": "Create recipe", "path": "/recipes/create", "icon": "create"},
            {"id": "categories", "label": "Categories", "path": "/categories", "icon": "category"},
            {"id": "favorites", "label": "Favorites", "path": "/favorites", "icon": "heart"},
            {"id": "settings", "label": "Settings", "path": "/settings", "icon": "settings"},
        ],
        "user": None,
        "notifications": {"unread_count": NotificationRepository().unread_count(session["user_id"])} if session.get("user_id") else {"unread_count": 0},
        "location": None,
    })


@ui_blueprint.get("/pages/")
def home_fragment():
    return render_page_fragment("")


@ui_blueprint.get("/pages/<path:view_path>")
def page_fragment(view_path):
    return render_page_fragment(view_path)


def render_page_fragment(view_path):
    alias_map = {
        "profile": "users/me",
        "recipes/new": "recipes/create",
        "inventory": "dashboard",
    }
    redirect_path = None
    if view_path in alias_map:
        view_path = alias_map[view_path]
        redirect_path = f"/{view_path}"

    auth_views = {"login", "register", "verify-email", "forgot-password", "reset-password/verify", "reset-password"}
    if view_path in auth_views and session.get("user_id") is not None:
        view_path = "admin/dashboard" if session.get("user_role") == "admin" else "dashboard"
        redirect_path = f"/{view_path}"
    elif view_path == "verify-email" and not session.get("pending_verification_user_id"):
        view_path = "login"
        redirect_path = "/login"
    elif view_path == "reset-password/verify" and not session.get("pending_reset_user_id"):
        view_path = "forgot-password"
        redirect_path = "/forgot-password"
    elif view_path == "reset-password":
        if not session.get("pending_reset_user_id"):
            view_path = "forgot-password"
            redirect_path = "/forgot-password"
        elif not session.get("pending_reset_otp_verified"):
            view_path = "reset-password/verify"
            redirect_path = "/reset-password/verify"

    if view_path.startswith("recipes/") and view_path.endswith("/edit") and view_path != "recipes/create":
        if session.get("user_id") is None:
            abort(401)
        slug = view_path.removeprefix("recipes/").removesuffix("/edit")
        recipe = HomeService().recipe_detail(slug, session.get("user_id"))
        if recipe is None:
            return jsonify({"error": {"code": "NOT_FOUND", "message": "Recipe not found", "fields": {}}}), 404
        if recipe["author_id"] != session.get("user_id") and session.get("user_role") != "admin":
            abort(403)
        html = render_template(
            "modules/recipe_create.html",
            layout="app",
            spa_fragment=True,
            edit_mode=True,
            recipe=recipe,
            categories=HomeRepository().active_categories(limit=100),
            locations=LocationRecipeService().locations(),
        )
        return jsonify({"title": f"Edit {recipe['title']} — RecipeShare", "html": html, "layout": "app", "page_state": {}})

    if view_path.startswith("recipes/") and view_path != "recipes/create":
        slug = view_path.removeprefix("recipes/")
        recipe = HomeService().recipe_detail(slug, session.get("user_id"))
        if recipe is None:
            return jsonify({"error": {"code": "NOT_FOUND", "message": "Recipe not found", "fields": {}}}), 404
        HomeRepository().increment_view(recipe["id"])
        recipe["view_count"] = recipe.get("view_count", 0) + 1
        detail_layout = "app" if session.get("user_id") else "public"
        html = render_template("recipes/detail.html", layout=detail_layout, spa_fragment=True, recipe=recipe)
        return jsonify({"title": f"{recipe['title']} — RecipeShare", "html": html, "layout": detail_layout, "page_state": {}})

    if view_path.startswith("users/") and view_path != "users/me":
        parts = view_path.split("/")
        username = parts[1]
        subview = parts[2] if len(parts) > 2 else "profile"
        target_user = UserRepository().find_by_identity(username)
        if not target_user:
            return jsonify({"error": {"code": "NOT_FOUND", "message": "User not found", "fields": {}}}), 404
        target_uid = target_user["id"]
        viewer_id = session.get("user_id")
        repo = UserRepository()
        profile_data = repo.profile_data(target_uid, viewer_id=viewer_id)
        is_owner = bool(viewer_id and viewer_id == target_uid)
        layout = "app" if viewer_id else "public"

        if subview == "profile":
            html = render_template("modules/profile.html", layout=layout, spa_fragment=True, is_owner=is_owner, **profile_data)
            return jsonify({"title": f"{profile_data['profile']['display_name']} — RecipeShare", "html": html, "layout": layout, "page_state": {}})
        elif subview == "followers":
            user_list = repo.followers(target_uid, viewer_id=viewer_id)
            html = render_template(
                "modules/profile_collection.html",
                layout=layout,
                spa_fragment=True,
                active_tab="followers",
                page_title="Followers",
                page_icon="♣",
                user_list=user_list,
                total_count=len(user_list),
                follower_count=len(user_list),
                item_label="follower" if len(user_list) == 1 else "followers",
                current_user_id=viewer_id,
                is_owner=is_owner,
                **profile_data,
            )
            return jsonify({"title": f"Followers — RecipeShare", "html": html, "layout": layout, "page_state": {}})
        elif subview == "following":
            user_list = repo.following(target_uid, viewer_id=viewer_id)
            html = render_template(
                "modules/profile_collection.html",
                layout=layout,
                spa_fragment=True,
                active_tab="following",
                page_title="Following",
                page_icon="⚑",
                user_list=user_list,
                total_count=len(user_list),
                following_count=len(user_list),
                item_label="chef" if len(user_list) == 1 else "chefs",
                current_user_id=viewer_id,
                is_owner=is_owner,
                **profile_data,
            )
            return jsonify({"title": f"Following — RecipeShare", "html": html, "layout": layout, "page_state": {}})
        elif subview == "likes":
            recipes = repo.liked_recipes(target_uid)
            html = render_template(
                "modules/profile_collection.html",
                layout=layout,
                spa_fragment=True,
                active_tab="likes",
                page_title="Liked Recipes",
                page_icon="♥",
                recipes=recipes,
                total_count=len(recipes),
                like_count=len(recipes),
                item_label="recipe" if len(recipes) == 1 else "recipes",
                current_user_id=viewer_id,
                is_owner=is_owner,
                **profile_data,
            )
            return jsonify({"title": f"Liked Recipes — RecipeShare", "html": html, "layout": layout, "page_state": {}})

    if view_path in {"home", "dashboard", "search", "recipes/create", "posts/create", "my-recipes", "drafts", "my-posts", "favorites", "followers", "following", "likes", "messages", "settings", "users/me"} and session.get("user_id") is None:
        abort(401)
    if view_path == "dashboard":
        if session.get("user_id") is None:
            abort(401)
        if session.get("user_role") not in {"user", "admin"}:
            abort(403)
        if session.get("user_role") == "admin":
            abort(403)
    if view_path == "admin/dashboard" or view_path.startswith("admin/"):
        if session.get("user_id") is None:
            abort(401)
        if session.get("user_role") != "admin":
            abort(403)

    templates = {
        "": ("home/index.html", "RecipeShare — Home"),
        "home": ("home/account.html", "Home — RecipeShare"),
        "dashboard": ("dashboard/index.html", "Recipe Inventory — RecipeShare"),
        "search": ("search/results.html", "Search — RecipeShare"),
        "admin/dashboard": ("dashboard/index.html", "Recipe Inventory — RecipeShare"),
        "admin/users": ("admin/modules.html", "User management — RecipeShare"),
        "admin/reports": ("admin/modules.html", "Reports and moderation — RecipeShare"),
        "admin/content": ("admin/modules.html", "Content moderation — RecipeShare"),
        "admin/categories": ("admin/modules.html", "Category management — RecipeShare"),
        "admin/activity": ("admin/modules.html", "Audit activity — RecipeShare"),
        "admin/notifications": ("admin/modules.html", "Notifications — RecipeShare"),
        "admin/settings": ("admin/settings.html", "System settings — RecipeShare"),
        "admin/system": ("admin/modules.html", "System health — RecipeShare"),
        "recipes": ("modules/recipes.html", "Recipes — RecipeShare"),
        "categories": ("modules/categories.html", "Categories — RecipeShare"),
        "locations": ("modules/locations.html", "Locations — RecipeShare"),
        "login": ("auth/login.html", "Log in — RecipeShare"),
        "register": ("auth/register.html", "Sign up — RecipeShare"),
        "verify-email": ("auth/verify_email.html", "Verify Email — RecipeShare"),
        "forgot-password": ("auth/forgot_password.html", "Forgot Password — RecipeShare"),
        "reset-password/verify": ("auth/forgot_password_verify.html", "Verify Reset OTP — RecipeShare"),
        "reset-password": ("auth/reset_password.html", "Reset Password — RecipeShare"),
        "recipes/create": ("modules/recipe_create.html", "Create Recipe — RecipeShare"),
        "posts/create": ("modules/post_create.html", "Create Post — RecipeShare"),
        "my-recipes": ("modules/profile_collection.html", "My Recipes — RecipeShare"),
        "drafts": ("modules/profile_collection.html", "Draft Recipes — RecipeShare"),
        "favorites": ("modules/profile_collection.html", "Saved Recipes — RecipeShare"),
        "followers": ("modules/profile_collection.html", "Followers — RecipeShare"),
        "following": ("modules/profile_collection.html", "Following — RecipeShare"),
        "likes": ("modules/profile_collection.html", "Liked Recipes — RecipeShare"),
        "messages": ("modules/placeholder.html", "Messages — RecipeShare"),
        "settings": ("modules/profile_settings.html", "Settings — RecipeShare"),
        "my-posts": ("modules/profile_collection.html", "My Posts — RecipeShare"),
        "users/me": ("modules/profile.html", "Profile — RecipeShare"),
        "about": ("modules/placeholder.html", "About RecipeShare — RecipeShare"),
        "privacy": ("modules/privacy.html", "Privacy Policy — RecipeShare"),
        "terms": ("modules/terms.html", "Terms of Service — RecipeShare"),
    }
    if view_path not in templates:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "View not found", "fields": {}}}), 404

    template_name, title = templates[view_path]
    app_placeholder_routes = {"recipes/create", "posts/create", "my-recipes", "drafts", "my-posts", "favorites", "followers", "following", "likes", "messages", "settings", "users/me"}
    if view_path.startswith("admin/"):
        app_placeholder_routes.add(view_path)
    is_app_view = view_path in {"home", "dashboard", "search", "admin/dashboard", *app_placeholder_routes} or (
        bool(session.get("user_id")) and view_path in {"recipes", "categories", "locations", "about", "privacy", "terms"}
    )
    context = {"layout": "app" if is_app_view else "public", "spa_fragment": True}
    placeholder_data = {
        "recipes/create": ("Create Recipe", "create"), "posts/create": ("Create Post", "create"), "inventory": ("Inventory", "inventory"),
        "my-recipes": ("My Recipes", "recipes"), "drafts": ("Draft Recipes", "create"), "my-posts": ("My Posts", "recipes"), "favorites": ("Favorites", "heart"),
        "messages": ("Messages", "message"), "settings": ("Settings", "settings"), "users/me": ("My Profile", "dashboard"),
        "about": ("About RecipeShare", "recipes"), "privacy": ("Privacy Policy", "settings"), "terms": ("Terms of Service", "settings"),
        "admin/users": ("User management", "dashboard"), "admin/reports": ("Reports and moderation", "message"),
        "admin/content": ("Content moderation", "recipes"), "admin/categories": ("Category management", "categories"),
        "admin/activity": ("Audit activity", "inventory"), "admin/notifications": ("Notifications", "message"),
        "admin/settings": ("System settings", "settings"), "admin/system": ("System health", "inventory"),
    }
    if view_path in placeholder_data:
        context.update(module_title=placeholder_data[view_path][0], module_icon=placeholder_data[view_path][1])
    if view_path == "home":
        profile_data = UserRepository().profile_data(session["user_id"])
        context.update(profile=profile_data["profile"], recipe_count=profile_data["recipe_count"])
        context.update(DashboardService().get_dashboard_data(session["user_id"]))
        discovery = HomeService().discovery()
        context.update(discovery)
    if view_path in {"dashboard", "admin/dashboard"}:
        target_uid = session.get("user_id") if session.get("user_role") != "admin" else None
        context.update(DashboardService().get_dashboard_data(target_uid))
    if view_path in {"admin/settings", "admin/system"}:
        redirect_path = "/admin/dashboard"
        view_path = "admin/dashboard"
        template_name, title = templates[view_path]
        context.update(DashboardService().get_dashboard_data())
    if view_path == "register":
        context.update(values={}, errors={})
    if view_path in {"login", "forgot-password"}:
        context.update(email_or_username="", errors={})
    if view_path == "verify-email":
        expires_seconds = session.get("pending_verification_expires_seconds", 60)
        pending_user_id = session.get("pending_verification_user_id")
        if pending_user_id:
            try:
                latest = UserRepository().latest_email_verification(int(pending_user_id))
                if latest and "remaining_seconds" in latest and latest["remaining_seconds"] is not None:
                    expires_seconds = int(latest["remaining_seconds"])
            except Exception:
                pass
        context.update(
            email=session.get("pending_verification_email", ""),
            masked_email=session.get("pending_verification_masked_email", ""),
            expires_seconds=expires_seconds,
            error="",
        )
    if view_path == "reset-password/verify":
        expires_seconds = session.get("pending_reset_expires_seconds", 60)
        pending_user_id = session.get("pending_reset_user_id")
        if pending_user_id:
            try:
                latest = UserRepository().latest_email_verification(int(pending_user_id))
                if latest and "remaining_seconds" in latest and latest["remaining_seconds"] is not None:
                    expires_seconds = int(latest["remaining_seconds"])
            except Exception:
                pass
        context.update(
            email=session.get("pending_reset_email", ""),
            masked_email=session.get("pending_reset_masked_email", ""),
            expires_seconds=expires_seconds,
            error="",
        )
    if view_path == "reset-password":
        context.update(
            email=session.get("pending_reset_email", ""),
            errors={},
        )
    if view_path in {"dashboard", "admin/dashboard"}:
        context.update(DashboardService().get_dashboard_data())
    if view_path == "users/me":
        context.update(UserRepository().profile_data(session["user_id"], viewer_id=session["user_id"]))
    if view_path == "settings":
        context.update(profile=UserRepository().profile_data(session["user_id"], viewer_id=session["user_id"])["profile"])
    if view_path == "recipes/create":
        context.update(
            categories=HomeRepository().active_categories(limit=100),
            locations=LocationRecipeService().locations(),
            edit_mode=False,
            recipe=None,
        )
    if view_path in {"my-recipes", "drafts", "my-posts", "favorites", "followers", "following", "likes"}:
        repository = UserRepository()
        user_id = session["user_id"]
        profile_data = repository.profile_data(user_id, viewer_id=user_id)
        profile = profile_data["profile"]
        user_list = []
        recipes = []
        if view_path == "my-recipes":
            active_tab, page_title, page_icon = "recipes", "My Recipes", "♨"
            recipes = repository.authored_recipes(user_id)
            total_count, item_label = len(recipes), ("recipe" if len(recipes) == 1 else "recipes")
        elif view_path == "drafts":
            active_tab, page_title, page_icon = "drafts", "Draft Recipes", "✎"
            recipes = repository.draft_recipes(user_id)
            total_count, item_label = len(recipes), ("draft recipe" if len(recipes) == 1 else "draft recipes")
        elif view_path == "my-posts":
            active_tab, page_title, page_icon = "posts", "My Posts", "▤"
            recipes = repository.authored_posts(user_id)
            total_count, item_label = len(recipes), ("post" if len(recipes) == 1 else "posts")
        elif view_path == "favorites":
            active_tab, page_title, page_icon = "saved", "Saved Recipes", "♡"
            recipes = repository.saved_recipes(user_id)
            total_count, item_label = len(recipes), ("recipe" if len(recipes) == 1 else "recipes")
        elif view_path == "followers":
            active_tab, page_title, page_icon = "followers", "Followers", "♣"
            user_list = repository.followers(user_id, viewer_id=user_id)
            total_count, item_label = len(user_list), ("follower" if len(user_list) == 1 else "followers")
            profile_data["follower_count"] = len(user_list)
        elif view_path == "following":
            active_tab, page_title, page_icon = "following", "Following", "⚑"
            user_list = repository.following(user_id, viewer_id=user_id)
            total_count, item_label = len(user_list), ("chef" if len(user_list) == 1 else "chefs")
            profile_data["following_count"] = len(user_list)
        elif view_path == "likes":
            active_tab, page_title, page_icon = "likes", "Liked Recipes", "♥"
            recipes = repository.liked_recipes(user_id)
            total_count, item_label = len(recipes), ("recipe" if len(recipes) == 1 else "recipes")
            profile_data["like_count"] = len(recipes)

        profile_data.update(
            active_tab=active_tab,
            page_title=page_title,
            page_icon=page_icon,
            recipes=recipes,
            user_list=user_list,
            total_count=total_count,
            item_label=item_label,
            current_user_id=user_id,
        )
        context.update(profile_data)
    if view_path.startswith("admin/") and view_path != "admin/dashboard" and view_path != "admin/settings":
        admin_module = view_path.removeprefix("admin/")
        admin_service = AdminService()
        context.update(module=admin_module, module_title=placeholder_data[view_path][0], module_icon=placeholder_data[view_path][1])
        if admin_module == "users":
            context["rows"] = admin_service.users()
        elif admin_module == "categories":
            context["rows"] = admin_service.categories()
        elif admin_module == "reports":
            context["rows"] = admin_service.reports()
        elif admin_module == "content":
            context["rows"] = admin_service.recipes()
        elif admin_module == "activity":
            context["rows"] = admin_service.activity()
        elif admin_module == "notifications":
            context["rows"] = admin_service.notifications(session["user_id"])
        elif admin_module == "system":
            context["system"] = admin_service.system_overview()
    if view_path == "search":
        query = request.args.get("q", "").strip()
        context.update(query=query, **HomeService().search(query))
    if view_path == "locations":
        location_id = request.args.get("location_id", type=int)
        location_slug = request.args.get("location", "").strip().lower() or None
        query = request.args.get("q", "").strip() or None
        context.update(
            LocationRecipeService().page_data(
                location_id=location_id,
                location_slug=location_slug,
                search_query=query,
            )
        )
    if view_path == "recipes":
        recipe_filter = request.args.get("filter", "all")
        valid_filters = {"all", "newest", "popular", "rating_high", "rating_low", "views"}
        if recipe_filter not in valid_filters:
            recipe_filter = "all"
        category_slug = (request.args.get("category", "") or request.args.get("category_id", "")).strip().lower() or None
        location_name = (request.args.get("location", "") or request.args.get("location_id", "")).strip().lower() or None
        query = request.args.get("q", "").strip() or None
        catalog_data = HomeService().recipe_catalog(recipe_filter, category_slug, location_name, query)
        context.update(
            recipe_filter=recipe_filter,
            category_slug=category_slug,
            location_name=location_name,
            query=query or "",
            **catalog_data,
        )
    if view_path == "":
        context.update(HomeService().discovery())
    elif view_path == "categories":
        context.update(HomeService().discovery(include_all=True))
    html = render_template(template_name, **context)
    layout_type = "app" if is_app_view else "auth" if view_path in {"login", "register", "verify-email"} else "public"
    payload = {"title": title, "html": html, "layout": layout_type, "page_state": {}}
    if redirect_path:
        payload["redirect_path"] = redirect_path
    return jsonify(payload)
