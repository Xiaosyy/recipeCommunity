from recipeshare.home.service import HomeService

def test_filter_button_and_chips_removed(client):
    response = client.get("/recipes")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # 1. Verify standalone "Filter" button is removed
    assert 'class="recipe-search-btn"' not in html
    assert '>Filter</button>' not in html

    # 2. Verify category chips bar is removed
    assert 'class="recipe-explore-chips"' not in html

    # 3. Verify auto-submit onchange is present on category & location selects
    assert 'data-filter-category onchange="this.form.submit()"' in html
    assert 'data-filter-location onchange="this.form.submit()"' in html

    # 4. Verify search glass button is present for submission
    assert 'class="recipe-search-glass-btn"' in html


def test_categories_page_has_pictures_for_all_categories(client):
    response = client.get("/categories")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Verify category cards and images are present
    assert 'class="category-showcase-grid"' in html
    assert 'class="category-showcase-card__img"' in html
    assert 'images.unsplash.com' in html


def test_home_service_categories_have_image_urls(app):
    with app.app_context():
        service = HomeService()
        catalog = service.recipe_catalog()
        categories = catalog["categories"]
        assert len(categories) > 0
        for cat in categories:
            assert cat.get("image_url"), f"Category {cat.get('slug')} is missing image_url"
            assert cat["image_url"].startswith("http")


def test_tablet_picture_is_replaced_with_real_recipe_photos(client):
    response = client.get("/recipes")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Ensure the old tablet image URL is completely absent
    assert "photo-1495521821757-a1efb6729352" not in html
    # Ensure real food recipe image URLs are present
    assert "photo-1612927601601-6638404737ce" in html or "photo-1546069901-ba9599a7e63c" in html or "photo-1604908176997" in html


def test_category_options_display_all_categories(client):
    response = client.get("/recipes")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # 1. Existing categories with recipes must be displayed
    assert "Asian" in html
    assert "Filipino" in html
    assert "Desserts" in html

    # 2. Newly added and recommended categories must be displayed in the category dropdown
    assert "Chicken" in html
    assert "Vegetarian" in html
    assert "Vegetables" in html
    assert "Snacks" in html
    assert "Baking" in html
    assert "Quick &amp; Easy" in html or "Quick & Easy" in html
    assert "Others" in html
    assert "Appetizers" in html
    assert "Cakes &amp; Pastries" in html or "Cakes & Pastries" in html
    assert "optgroup" in html


def test_dark_mode_removed_from_settings_and_layouts(client):
    # 1. Check layout does NOT include theme-dark.css or theme.js
    res_home = client.get("/")
    assert res_home.status_code == 200
    home_html = res_home.get_data(as_text=True)
    assert "theme-dark.css" not in home_html
    assert "theme.js" not in home_html

    # 2. Check settings page renders clean title without dark mode toggles
    from unittest.mock import patch
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "testuser"

    mock_profile = {"display_name": "Test User", "bio": "Hello world", "avatar_path": None}
    with patch("recipeshare.home.routes.UserRepository.profile_data", return_value={"profile": mock_profile}):
        res_settings = client.get("/settings")
        assert res_settings.status_code == 200
        settings_html = res_settings.get_data(as_text=True)
        assert "<h1>Profile Settings</h1>" in settings_html
        assert "data-theme-pill-toggle" not in settings_html
        assert "theme-pill-track" not in settings_html
        assert "theme-switcher-grid" not in settings_html
        assert "theme-choice-card" not in settings_html
        # Verify My Posts, My Recipes, Saved tabs removed from settings profile-tabs
        tabs_section = settings_html[settings_html.find('class="profile-tabs"'):settings_html.find('</nav>', settings_html.find('class="profile-tabs"'))]
        assert "My Posts" not in tabs_section
        assert "My Recipes" not in tabs_section
        assert "Saved" not in tabs_section


def test_popular_categories_and_recipes_ordered_by_ratings(app):
    with app.app_context():
        from recipeshare.home.repository import HomeRepository
        service = HomeService()
        repo = HomeRepository()

        # 1. Verify Home Discovery categories are ordered by average rating descending
        discovery = service.discovery()
        categories = discovery["categories"]
        assert len(categories) > 0
        cat_ratings = [float(c.get("average_rating") or 0) for c in categories]
        assert cat_ratings == sorted(cat_ratings, reverse=True), "Categories should be ranked by ratings"

        # 2. Verify published_recipes with 'popular' filter ranks highest rated first
        popular_recipes = repo.published_recipes(recipe_filter="popular")
        assert len(popular_recipes) > 0
        recipe_ratings = [float(r.get("average_rating") or 0) for r in popular_recipes]
        assert recipe_ratings == sorted(recipe_ratings, reverse=True), "Popular recipes should be ranked by ratings"

        # 3. Verify featured recipes are ordered by ratings
        featured = repo.featured_recipes()
        assert len(featured) > 0
        featured_ratings = [float(f.get("average_rating") or 0) for f in featured]
        assert featured_ratings == sorted(featured_ratings, reverse=True), "Featured recipes should be ranked by ratings"


def test_new_and_recommended_categories_loaded(client, app):
    res = client.get("/categories")
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    expected_categories = [
        "Chicken", "Vegetarian", "Vegetables", "Snacks", "Baking",
        "Quick &amp; Easy", "Others", "Pork", "Lamb", "Fish",
        "Rice Meals", "Grilled &amp; BBQ", "Fried Foods", "Appetizers",
        "Salads", "Sandwiches", "Street Food", "Vegan", "Low-Carb Meals",
        "Dairy-Free", "Gluten-Free", "Drinks &amp; Beverages", "Smoothies",
        "Cakes &amp; Pastries", "Sauces &amp; Dips", "Traditional Filipino Food"
    ]
    for cat in expected_categories:
        assert cat in html, f"Expected category '{cat}' to be rendered on /categories"

    # Test filtering by new category slugs
    for slug in ["chicken", "vegetarian", "vegetables", "snacks", "baking", "quick-easy", "others", "rice-meals", "grilled-bbq", "traditional-filipino-food"]:
        res_cat = client.get(f"/recipes?category={slug}")
        assert res_cat.status_code == 200





