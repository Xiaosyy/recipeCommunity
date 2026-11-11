from unittest.mock import patch


def test_dashboard_stats_api(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "foodie_chef"
        session["user_role"] = "user"

    response = client.get("/api/v1/ui/dashboard-stats?period=all")
    assert response.status_code == 200
    data = response.get_json()
    assert "metrics" in data
    assert "recipe_count" in data["metrics"]
    assert "total_views" in data["metrics"]
    assert "total_likes" in data["metrics"]
    assert "active_chefs" in data["metrics"]
    assert "chart_views" in data
    assert "chart_likes" in data
    assert isinstance(data["chart_views"], list)
    assert isinstance(data["chart_likes"], list)


def test_dashboard_stats_api_with_period(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "foodie_chef"
        session["user_role"] = "user"

    response = client.get("/api/v1/ui/dashboard-stats?period=week")
    assert response.status_code == 200
    data = response.get_json()
    assert "metrics" in data
    assert "chart_views" in data


def test_dashboard_inventory_reliable_statistics_updates(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "foodie_chef"
        session["user_role"] = "user"

    # 1. Fetch dashboard stats API
    res = client.get("/api/v1/ui/dashboard-stats?period=all")
    assert res.status_code == 200
    data = res.get_json()
    assert "inventory" in data
    assert len(data["inventory"]) >= 25, f"Expected full inventory, got {len(data['inventory'])}"
    assert "top_views" in data
    assert "top_likes" in data

    # 2. Verify dashboard page HTML renders inventory with reliable statistic attributes
    page_res = client.get("/dashboard")
    assert page_res.status_code == 200
    html = page_res.get_data(as_text=True)
    assert 'data-inventory-card' in html
    assert 'data-latest=' in html
    assert 'data-views=' in html
    assert 'data-likes=' in html
    assert 'data-recipe-views' in html
    assert 'data-recipe-likes' in html
    assert 'data-ranking-container="view_count"' in html
    assert 'data-ranking-container="like_count"' in html

    # 3. Verify location options contains all locations
    assert len(data.get("locations", [])) > 150
    assert "Philippines" in html
    assert "United States" in html
    assert "Japan" in html
    assert "Italy" in html



def test_user_follow_toggle(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["username"] = "follower_user"
        session["user_role"] = "user"

    # User 2 follows User 1
    with patch("recipeshare.ui.UserRepository.find_by_id", return_value={"id": 1, "username": "chef_one"}):
        with patch("recipeshare.ui.HomeRepository.toggle_follow", return_value=True) as mock_toggle:
            with patch("recipeshare.ui.NotificationRepository.create") as mock_notif:
                with patch("recipeshare.ui.UserRepository.follower_count", return_value=5):
                    with patch("recipeshare.ui.UserRepository.following_count", return_value=3):
                        res = client.post("/api/v1/ui/users/1/follow")
                        assert res.status_code == 200
                        json_data = res.get_json()
                        assert json_data["active"] is True
                        assert json_data["follower_count"] == 5
                        assert json_data["following_count"] == 3
                        mock_toggle.assert_called_once_with(1, 2)
                        mock_notif.assert_called_once()
                        args = mock_notif.call_args[0]
                        assert args[0] == 1  # target_user_id
                        assert args[1] == "user_followed"


def test_user_cannot_follow_self(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "chef_one"
        session["user_role"] = "user"

    res = client.post("/api/v1/ui/users/1/follow")
    assert res.status_code == 422
    assert "own account" in res.get_json()["error"]["message"]


def test_recipe_action_follow(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["username"] = "cooking_fan"
        session["user_role"] = "user"

    mock_recipe = {"id": 10, "author_id": 1, "slug": "tasty-soup", "title": "Tasty Soup", "author_name": "master_chef"}
    with patch("recipeshare.ui.HomeService.recipe_detail", return_value=mock_recipe):
        with patch("recipeshare.ui.HomeRepository.toggle_follow", return_value=True) as mock_toggle:
            with patch("recipeshare.ui.NotificationRepository.create") as mock_notif:
                with patch("recipeshare.ui.UserRepository.follower_count", return_value=12):
                    res = client.post("/api/v1/ui/recipe-actions/follow", json={"slug": "tasty-soup"})
                    assert res.status_code == 200
                    payload = res.get_json()
                    assert payload["active"] is True
                    assert payload["follower_count"] == 12
                    assert payload["author_id"] == 1
                    mock_toggle.assert_called_once_with(1, 2)
                    mock_notif.assert_called_once()


def test_view_user_profile(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["username"] = "browser_user"
        session["user_role"] = "user"

    mock_target = {"id": 1, "username": "chef_maria"}
    mock_data = {
        "profile": {"id": 1, "username": "chef_maria", "display_name": "Maria", "bio": "Passionate cook"},
        "recipe_count": 8,
        "saved_count": 3,
        "follower_count": 25,
        "following_count": 10,
        "like_count": 140,
        "is_following": False,
        "is_owner": False,
        "recipes": [],
        "favorites": [],
    }

    with patch("recipeshare.home.routes.UserRepository.find_by_identity", return_value=mock_target):
        with patch("recipeshare.home.routes.UserRepository.profile_data", return_value=mock_data):
            res = client.get("/users/chef_maria")
            assert res.status_code == 200
            assert b"Maria" in res.data
            assert b"Follow" in res.data


def test_real_metrics_start_at_zero_and_increment(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "admin"
        session["user_role"] = "admin"

    # Fetch initial stats
    res = client.get("/api/v1/ui/dashboard-stats?period=all")
    assert res.status_code == 200
    metrics = res.get_json()["metrics"]
    initial_views = metrics["total_views"]

    # View chicken-adobo recipe
    view_res = client.get("/recipes/chicken-adobo")
    assert view_res.status_code == 200

    # Fetch updated stats: views should increment in real time
    res2 = client.get("/api/v1/ui/dashboard-stats?period=all")
    assert res2.status_code == 200
    metrics2 = res2.get_json()["metrics"]
    assert metrics2["total_views"] >= initial_views + 1


def test_user_followers_and_following_pages(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "foodie_chef"
        session["user_role"] = "user"

    mock_followers = [
        {"id": 2, "username": "follower_one", "display_name": "Follower One", "bio": "Loves baking", "avatar_url": None, "recipe_count": 3, "follower_count": 10, "is_following": False}
    ]
    mock_following = [
        {"id": 3, "username": "chef_two", "display_name": "Chef Two", "bio": "Master cook", "avatar_url": None, "recipe_count": 15, "follower_count": 50, "is_following": True}
    ]

    with patch("recipeshare.home.routes.UserRepository.followers", return_value=mock_followers):
        res_followers = client.get("/followers")
        assert res_followers.status_code == 200
        assert b"follower_one" in res_followers.data
        assert b"Follower One" in res_followers.data

    with patch("recipeshare.home.routes.UserRepository.following", return_value=mock_following):
        res_following = client.get("/following")
        assert res_following.status_code == 200
        assert b"chef_two" in res_following.data
        assert b"Chef Two" in res_following.data


def test_user_likes_page(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "foodie_chef"
        session["user_role"] = "user"

    mock_liked = [
        {"id": 5, "slug": "adobo-special", "title": "Adobo Special", "image_url": None, "author_name": "Chef Juan", "like_count": 12, "view_count": 80}
    ]

    with patch("recipeshare.home.routes.UserRepository.liked_recipes", return_value=mock_liked):
        res_likes = client.get("/likes")
        assert res_likes.status_code == 200
        assert b"Adobo Special" in res_likes.data


def test_spa_followers_following_likes_fragments(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "foodie_chef"
        session["user_role"] = "user"

    with patch("recipeshare.ui.UserRepository.followers", return_value=[]):
        res = client.get("/api/v1/ui/pages/followers")
        assert res.status_code == 200
        assert "html" in res.get_json()

    with patch("recipeshare.ui.UserRepository.following", return_value=[]):
        res = client.get("/api/v1/ui/pages/following")
        assert res.status_code == 200
        assert "html" in res.get_json()

    with patch("recipeshare.ui.UserRepository.liked_recipes", return_value=[]):
        res = client.get("/api/v1/ui/pages/likes")
        assert res.status_code == 200
        assert "html" in res.get_json()


def test_home_displays_category_and_recipe_photos(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "foodie_chef"
        session["user_role"] = "user"

    res = client.get("/home")
    assert res.status_code == 200
    html = res.data.decode()
    assert "category-showcase-card__img" in html
    assert "Popular Recipe Categories" in html
    assert "Featured Recipes" in html
    assert "recipe-card" in html


def test_admin_can_access_home_page_and_sidebar_has_home_link(client):
    with client.session_transaction() as session:
        session["user_id"] = 7
        session["username"] = "recipe_admin"
        session["user_role"] = "admin"

    res = client.get("/home")
    assert res.status_code == 200
    html = res.data.decode()
    assert 'href="/home"' in html
    assert 'href="/admin/dashboard"' in html
    assert "Popular Recipe Categories" in html

    res_spa = client.get("/api/v1/ui/pages/home")
    assert res_spa.status_code == 200
    assert "html" in res_spa.get_json()


def test_recipe_create_form_and_detail_additional_info(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "foodie_chef"
        session["user_role"] = "user"

    # Verify fields are in the create form
    res = client.get("/recipes/create")
    assert res.status_code == 200
    html = res.data.decode()
    assert "Additional Information" in html
    assert 'name="cooking_tips"' in html
    assert 'name="serving_suggestion"' in html
    assert 'name="food_type"' in html
    assert 'name="taste"' in html
    assert 'name="best_served"' in html

    # Submit recipe with additional info
    form_data = {
        "title": "Test Palabok Additional Info",
        "description": "Savory noodle dish topped with golden shrimp sauce and crushed chicharon.",
        "status": "published",
        "ingredient_name": ["Bihon noodles", "Shrimp sauce"],
        "ingredient_quantity": ["200", "1"],
        "ingredient_unit": ["g", "cup"],
        "instructions": "Soak noodles\nPour shrimp sauce\nGarnish and serve",
        "cooking_tips": "Simmer gently to bring out the full flavor.",
        "serving_suggestion": "Serve warm with calamansi and hard boiled eggs.",
        "food_type": "Filipino Delicacy",
        "taste": "Rich, savory and citrusy",
        "best_served": "Merienda or Dinner",
    }
    try:
        post_res = client.post("/recipes/create", data=form_data, follow_redirects=True)
        assert post_res.status_code == 200
        post_html = post_res.data.decode()
        assert "Test Palabok Additional Info" in post_html
        assert "Simmer gently to bring out the full flavor." in post_html
        assert "Serve warm with calamansi and hard boiled eggs." in post_html
        assert "Filipino Delicacy" in post_html
        assert "Rich, savory and citrusy" in post_html
        assert "Merienda or Dinner" in post_html
    finally:
        with client.application.app_context():
            from recipeshare.shared.database import get_connection
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM recipes WHERE title = %s", ("Test Palabok Additional Info",))
            conn.commit()


def test_user_can_create_and_view_draft_recipes(client):
    with client.session_transaction() as session:
        session["user_id"] = 8
        session["username"] = "precious"
        session["user_role"] = "user"

    form_data = {
        "title": "Secret Draft Sisig",
        "description": "My top secret unfinished sisig formulation.",
        "status": "draft",
        "ingredient_name": ["Pork cheeks", "Calamansi"],
        "ingredient_quantity": ["500", "4"],
        "ingredient_unit": ["g", "pcs"],
        "instructions": "Boil pork cheeks\nChop finely\nSeason and test",
        "cooking_tips": "Do not rush the boiling step.",
    }
    post_res = client.post("/recipes/create", data=form_data, follow_redirects=True)
    assert post_res.status_code == 200
    post_html = post_res.data.decode()
    # User is redirected to /drafts and sees the draft recipe
    assert "Draft Recipes" in post_html
    assert "Secret Draft Sisig" in post_html
    assert "✎ Draft" in post_html
    assert "Edit &amp; Publish" in post_html or "Edit & Publish" in post_html

    # Check direct GET /drafts
    drafts_res = client.get("/drafts")
    assert drafts_res.status_code == 200
    assert "Secret Draft Sisig" in drafts_res.data.decode()

    # Author can view draft detail page and see draft alert banner
    detail_res = client.get("/recipes/secret-draft-sisig")
    assert detail_res.status_code == 200
    detail_html = detail_res.data.decode()
    assert "Draft Recipe" in detail_html
    assert "unpublished and only visible to you" in detail_html


def test_draft_hidden_from_other_users(client):
    # Other user logs in
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["username"] = "maria_santos"
        session["user_role"] = "user"

    # Other user cannot see the draft in catalog
    cat_res = client.get("/recipes")
    assert "Secret Draft Sisig" not in cat_res.data.decode()

    # Other user gets 404 trying to access draft detail
    detail_res = client.get("/recipes/secret-draft-sisig")
    assert detail_res.status_code == 404

    # Other user cannot see draft in user precious's public profile
    user_res = client.get("/users/precious")
    assert user_res.status_code == 200
    assert "Secret Draft Sisig" not in user_res.data.decode()


def test_spa_drafts_fragment(client):
    with client.session_transaction() as session:
        session["user_id"] = 8
        session["username"] = "precious"
        session["user_role"] = "user"

    res = client.get("/api/v1/ui/pages/drafts")
    assert res.status_code == 200
    data = res.get_json()
    assert "Draft Recipes" in data["title"]
    assert "Secret Draft Sisig" in data["html"]

    # Clean up test draft
    with client.application.app_context():
        from recipeshare.shared.database import get_connection
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM recipes WHERE title LIKE %s", ("%Secret Draft Sisig%",))
        conn.commit()


def test_user_likes_tab_badge_reflects_actual_liked_recipes_count(client):
    # Log in as user 18 (Mizu) who liked 3 recipes in DB
    with client.session_transaction() as session:
        session["user_id"] = 18
        session["username"] = "Mizu"
        session["user_role"] = "user"

    # 1. Test profile_statistics returns like_count = 3
    stats_res = client.get("/api/v1/ui/profile-statistics")
    assert stats_res.status_code == 200
    stats = stats_res.get_json()
    assert stats["like_count"] == 3

    # 2. Test SSR /likes renders badge with 3
    likes_res = client.get("/likes")
    assert likes_res.status_code == 200
    html = likes_res.data.decode()
    assert 'data-profile-badge="likes">3</small>' in html

    # 3. Test SPA fragment /api/v1/ui/pages/likes renders badge with 3
    spa_res = client.get("/api/v1/ui/pages/likes")
    assert spa_res.status_code == 200
    spa_html = spa_res.get_json()["html"]
    assert 'data-profile-badge="likes">3</small>' in spa_html







