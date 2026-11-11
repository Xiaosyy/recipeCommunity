from recipeshare import create_app


def test_keyword_search_filters_by_recipe_name():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/recipes?q=chicken")
        assert response.status_code == 200
        assert b"Chicken Adobo" in response.data
        assert b"Chicken Kare-Kare" in response.data
        assert b"Spaghetti Bolognese" not in response.data
        assert b"Batangas Lomi" not in response.data


def test_keyword_search_filters_by_word():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/recipes?q=pork")
        assert response.status_code == 200
        assert b"Pork Sisig" in response.data
        assert b"Pork Sinigang" in response.data
        assert b"Spaghetti Bolognese" not in response.data
        assert b"Chicken Adobo" not in response.data


def test_keyword_search_case_insensitive():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/recipes?q=SPAGHETTI")
        assert response.status_code == 200
        assert b"Spaghetti Bolognese" in response.data
        assert b"Chicken Adobo" not in response.data


def test_keyword_search_with_location_filter():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        # Philippines has Chicken Adobo and Chicken Kare-Kare
        response = client.get("/recipes?location=philippines&q=chicken")
        assert response.status_code == 200
        assert b"Chicken Adobo" in response.data
        assert b"Chicken Kare-Kare" in response.data

        # Italy does not have chicken recipes
        response_italy = client.get("/recipes?location=italy&q=chicken")
        assert response_italy.status_code == 200
        assert b"No recipes found matching" in response_italy.data
        assert b"Chicken Adobo" not in response_italy.data


def test_locations_page_navigation_and_recipes():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/locations?location_id=1")
        assert response.status_code == 200
        assert b"View recipes from Philippines" in response.data
        assert b"Inihaw na Baboy" in response.data
        assert b"/recipes?location=philippines" in response.data


def test_spa_page_recipes_with_keyword_search():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/api/v1/ui/pages/recipes?q=pork")
        assert response.status_code == 200
        html = response.json["html"]
        assert "Pork Sisig" in html
        assert "Pork Sinigang" in html
        assert "Spaghetti Bolognese" not in html


def test_spa_page_locations_selection():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/api/v1/ui/pages/locations?location_id=1")
        assert response.status_code == 200
        html = response.json["html"]
        assert "View recipes from Philippines" in html
        assert "Inihaw na Baboy" in html
        assert 'href="/recipes?location=italy"' not in html


def test_locations_page_keyword_search_filters_by_recipe_name_or_word():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/locations?q=adobo")
        assert response.status_code == 200
        assert b"Inihaw na Baboy" in response.data
        assert b"Roman Carbonara" not in response.data

        spa_resp = client.get("/api/v1/ui/pages/locations?q=spaghetti")
        assert spa_resp.status_code == 200
        spa_html = spa_resp.json["html"]
        assert "Roman Carbonara" in spa_html
        assert "Inihaw na Baboy" not in spa_html


def test_recipe_posted_goes_to_assigned_category_and_location():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = 8
            session["username"] = "precious"
            session["user_role"] = "user"

        form_data = {
            "title": "Cebu Lechon Belly Special",
            "description": "Crispy pork belly stuffed with lemongrass and garlic.",
            "status": "published",
            "category_id": "32",  # Pork category
            "location_id": "1",    # Philippines
            "ingredient_name": ["Pork belly", "Lemongrass"],
            "ingredient_quantity": ["1000", "3"],
            "ingredient_unit": ["g", "stalks"],
            "instructions": "Roll pork belly with herbs\nRoast at 180C\nCrack skin at high heat",
        }
        res = client.post("/recipes/create", data=form_data, follow_redirects=True)
        assert res.status_code == 200
        assert "Cebu Lechon Belly Special" in res.data.decode()

        # 1. Check it appears under its category: /recipes?category=pork
        cat_resp = client.get("/recipes?category=pork")
        assert cat_resp.status_code == 200
        assert "Cebu Lechon Belly Special" in cat_resp.data.decode()

        # 2. Check it does NOT appear under another category: /recipes?category=desserts
        other_cat = client.get("/recipes?category=desserts")
        assert other_cat.status_code == 200
        assert "Cebu Lechon Belly Special" not in other_cat.data.decode()

        # 3. Check it appears under its location: /recipes?location=philippines
        loc_resp = client.get("/recipes?location=philippines")
        assert loc_resp.status_code == 200
        assert "Cebu Lechon Belly Special" in loc_resp.data.decode()

        # 4. Check it does NOT appear under another location: /recipes?location=italy
        other_loc = client.get("/recipes?location=italy")
        assert other_loc.status_code == 200
        assert "Cebu Lechon Belly Special" not in other_loc.data.decode()

        # 5. Check combined filter: category + location + recipe keyword
        combined = client.get("/recipes?category=pork&location=philippines&q=lechon")
        assert combined.status_code == 200
        assert "Cebu Lechon Belly Special" in combined.data.decode()

        # 6. Check location showcase links to its recipes
        locations_page = client.get("/locations?location_id=1")
        assert locations_page.status_code == 200
        assert "/recipes?location=philippines" in locations_page.data.decode()
        assert "View recipes from Philippines" in locations_page.data.decode()

        # Clean up
        with app.app_context():
            from recipeshare.shared.database import get_connection
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM recipes WHERE title = %s", ("Cebu Lechon Belly Special",))
            conn.commit()

