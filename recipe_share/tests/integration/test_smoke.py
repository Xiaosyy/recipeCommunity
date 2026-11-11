import io
from unittest.mock import patch


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"RecipeShare" in response.data


def test_dashboard_page(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "test_user"
        session["user_role"] = "user"
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Recipe Inventory" in response.data


@patch("recipeshare.home.routes.HomeRepository.active_categories", return_value=[{"id": 1, "name": "Dinner"}])
def test_create_recipe_page(mock_categories, client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "test_user"
        session["user_role"] = "user"
    response = client.get("/recipes/create")
    assert response.status_code == 200
    assert b"Create Recipe" in response.data
    assert b"Add Recipe Photo" in response.data
    assert b"Upload Photo" in response.data
    assert b"Upload Video" in response.data


@patch("recipeshare.ui.HomeRepository.active_categories", return_value=[{"id": 1, "name": "Dinner"}])
def test_create_recipe_spa_fragment(mock_categories, client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "test_user"
        session["user_role"] = "user"
    response = client.get("/api/v1/ui/pages/recipes/create")
    assert response.status_code == 200
    assert "Create Recipe" in response.get_json()["html"]
    assert "Upload Video" in response.get_json()["html"]


@patch("recipeshare.home.routes.HomeRepository.recipe_by_id", return_value={"id": 99, "slug": "demo-video-dish"})
@patch("recipeshare.home.routes.HomeRepository.create_recipe", return_value=99)
def test_save_recipe_accepts_video_and_photo_uploads(mock_create_recipe, mock_recipe_by_id, client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "test_user"
        session["user_role"] = "user"

    # 1. Test Video Upload (MP4 magic header: \x00\x00\x00\x18ftypmp42...)
    mp4_bytes = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 64
    response_video = client.post(
        "/recipes/create",
        data={
            "title": "Demo Video Dish",
            "description": "Cooking walkthrough video",
            "status": "published",
            "ingredient_name": ["Flour"],
            "ingredient_quantity": ["2"],
            "ingredient_unit": ["cups"],
            "instructions": "Mix well\nBake until golden",
            "recipe_video": (io.BytesIO(mp4_bytes), "cooking_tutorial.mp4", "video/mp4"),
        },
        content_type="multipart/form-data",
    )
    assert response_video.status_code == 302
    assert response_video.headers["Location"].endswith("/recipes/demo-video-dish")
    assert mock_create_recipe.called
    saved_media = mock_create_recipe.call_args[0][11]
    assert saved_media is not None
    assert saved_media["mime_type"] == "video/mp4"
    assert saved_media["storage_path"].endswith(".mp4")

    # 2. Test Photo Upload (PNG magic header: \x89PNG\r\n\x1a\n...)
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 64
    response_photo = client.post(
        "/recipes/create",
        data={
            "title": "Demo Photo Dish",
            "description": "Dish with cover photo",
            "status": "published",
            "ingredient_name": ["Sugar"],
            "ingredient_quantity": ["1"],
            "ingredient_unit": ["cup"],
            "instructions": "Stir\nServe",
            "recipe_image": (io.BytesIO(png_bytes), "dish_cover.png", "image/png"),
        },
        content_type="multipart/form-data",
    )
    assert response_photo.status_code == 302
    saved_photo = mock_create_recipe.call_args[0][11]
    assert saved_photo is not None
    assert saved_photo["mime_type"] == "image/png"
    assert saved_photo["storage_path"].endswith(".png")

    # Clean up test uploaded files
    from pathlib import Path
    uploads_dir = Path(client.application.root_path) / "static" / "uploads" / "recipes"
    for media_item in (saved_media, saved_photo):
        file_name = media_item["storage_path"].rsplit("/", 1)[-1]
        (uploads_dir / file_name).unlink(missing_ok=True)


def test_not_found_page(client):
    response = client.get("/missing-page")
    assert response.status_code == 404
    assert b"404" in response.data


def test_ui_navigation(client):
    response = client.get("/api/v1/ui/navigation")
    assert response.status_code == 200
    assert response.is_json
    assert isinstance(response.get_json()["navigation"], list)


def test_dashboard_fragment(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["username"] = "test_user"
        session["user_role"] = "user"
    response = client.get("/api/v1/ui/pages/dashboard")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["title"] == "Recipe Inventory — RecipeShare"
    assert "Recipe Inventory" in payload["html"]
