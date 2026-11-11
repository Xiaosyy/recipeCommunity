from pathlib import Path
from uuid import uuid4

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from recipeshare.dashboard.service import DashboardService
from recipeshare.location.service import LocationRecipeService
from recipeshare.auth.repository import UserRepository
from recipeshare.shared.decorators import login_required, role_required
from .repository import HomeRepository
from .service import HomeService, NEW_CATEGORY_SLUGS, RECOMMENDED_CATEGORY_SLUGS


home_blueprint = Blueprint("home", __name__, url_prefix="/")


@home_blueprint.get("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("home.user_home"))
    discovery = HomeService().discovery()
    return render_template("home/index.html", **discovery)


@home_blueprint.get("/home")
@role_required("user", "admin")
def user_home():
    discovery = HomeService().discovery()
    profile_data = UserRepository().profile_data(session["user_id"])
    dashboard_data = DashboardService().get_dashboard_data()
    context = {
        "layout": "app",
        "profile": profile_data["profile"],
        "recipe_count": profile_data["recipe_count"],
        "recent_recipes": dashboard_data.get("inventory", []),
    }
    context.update(dashboard_data)
    context.update(discovery)
    return render_template(
        "home/account.html",
        **context,
    )


@home_blueprint.get("/dashboard")
@role_required("user", "admin")
def dashboard():
    if session.get("user_role") == "admin":
        return redirect(url_for("admin.dashboard"))
    return render_template("dashboard/index.html", layout="app", **DashboardService().get_dashboard_data())


@home_blueprint.get("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    return render_template("search/results.html", layout="app", query=query, **HomeService().search(query))


@home_blueprint.get("/recipes")
def recipes():
    recipe_filter = request.args.get("filter", "all")
    category_slug = (request.args.get("category", "") or request.args.get("category_id", "")).strip().lower() or None
    location_name = (request.args.get("location", "") or request.args.get("location_id", "")).strip().lower() or None
    query = request.args.get("q", "").strip() or None
    valid_filters = {"all", "newest", "popular", "rating_high", "rating_low", "views"}
    if recipe_filter not in valid_filters:
        recipe_filter = "all"
    catalog_data = HomeService().recipe_catalog(recipe_filter, category_slug, location_name, query)
    layout = "app" if session.get("user_id") else "public"
    return render_template(
        "modules/recipes.html",
        layout=layout,
        recipe_filter=recipe_filter,
        category_slug=category_slug,
        location_name=location_name,
        query=query or "",
        **catalog_data,
    )


@home_blueprint.get("/recipes/<slug>")
def recipe_detail(slug):
    recipe = HomeService().recipe_detail(slug, session.get("user_id"))
    if recipe is None:
        return render_template("errors/404.html"), 404
    HomeRepository().increment_view(recipe["id"])
    recipe["view_count"] = recipe.get("view_count", 0) + 1
    layout = "app" if session.get("user_id") else "public"
    return render_template("recipes/detail.html", layout=layout, recipe=recipe)


@home_blueprint.get("/categories")
def categories():
    discovery = HomeService().discovery(include_all=True)
    layout = "app" if session.get("user_id") else "public"
    return render_template(
        "modules/categories.html",
        layout=layout,
        categories=discovery["categories"],
        new_categories=discovery.get("new_categories", []),
        recommended_categories=discovery.get("recommended_categories", []),
    )


@home_blueprint.get("/locations")
def locations():
    location_id = request.args.get("location_id", type=int)
    location_slug = request.args.get("location", "").strip().lower() or None
    query = request.args.get("q", "").strip() or None
    location_data = LocationRecipeService().page_data(
        location_id=location_id,
        location_slug=location_slug,
        search_query=query,
    )
    return render_template("modules/locations.html", layout="app" if session.get("user_id") else "public", **location_data)


@home_blueprint.post("/locations/generate")
def generate_location_recipe():
    location_id = request.form.get("location_id", type=int) or request.args.get("location_id", type=int) or 1
    service = LocationRecipeService()
    raw_loc = service.repository.location_by_id(location_id)
    if raw_loc:
        existing_count = int(raw_loc.get("recipe_count") or 0)
        try:
            service.generate_recipe_for_location(raw_loc, existing_count=existing_count)
            flash(f"Auto-generated a new authentic recipe for {raw_loc['name']}!", "success")
        except Exception:
            current_app.logger.exception("Failed to auto-generate recipe for location %s", location_id)
    return redirect(url_for("home.locations", location_id=location_id))


@home_blueprint.get("/recipes/create")
@login_required
def create_recipe():
    categories = HomeRepository().active_categories(limit=100)
    locations = LocationRecipeService().locations()
    by_slug = {(c.get("slug") or "").strip().lower(): c for c in categories}
    new_categories = [by_slug[s] for s in NEW_CATEGORY_SLUGS if s in by_slug]
    recommended_categories = [by_slug[s] for s in RECOMMENDED_CATEGORY_SLUGS if s in by_slug]
    seen_ids = {c["id"] for c in new_categories} | {c["id"] for c in recommended_categories}
    other_categories = [c for c in categories if c["id"] not in seen_ids]
    return render_template(
        "modules/recipe_create.html",
        layout="app",
        categories=categories,
        new_categories=new_categories,
        recommended_categories=recommended_categories,
        other_categories=other_categories,
        locations=locations,
        edit_mode=False,
        recipe=None,
    )


@home_blueprint.get("/recipes/<slug>/edit")
@login_required
def edit_recipe(slug: str):
    recipe = HomeService().recipe_detail(slug, session.get("user_id"))
    if recipe is None:
        return render_template("errors/404.html"), 404
    if recipe["author_id"] != session.get("user_id") and session.get("user_role") != "admin":
        abort(403)
    categories = HomeRepository().active_categories(limit=100)
    locations = LocationRecipeService().locations()
    by_slug = {(c.get("slug") or "").strip().lower(): c for c in categories}
    new_categories = [by_slug[s] for s in NEW_CATEGORY_SLUGS if s in by_slug]
    recommended_categories = [by_slug[s] for s in RECOMMENDED_CATEGORY_SLUGS if s in by_slug]
    seen_ids = {c["id"] for c in new_categories} | {c["id"] for c in recommended_categories}
    other_categories = [c for c in categories if c["id"] not in seen_ids]
    return render_template(
        "modules/recipe_create.html",
        layout="app",
        categories=categories,
        new_categories=new_categories,
        recommended_categories=recommended_categories,
        other_categories=other_categories,
        locations=locations,
        edit_mode=True,
        recipe=recipe,
    )


@home_blueprint.get("/posts/create")
@login_required
def create_post():
    return render_template("modules/post_create.html", layout="app")


@home_blueprint.post("/posts/create")
@login_required
def save_post():
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    status = request.form.get("status", "draft")
    if status not in {"draft", "published"}:
        status = "draft"
    if len(title) < 3:
        flash("Post title must be at least 3 characters.", "error")
        return redirect(url_for("home.create_post"))
    if len(body) < 10:
        flash("Post content must be at least 10 characters.", "error")
        return redirect(url_for("home.create_post"))
    try:
        HomeRepository().create_post(session["user_id"], title, body, status)
    except Exception:
        current_app.logger.exception("Community post creation failed")
        flash("The post could not be saved. Please try again.", "error")
        return redirect(url_for("home.create_post"))
    flash("Post published." if status == "published" else "Post draft saved.", "success")
    return redirect(url_for("home.my_posts"))


def _process_recipe_media_upload(media):
    if not media or not media.filename:
        return None, None
    extension = media.filename.rsplit(".", 1)[-1].lower() if "." in media.filename else ""
    media.seek(0, 2)
    size = media.tell()
    media.seek(0)
    signature = media.read(16)
    media.seek(0)

    image_mimes = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "gif": "image/gif",
    }
    video_mimes = {
        "mp4": "video/mp4",
        "m4v": "video/mp4",
        "webm": "video/webm",
        "mov": "video/quicktime",
        "ogg": "video/ogg",
        "ogv": "video/ogg",
    }

    if extension in image_mimes:
        valid_signature = (
            signature.startswith(b"\x89PNG\r\n\x1a\n")
            or signature.startswith(b"\xff\xd8\xff")
            or (signature.startswith(b"RIFF") and signature[8:12] == b"WEBP")
            or signature.startswith((b"GIF87a", b"GIF89a"))
        )
        if size <= 0 or size > 10 * 1024 * 1024 or not valid_signature:
            return None, "Recipe photo must be a valid PNG, JPG, JPEG, WEBP, or GIF image smaller than 10 MB."
        mime_type = media.mimetype if (media.mimetype and media.mimetype.startswith("image/")) else image_mimes[extension]
    elif extension in video_mimes:
        valid_signature = (
            b"ftyp" in signature[:16]
            or signature[4:8] in {b"ftyp", b"moov", b"mdat", b"wide", b"free", b"skip"}
            or signature.startswith(b"\x1a\x45\xdf\xa3")
            or signature.startswith(b"OggS")
        )
        if size <= 0 or size > 50 * 1024 * 1024 or not valid_signature:
            return None, "Recipe video must be a valid MP4, WEBM, MOV, or OGG video smaller than 50 MB."
        mime_type = media.mimetype if (media.mimetype and media.mimetype.startswith("video/")) else video_mimes[extension]
    else:
        return None, "Recipe media must be a valid photo (PNG, JPG, WEBP, GIF) or video (MP4, WEBM, MOV, OGG)."

    directory = Path(current_app.root_path) / "static" / "uploads" / "recipes"
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.{extension}"
    media.save(directory / filename)
    return {
        "storage_path": url_for("static", filename=f"uploads/recipes/{filename}"),
        "original_name": media.filename,
        "mime_type": mime_type,
    }, None


def _duration_minutes(prefix: str) -> int | None:
    direct = request.form.get(f"{prefix}_minutes")
    if direct:
        try:
            val = int(direct)
            if val > 0:
                return val
        except (TypeError, ValueError):
            pass

    hours_raw = request.form.get(f"{prefix}_hours")
    mins_raw = request.form.get(f"{prefix}_mins")
    hours = 0
    mins = 0
    has_input = False
    if hours_raw not in (None, ""):
        try:
            hours = max(0, int(hours_raw))
            has_input = True
        except (TypeError, ValueError):
            pass
    if mins_raw not in (None, ""):
        try:
            mins = max(0, int(mins_raw))
            has_input = True
        except (TypeError, ValueError):
            pass

    total = hours * 60 + mins
    if total > 0:
        return total
    if has_input:
        return 0
    return None


@home_blueprint.post("/recipes/create")
@login_required
def save_recipe():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", "draft")
    if status not in {"draft", "published"}:
        status = "draft"
    if len(title) < 3:
        flash("Recipe title must be at least 3 characters.", "error")
        return redirect(url_for("home.create_recipe"))

    ingredient_names = request.form.getlist("ingredient_name")
    quantities = request.form.getlist("ingredient_quantity")
    units = request.form.getlist("ingredient_unit")
    ingredients = []
    for name, quantity, unit in zip(ingredient_names, quantities, units):
        name = name.strip()
        unit = unit.strip()
        if not name:
            continue
        try:
            parsed_quantity = float(quantity)
        except (TypeError, ValueError):
            import re
            raw_qty = str(quantity or "").strip()
            frac_match = re.match(r"^\s*(?:(\d+)\s+)?(\d+)\s*/\s*(\d+)\s*([a-zA-Z]+)?", raw_qty)
            match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?", raw_qty)
            if frac_match and int(frac_match.group(3)) != 0:
                whole = float(frac_match.group(1) or 0)
                parsed_quantity = whole + (float(frac_match.group(2)) / float(frac_match.group(3)))
                if not unit and frac_match.group(4):
                    unit = frac_match.group(4).strip()
            elif match:
                parsed_quantity = float(match.group(1))
                if not unit and match.group(2):
                    unit = match.group(2).strip()
            elif raw_qty:
                parsed_quantity = 1.0
                if not unit:
                    unit = raw_qty[:30]
            else:
                parsed_quantity = 0
        if parsed_quantity <= 0:
            flash("Each ingredient needs a valid quantity.", "error")
            return redirect(url_for("home.create_recipe"))
        ingredients.append({"name": name, "quantity": parsed_quantity, "unit": unit or "piece"})
    if not ingredients:
        flash("Add at least one ingredient.", "error")
        return redirect(url_for("home.create_recipe"))

    instructions = [line.strip() for line in request.form.get("instructions", "").splitlines() if line.strip()]
    if not instructions:
        flash("Add at least one instruction step.", "error")
        return redirect(url_for("home.create_recipe"))

    def positive_integer(field: str):
        try:
            value = int(request.form.get(field, 0))
            return value if value > 0 else None
        except (TypeError, ValueError):
            return None

    prep_minutes = _duration_minutes("prep")
    cook_minutes = _duration_minutes("cook")

    raw_cat = request.form.get("category_id") or request.form.get("category")
    category_id = None
    if raw_cat:
        try:
            category_id = int(raw_cat)
            if category_id <= 0:
                category_id = None
        except (ValueError, TypeError):
            cat_row = HomeRepository().category_by_slug_or_name(str(raw_cat))
            if cat_row:
                category_id = cat_row["id"]

    raw_loc = request.form.get("location_id") or request.form.get("location")
    location_id = None
    if raw_loc:
        try:
            location_id = int(raw_loc)
            if location_id <= 0:
                location_id = None
        except (ValueError, TypeError):
            loc_row = LocationRepository().location_by_name(str(raw_loc))
            if loc_row:
                location_id = loc_row["id"]

    media_items = []
    for field_name in ("recipe_image", "recipe_video", "recipe_media"):
        file_obj = request.files.get(field_name)
        if file_obj and file_obj.filename:
            item_data, error_msg = _process_recipe_media_upload(file_obj)
            if error_msg:
                flash(error_msg, "error")
                return redirect(url_for("home.create_recipe"))
            if item_data:
                media_items.append(item_data)

    primary_media = media_items[0] if media_items else None
    extra_media = media_items[1:] if len(media_items) > 1 else None

    cooking_tips = request.form.get("cooking_tips", "").strip() or None
    serving_suggestion = request.form.get("serving_suggestion", "").strip() or None
    food_type = request.form.get("food_type", "").strip() or None
    taste = request.form.get("taste", "").strip() or None
    best_served = request.form.get("best_served", "").strip() or None

    try:
        recipe_id = HomeRepository().create_recipe(
            session["user_id"], title, description, category_id, location_id,
            None, prep_minutes, cook_minutes,
            ingredients, instructions, status, primary_media, extra_media=extra_media,
            cooking_tips=cooking_tips, serving_suggestion=serving_suggestion,
            food_type=food_type, taste=taste, best_served=best_served,
        )
    except Exception:
        current_app.logger.exception("Recipe creation failed")
        flash("The recipe could not be saved. Please try again.", "error")
        return redirect(url_for("home.create_recipe"))
    flash("Recipe published." if status == "published" else "Recipe draft saved.", "success")
    return redirect(url_for("home.drafts") if status == "draft" else url_for("home.recipe_detail", slug=HomeRepository().recipe_by_id(recipe_id)["slug"]))


@home_blueprint.post("/recipes/<slug>/edit")
@login_required
def update_recipe(slug: str):
    existing = HomeService().recipe_detail(slug, session.get("user_id"))
    if existing is None:
        return render_template("errors/404.html"), 404
    if existing["author_id"] != session.get("user_id") and session.get("user_role") != "admin":
        abort(403)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", existing.get("status") or "published")
    if status not in {"draft", "published"}:
        status = "published"
    if len(title) < 3:
        flash("Recipe title must be at least 3 characters.", "error")
        return redirect(url_for("home.edit_recipe", slug=slug))

    ingredient_names = request.form.getlist("ingredient_name")
    quantities = request.form.getlist("ingredient_quantity")
    units = request.form.getlist("ingredient_unit")
    ingredients = []
    for name, quantity, unit in zip(ingredient_names, quantities, units):
        name = name.strip()
        unit = unit.strip()
        if not name:
            continue
        try:
            parsed_quantity = float(quantity)
        except (TypeError, ValueError):
            import re
            raw_qty = str(quantity or "").strip()
            frac_match = re.match(r"^\s*(?:(\d+)\s+)?(\d+)\s*/\s*(\d+)\s*([a-zA-Z]+)?", raw_qty)
            match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?", raw_qty)
            if frac_match and int(frac_match.group(3)) != 0:
                whole = float(frac_match.group(1) or 0)
                parsed_quantity = whole + (float(frac_match.group(2)) / float(frac_match.group(3)))
                if not unit and frac_match.group(4):
                    unit = frac_match.group(4).strip()
            elif match:
                parsed_quantity = float(match.group(1))
                if not unit and match.group(2):
                    unit = match.group(2).strip()
            elif raw_qty:
                parsed_quantity = 1.0
                if not unit:
                    unit = raw_qty[:30]
            else:
                parsed_quantity = 0
        if parsed_quantity <= 0:
            flash("Each ingredient needs a valid quantity.", "error")
            return redirect(url_for("home.edit_recipe", slug=slug))
        ingredients.append({"name": name, "quantity": parsed_quantity, "unit": unit or "piece"})
    if not ingredients:
        flash("Add at least one ingredient.", "error")
        return redirect(url_for("home.edit_recipe", slug=slug))

    instructions = [line.strip() for line in request.form.get("instructions", "").splitlines() if line.strip()]
    if not instructions:
        flash("Add at least one instruction step.", "error")
        return redirect(url_for("home.edit_recipe", slug=slug))

    def positive_integer(field: str):
        try:
            value = int(request.form.get(field, 0))
            return value if value > 0 else None
        except (TypeError, ValueError):
            return None

    prep_minutes = _duration_minutes("prep")
    cook_minutes = _duration_minutes("cook")

    raw_cat = request.form.get("category_id") or request.form.get("category")
    category_id = None
    if raw_cat:
        try:
            category_id = int(raw_cat)
            if category_id <= 0:
                category_id = None
        except (ValueError, TypeError):
            cat_row = HomeRepository().category_by_slug_or_name(str(raw_cat))
            if cat_row:
                category_id = cat_row["id"]

    raw_loc = request.form.get("location_id") or request.form.get("location")
    location_id = None
    if raw_loc:
        try:
            location_id = int(raw_loc)
            if location_id <= 0:
                location_id = None
        except (ValueError, TypeError):
            loc_row = LocationRepository().location_by_name(str(raw_loc))
            if loc_row:
                location_id = loc_row["id"]

    media_items = []
    for field_name in ("recipe_image", "recipe_video", "recipe_media"):
        file_obj = request.files.get(field_name)
        if file_obj and file_obj.filename:
            item_data, error_msg = _process_recipe_media_upload(file_obj)
            if error_msg:
                flash(error_msg, "error")
                return redirect(url_for("home.edit_recipe", slug=slug))
            if item_data:
                media_items.append(item_data)

    primary_media = media_items[0] if media_items else None
    extra_media = media_items[1:] if len(media_items) > 1 else None

    cooking_tips = request.form.get("cooking_tips", "").strip() or None
    serving_suggestion = request.form.get("serving_suggestion", "").strip() or None
    food_type = request.form.get("food_type", "").strip() or None
    taste = request.form.get("taste", "").strip() or None
    best_served = request.form.get("best_served", "").strip() or None

    try:
        HomeRepository().update_recipe(
            existing["id"],
            title,
            description,
            category_id,
            location_id,
            existing.get("servings"),
            prep_minutes,
            cook_minutes,
            ingredients,
            instructions,
            status,
            primary_media,
            extra_media=extra_media,
            cooking_tips=cooking_tips,
            serving_suggestion=serving_suggestion,
            food_type=food_type,
            taste=taste,
            best_served=best_served,
        )
    except Exception:
        current_app.logger.exception("Recipe update failed")
        flash("The recipe could not be updated. Please try again.", "error")
        return redirect(url_for("home.edit_recipe", slug=slug))

    flash("Recipe updated!", "success")
    return redirect(url_for("home.drafts") if status == "draft" else url_for("home.recipe_detail", slug=slug))


@home_blueprint.post("/recipes/<slug>/delete")
@login_required
def delete_recipe(slug: str):
    existing = HomeService().recipe_detail(slug, session.get("user_id"))
    if existing is None:
        return render_template("errors/404.html"), 404
    if existing["author_id"] != session.get("user_id") and session.get("user_role") != "admin":
        abort(403)
    HomeRepository().delete_recipe(existing["id"])
    flash(f"Recipe “{existing['title']}” has been deleted.", "success")
    return redirect(url_for("home.my_recipes"))


@home_blueprint.get("/inventory")
@login_required
def inventory():
    return redirect(url_for("home.dashboard"))


@home_blueprint.get("/my-recipes")
@login_required
def my_recipes():
    repository = UserRepository()
    user_id = session["user_id"]
    profile_data = repository.profile_data(user_id, viewer_id=user_id)
    recipes = repository.authored_recipes(user_id)
    profile_data.update(
        active_tab="recipes",
        page_title="My Recipes",
        page_icon="♨",
        recipes=recipes,
        total_count=len(recipes),
        item_label="recipe" if len(recipes) == 1 else "recipes",
        current_user_id=user_id,
    )
    return render_template("modules/profile_collection.html", layout="app", **profile_data)


@home_blueprint.get("/drafts")
@login_required
def drafts():
    repository = UserRepository()
    user_id = session["user_id"]
    profile_data = repository.profile_data(user_id, viewer_id=user_id)
    recipes = repository.draft_recipes(user_id)
    profile_data.update(
        active_tab="drafts",
        page_title="Draft Recipes",
        page_icon="✎",
        recipes=recipes,
        total_count=len(recipes),
        item_label="draft recipe" if len(recipes) == 1 else "draft recipes",
        current_user_id=user_id,
    )
    return render_template("modules/profile_collection.html", layout="app", **profile_data)


@home_blueprint.get("/my-posts")
@login_required
def my_posts():
    repository = UserRepository()
    user_id = session["user_id"]
    profile_data = repository.profile_data(user_id, viewer_id=user_id)
    recipes = repository.authored_posts(user_id)
    profile_data.update(
        active_tab="posts",
        page_title="My Posts",
        page_icon="▤",
        recipes=recipes,
        total_count=len(recipes),
        item_label="post" if len(recipes) == 1 else "posts",
        current_user_id=user_id,
    )
    return render_template("modules/profile_collection.html", layout="app", **profile_data)


@home_blueprint.get("/favorites")
@login_required
def favorites():
    repository = UserRepository()
    user_id = session["user_id"]
    profile_data = repository.profile_data(user_id, viewer_id=user_id)
    recipes = repository.saved_recipes(user_id)
    profile_data.update(
        active_tab="saved",
        page_title="Saved Recipes",
        page_icon="♡",
        recipes=recipes,
        total_count=len(recipes),
        item_label="recipe" if len(recipes) == 1 else "recipes",
        current_user_id=user_id,
    )
    return render_template("modules/profile_collection.html", layout="app", **profile_data)


@home_blueprint.get("/followers")
@login_required
def my_followers():
    user_id = session["user_id"]
    repository = UserRepository()
    profile_data = repository.profile_data(user_id, viewer_id=user_id)
    user_list = repository.followers(user_id, viewer_id=user_id)
    profile_data.update(
        active_tab="followers",
        page_title="Followers",
        page_icon="♣",
        user_list=user_list,
        total_count=len(user_list),
        follower_count=len(user_list),
        item_label="follower" if len(user_list) == 1 else "followers",
        current_user_id=user_id,
    )
    return render_template("modules/profile_collection.html", layout="app", **profile_data)


@home_blueprint.get("/following")
@login_required
def my_following():
    user_id = session["user_id"]
    repository = UserRepository()
    profile_data = repository.profile_data(user_id, viewer_id=user_id)
    user_list = repository.following(user_id, viewer_id=user_id)
    profile_data.update(
        active_tab="following",
        page_title="Following",
        page_icon="⚑",
        user_list=user_list,
        total_count=len(user_list),
        following_count=len(user_list),
        item_label="chef" if len(user_list) == 1 else "chefs",
        current_user_id=user_id,
    )
    return render_template("modules/profile_collection.html", layout="app", **profile_data)


@home_blueprint.get("/likes")
@login_required
def my_likes():
    user_id = session["user_id"]
    repository = UserRepository()
    profile_data = repository.profile_data(user_id, viewer_id=user_id)
    recipes = repository.liked_recipes(user_id)
    profile_data.update(
        active_tab="likes",
        page_title="Liked Recipes",
        page_icon="♥",
        recipes=recipes,
        total_count=len(recipes),
        like_count=len(recipes),
        item_label="recipe" if len(recipes) == 1 else "recipes",
        current_user_id=user_id,
    )
    return render_template("modules/profile_collection.html", layout="app", **profile_data)


@home_blueprint.get("/messages")
@login_required
def messages():
    return render_template("modules/placeholder.html", layout="app", module_title="Messages", module_icon="message")


@home_blueprint.get("/settings")
@login_required
def settings():
    return render_template("modules/profile_settings.html", layout="app",
                           profile=UserRepository().profile_data(session["user_id"])["profile"])


@home_blueprint.post("/settings/profile")
@login_required
def save_profile():
    repository = UserRepository()
    display_name = request.form.get("display_name", "").strip()
    bio = request.form.get("bio", "").strip()
    if not display_name:
        flash("Display name is required.", "error")
        return redirect(url_for("home.settings"))
    repository.save_profile(session["user_id"], display_name, bio)
    session["username"] = display_name

    avatar = request.files.get("avatar")
    if avatar and avatar.filename:
        extension = avatar.filename.rsplit(".", 1)[-1].lower() if "." in avatar.filename else ""
        avatar.seek(0, 2)
        size = avatar.tell()
        avatar.seek(0)
        signature = avatar.read(12)
        avatar.seek(0)
        valid_signature = (
            signature.startswith(b"\x89PNG\r\n\x1a\n")
            or signature.startswith(b"\xff\xd8\xff")
            or (signature.startswith(b"RIFF") and signature[8:12] == b"WEBP")
            or signature.startswith((b"GIF87a", b"GIF89a"))
        )
        if extension not in {"png", "jpg", "jpeg", "webp", "gif"} or size <= 0 or size > 10 * 1024 * 1024 or not valid_signature:
            flash("Profile picture must be a valid image smaller than 10 MB.", "error")
            return redirect(url_for("home.settings"))
        directory = Path(current_app.root_path) / "static" / "uploads" / "avatars"
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}.{extension}"
        avatar.save(directory / filename)
        repository.save_avatar(session["user_id"], url_for("static", filename=f"uploads/avatars/{filename}"))
    flash("Profile settings saved.", "success")
    return redirect(url_for("home.settings"))


@home_blueprint.post("/settings/profile-picture")
@login_required
def save_profile_picture():
    repository = UserRepository()
    avatar = request.files.get("avatar")
    if not avatar or not avatar.filename:
        flash("Choose a profile picture first.", "error")
        return redirect(url_for("home.settings"))

    extension = avatar.filename.rsplit(".", 1)[-1].lower() if "." in avatar.filename else ""
    avatar.seek(0, 2)
    size = avatar.tell()
    avatar.seek(0)
    signature = avatar.read(12)
    avatar.seek(0)
    valid_signature = (
        signature.startswith(b"\x89PNG\r\n\x1a\n")
        or signature.startswith(b"\xff\xd8\xff")
        or (signature.startswith(b"RIFF") and signature[8:12] == b"WEBP")
        or signature.startswith((b"GIF87a", b"GIF89a"))
    )
    if extension not in {"png", "jpg", "jpeg", "webp", "gif"} or size <= 0 or size > 10 * 1024 * 1024 or not valid_signature:
        flash("Profile picture must be a valid PNG, JPG, JPEG, WEBP, or GIF image smaller than 10 MB.", "error")
        return redirect(url_for("home.settings"))

    directory = Path(current_app.root_path) / "static" / "uploads" / "avatars"
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{session['user_id']}-{uuid4().hex}.{extension}"
    avatar.save(directory / filename)
    repository.save_avatar(session["user_id"], url_for("static", filename=f"uploads/avatars/{filename}"))
    flash("Profile picture updated.", "success")
    return redirect(url_for("home.settings"))


@home_blueprint.get("/users/me")
@login_required
def profile():
    viewer_id = session.get("user_id")
    data = UserRepository().profile_data(viewer_id, viewer_id=viewer_id)
    return render_template("modules/profile.html", layout="app", **data)


@home_blueprint.get("/users/<username>")
def user_profile(username: str):
    if username == "me":
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return profile()
    viewer_id = session.get("user_id")
    target_user = UserRepository().find_by_identity(username)
    if not target_user:
        return render_template("errors/404.html"), 404
    data = UserRepository().profile_data(target_user["id"], viewer_id=viewer_id)
    layout = "app" if viewer_id else "public"
    return render_template("modules/profile.html", layout=layout, **data)


@home_blueprint.get("/users/<username>/followers")
def user_followers(username: str):
    if username == "me":
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return my_followers()
    viewer_id = session.get("user_id")
    target_user = UserRepository().find_by_identity(username)
    if not target_user:
        return render_template("errors/404.html"), 404
    repo = UserRepository()
    profile_data = repo.profile_data(target_user["id"], viewer_id=viewer_id)
    user_list = repo.followers(target_user["id"], viewer_id=viewer_id)
    layout = "app" if viewer_id else "public"
    profile_data.update(
        active_tab="followers",
        page_title="Followers",
        page_icon="♣",
        user_list=user_list,
        total_count=len(user_list),
        follower_count=len(user_list),
        item_label="follower" if len(user_list) == 1 else "followers",
        current_user_id=viewer_id,
    )
    return render_template("modules/profile_collection.html", layout=layout, **profile_data)


@home_blueprint.get("/users/<username>/following")
def user_following(username: str):
    if username == "me":
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return my_following()
    viewer_id = session.get("user_id")
    target_user = UserRepository().find_by_identity(username)
    if not target_user:
        return render_template("errors/404.html"), 404
    repo = UserRepository()
    profile_data = repo.profile_data(target_user["id"], viewer_id=viewer_id)
    user_list = repo.following(target_user["id"], viewer_id=viewer_id)
    layout = "app" if viewer_id else "public"
    profile_data.update(
        active_tab="following",
        page_title="Following",
        page_icon="⚑",
        user_list=user_list,
        total_count=len(user_list),
        following_count=len(user_list),
        item_label="chef" if len(user_list) == 1 else "chefs",
        current_user_id=viewer_id,
    )
    return render_template("modules/profile_collection.html", layout=layout, **profile_data)


@home_blueprint.get("/users/<username>/likes")
def user_likes(username: str):
    if username == "me":
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return my_likes()
    viewer_id = session.get("user_id")
    target_user = UserRepository().find_by_identity(username)
    if not target_user:
        return render_template("errors/404.html"), 404
    repo = UserRepository()
    profile_data = repo.profile_data(target_user["id"], viewer_id=viewer_id)
    recipes = repo.liked_recipes(target_user["id"])
    layout = "app" if viewer_id else "public"
    profile_data.update(
        active_tab="likes",
        page_title="Liked Recipes",
        page_icon="♥",
        recipes=recipes,
        total_count=len(recipes),
        like_count=len(recipes),
        item_label="recipe" if len(recipes) == 1 else "recipes",
        current_user_id=viewer_id,
    )
    return render_template("modules/profile_collection.html", layout=layout, **profile_data)


@home_blueprint.get("/profile")
@login_required
def profile_redirect():
    return redirect(url_for("home.profile"))


@home_blueprint.get("/recipes/new")
@login_required
def recipes_new_redirect():
    return redirect(url_for("home.create_recipe"))


@home_blueprint.get("/about")
def about_page():
    layout = "app" if session.get("user_id") else "public"
    return render_template("modules/placeholder.html", layout=layout, module_title="About RecipeShare", module_icon="recipes")


@home_blueprint.get("/privacy")
def privacy_page():
    layout = "app" if session.get("user_id") else "public"
    return render_template("modules/privacy.html", layout=layout, module_title="Privacy Policy", module_icon="settings")


@home_blueprint.get("/terms")
def terms_page():
    layout = "app" if session.get("user_id") else "public"
    return render_template("modules/terms.html", layout=layout, module_title="Terms of Service", module_icon="settings")
