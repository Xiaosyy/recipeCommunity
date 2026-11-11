import json
import mysql.connector

from recipeshare.location.repository import LocationRepository, get_flag
from .repository import HomeRepository

CATEGORY_ICONS = {
    "american": "🍔",
    "appetizers": "🥟",
    "asian": "🥢",
    "baking": "🥖",
    "beef": "🥩",
    "bread-bakery": "🥖",
    "breakfast": "🥞",
    "cakes-pastries": "🎂",
    "chicken": "🍗",
    "chinese": "🥟",
    "dairy-free": "🥛",
    "desserts": "🍰",
    "dinner": "🍽",
    "drinks-beverages": "🥤",
    "eggs": "🍳",
    "fast-food": "🍟",
    "filipino": "🍲",
    "filipino-breakfast": "🍳",
    "filipino-desserts": "🍨",
    "filipino-snacks-merienda": "🥟",
    "filipino-soups": "🍲",
    "filipino-street-food": "🍢",
    "fish": "🐟",
    "french": "🥐",
    "fried-foods": "🍤",
    "gluten-free": "🌾",
    "grilled-bbq": "🔥",
    "grilled-dishes": "🔥",
    "healthy-meals": "🥗",
    "indian": "🍛",
    "italian": "🍝",
    "japanese": "🍣",
    "kakanin": "🍡",
    "korean": "🍲",
    "lamb": "🥩",
    "low-carb-meals": "🥑",
    "lunch": "🍱",
    "main-course": "🍛",
    "mediterranean": "🫒",
    "mexican": "🌮",
    "native-delicacies": "🫔",
    "noodles-pasta": "🍜",
    "others": "🍽",
    "pork": "🥓",
    "quick-easy": "⚡",
    "rice-dishes": "🍚",
    "rice-meals": "🍚",
    "salads": "🥗",
    "sandwiches": "🥪",
    "sandwiches-burgers": "🍔",
    "sauces-dips": "🥣",
    "seafood": "🦐",
    "side-dishes": "🥦",
    "smoothies": "🧃",
    "smoothies-juices": "🧃",
    "snacks": "🍿",
    "snacks-appetizers": "🥟",
    "soups": "🍲",
    "stews": "🥘",
    "street-food": "🍢",
    "thai": "🍲",
    "traditional-filipino-food": "🇵🇭",
    "vegan": "🌱",
    "vegetables": "🥦",
    "vegetarian": "🥗",
}

CATEGORY_IMAGES = {
    "american": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=800&q=80",
    "appetizers": "https://images.unsplash.com/photo-1541529086526-db283c563270?auto=format&fit=crop&w=800&q=80",
    "asian": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80",
    "baking": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80",
    "beef": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "bread-bakery": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80",
    "breakfast": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?auto=format&fit=crop&w=800&q=80",
    "cakes-pastries": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
    "chicken": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&w=800&q=80",
    "chinese": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?auto=format&fit=crop&w=800&q=80",
    "dairy-free": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=800&q=80",
    "desserts": "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80",
    "dinner": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "drinks-beverages": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80",
    "eggs": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
    "fast-food": "https://images.unsplash.com/photo-1561758033-d89a9ad46330?auto=format&fit=crop&w=800&q=80",
    "filipino": "https://images.unsplash.com/photo-1541544741938-0af808871cc0?auto=format&fit=crop&w=800&q=80",
    "filipino-breakfast": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=800&q=80",
    "filipino-desserts": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=800&q=80",
    "filipino-snacks-merienda": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80",
    "filipino-soups": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
    "filipino-street-food": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80",
    "fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",
    "french": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=800&q=80",
    "fried-foods": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=800&q=80",
    "gluten-free": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
    "grilled-bbq": "https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?auto=format&fit=crop&w=800&q=80",
    "grilled-dishes": "https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?auto=format&fit=crop&w=800&q=80",
    "healthy-meals": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
    "indian": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=800&q=80",
    "italian": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80",
    "japanese": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=800&q=80",
    "kakanin": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80",
    "korean": "https://images.unsplash.com/photo-1553163147-622ab57be1c7?auto=format&fit=crop&w=800&q=80",
    "lamb": "https://images.unsplash.com/photo-1603360946369-dc9bb6258143?auto=format&fit=crop&w=800&q=80",
    "low-carb-meals": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=800&q=80",
    "lunch": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
    "main-course": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80",
    "mediterranean": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=800&q=80",
    "mexican": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=800&q=80",
    "native-delicacies": "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&w=800&q=80",
    "noodles-pasta": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=800&q=80",
    "others": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80",
    "pork": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "quick-easy": "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80",
    "rice-dishes": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?auto=format&fit=crop&w=800&q=80",
    "rice-meals": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?auto=format&fit=crop&w=800&q=80",
    "salads": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
    "sandwiches": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
    "sandwiches-burgers": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
    "sauces-dips": "https://images.unsplash.com/photo-1472476443507-c7a5948772fc?auto=format&fit=crop&w=800&q=80",
    "seafood": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=800&q=80",
    "side-dishes": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
    "smoothies": "https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=800&q=80",
    "smoothies-juices": "https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=800&q=80",
    "snacks": "https://images.unsplash.com/photo-1621996346565-e3d5d6281781?auto=format&fit=crop&w=800&q=80",
    "snacks-appetizers": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80",
    "soups": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
    "street-food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80",
    "thai": "https://images.unsplash.com/photo-1559314809-0d155014e29e?auto=format&fit=crop&w=800&q=80",
    "traditional-filipino-food": "https://images.unsplash.com/photo-1541544741938-0af808871cc0?auto=format&fit=crop&w=800&q=80",
    "vegan": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
    "vegetables": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
    "vegetarian": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
}

CATEGORY_SHOWCASE = [
    {
        "name": "Chicken",
        "slug": "chicken",
        "description": "Roasted, grilled, and homestyle poultry dishes",
        "image_url": CATEGORY_IMAGES["chicken"],
    },
    {
        "name": "Vegetarian",
        "slug": "vegetarian",
        "description": "Vibrant plant-forward meals and garden-fresh medleys",
        "image_url": CATEGORY_IMAGES["vegetarian"],
    },
    {
        "name": "Vegetables",
        "slug": "vegetables",
        "description": "Fresh garden vegetables, stir-fries, and healthy greens",
        "image_url": CATEGORY_IMAGES["vegetables"],
    },
    {
        "name": "Snacks",
        "slug": "snacks",
        "description": "Quick finger foods, savory bites, and afternoon snacks",
        "image_url": CATEGORY_IMAGES["snacks"],
    },
    {
        "name": "Baking",
        "slug": "baking",
        "description": "Oven-baked breads, cookies, pies, and artisan pastries",
        "image_url": CATEGORY_IMAGES["baking"],
    },
    {
        "name": "Quick & Easy",
        "slug": "quick-easy",
        "description": "Simple, delicious meals ready in 30 minutes or less",
        "image_url": CATEGORY_IMAGES["quick-easy"],
    },
    {
        "name": "Traditional Filipino Food",
        "slug": "traditional-filipino-food",
        "description": "Authentic Filipino heirloom recipes, adobo, and regional comfort classics",
        "image_url": CATEGORY_IMAGES["traditional-filipino-food"],
    },
    {
        "name": "Rice Meals",
        "slug": "rice-meals",
        "description": "Fried rice, silog plates, biryani, paella, and flavorful rice bowls",
        "image_url": CATEGORY_IMAGES["rice-meals"],
    },
    {
        "name": "Grilled & BBQ",
        "slug": "grilled-bbq",
        "description": "Charcoal-grilled meats, skewers, barbecue, and smoky favorites",
        "image_url": CATEGORY_IMAGES["grilled-bbq"],
    },
    {
        "name": "Seafood",
        "slug": "seafood",
        "description": "Fresh ocean catches, garlic shrimp, and coastal favorites",
        "image_url": CATEGORY_IMAGES["seafood"],
    },
    {
        "name": "Desserts",
        "slug": "desserts",
        "description": "Cakes, cupcakes, pastries, and sweet treats",
        "image_url": CATEGORY_IMAGES["desserts"],
    },
    {
        "name": "Others",
        "slug": "others",
        "description": "Unique fusion dishes, specialty recipes, and homemade creations",
        "image_url": CATEGORY_IMAGES["others"],
    },
]


NEW_CATEGORY_SLUGS = [
    "chicken",
    "vegetarian",
    "vegetables",
    "snacks",
    "baking",
    "quick-easy",
    "others",
]

RECOMMENDED_CATEGORY_SLUGS = [
    "pork",
    "lamb",
    "fish",
    "rice-meals",
    "grilled-bbq",
    "fried-foods",
    "appetizers",
    "salads",
    "sandwiches",
    "street-food",
    "vegan",
    "low-carb-meals",
    "dairy-free",
    "gluten-free",
    "drinks-beverages",
    "smoothies",
    "cakes-pastries",
    "sauces-dips",
    "traditional-filipino-food",
]


class HomeService:
    def __init__(self, repository: HomeRepository | None = None, location_repository: LocationRepository | None = None) -> None:
        self.repository = repository or HomeRepository()
        self.location_repository = location_repository or LocationRepository()

    def search(self, query: str) -> dict[str, list[dict]]:
        query = query.strip()
        if not query:
            return {"recipes": []}
        try:
            return self.repository.search(query)
        except mysql.connector.Error:
            return {"recipes": []}

    def recipe_detail(self, slug: str, user_id: int | None = None) -> dict | None:
        recipe = self.repository.recipe_by_slug(slug, user_id)
        if recipe is None:
            return None
        try:
            instructions = json.loads(recipe.get("instructions") or "[]")
        except (TypeError, json.JSONDecodeError):
            instructions = []
        recipe["steps"] = instructions if isinstance(instructions, list) else []
        return recipe

    def recipe_catalog(
        self,
        recipe_filter: str = "all",
        category_slug: str | None = None,
        location_name: str | None = None,
        search_query: str | None = None,
    ) -> dict[str, list[dict]]:
        try:
            recipes = self.repository.published_recipes(
                recipe_filter=recipe_filter,
                category_slug=category_slug,
                location_name=location_name,
                search_query=search_query,
            )
            if not recipes and location_name and not search_query:
                from recipeshare.location.service import LocationRecipeService
                raw_loc = self.location_repository.location_by_name(location_name)
                if raw_loc:
                    LocationRecipeService(self.location_repository).ensure_location_has_recipes(raw_loc)
                    recipes = self.repository.published_recipes(
                        recipe_filter=recipe_filter,
                        category_slug=category_slug,
                        location_name=location_name,
                        search_query=search_query,
                    )
            for recipe in recipes:
                slug = recipe.get("slug")
                avg_rating = float(recipe.get("average_rating") or 0)
                rev_count = int(recipe.get("review_count") or 0)

                recipe["average_rating_display"] = f"{avg_rating:.1f}" if avg_rating > 0 else "0.0"
                if rev_count >= 1000:
                    recipe["review_count_formatted"] = f"{rev_count / 1000:.1f}k reviews"
                elif rev_count > 0:
                    recipe["review_count_formatted"] = f"{rev_count} reviews" if rev_count != 1 else "1 review"
                else:
                    recipe["review_count_formatted"] = "0 reviews"

                cook_time = recipe.get("cook_minutes") or recipe.get("prep_minutes") or 30
                recipe["display_time"] = f"{cook_time} mins"

                cat_slug = (recipe.get("category_slug") or "").strip().lower()
                loc_name = (recipe.get("location_name") or "").strip()

                if location_name and loc_name:
                    recipe["badge_text"] = loc_name
                    recipe["badge_icon"] = ""
                elif loc_name:
                    recipe["badge_text"] = loc_name
                    recipe["badge_icon"] = ""
                elif recipe.get("category_name"):
                    recipe["badge_text"] = recipe.get("category_name")
                    recipe["badge_icon"] = CATEGORY_ICONS.get(cat_slug, "🍽")
                else:
                    recipe["badge_text"] = "Recipe"
                    recipe["badge_icon"] = "🍽"
        except mysql.connector.Error:
            recipes = []
        try:
            db_cats = self.repository.active_categories(limit=100)
            categories = self._enrich_categories(db_cats, only_db=True, sort_by_name=True)
            by_slug = {c["slug"]: c for c in categories}
            new_categories = [by_slug[s] for s in NEW_CATEGORY_SLUGS if s in by_slug]
            recommended_categories = [by_slug[s] for s in RECOMMENDED_CATEGORY_SLUGS if s in by_slug]
            seen_ids = {c["id"] for c in new_categories} | {c["id"] for c in recommended_categories}
            other_categories = [c for c in categories if c["id"] not in seen_ids]
        except mysql.connector.Error:
            categories = self._enrich_categories([], include_all=False)
            new_categories = []
            recommended_categories = []
            other_categories = []
        try:
            locations = self.location_repository.locations()
        except Exception:
            locations = []
        return {
            "recipes": recipes,
            "categories": categories,
            "new_categories": new_categories,
            "recommended_categories": recommended_categories,
            "other_categories": other_categories,
            "locations": locations,
        }

    def _enrich_categories(self, db_categories: list[dict], include_all: bool = False, only_db: bool = False, sort_by_name: bool = False) -> list[dict]:
        if only_db:
            enriched: list[dict] = []
            for cat in db_categories:
                slug = (cat.get("slug") or "").strip().lower()
                image_url = cat.get("image_url") or CATEGORY_IMAGES.get(slug) or "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80"
                enriched.append({
                    "id": cat.get("id"),
                    "name": cat.get("name"),
                    "slug": slug,
                    "description": cat.get("description") or "",
                    "image_url": image_url,
                    "recipe_count": cat.get("recipe_count", 0),
                    "average_rating": float(cat.get("average_rating") or 0),
                    "review_count": int(cat.get("review_count") or 0),
                })
            if sort_by_name:
                enriched.sort(key=lambda item: (item.get("name") or "").lower())
            return enriched

        by_slug = {(c.get("slug") or "").strip().lower(): dict(c) for c in db_categories}
        enriched: list[dict] = []
        seen_slugs: set[str] = set()
        for idx, showcase in enumerate(CATEGORY_SHOWCASE, start=1):
            slug = showcase["slug"]
            seen_slugs.add(slug)
            cat = by_slug.get(slug, {})
            image_url = cat.get("image_url") or showcase.get("image_url") or CATEGORY_IMAGES.get(slug)
            enriched.append({
                "id": cat.get("id") or idx,
                "name": cat.get("name") or showcase["name"],
                "slug": slug,
                "description": cat.get("description") or showcase["description"],
                "image_url": image_url,
            })
        if include_all:
            for cat in db_categories:
                slug = (cat.get("slug") or "").strip().lower()
                if not slug or slug in seen_slugs:
                    continue
                seen_slugs.add(slug)
                image_url = cat.get("image_url") or CATEGORY_IMAGES.get(slug) or "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80"
                enriched.append({
                    "id": cat.get("id"),
                    "name": cat.get("name"),
                    "slug": slug,
                    "description": cat.get("description") or "",
                    "image_url": image_url,
                })
            enriched.sort(key=lambda item: (item.get("name") or "").lower())
        return enriched

    def discovery(self, include_all: bool = False) -> dict[str, list[dict]]:
        new_categories: list[dict] = []
        recommended_categories: list[dict] = []
        try:
            if include_all:
                all_active = self.repository.active_categories(limit=100)
                all_enriched = self._enrich_categories(all_active, only_db=True, sort_by_name=False)
                by_slug = {c["slug"]: c for c in all_enriched}
                new_categories = [by_slug[s] for s in NEW_CATEGORY_SLUGS if s in by_slug]
                recommended_categories = [by_slug[s] for s in RECOMMENDED_CATEGORY_SLUGS if s in by_slug]
                categories = sorted(all_enriched, key=lambda c: (c.get("name") or "").lower())
            else:
                db_cats = self.repository.categories_with_recipes(limit=100)
                if not db_cats:
                    db_cats = self.repository.active_categories(limit=100)
                categories = self._enrich_categories(db_cats, only_db=True, sort_by_name=False)
                if len(categories) > 6:
                    categories = categories[:6]
        except mysql.connector.Error:
            categories = self._enrich_categories([], include_all=include_all, sort_by_name=include_all)
        try:
            featured_recipes = self.repository.featured_recipes()
        except mysql.connector.Error:
            featured_recipes = []
        try:
            locations = self.location_repository.locations()
        except Exception:
            locations = []
        return {
            "categories": categories,
            "new_categories": new_categories,
            "recommended_categories": recommended_categories,
            "featured_recipes": featured_recipes,
            "locations": locations,
        }
