import json
from re import sub

from recipeshare.shared.database import get_connection


DEFAULT_CATEGORIES: list[tuple[str, str, str]] = [
    ("American", "american", "Classic barbecue, burgers, comfort pies, and diner favorites"),
    ("Appetizers", "appetizers", "Starters, finger foods, and small plates"),
    ("Asian", "asian", "Savory stir-fries, noodles, and Asian culinary classics"),
    ("Baking", "baking", "Oven-baked breads, cookies, pies, and artisan pastries"),
    ("Beef", "beef", "Hearty beef steaks, roasts, and braised dishes"),
    ("Bread & Bakery", "bread-bakery", "Freshly baked breads, rolls, and artisanal loaves"),
    ("Breakfast", "breakfast", "Fluffy pancakes, morning favorites, and brunch classics"),
    ("Cakes & Pastries", "cakes-pastries", "Layer cakes, flaky pastries, and baked confections"),
    ("Chicken", "chicken", "Roasted, grilled, and homestyle poultry dishes"),
    ("Chinese", "chinese", "Dim sum, stir-fries, Peking duck, and regional Chinese cuisine"),
    ("Dairy-Free", "dairy-free", "Delicious lactose-free and dairy-free wholesome recipes"),
    ("Desserts", "desserts", "Cakes, cupcakes, pastries, and sweet treats"),
    ("Dinner", "dinner", "Hearty seared steaks, roasts, and evening family meals"),
    ("Drinks & Beverages", "drinks-beverages", "Refreshing coolers, hot drinks, and specialty beverages"),
    ("Eggs", "eggs", "Omelets, frittatas, deviled eggs, and savory egg dishes"),
    ("Fast Food", "fast-food", "Quick-serve favorites, crispy bites, and comfort classics"),
    ("Filipino", "filipino", "Authentic home-cooked Filipino comfort dishes"),
    ("Filipino Breakfast", "filipino-breakfast", "Silog meals, pandesal, and hearty Filipino morning dishes"),
    ("Filipino Desserts", "filipino-desserts", "Halo-halo, leche flan, and classic Filipino sweets"),
    ("Filipino Snacks (Merienda)", "filipino-snacks-merienda", "Afternoon merienda favorites, pancit, and lumpia"),
    ("Filipino Soups", "filipino-soups", "Sinigang, tinola, nilaga, and comforting Filipino broths"),
    ("Filipino Street Food", "filipino-street-food", "Isaw, kwek-kwek, fishball, and iconic local street bites"),
    ("Fish", "fish", "Fresh grilled, pan-seared, and steamed fish favorites"),
    ("French", "french", "Classic bistro fare, pastries, and French culinary traditions"),
    ("Fried Foods", "fried-foods", "Golden-crispy fried specialties and crunch-packed favorites"),
    ("Gluten-Free", "gluten-free", "Naturally wheat-free and gluten-friendly recipes"),
    ("Grilled & BBQ", "grilled-bbq", "Charcoal-grilled meats, skewers, barbecue, and smoky favorites"),
    ("Grilled Dishes", "grilled-dishes", "Charcoal-grilled meats, skewers, and smoky barbecue"),
    ("Healthy Meals", "healthy-meals", "Wholesome grain bowls, avocado salads, and nutrient-packed dishes"),
    ("Indian", "indian", "Fragrant curries, tandoori specialties, biryanis, and naan"),
    ("Italian", "italian", "Handcrafted pastas, wood-fired pizzas, and risottos"),
    ("Japanese", "japanese", "Sushi, ramen, teriyaki, and traditional Japanese cuisine"),
    ("Kakanin", "kakanin", "Traditional Filipino rice cakes, bibingka, biko, and puto"),
    ("Korean", "korean", "Kimchi stews, Korean barbecue, bibimbap, and savory pancakes"),
    ("Lamb", "lamb", "Tender braised lamb shanks, chops, and roasted specialties"),
    ("Low-Carb Meals", "low-carb-meals", "Keto-friendly, protein-rich, and low-carbohydrate plates"),
    ("Lunch", "lunch", "Satisfying midday rice bowls, wraps, and plates"),
    ("Main Course", "main-course", "Centerpiece entrees and satisfying family mains"),
    ("Mediterranean", "mediterranean", "Sun-drenched coastal salads, olive oil, and seafood specialties"),
    ("Mexican", "mexican", "Tacos, enchiladas, salsas, and vibrant Mexican dishes"),
    ("Native Delicacies", "native-delicacies", "Regional heritage delicacies and heirloom Filipino treats"),
    ("Noodles & Pasta", "noodles-pasta", "Stir-fried noodles, pancit, ramen, and artisan pastas"),
    ("Others", "others", "Unique fusion dishes, specialty recipes, and homemade creations"),
    ("Pork", "pork", "Savory pork belly, chops, roasts, and braised favorites"),
    ("Quick & Easy", "quick-easy", "Simple, delicious meals ready in 30 minutes or less"),
    ("Rice Dishes", "rice-dishes", "Fried rice, biryani, paella, and flavorful rice bowls"),
    ("Rice Meals", "rice-meals", "Fried rice, silog plates, biryani, paella, and flavorful rice bowls"),
    ("Salads", "salads", "Crisp greens, grain salads, and vibrant dressings"),
    ("Sandwiches", "sandwiches", "Stacked club sandwiches, paninis, subs, and handheld wraps"),
    ("Sandwiches & Burgers", "sandwiches-burgers", "Stacked club sandwiches, paninis, and juicy burgers"),
    ("Sauces & Dips", "sauces-dips", "Savory dips, salsas, marinades, and homemade dressings"),
    ("Seafood", "seafood", "Fresh ocean catches, garlic shrimp, and coastal favorites"),
    ("Side Dishes", "side-dishes", "Complementary vegetable, grain, and potato sides"),
    ("Smoothies", "smoothies", "Blended fruit smoothies, protein shakes, and acai bowls"),
    ("Smoothies & Juices", "smoothies-juices", "Fresh fruit blends, green smoothies, and pressed juices"),
    ("Snacks", "snacks", "Quick finger foods, savory bites, and afternoon snacks"),
    ("Snacks & Appetizers", "snacks-appetizers", "Crispy spring rolls, finger foods, and party starters"),
    ("Soups", "soups", "Velvety bisques, warm broths, and comforting bowls"),
    ("Stews", "stews", "Slow-simmered, rich, and hearty braised stews"),
    ("Street Food", "street-food", "Global night-market snacks, skewers, and handheld bites"),
    ("Thai", "thai", "Aromatic Thai curries, pad Thai, satay, and tom yum soups"),
    ("Traditional Filipino Food", "traditional-filipino-food", "Authentic Filipino heirloom recipes, adobo, sinigang, and regional heritage dishes"),
    ("Vegan", "vegan", "100% plant-based dishes free from animal products"),
    ("Vegetables", "vegetables", "Fresh garden vegetables, stir-fries, and healthy greens"),
    ("Vegetarian", "vegetarian", "Vibrant plant-forward meals and garden-fresh medleys"),
]


class HomeRepository:
    def ensure_default_categories(self) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.executemany(
                "INSERT INTO categories (name, slug, description, is_active) VALUES (%s, %s, %s, TRUE) "
                "ON DUPLICATE KEY UPDATE name = VALUES(name), "
                "description = COALESCE(categories.description, VALUES(description)), is_active = TRUE",
                DEFAULT_CATEGORIES,
            )
            connection.commit()
        finally:
            cursor.close()

    def active_categories(self, limit=100) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, name, slug, description, image_url FROM categories "
                "WHERE is_active = TRUE ORDER BY LOWER(name) ASC, name ASC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            if len(rows) < len(DEFAULT_CATEGORIES):
                self.ensure_default_categories()
                cursor.execute(
                    "SELECT id, name, slug, description, image_url FROM categories "
                    "WHERE is_active = TRUE ORDER BY LOWER(name) ASC, name ASC LIMIT %s",
                    (limit,),
                )
                rows = cursor.fetchall()
            return rows
        finally:
            cursor.close()

    def categories_with_recipes(self, limit=100) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT c.id, c.name, c.slug, c.description, c.image_url, "
                "COUNT(DISTINCT r.id) AS recipe_count, "
                "COALESCE(AVG(rt.score), 0) AS average_rating, "
                "COUNT(rt.score) AS review_count "
                "FROM categories c "
                "INNER JOIN recipes r ON r.category_id = c.id AND r.status = 'published' "
                "LEFT JOIN ratings rt ON rt.recipe_id = r.id "
                "WHERE c.is_active = TRUE "
                "GROUP BY c.id, c.name, c.slug, c.description, c.image_url "
                "HAVING COUNT(DISTINCT r.id) > 0 "
                "ORDER BY average_rating DESC, review_count DESC, recipe_count DESC, c.name ASC LIMIT %s",
                (limit,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def create_recipe(self, author_id: int, title: str, description: str, category_id: int | None,
                      location_id: int | None, servings: int | None, prep_minutes: int | None, cook_minutes: int | None,
                      ingredients: list[dict], instructions: list[str], status: str,
                      image: dict | None = None, extra_media: list[dict] | None = None,
                      cooking_tips: str | None = None, serving_suggestion: str | None = None,
                      food_type: str | None = None, taste: str | None = None, best_served: str | None = None) -> int:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            base_slug = sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "recipe"
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE slug = %s OR slug LIKE %s", (base_slug, f"{base_slug}-%"))
            slug_count = cursor.fetchone()[0]
            slug = base_slug if slug_count == 0 else f"{base_slug}-{slug_count + 1}"
            cursor.execute(
                "INSERT INTO recipes (author_id, category_id, location_id, title, slug, description, servings, prep_minutes, "
                "cook_minutes, instructions, cooking_tips, serving_suggestion, food_type, taste, best_served, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (author_id, category_id, location_id, title, slug, description or None, servings, prep_minutes, cook_minutes,
                 json.dumps(instructions), cooking_tips or None, serving_suggestion or None, food_type or None, taste or None, best_served or None, status),
            )
            recipe_id = cursor.lastrowid
            if status == "published":
                cursor.execute("UPDATE recipes SET published_at = CURRENT_TIMESTAMP WHERE id = %s", (recipe_id,))
            for index, ingredient in enumerate(ingredients):
                ing_name = ingredient["name"].strip()
                normalized_name = sub(r"[^a-z0-9]+", " ", ing_name.lower()).strip()
                cursor.execute(
                    "SELECT id FROM ingredients WHERE normalized_name = %s OR LOWER(name) = %s LIMIT 1",
                    (normalized_name, ing_name.lower()),
                )
                row = cursor.fetchone()
                if row:
                    ingredient_id = row[0]
                else:
                    cursor.execute(
                        "INSERT INTO ingredients (name, normalized_name) VALUES (%s,%s) "
                        "ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                        (ing_name, normalized_name),
                    )
                    ingredient_id = cursor.lastrowid
                    if not ingredient_id:
                        cursor.execute(
                            "SELECT id FROM ingredients WHERE normalized_name = %s OR LOWER(name) = %s LIMIT 1",
                            (normalized_name, ing_name.lower()),
                        )
                        ingredient_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order) VALUES (%s,%s,%s,%s,%s)",
                    (recipe_id, ingredient_id, ingredient["quantity"], ingredient["unit"], index),
                )
            if image:
                cursor.execute(
                    "INSERT INTO recipe_images (recipe_id, storage_path, original_name, mime_type, width, height, is_primary) VALUES (%s,%s,%s,%s,%s,%s,TRUE)",
                    (recipe_id, image["storage_path"], image["original_name"], image["mime_type"], None, None),
                )
            if extra_media:
                for media_item in extra_media:
                    cursor.execute(
                        "INSERT INTO recipe_images (recipe_id, storage_path, original_name, mime_type, width, height, is_primary) VALUES (%s,%s,%s,%s,%s,%s,FALSE)",
                        (recipe_id, media_item["storage_path"], media_item["original_name"], media_item["mime_type"], None, None),
                    )
            connection.commit()
            return recipe_id
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    def update_recipe(
        self,
        recipe_id: int,
        title: str,
        description: str,
        category_id: int | None,
        location_id: int | None,
        servings: int | None,
        prep_minutes: int | None,
        cook_minutes: int | None,
        ingredients: list[dict],
        instructions: list[str],
        status: str,
        image: dict | None = None,
        extra_media: list[dict] | None = None,
        cooking_tips: str | None = None,
        serving_suggestion: str | None = None,
        food_type: str | None = None,
        taste: str | None = None,
        best_served: str | None = None,
    ) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "UPDATE recipes SET category_id = %s, location_id = %s, title = %s, description = %s, "
                "servings = %s, prep_minutes = %s, cook_minutes = %s, instructions = %s, "
                "cooking_tips = %s, serving_suggestion = %s, food_type = %s, taste = %s, best_served = %s, status = %s, "
                "published_at = CASE WHEN %s = 'published' AND published_at IS NULL THEN CURRENT_TIMESTAMP ELSE published_at END "
                "WHERE id = %s",
                (
                    category_id,
                    location_id,
                    title,
                    description or None,
                    servings,
                    prep_minutes,
                    cook_minutes,
                    json.dumps(instructions),
                    cooking_tips or None,
                    serving_suggestion or None,
                    food_type or None,
                    taste or None,
                    best_served or None,
                    status,
                    status,
                    recipe_id,
                ),
            )
            cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
            for index, ingredient in enumerate(ingredients):
                ing_name = ingredient["name"].strip()
                normalized_name = sub(r"[^a-z0-9]+", " ", ing_name.lower()).strip()
                cursor.execute(
                    "SELECT id FROM ingredients WHERE normalized_name = %s OR LOWER(name) = %s LIMIT 1",
                    (normalized_name, ing_name.lower()),
                )
                row = cursor.fetchone()
                if row:
                    ingredient_id = row[0]
                else:
                    cursor.execute(
                        "INSERT INTO ingredients (name, normalized_name) VALUES (%s,%s) "
                        "ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                        (ing_name, normalized_name),
                    )
                    ingredient_id = cursor.lastrowid
                    if not ingredient_id:
                        cursor.execute(
                            "SELECT id FROM ingredients WHERE normalized_name = %s OR LOWER(name) = %s LIMIT 1",
                            (normalized_name, ing_name.lower()),
                        )
                        ingredient_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order) VALUES (%s,%s,%s,%s,%s)",
                    (recipe_id, ingredient_id, ingredient["quantity"], ingredient["unit"], index),
                )
            if image:
                cursor.execute("DELETE FROM recipe_images WHERE recipe_id = %s AND is_primary = TRUE", (recipe_id,))
                cursor.execute(
                    "INSERT INTO recipe_images (recipe_id, storage_path, original_name, mime_type, width, height, is_primary) VALUES (%s,%s,%s,%s,%s,%s,TRUE)",
                    (recipe_id, image["storage_path"], image["original_name"], image["mime_type"], None, None),
                )
            if extra_media:
                for media_item in extra_media:
                    cursor.execute(
                        "INSERT INTO recipe_images (recipe_id, storage_path, original_name, mime_type, width, height, is_primary) VALUES (%s,%s,%s,%s,%s,%s,FALSE)",
                        (recipe_id, media_item["storage_path"], media_item["original_name"], media_item["mime_type"], None, None),
                    )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    def delete_recipe(self, recipe_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    def create_post(self, author_id: int, title: str, body: str, status: str) -> int:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO community_posts (author_id, title, body, status, published_at) "
                "VALUES (%s,%s,%s,%s,%s)",
                (author_id, title, body, status, None),
            )
            post_id = cursor.lastrowid
            if status == "published":
                cursor.execute("UPDATE community_posts SET published_at = CURRENT_TIMESTAMP WHERE id = %s", (post_id,))
            connection.commit()
            return post_id
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()

    def recipe_by_id(self, recipe_id: int) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, slug FROM recipes WHERE id = %s LIMIT 1", (recipe_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def recipe_by_slug(self, slug: str, user_id: int | None = None) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.*, c.name AS category_name, l.name AS location_name, u.username AS author_name, up.avatar_path AS author_avatar, "
                "COALESCE((SELECT AVG(rt.score) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS average_rating, "
                "COALESCE((SELECT COUNT(*) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS review_count, "
                "COALESCE((SELECT COUNT(*) FROM likes lk WHERE lk.recipe_id = r.id), 0) AS like_count, "
                "COALESCE((SELECT COUNT(*) FROM favorites f WHERE f.recipe_id = r.id), 0) AS save_count, "
                "COALESCE((SELECT lk.user_id FROM likes lk WHERE lk.recipe_id = r.id AND lk.user_id = %s), 0) AS is_liked, "
                "COALESCE((SELECT f.user_id FROM favorites f WHERE f.recipe_id = r.id AND f.user_id = %s), 0) AS is_saved, "
                "COALESCE((SELECT rt.score FROM ratings rt WHERE rt.recipe_id = r.id AND rt.user_id = %s), 0) AS user_rating, "
                "COALESCE((SELECT 1 FROM user_follows uf WHERE uf.follower_id = %s AND uf.following_id = r.author_id), 0) AS is_following, "
                "COALESCE((SELECT COUNT(*) FROM user_follows uf WHERE uf.following_id = r.author_id), 0) AS author_follower_count, "
                "COALESCE((SELECT COUNT(*) FROM recipes ar WHERE ar.author_id = r.author_id AND ar.status = 'published'), 0) AS author_recipe_count, "
                "(SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id "
                "ORDER BY ri.is_primary DESC, ri.id LIMIT 1) AS image_path, "
                "(SELECT ri.mime_type FROM recipe_images ri WHERE ri.recipe_id = r.id "
                "ORDER BY ri.is_primary DESC, ri.id LIMIT 1) AS media_mime_type, "
                "(SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id "
                "AND (ri.mime_type LIKE 'video/%' OR ri.storage_path LIKE '%.mp4' OR ri.storage_path LIKE '%.webm' OR ri.storage_path LIKE '%.mov' OR ri.storage_path LIKE '%.ogg') "
                "ORDER BY ri.is_primary DESC, ri.id LIMIT 1) AS video_path "
                "FROM recipes r LEFT JOIN categories c ON c.id = r.category_id "
                "LEFT JOIN locations l ON l.id = r.location_id "
                "LEFT JOIN users u ON u.id = r.author_id "
                "LEFT JOIN user_profiles up ON up.user_id = u.id "
                "WHERE r.slug = %s AND (r.status = 'published' OR r.author_id = %s) LIMIT 1",
                (user_id or 0, user_id or 0, user_id or 0, user_id or 0, slug, user_id or 0),
            )
            recipe = cursor.fetchone()
            if recipe is None:
                return None
            cursor.execute(
                "SELECT i.name, ri.quantity, ri.unit FROM recipe_ingredients ri "
                "JOIN ingredients i ON i.id = ri.ingredient_id WHERE ri.recipe_id = %s "
                "ORDER BY ri.sort_order, ri.id",
                (recipe["id"],),
            )
            recipe["ingredients"] = cursor.fetchall()
            return recipe
        finally:
            cursor.close()

    def increment_view(self, recipe_id: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE recipes SET view_count = COALESCE(view_count, 0) + 1 WHERE id = %s", (recipe_id,))
            connection.commit()
        finally:
            cursor.close()

    def toggle_like(self, recipe_id: int, user_id: int) -> bool:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1 FROM likes WHERE recipe_id = %s AND user_id = %s", (recipe_id, user_id))
            exists = cursor.fetchone() is not None
            if exists:
                cursor.execute("DELETE FROM likes WHERE recipe_id = %s AND user_id = %s", (recipe_id, user_id))
            else:
                cursor.execute("INSERT INTO likes (recipe_id, user_id) VALUES (%s, %s)", (recipe_id, user_id))
            connection.commit()
            return not exists
        finally:
            cursor.close()

    def toggle_favorite(self, recipe_id: int, user_id: int) -> bool:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1 FROM favorites WHERE recipe_id = %s AND user_id = %s", (recipe_id, user_id))
            exists = cursor.fetchone() is not None
            if exists:
                cursor.execute("DELETE FROM favorites WHERE recipe_id = %s AND user_id = %s", (recipe_id, user_id))
            else:
                cursor.execute("INSERT INTO favorites (recipe_id, user_id) VALUES (%s, %s)", (recipe_id, user_id))
            connection.commit()
            return not exists
        finally:
            cursor.close()

    def set_rating(self, recipe_id: int, user_id: int, score: int) -> None:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO ratings (recipe_id, user_id, score) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE score = VALUES(score)",
                (recipe_id, user_id, score),
            )
            connection.commit()
        finally:
            cursor.close()

    def toggle_follow(self, author_id: int, user_id: int) -> bool:
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1 FROM user_follows WHERE follower_id = %s AND following_id = %s", (user_id, author_id))
            exists = cursor.fetchone() is not None
            if exists:
                cursor.execute("DELETE FROM user_follows WHERE follower_id = %s AND following_id = %s", (user_id, author_id))
            else:
                cursor.execute("INSERT INTO user_follows (follower_id, following_id) VALUES (%s, %s)", (user_id, author_id))
            connection.commit()
            return not exists
        finally:
            cursor.close()

    def interaction_counts(self, recipe_id: int) -> dict:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT (SELECT COUNT(*) FROM likes WHERE recipe_id=%s) AS like_count, "
                "(SELECT COUNT(*) FROM favorites WHERE recipe_id=%s) AS save_count, "
                "COALESCE((SELECT AVG(score) FROM ratings WHERE recipe_id=%s), 0) AS average_rating, "
                "(SELECT COUNT(*) FROM ratings WHERE recipe_id=%s) AS review_count",
                (recipe_id, recipe_id, recipe_id, recipe_id),
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def search(self, query: str, limit: int = 20) -> dict[str, list[dict]]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = query.strip()
        if not query:
            return {"recipes": []}
        words = [w.strip().lower() for w in query.split() if w.strip()]
        if not words:
            return {"recipes": []}
        try:
            conditions = ["r.status = 'published'"]
            params = []
            for word in words:
                conditions.append("LOWER(r.title) LIKE %s")
                params.append(f"%{word}%")
            params.append(limit)
            cursor.execute(
                "SELECT r.id, r.title, r.slug, r.description, r.view_count, "
                "c.name AS category_name, l.name AS location_name, u.username AS author_name, "
                "(SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id "
                "ORDER BY ri.is_primary DESC, ri.id LIMIT 1) AS image_path "
                "FROM recipes r LEFT JOIN categories c ON c.id = r.category_id "
                "LEFT JOIN locations l ON l.id = r.location_id "
                "LEFT JOIN users u ON u.id = r.author_id "
                f"WHERE {' AND '.join(conditions)} "
                "ORDER BY r.view_count DESC, r.created_at DESC LIMIT %s",
                tuple(params),
            )
            recipes = cursor.fetchall()
            return {"recipes": recipes}
        finally:
            cursor.close()

    def category_by_slug_or_name(self, identifier: str) -> dict | None:
        clean = (identifier or "").strip().lower()
        if not clean:
            return None
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cat_id = int(clean) if clean.isdigit() else 0
            cursor.execute(
                "SELECT id, name, slug, description, image_url FROM categories "
                "WHERE slug = %s OR LOWER(name) = %s OR REPLACE(LOWER(name), ' ', '-') = %s OR id = %s LIMIT 1",
                (clean, clean, clean, cat_id),
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def published_recipes(
        self,
        limit: int = 40,
        recipe_filter: str = "all",
        category_slug: str | None = None,
        location_name: str | None = None,
        search_query: str | None = None,
    ) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            order_by = "r.created_at DESC, r.id DESC"
            if recipe_filter == "newest":
                order_by = "r.created_at DESC, r.id DESC"
            elif recipe_filter == "popular":
                order_by = "average_rating DESC, review_count DESC, r.view_count DESC, r.id DESC"
            elif recipe_filter == "rating_high":
                order_by = "average_rating DESC, review_count DESC, r.id DESC"
            elif recipe_filter == "rating_low":
                order_by = "average_rating ASC, r.id DESC"
            elif recipe_filter == "views":
                order_by = "r.view_count DESC, r.id DESC"

            conditions = ["r.status = 'published'"]
            params = []

            if category_slug:
                cat_clean = category_slug.strip().lower()
                cat_id = int(cat_clean) if cat_clean.isdigit() else 0
                slug_variants = {cat_clean}
                if cat_clean in {"traditional-filipino-food", "filipino"}:
                    slug_variants.update(["traditional-filipino-food", "filipino"])
                elif cat_clean in {"rice-meals", "rice-dishes"}:
                    slug_variants.update(["rice-meals", "rice-dishes"])
                elif cat_clean in {"grilled-bbq", "grilled-dishes"}:
                    slug_variants.update(["grilled-bbq", "grilled-dishes"])
                elif cat_clean in {"sandwiches", "sandwiches-burgers"}:
                    slug_variants.update(["sandwiches", "sandwiches-burgers"])
                elif cat_clean in {"smoothies", "smoothies-juices"}:
                    slug_variants.update(["smoothies", "smoothies-juices"])
                elif cat_clean in {"snacks", "snacks-appetizers"}:
                    slug_variants.update(["snacks", "snacks-appetizers"])
                elif cat_clean in {"quick-easy", "quick-and-easy"}:
                    slug_variants.update(["quick-easy", "quick-and-easy"])

                clause_parts = []
                for s in slug_variants:
                    clause_parts.append("c.slug = %s OR LOWER(c.name) = %s OR REPLACE(LOWER(c.name), ' ', '-') = %s")
                    params.extend([s, s, s])
                if cat_id:
                    clause_parts.append("c.id = %s")
                    params.append(cat_id)
                conditions.append(f"({' OR '.join(clause_parts)})")

            if location_name:
                loc_clean = location_name.strip().lower()
                loc_id = int(loc_clean) if loc_clean.isdigit() else 0
                conditions.append("(LOWER(l.name) = %s OR REPLACE(LOWER(l.name), ' ', '-') = %s OR LOWER(COALESCE(l.country_code, '')) = %s OR l.id = %s)")
                params.extend([loc_clean, loc_clean, loc_clean, loc_id])

            if search_query and search_query.strip():
                words = [w.strip().lower() for w in search_query.strip().split() if w.strip()]
                for word in words:
                    conditions.append("LOWER(r.title) LIKE %s")
                    params.append(f"%{word}%")

            params.append(limit)
            sql = (
                "SELECT r.id, r.title, r.slug, r.description, r.servings, r.prep_minutes, r.cook_minutes, r.view_count, r.created_at, "
                "c.name AS category_name, c.slug AS category_slug, l.name AS location_name, l.country_code AS location_country_code, "
                "u.username AS author_name, up.avatar_path AS author_avatar, "
                "COALESCE((SELECT AVG(rt.score) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS average_rating, "
                "COALESCE((SELECT COUNT(*) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS review_count, "
                "COALESCE((SELECT COUNT(*) FROM likes lk WHERE lk.recipe_id = r.id), 0) AS like_count, "
                "(SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id "
                "ORDER BY ri.is_primary DESC, ri.id LIMIT 1) AS image_path "
                "FROM recipes r LEFT JOIN categories c ON c.id = r.category_id "
                "LEFT JOIN locations l ON l.id = r.location_id "
                "LEFT JOIN users u ON u.id = r.author_id "
                "LEFT JOIN user_profiles up ON up.user_id = u.id "
                f"WHERE {' AND '.join(conditions)} "
                f"ORDER BY {order_by} LIMIT %s"
            )
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()

    def featured_recipes(self, limit=6) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.id, r.title, r.slug, r.description, r.view_count, c.name AS category_name, "
                "COALESCE((SELECT AVG(rt.score) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS average_rating, "
                "COALESCE((SELECT COUNT(rt.score) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS review_count, "
                "COALESCE((SELECT COUNT(*) FROM likes lk WHERE lk.recipe_id = r.id), 0) AS like_count, "
                "(SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id ORDER BY ri.is_primary DESC, ri.id LIMIT 1) AS image_path "
                "FROM recipes r LEFT JOIN categories c ON c.id = r.category_id "
                "WHERE r.status = 'published' "
                "ORDER BY average_rating DESC, review_count DESC, r.view_count DESC, r.created_at DESC, r.id DESC LIMIT %s",
                (limit,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
