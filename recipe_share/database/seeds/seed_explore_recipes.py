"""
Seed explore recipes matching the reference UI design.
"""
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from recipeshare import create_app
from recipeshare.shared.database import get_connection


def seed():
    app = create_app()
    with app.app_context():
        conn = get_connection()
        c = conn.cursor(dictionary=True)

        # 1. Categories
        categories = [
            ("Beef", "beef", "Hearty and savory beef recipes"),
            ("Seafood", "seafood", "Fresh and delicious ocean catches"),
            ("Breakfast", "breakfast", "Morning favorites and brunch recipes"),
            ("Lunch", "lunch", "Satisfying midday rice bowls, wraps, and plates"),
            ("Dinner", "dinner", "Hearty seared steaks, roasts, and evening family meals"),
            ("Snacks & Appetizers", "snacks-appetizers", "Crispy spring rolls, finger foods, and party starters"),
            ("Soups", "soups", "Comforting warm soups and broths"),
            ("Healthy Meals", "healthy-meals", "Nutritious and balanced culinary creations"),
        ]
        for name, slug, desc in categories:
            c.execute("SELECT id FROM categories WHERE slug = %s", (slug,))
            row = c.fetchone()
            if not row:
                c.execute(
                    "INSERT INTO categories (name, slug, description, is_active) VALUES (%s, %s, %s, 1)",
                    (name, slug, desc),
                )
        conn.commit()

        # Fetch category map
        c.execute("SELECT id, slug FROM categories")
        cat_map = {row["slug"]: row["id"] for row in c.fetchall()}

        # Fetch location map
        c.execute("SELECT id, name FROM locations")
        loc_map = {row["name"].lower(): row["id"] for row in c.fetchall()}

        # 2. Users & Profiles
        users = [
            ("sweetbaker", "sweetbaker@example.com", "Sweet Baker", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=120&q=80"),
            ("italianchef", "italianchef@example.com", "Italian Chef", "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=120&q=80"),
            ("greenchef", "greenchef@example.com", "Green Chef", "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=120&q=80"),
        ]
        user_ids = {}
        for username, email, display_name, avatar in users:
            c.execute("SELECT id FROM users WHERE username = %s", (username,))
            row = c.fetchone()
            if not row:
                pwd_hash = generate_password_hash("Secret123!")
                c.execute(
                    "INSERT INTO users (role_id, username, email, password_hash, status) VALUES (2, %s, %s, %s, 'active')",
                    (username, email, pwd_hash),
                )
                uid = c.lastrowid
            else:
                uid = row["id"]
            user_ids[username] = uid

            # Update or insert profile
            c.execute("SELECT user_id FROM user_profiles WHERE user_id = %s", (uid,))
            if not c.fetchone():
                c.execute(
                    "INSERT INTO user_profiles (user_id, display_name, avatar_path) VALUES (%s, %s, %s)",
                    (uid, display_name, avatar),
                )
            else:
                c.execute(
                    "UPDATE user_profiles SET display_name = %s, avatar_path = %s WHERE user_id = %s",
                    (display_name, avatar, uid),
                )
        conn.commit()

        # Update juan_cruz profile with avatar
        c.execute("SELECT id FROM users WHERE username = 'juan_cruz'")
        jc_row = c.fetchone()
        if jc_row:
            jc_id = jc_row["id"]
            jc_avatar = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=120&q=80"
            c.execute("SELECT user_id FROM user_profiles WHERE user_id = %s", (jc_id,))
            if not c.fetchone():
                c.execute(
                    "INSERT INTO user_profiles (user_id, display_name, avatar_path) VALUES (%s, 'Juan Cruz', %s)",
                    (jc_id, jc_avatar),
                )
            else:
                c.execute("UPDATE user_profiles SET avatar_path = %s WHERE user_id = %s", (jc_avatar, jc_id))
            conn.commit()

        # 3. Recipes
        now = datetime.now()
        recipes_to_seed = [
            {
                "title": "Margherita Pizza",
                "slug": "margherita-pizza",
                "desc": "Classic Neapolitan Margherita pizza with San Marzano tomatoes, fresh mozzarella, fresh basil, and extra-virgin olive oil.",
                "category_slug": "italian",
                "location_name": "italy",
                "author": "sweetbaker",
                "prep": 15,
                "cook": 30,
                "servings": 4,
                "views": 0,
                "published_offset": 2,
                "image": "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?auto=format&fit=crop&w=800&q=80",
                "rating": 4.7,
                "reviews": 1800,
            },
            {
                "title": "Strawberry Shortcake",
                "slug": "strawberry-shortcake",
                "desc": "Delightful layered sponge cake with sweetened whipped chantilly cream and glazed fresh strawberries.",
                "category_slug": "desserts",
                "location_name": None,
                "author": "italianchef",
                "prep": 25,
                "cook": 60,
                "servings": 6,
                "views": 0,
                "published_offset": 3,
                "image": "https://images.unsplash.com/photo-1565958011703-44f9829ba187?auto=format&fit=crop&w=800&q=80",
                "rating": 4.9,
                "reviews": 3200,
            },
            {
                "title": "Beef Stir-Fry",
                "slug": "beef-stir-fry",
                "desc": "Tender strips of flank steak sizzled with crisp bell peppers, broccoli florets, and ginger soy sauce.",
                "category_slug": "beef",
                "location_name": None,
                "author": "greenchef",
                "prep": 15,
                "cook": 25,
                "servings": 3,
                "views": 0,
                "published_offset": 4,
                "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80",
                "rating": 4.7,
                "reviews": 1500,
            },
            {
                "title": "Garlic Butter Shrimp",
                "slug": "garlic-butter-shrimp",
                "desc": "Plump juicy shrimp tossed in rich toasted garlic butter, lemon juice, and freshly chopped parsley.",
                "category_slug": "seafood",
                "location_name": None,
                "author": "greenchef",
                "prep": 10,
                "cook": 20,
                "servings": 4,
                "views": 0,
                "published_offset": 5,
                "image": "https://images.unsplash.com/photo-1559742811-82286364ceaf?auto=format&fit=crop&w=800&q=80",
                "rating": 4.8,
                "reviews": 1700,
            },
            {
                "title": "Fluffy Pancakes",
                "slug": "fluffy-pancakes",
                "desc": "Golden fluffy buttermilk pancakes stacked high, topped with fresh wild blueberries and warm maple syrup.",
                "category_slug": "breakfast",
                "location_name": None,
                "author": "sweetbaker",
                "prep": 10,
                "cook": 15,
                "servings": 4,
                "views": 0,
                "published_offset": 6,
                "image": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?auto=format&fit=crop&w=800&q=80",
                "rating": 4.7,
                "reviews": 1300,
            },
            {
                "title": "Creamy Mushroom Soup",
                "slug": "creamy-mushroom-soup",
                "desc": "Velvety smooth soup with sauteed cremini and shiitake mushrooms, fresh thyme, and cream.",
                "category_slug": "soups",
                "location_name": None,
                "author": "sweetbaker",
                "prep": 15,
                "cook": 35,
                "servings": 4,
                "views": 0,
                "published_offset": 7,
                "image": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
                "rating": 4.6,
                "reviews": 1100,
            },
            {
                "title": "Quinoa Salad",
                "slug": "quinoa-salad",
                "desc": "Vibrant and nourishing bowl of fluffy quinoa, crisp cucumbers, cherry tomatoes, herbs, and lemon vinaigrette.",
                "category_slug": "healthy-meals",
                "location_name": None,
                "author": "greenchef",
                "prep": 15,
                "cook": 20,
                "servings": 2,
                "views": 0,
                "published_offset": 8,
                "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
                "rating": 4.8,
                "reviews": 1200,
            },
        ]

        # Ensure Chicken Adobo has the highest published_at and Pancit Canton belongs to Philippines / Filipino
        c.execute("UPDATE recipes SET published_at = %s, cook_minutes = 30 WHERE slug = 'chicken-adobo'", (now,))
        c.execute(
            "UPDATE recipes SET location_id = %s, category_id = %s WHERE slug = 'pancit-canton'",
            (loc_map.get("philippines"), cat_map.get("filipino")),
        )
        # Remove duplicate auto-generated test spam recipes
        c.execute(
            "SELECT id FROM recipes WHERE slug LIKE 'chimichurri-grilled-steak-bowl%' "
            "OR slug LIKE 'savory-empanadas%' OR slug LIKE 'artisan-%-spiced-noodle-stir-fry%'"
        )
        spam_ids = [r["id"] for r in c.fetchall()]
        for sid in spam_ids:
            c.execute("DELETE FROM recipe_images WHERE recipe_id = %s", (sid,))
            c.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (sid,))
            c.execute("DELETE FROM ratings WHERE recipe_id = %s", (sid,))
            c.execute("DELETE FROM likes WHERE recipe_id = %s", (sid,))
            c.execute("DELETE FROM favorites WHERE recipe_id = %s", (sid,))
            c.execute("DELETE FROM recipes WHERE id = %s", (sid,))
        conn.commit()

        for idx, item in enumerate(recipes_to_seed):
            c.execute("SELECT id FROM recipes WHERE slug = %s", (item["slug"],))
            row = c.fetchone()
            pub_date = now - timedelta(hours=item["published_offset"])
            author_id = user_ids.get(item["author"], 1)
            cat_id = cat_map.get(item["category_slug"])
            loc_id = loc_map.get(item["location_name"])
            instr = json.dumps([
                f"Prepare and measure all fresh ingredients for {item['title']}.",
                "Heat the cooking pan and saute aromatic ingredients until fragrant.",
                "Combine remaining ingredients and simmer until cooked through and flavor develops.",
                "Garnish with fresh herbs and serve immediately while hot.",
            ])

            if not row:
                c.execute(
                    "INSERT INTO recipes (author_id, category_id, location_id, title, slug, description, servings, "
                    "prep_minutes, cook_minutes, instructions, status, published_at, view_count) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'published', %s, %s)",
                    (author_id, cat_id, loc_id, item["title"], item["slug"], item["desc"], item["servings"],
                     item["prep"], item["cook"], instr, pub_date, item["views"]),
                )
                rec_id = c.lastrowid
            else:
                rec_id = row["id"]
                c.execute(
                    "UPDATE recipes SET author_id = %s, category_id = %s, location_id = %s, title = %s, "
                    "description = %s, servings = %s, prep_minutes = %s, cook_minutes = %s, "
                    "status = 'published', published_at = %s, view_count = %s WHERE id = %s",
                    (author_id, cat_id, loc_id, item["title"], item["desc"], item["servings"], item["prep"],
                     item["cook"], pub_date, item["views"], rec_id),
                )

            # Insert/update image
            c.execute("SELECT id FROM recipe_images WHERE recipe_id = %s", (rec_id,))
            img_row = c.fetchone()
            if not img_row:
                c.execute(
                    "INSERT INTO recipe_images (recipe_id, storage_path, original_name, mime_type, is_primary) "
                    "VALUES (%s, %s, %s, 'image/jpeg', 1)",
                    (rec_id, item["image"], f"{item['slug']}.jpg"),
                )
            else:
                c.execute(
                    "UPDATE recipe_images SET storage_path = %s WHERE id = %s",
                    (item["image"], img_row["id"]),
                )

            # Insert ratings
            c.execute("SELECT COUNT(*) as cnt FROM ratings WHERE recipe_id = %s", (rec_id,))
            if c.fetchone()["cnt"] == 0:
                c.execute("INSERT INTO ratings (recipe_id, user_id, score) VALUES (%s, 1, %s)", (rec_id, int(round(item["rating"]))))
                c.execute("INSERT INTO ratings (recipe_id, user_id, score) VALUES (%s, 2, %s)", (rec_id, 5))

        conn.commit()
        c.close()

        # Ensure all 6 featured locations have their authentic signature recipes
        from recipeshare.location.service import LocationRecipeService
        LocationRecipeService().page_data()
        print("Successfully seeded explore recipes!")


if __name__ == "__main__":
    seed()

