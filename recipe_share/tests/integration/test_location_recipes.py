from flask import session

from recipeshare import create_app


def test_locations_page_shows_location_generator():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/locations")
        assert response.status_code == 200
        assert b"Recipes by location" in response.data
        assert b"location-card" in response.data


def test_recipe_detail_has_steps_and_ingredients():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/recipes/chicken-adobo")
        assert response.status_code == 200
        assert b"Ingredients" in response.data
        assert b"Step-by-Step Cooking Instructions" in response.data


def test_location_spa_fragment_has_recipes():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/api/v1/ui/pages/locations")
        assert response.status_code == 200
        assert response.json["html"]
        assert "Recipes by location" in response.json["html"]
        assert "location-card" in response.json["html"]


def test_category_filters_recipe_catalog():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/recipes?category=filipino")
        assert response.status_code == 200
        assert b"Category" in response.data
        assert b"Filipino" in response.data


def test_location_recipe_selection():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/locations?location_id=1")
        assert response.status_code == 200
        assert b"/recipes?location=" in response.data
        assert b"View recipes from Philippines" in response.data


def test_location_click_opens_filtered_recipe_catalog():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/recipes?location=italy")
        assert response.status_code == 200
        assert b"Italy" in response.data
        assert b"Spaghetti Bolognese" in response.data
        assert b"Chicken Adobo" not in response.data


def test_location_spa_selection_contains_only_selected_location_recipes():
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    with app.test_client() as client:
        response = client.get("/api/v1/ui/pages/locations?location_id=1")
        assert response.status_code == 200
        html = response.json["html"]
        assert "/recipes?location=philippines" in html


def test_location_dropdown_is_alphabetical_and_auto_generates_recipes(client):
    response = client.get("/locations")
    assert response.status_code == 200
    text = response.data.decode("utf-8")
    list_start = text.find('class="location-dropdown-list"')
    assert list_start != -1
    dropdown_slice = text[list_start:]
    assert dropdown_slice.find("Afghanistan") < dropdown_slice.find("Italy") < dropdown_slice.find("Philippines") < dropdown_slice.find("Zimbabwe")

    gen_resp = client.post("/api/v1/ui/locations/generate", json={"location_id": 4})
    assert gen_resp.status_code == 200
    assert gen_resp.json["ok"] is True
    recipe_id = gen_resp.json["recipe_id"]
    assert recipe_id is not None

    from recipeshare.shared.database import get_connection
    with client.application.app_context():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM recipe_images WHERE recipe_id = %s", (recipe_id,))
        cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
        cur.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
        conn.commit()
        cur.close()
