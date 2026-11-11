import json
from re import sub
from recipeshare.shared.database import get_connection

COUNTRY_FLAGS = {
    "ph": "🇵🇭",
    "it": "🇮🇹",
    "jp": "🇯🇵",
    "mx": "🇲🇽",
    "th": "🇹🇭",
    "xx": "🌐",
    "philippines": "🇵🇭",
    "italy": "🇮🇹",
    "japan": "🇯🇵",
    "mexico": "🇲🇽",
    "thailand": "🇹🇭",
    "mediterranean": "🌐",
}


def get_flag(country_code: str | None = None, name: str | None = "") -> str:
    code = (country_code or "").strip().upper()
    if len(code) == 2 and code != "XX" and code.isalpha():
        try:
            return chr(127397 + ord(code[0])) + chr(127397 + ord(code[1]))
        except Exception:
            pass
    code_lower = code.lower()
    if code_lower in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[code_lower]
    name_clean = (name or "").strip().lower()
    if name_clean in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[name_clean]
    return "🌐"


class LocationRepository:
    def locations(self) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT l.id, l.name, l.region, l.country_code, "
                           "COALESCE((SELECT ri.storage_path FROM recipes recipe_cover "
                           "JOIN recipe_images ri ON ri.recipe_id = recipe_cover.id "
                           "WHERE recipe_cover.location_id = l.id AND recipe_cover.status = 'published' "
                           "ORDER BY ri.is_primary DESC, recipe_cover.view_count DESC, ri.id LIMIT 1), l.image_path) AS image_path, "
                           "COUNT(r.id) AS recipe_count FROM locations l "
                           "LEFT JOIN recipes r ON r.location_id = l.id AND r.status = 'published' "
                           "GROUP BY l.id, l.name, l.region, l.country_code, l.image_path ORDER BY l.id")
            rows = cursor.fetchall()
            for row in rows:
                row["flag"] = get_flag(row.get("country_code"), row.get("name"))
            return rows
        finally:
            cursor.close()

    def location_by_id(self, location_id: int) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT l.id, l.name, l.region, l.country_code, l.image_path, COUNT(r.id) AS recipe_count FROM locations l LEFT JOIN recipes r ON r.location_id = l.id AND r.status = 'published' WHERE l.id = %s GROUP BY l.id, l.name, l.region, l.country_code, l.image_path",
                (location_id,),
            )
            row = cursor.fetchone()
            if row:
                row["flag"] = get_flag(row.get("country_code"), row.get("name"))
            return row
        finally:
            cursor.close()

    def location_by_name(self, location_name: str) -> dict | None:
        clean = (location_name or "").strip().lower()
        if not clean:
            return None
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            loc_id = int(clean) if clean.isdigit() else 0
            cursor.execute(
                "SELECT l.id, l.name, l.region, l.country_code, l.image_path, COUNT(r.id) AS recipe_count "
                "FROM locations l LEFT JOIN recipes r ON r.location_id = l.id AND r.status = 'published' "
                "WHERE LOWER(l.name) = %s OR REPLACE(LOWER(l.name), ' ', '-') = %s OR LOWER(COALESCE(l.country_code, '')) = %s OR l.id = %s "
                "GROUP BY l.id, l.name, l.region, l.country_code, l.image_path LIMIT 1",
                (clean, clean, clean, loc_id),
            )
            row = cursor.fetchone()
            if row:
                row["flag"] = get_flag(row.get("country_code"), row.get("name"))
            return row
        finally:
            cursor.close()

    def recipes_for_location(self, location_id: int, limit: int = 20) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.id, r.title, r.slug, r.description, r.servings, r.prep_minutes, r.cook_minutes, "
                "r.instructions, r.view_count, l.id AS location_id, l.name AS location_name, "
                "c.name AS category_name, u.username AS author_name, "
                "COALESCE((SELECT AVG(rt.score) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS average_rating, "
                "COALESCE((SELECT COUNT(*) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS review_count, "
                "COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id "
                "ORDER BY ri.is_primary DESC, ri.id LIMIT 1), '') AS image_path "
                "FROM recipes r LEFT JOIN locations l ON l.id = r.location_id "
                "LEFT JOIN categories c ON c.id = r.category_id "
                "LEFT JOIN users u ON u.id = r.author_id "
                "WHERE r.status = 'published' AND r.location_id = %s "
                "ORDER BY r.view_count DESC, r.created_at DESC, r.id DESC LIMIT %s",
                (location_id, limit),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def all_location_recipes(self, limit: int = 20) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.id, r.title, r.slug, r.description, r.servings, r.prep_minutes, r.cook_minutes, "
                "r.instructions, r.view_count, l.id AS location_id, l.name AS location_name, "
                "c.name AS category_name, u.username AS author_name, "
                "COALESCE((SELECT AVG(rt.score) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS average_rating, "
                "COALESCE((SELECT COUNT(*) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS review_count, "
                "COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id "
                "ORDER BY ri.is_primary DESC, ri.id LIMIT 1), '') AS image_path "
                "FROM recipes r LEFT JOIN locations l ON l.id = r.location_id "
                "LEFT JOIN categories c ON c.id = r.category_id "
                "LEFT JOIN users u ON u.id = r.author_id "
                "WHERE r.status = 'published' AND r.location_id IS NOT NULL "
                "ORDER BY r.view_count DESC, r.created_at DESC, r.id DESC LIMIT %s",
                (limit,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def recipe_sources(self, limit: int = 20) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.id, r.title, r.description, r.servings, r.prep_minutes, r.cook_minutes, "
                "r.instructions, l.id AS location_id, l.name AS location_name, "
                "COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id "
                "ORDER BY ri.is_primary DESC, ri.id LIMIT 1), '') AS image_path "
                "FROM recipes r LEFT JOIN locations l ON l.id = r.location_id "
                "WHERE r.status = 'published' ORDER BY r.view_count DESC LIMIT %s",
                (limit,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def create_generated_recipe(
        self,
        location_id: int,
        title: str,
        description: str,
        servings: int,
        prep_minutes: int,
        cook_minutes: int,
        instructions: list[str],
        ingredients: list[dict],
        image_url: str,
        author_id: int = 3,
        category_id: int | None = 3,
        view_count: int = 1280,
    ) -> int:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            # Ensure author_id exists; fallback to first user
            cursor.execute("SELECT id FROM users WHERE id = %s LIMIT 1", (author_id,))
            if not cursor.fetchone():
                cursor.execute("SELECT id FROM users ORDER BY id LIMIT 1")
                user_row = cursor.fetchone()
                author_id = user_row[0] if user_row else 1

            # Determine appropriate category_id based on location if default
            if category_id == 3:
                cursor.execute("SELECT name, region FROM locations WHERE id = %s LIMIT 1", (location_id,))
                loc_info = cursor.fetchone()
                if loc_info:
                    loc_name_lower = (loc_info[0] or "").lower()
                    loc_region_lower = (loc_info[1] or "").lower()
                    preferred_slug = "dinner"
                    if loc_name_lower == "philippines":
                        preferred_slug = "filipino"
                    elif loc_name_lower == "italy":
                        preferred_slug = "italian"
                    elif loc_name_lower == "mediterranean":
                        preferred_slug = "healthy-meals"
                    elif "asia" in loc_region_lower or loc_name_lower in {"japan", "thailand"}:
                        preferred_slug = "asian"
                    cursor.execute("SELECT id FROM categories WHERE slug = %s LIMIT 1", (preferred_slug,))
                    pref_row = cursor.fetchone()
                    if pref_row:
                        category_id = pref_row[0]

            # Ensure category_id exists
            if category_id:
                cursor.execute("SELECT id FROM categories WHERE id = %s LIMIT 1", (category_id,))
                if not cursor.fetchone():
                    cursor.execute("SELECT id FROM categories ORDER BY id LIMIT 1")
                    cat_row = cursor.fetchone()
                    category_id = cat_row[0] if cat_row else None

            base_slug = sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "regional-recipe"
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE slug = %s OR slug LIKE %s", (base_slug, f"{base_slug}-%"))
            slug_count = cursor.fetchone()[0]
            slug = base_slug if slug_count == 0 else f"{base_slug}-{slug_count + 1}"

            cursor.execute(
                "INSERT INTO recipes (author_id, category_id, location_id, title, slug, description, servings, "
                "prep_minutes, cook_minutes, instructions, status, published_at, view_count) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'published', CURRENT_TIMESTAMP, %s)",
                (
                    author_id,
                    category_id,
                    location_id,
                    title,
                    slug,
                    description,
                    servings,
                    prep_minutes,
                    cook_minutes,
                    json.dumps(instructions),
                    view_count,
                ),
            )
            recipe_id = cursor.lastrowid

            for index, ing in enumerate(ingredients):
                ing_name = ing["name"].strip()
                norm_name = sub(r"[^a-z0-9]+", " ", ing_name.lower()).strip()
                cursor.execute("SELECT id FROM ingredients WHERE normalized_name = %s LIMIT 1", (norm_name,))
                row = cursor.fetchone()
                if row:
                    ing_id = row[0]
                else:
                    cursor.execute(
                        "INSERT INTO ingredients (name, normalized_name) VALUES (%s, %s)",
                        (ing_name, norm_name),
                    )
                    ing_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (recipe_id, ing_id, ing.get("quantity", 1), ing.get("unit", "cup"), index),
                )

            if image_url:
                cursor.execute(
                    "INSERT INTO recipe_images (recipe_id, storage_path, original_name, mime_type, is_primary) "
                    "VALUES (%s, %s, %s, 'image/jpeg', TRUE)",
                    (recipe_id, image_url, f"{slug}.jpg"),
                )

            connection.commit()
            return recipe_id
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()


