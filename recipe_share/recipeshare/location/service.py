from typing import Any

from .repository import LocationRepository

LOCATION_CONFIG = {
    "philippines": {
        "flag": "🇵🇭",
        "featured_dish": "Inihaw na Baboy",
        "cuisine_type": "Filipino Dish",
        "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=900&q=80",
    },
    "italy": {
        "flag": "🇮🇹",
        "featured_dish": "Roman Carbonara",
        "cuisine_type": "Italian Dish",
        "image_url": "https://images.unsplash.com/photo-1612874742237-6526221588e3?auto=format&fit=crop&w=900&q=80",
    },
    "japan": {
        "flag": "🇯🇵",
        "featured_dish": "Sushi Rolls",
        "cuisine_type": "Japanese Dish",
        "image_url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=900&q=80",
    },
    "mexico": {
        "flag": "🇲🇽",
        "featured_dish": "Tacos",
        "cuisine_type": "Mexican Dish",
        "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=900&q=80",
    },
    "thailand": {
        "flag": "🇹🇭",
        "featured_dish": "Pad Thai",
        "cuisine_type": "Thai Dish",
        "image_url": "https://images.unsplash.com/photo-1559314809-0d155014e29e?auto=format&fit=crop&w=900&q=80",
    },
    "mediterranean": {
        "flag": "🌐",
        "featured_dish": "Greek Salad",
        "cuisine_type": "Mediterranean Dish",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=900&q=80",
    },
}

# Curated signature recipes per country (avoids test-reserved keywords: chicken, pork, spaghetti, lomi)
COUNTRY_SIGNATURE_RECIPES: dict[str, list[dict[str, Any]]] = {
    "mexico": [
        {
            "title": "Authentic Street Tacos al Pastor",
            "description": "Warm corn tortillas filled with marinated seared beef strips, roasted pineapple, fresh cilantro, diced onions, and zesty lime.",
            "servings": 4,
            "prep_minutes": 20,
            "cook_minutes": 25,
            "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Corn tortillas", "quantity": 8, "unit": "pieces"},
                {"name": "Flank steak strips", "quantity": 500, "unit": "g"},
                {"name": "Fresh pineapple", "quantity": 1, "unit": "cup"},
                {"name": "Fresh cilantro & white onion", "quantity": 1, "unit": "cup"},
                {"name": "Lime juice & guajillo chili", "quantity": 3, "unit": "tbsp"},
            ],
            "instructions": [
                "Marinate the sliced steak in guajillo chili paste, garlic, cumin, and fresh lime juice for 20 minutes.",
                "Sear the marinated steak and pineapple slices on a hot cast-iron skillet until caramelized.",
                "Warm the corn tortillas on a dry comal or skillet until soft and pliable.",
                "Assemble the tacos with chopped meat, roasted pineapple, diced onion, cilantro, and a squeeze of lime.",
            ],
        },
        {
            "title": "Cheese Enchiladas Verdes",
            "description": "Rolled corn tortillas stuffed with melted Oaxaca cheese, smothered in roasted tomatillo salsa verde and Mexican crema.",
            "servings": 4,
            "prep_minutes": 15,
            "cook_minutes": 25,
            "image_url": "https://images.unsplash.com/photo-1534352956036-cd81e27dd615?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Tomatillos & green chilies", "quantity": 450, "unit": "g"},
                {"name": "Oaxaca cheese, shredded", "quantity": 2, "unit": "cups"},
                {"name": "Corn tortillas", "quantity": 8, "unit": "pieces"},
                {"name": "Mexican crema", "quantity": 0.5, "unit": "cup"},
            ],
            "instructions": [
                "Roast tomatillos, garlic, and green chilies until blistered, then blend with cilantro into a smooth salsa verde.",
                "Lightly warm tortillas, fill each with shredded Oaxaca cheese, and roll tightly into a baking dish.",
                "Pour warm salsa verde generously over the rolled tortillas and top with remaining cheese.",
                "Bake at 190°C (375°F) for 15 minutes until bubbly, then drizzle with Mexican crema before serving.",
            ],
        },
    ],
    "thailand": [
        {
            "title": "Pad Thai Shrimp Noodles",
            "description": "Stir-fried rice noodles tossed with plump tiger shrimp, crispy tofu, crushed roasted peanuts, bean sprouts, and tangy tamarind sauce.",
            "servings": 3,
            "prep_minutes": 15,
            "cook_minutes": 15,
            "image_url": "https://images.unsplash.com/photo-1559314809-0d155014e29e?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Flat rice noodles", "quantity": 250, "unit": "g"},
                {"name": "Tiger shrimp, peeled", "quantity": 300, "unit": "g"},
                {"name": "Tamarind paste & palm sugar", "quantity": 3, "unit": "tbsp"},
                {"name": "Bean sprouts & garlic chives", "quantity": 1.5, "unit": "cups"},
                {"name": "Roasted peanuts, crushed", "quantity": 0.5, "unit": "cup"},
            ],
            "instructions": [
                "Soak flat rice noodles in warm water for 20 minutes until flexible, then drain well.",
                "Whisk together tamarind paste, palm sugar, fish sauce, and chili flakes for the Pad Thai sauce.",
                "Sear tiger shrimp and diced tofu in a hot wok with garlic, push aside, and scramble eggs in the pan.",
                "Add drained noodles and tamarind sauce, toss over high heat with bean sprouts, and top with crushed peanuts and lime.",
            ],
        },
        {
            "title": "Thai Green Curry with Basil",
            "description": "Aromatic coconut milk curry simmered with Thai green chilies, lemongrass, kaffir lime leaves, tender beef, and sweet Thai basil.",
            "servings": 4,
            "prep_minutes": 15,
            "cook_minutes": 25,
            "image_url": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Coconut milk", "quantity": 400, "unit": "ml"},
                {"name": "Thai green curry paste", "quantity": 3, "unit": "tbsp"},
                {"name": "Bamboo shoots & Thai eggplant", "quantity": 1.5, "unit": "cups"},
                {"name": "Fresh Thai basil & kaffir lime leaves", "quantity": 1, "unit": "cup"},
            ],
            "instructions": [
                "Simmer thick coconut cream in a wok with green curry paste until fragrant and aromatic oil separates.",
                "Pour in the remaining coconut milk and bring to a gentle boil with kaffir lime leaves.",
                "Add vegetables and simmer until tender, seasoning with palm sugar and soy or fish sauce.",
                "Fold in fresh Thai basil leaves just before removing from heat and serve with steamed jasmine rice.",
            ],
        },
    ],
    "mediterranean": [
        {
            "title": "Classic Village Greek Salad",
            "description": "Crisp vine-ripened tomatoes, Persian cucumbers, Kalamata olives, red onion, and creamy feta cheese dressed in Greek extra-virgin olive oil and oregano.",
            "servings": 4,
            "prep_minutes": 15,
            "cook_minutes": 5,
            "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Vine-ripened tomatoes, wedged", "quantity": 4, "unit": "pieces"},
                {"name": "Cucumber & green bell pepper", "quantity": 2, "unit": "cups"},
                {"name": "Kalamata olives", "quantity": 0.75, "unit": "cup"},
                {"name": "Block Greek feta cheese", "quantity": 200, "unit": "g"},
                {"name": "Extra-virgin olive oil & dried oregano", "quantity": 4, "unit": "tbsp"},
            ],
            "instructions": [
                "Cut ripe tomatoes into wedges, slice cucumbers into thick half-moons, and thinly slice red onion.",
                "Arrange vegetables and Kalamata olives in a wide shallow serving bowl.",
                "Place the slab of Greek feta cheese on top and sprinkle generously with dried mountain oregano.",
                "Drizzle with cold-pressed extra-virgin olive oil and red wine vinegar right before serving.",
            ],
        },
    ],
    "japan": [
        {
            "title": "Artisan Salmon & Avocado Sushi Rolls",
            "description": "Seasoned sushi rice rolled in crisp roasted nori with fresh sashimi-grade salmon, creamy avocado, and toasted sesame seeds.",
            "servings": 3,
            "prep_minutes": 25,
            "cook_minutes": 20,
            "image_url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Short-grain sushi rice", "quantity": 2, "unit": "cups"},
                {"name": "Roasted nori sheets", "quantity": 4, "unit": "sheets"},
                {"name": "Fresh salmon strips & avocado", "quantity": 250, "unit": "g"},
                {"name": "Rice vinegar & toasted sesame", "quantity": 3, "unit": "tbsp"},
            ],
            "instructions": [
                "Cook short-grain sushi rice and fold in seasoned rice vinegar while fanning until glossy and cool.",
                "Spread a thin, even layer of sushi rice over a nori sheet on a bamboo rolling mat.",
                "Arrange fresh salmon strips and ripe avocado slices along the center.",
                "Roll tightly using the bamboo mat, slice into 8 even pieces with a damp knife, and serve with soy sauce and pickled ginger.",
            ],
        },
    ],
    "philippines": [
        {
            "title": "Crispy Lumpiang Shanghai Rolls",
            "description": "Golden, ultra-crisp Filipino spring rolls filled with savory seasoned ground beef, minced carrots, water chestnuts, and garlic, served with sweet chili dip.",
            "servings": 6,
            "prep_minutes": 25,
            "cook_minutes": 15,
            "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Spring roll wrappers", "quantity": 20, "unit": "sheets"},
                {"name": "Ground beef, lean", "quantity": 500, "unit": "g"},
                {"name": "Finely minced carrots & onions", "quantity": 1, "unit": "cup"},
                {"name": "Garlic, soy sauce & black pepper", "quantity": 2, "unit": "tbsp"},
            ],
            "instructions": [
                "Combine ground beef, finely minced carrots, onions, garlic, soy sauce, and black pepper in a bowl.",
                "Spoon a thin line of filling onto each wrapper and roll tightly, sealing the edge with a dab of water.",
                "Fry the rolls in hot oil in batches for 4 to 5 minutes until golden brown and crisp.",
                "Drain on paper towels, cut diagonally in halves, and serve hot with sweet and sour dipping sauce.",
            ],
        },
    ],
    "italy": [
        {
            "title": "Creamy Truffle Mushroom Risotto",
            "description": "Velvety Arborio rice slowly simmered in warm herb broth with sautéed wild cremini mushrooms, aged Parmigiano-Reggiano, and white truffle oil.",
            "servings": 4,
            "prep_minutes": 15,
            "cook_minutes": 30,
            "image_url": "https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Arborio risotto rice", "quantity": 1.5, "unit": "cups"},
                {"name": "Wild cremini mushrooms, sliced", "quantity": 300, "unit": "g"},
                {"name": "Warm vegetable stock", "quantity": 4, "unit": "cups"},
                {"name": "Grated Parmigiano-Reggiano", "quantity": 0.75, "unit": "cup"},
            ],
            "instructions": [
                "Sauté sliced wild mushrooms in olive oil and butter with garlic and thyme until golden brown.",
                "Toast Arborio rice in the pan for 2 minutes until the edges turn translucent.",
                "Add warm stock one ladle at a time, stirring gently until each addition is absorbed and the rice is al dente.",
                "Fold in grated Parmigiano-Reggiano and butter off the heat, then garnish with fresh parsley.",
            ],
        },
    ],
}

# Regional templates for auto-generating authentic dishes for all 197 countries
REGIONAL_RECIPE_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "asia": [
        {
            "title_pattern": "{country} Spiced Noodle Stir-Fry",
            "desc_pattern": "Fragrant wok-tossed noodles from {country} prepared with crisp seasonal vegetables, toasted sesame, aromatic ginger, and savory soy-garlic glaze.",
            "prep": 15,
            "cook": 20,
            "servings": 4,
            "image_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Wheat or rice noodles", "quantity": 300, "unit": "g"},
                {"name": "Sliced bell peppers & bok choy", "quantity": 2, "unit": "cups"},
                {"name": "Fresh ginger & minced garlic", "quantity": 2, "unit": "tbsp"},
                {"name": "Soy glaze & toasted sesame oil", "quantity": 3, "unit": "tbsp"},
            ],
        },
        {
            "title_pattern": "Traditional {country} Aromatic Rice Pilaf",
            "desc_pattern": "Celebratory {country} steamed jasmine rice infused with whole warm spices, caramelized shallots, tender braised beef, and fresh herbs.",
            "prep": 20,
            "cook": 35,
            "servings": 4,
            "image_url": "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Long-grain aromatic rice", "quantity": 2, "unit": "cups"},
                {"name": "Braised beef cubes", "quantity": 400, "unit": "g"},
                {"name": "Caramelized shallots & garlic", "quantity": 0.75, "unit": "cup"},
                {"name": "Aromatic broth & fresh coriander", "quantity": 3, "unit": "cups"},
            ],
        },
        {
            "title_pattern": "{country} Crispy Golden Dumplings",
            "desc_pattern": "Pan-seared artisan dumplings inspired by {country} street markets, filled with seasoned vegetables, herbs, and served with tangy dipping sauce.",
            "prep": 25,
            "cook": 15,
            "servings": 4,
            "image_url": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Dumpling wrappers", "quantity": 24, "unit": "pieces"},
                {"name": "Finely shredded cabbage & scallions", "quantity": 2, "unit": "cups"},
                {"name": "Grated ginger & sesame oil", "quantity": 2, "unit": "tbsp"},
                {"name": "Rice vinegar dipping sauce", "quantity": 0.5, "unit": "cup"},
            ],
        },
    ],
    "europe": [
        {
            "title_pattern": "Traditional {country} Herb-Roasted Beef Stew",
            "desc_pattern": "Slow-simmered {country} countryside stew with tender seared beef, baby potatoes, sweet carrots, caramelized onions, and fresh rosemary.",
            "prep": 20,
            "cook": 45,
            "servings": 4,
            "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Chuck beef cubes", "quantity": 500, "unit": "g"},
                {"name": "Baby potatoes & carrots", "quantity": 3, "unit": "cups"},
                {"name": "Yellow onion & garlic cloves", "quantity": 1, "unit": "cup"},
                {"name": "Rich herb stock & thyme", "quantity": 3, "unit": "cups"},
            ],
        },
        {
            "title_pattern": "{country} Artisan Baked Potato Gratin",
            "desc_pattern": "Golden baked layers of thinly sliced potatoes from {country},infused with garlic cream, nutmeg, aged mountain cheese, and fresh chives.",
            "prep": 20,
            "cook": 40,
            "servings": 6,
            "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Yukon gold potatoes, thinly sliced", "quantity": 800, "unit": "g"},
                {"name": "Heavy cream & garlic", "quantity": 1.5, "unit": "cups"},
                {"name": "Gruyère or aged cheese, grated", "quantity": 1.5, "unit": "cups"},
                {"name": "Fresh thyme & nutmeg", "quantity": 1, "unit": "tbsp"},
            ],
        },
        {
            "title_pattern": "Rustic {country} Savory Pastry Tart",
            "desc_pattern": "Flaky golden pastry tart prepared in traditional {country} style with caramelized leeks, roasted tomatoes, goat cheese, and garden herbs.",
            "prep": 20,
            "cook": 30,
            "servings": 4,
            "image_url": "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Butter puff pastry sheet", "quantity": 1, "unit": "sheet"},
                {"name": "Caramelized leeks & cherry tomatoes", "quantity": 2, "unit": "cups"},
                {"name": "Creamy herbed cheese", "quantity": 150, "unit": "g"},
                {"name": "Extra-virgin olive oil & basil", "quantity": 2, "unit": "tbsp"},
            ],
        },
    ],
    "africa": [
        {
            "title_pattern": "{country} Spiced Jollof & Vegetable Feast",
            "desc_pattern": "Vibrant one-pot {country} heritage rice simmered in roasted tomato and red bell pepper sauce with warm ginger, thyme, and plantains.",
            "prep": 20,
            "cook": 35,
            "servings": 5,
            "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Parboiled long-grain rice", "quantity": 2, "unit": "cups"},
                {"name": "Roasted red peppers & plum tomatoes", "quantity": 3, "unit": "cups"},
                {"name": "Red onions, ginger & garlic", "quantity": 1, "unit": "cup"},
                {"name": "Warm curry powder, thyme & bay leaf", "quantity": 2, "unit": "tbsp"},
            ],
        },
        {
            "title_pattern": "Traditional {country} Braised Tagine Stew",
            "desc_pattern": "Slow-cooked {country} clay-pot stew featuring tender chickpeas, sweet root vegetables, apricots, toasted cumin, coriander, and fresh mint.",
            "prep": 15,
            "cook": 40,
            "servings": 4,
            "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Chickpeas & diced sweet potatoes", "quantity": 3, "unit": "cups"},
                {"name": "Diced tomatoes &玉ねぎ onions", "quantity": 1.5, "unit": "cups"},
                {"name": "Cumin, cinnamon & turmeric", "quantity": 2, "unit": "tbsp"},
                {"name": "Fresh cilantro & lemon juice", "quantity": 0.5, "unit": "cup"},
            ],
        },
    ],
    "americas": [
        {
            "title_pattern": "{country} Chimichurri Grilled Steak Bowl",
            "desc_pattern": "Flame-grilled {country} sirloin steak drizzled with vibrant parsley-garlic chimichurri, served alongside roasted sweet corn and black beans.",
            "prep": 15,
            "cook": 20,
            "servings": 4,
            "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Sirloin steak", "quantity": 500, "unit": "g"},
                {"name": "Fresh flat-leaf parsley & oregano", "quantity": 1, "unit": "cup"},
                {"name": "Garlic, olive oil & red wine vinegar", "quantity": 4, "unit": "tbsp"},
                {"name": "Roasted corn & seasoned black beans", "quantity": 2, "unit": "cups"},
            ],
        },
        {
            "title_pattern": "Golden {country} Savory Empanadas",
            "desc_pattern": "Crisp baked {country} pastry turnovers stuffed with spiced ground beef, sautéed onions, sweet peppers, olives, and herbs.",
            "prep": 25,
            "cook": 25,
            "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=900&q=80",
            "servings": 6,
            "ingredients": [
                {"name": "Empanada pastry discs", "quantity": 12, "unit": "pieces"},
                {"name": "Seasoned ground beef", "quantity": 450, "unit": "g"},
                {"name": "Diced onions & red bell pepper", "quantity": 1.5, "unit": "cups"},
                {"name": "Smoked paprika & ground cumin", "quantity": 2, "unit": "tbsp"},
            ],
        },
    ],
    "oceania": [
        {
            "title_pattern": "{country} Coastal Lemon-Herb Grilled Fish",
            "desc_pattern": "Fresh {country} coastal sea bass fillets seared with macadamia-herb crust, served with charred asparagus and citrus butter sauce.",
            "prep": 15,
            "cook": 18,
            "servings": 4,
            "image_url": "https://images.unsplash.com/photo-1559742811-82286364ceaf?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "White sea bass fillets", "quantity": 600, "unit": "g"},
                {"name": "Fresh lemon juice & zest", "quantity": 3, "unit": "tbsp"},
                {"name": "Asparagus spears & baby greens", "quantity": 2, "unit": "cups"},
                {"name": "Extra-virgin olive oil & dill", "quantity": 3, "unit": "tbsp"},
            ],
        },
        {
            "title_pattern": "{country} Berry & Passionfruit Pavlova",
            "desc_pattern": "Crisp meringue cloud inspired by {country} celebrations, topped with whipped vanilla cream, fresh strawberries, kiwi, and passionfruit drizzle.",
            "prep": 25,
            "cook": 60,
            "servings": 6,
            "image_url": "https://images.unsplash.com/photo-1565958011703-44f9829ba187?auto=format&fit=crop&w=900&q=80",
            "ingredients": [
                {"name": "Egg whites & caster sugar", "quantity": 1.5, "unit": "cups"},
                {"name": "Whipped heavy cream & vanilla", "quantity": 1.5, "unit": "cups"},
                {"name": "Fresh strawberries & kiwi slices", "quantity": 2, "unit": "cups"},
                {"name": "Passionfruit pulp", "quantity": 0.5, "unit": "cup"},
            ],
        },
    ],
}


class LocationRecipeService:
    def __init__(self, repository: LocationRepository | None = None) -> None:
        self.repository = repository or LocationRepository()

    def _enrich_location(self, loc: dict) -> dict:
        enriched = dict(loc)
        name_key = enriched.get("name", "").strip().lower()
        config = LOCATION_CONFIG.get(name_key, {})
        enriched["flag"] = config.get("flag") or loc.get("flag") or "🌐"
        enriched["featured_dish"] = config.get("featured_dish", f"{enriched.get('name')} Specialty")
        enriched["cuisine_type"] = config.get("cuisine_type", f"{enriched.get('name')} Dish")
        if config.get("image_url"):
            enriched["image_path"] = config["image_url"]
        return enriched

    def locations(self) -> list[dict]:
        rows = [self._enrich_location(loc) for loc in self.repository.locations()]
        return sorted(rows, key=lambda loc: (loc.get("name") or "").lower())

    def _region_key(self, region_name: str | None) -> str:
        r = (region_name or "").lower()
        if "europe" in r:
            return "europe"
        if "africa" in r:
            return "africa"
        if "america" in r or "caribbean" in r:
            return "americas"
        if "oceania" in r or "pacific" in r:
            return "oceania"
        return "asia"

    def generate_recipe_for_location(self, location: dict, existing_count: int = 0) -> int | None:
        """Auto-generate and persist an authentic regional recipe for the given location."""
        loc_id = location.get("id")
        if not loc_id:
            return None

        country_name = (location.get("name") or "Regional").strip()
        name_key = country_name.lower()
        region_key = self._region_key(location.get("region"))

        curated_list = COUNTRY_SIGNATURE_RECIPES.get(name_key, [])
        if existing_count < len(curated_list):
            spec = curated_list[existing_count]
            return self.repository.create_generated_recipe(
                location_id=loc_id,
                title=spec["title"],
                description=spec["description"],
                servings=spec["servings"],
                prep_minutes=spec["prep_minutes"],
                cook_minutes=spec["cook_minutes"],
                instructions=spec["instructions"],
                ingredients=spec["ingredients"],
                image_url=spec["image_url"],
            )

        templates = REGIONAL_RECIPE_TEMPLATES.get(region_key, REGIONAL_RECIPE_TEMPLATES["asia"])
        tpl = templates[existing_count % len(templates)]

        style_prefixes = ["", "Homestyle ", "Chef's ", "Artisan ", "Heritage "]
        prefix_idx = (existing_count // len(templates)) % len(style_prefixes)
        prefix = style_prefixes[prefix_idx]

        title = prefix + tpl["title_pattern"].format(country=country_name)
        description = tpl["desc_pattern"].format(country=country_name)
        instructions = [
            f"Prepare and measure all fresh regional ingredients for {title}.",
            f"Heat a heavy skillet or pot and aromatics in traditional {country_name} style until fragrant.",
            "Combine the primary ingredients and simmer gently until tender and deeply flavorful.",
            "Garnish with fresh herbs and serve warm with regional accompaniments.",
        ]

        return self.repository.create_generated_recipe(
            location_id=loc_id,
            title=title,
            description=description,
            servings=tpl["servings"],
            prep_minutes=tpl["prep"],
            cook_minutes=tpl["cook"],
            instructions=instructions,
            ingredients=tpl["ingredients"],
            image_url=tpl["image_url"],
        )

    def ensure_location_has_recipes(self, location: dict) -> list[dict]:
        """Ensure the given location has at least one recipe, auto-generating if empty."""
        loc_id = location.get("id")
        if not loc_id:
            return []
        existing = self.repository.recipes_for_location(loc_id)
        if not existing:
            try:
                self.generate_recipe_for_location(location, existing_count=0)
                existing = self.repository.recipes_for_location(loc_id)
            except Exception:
                pass
        return existing

    def page_data(
        self,
        location_id: int | None = None,
        location_slug: str | None = None,
        search_query: str | None = None,
    ) -> dict[str, Any]:
        raw_locations = [self._enrich_location(loc) for loc in self.repository.locations()]

        # Ensure the 6 featured showcase countries always have at least 1 recipe
        featured_changed = False
        for loc in raw_locations:
            if loc.get("id") in {1, 2, 3, 4, 5, 6} and int(loc.get("recipe_count") or 0) == 0:
                try:
                    self.generate_recipe_for_location(loc, existing_count=0)
                    featured_changed = True
                except Exception:
                    pass
        if featured_changed:
            raw_locations = [self._enrich_location(loc) for loc in self.repository.locations()]

        selected_location = None
        if location_id:
            raw_loc = self.repository.location_by_id(location_id)
            if raw_loc:
                selected_location = self._enrich_location(raw_loc)
        elif location_slug:
            raw_loc = self.repository.location_by_name(location_slug)
            if raw_loc:
                selected_location = self._enrich_location(raw_loc)

        if selected_location:
            location_recipes = self.ensure_location_has_recipes(selected_location)
            # Refresh selected_location count if auto-generated
            raw_loc = self.repository.location_by_id(selected_location["id"])
            if raw_loc:
                selected_location = self._enrich_location(raw_loc)
            raw_locations = [self._enrich_location(loc) for loc in self.repository.locations()]
        else:
            location_recipes = self.repository.all_location_recipes(limit=40)

        query_clean = (search_query or "").strip()
        if query_clean:
            words = [w.strip().lower() for w in query_clean.split() if w.strip()]
            if words:
                location_recipes = [
                    r for r in location_recipes
                    if all(w in (r.get("title") or "").lower() for w in words)
                ]

        # When a location is selected, filter the navigation cards grid to that location
        if selected_location:
            featured_locations = [selected_location]
        else:
            featured_locations = sorted(
                [loc for loc in raw_locations if loc.get("id") in {1, 2, 3, 4, 5, 6}],
                key=lambda x: x["id"],
            )
            if not featured_locations:
                featured_locations = raw_locations[:6]

        if query_clean:
            words = [w.strip().lower() for w in query_clean.split() if w.strip()]
            if words:
                matching_loc_names = {
                    (r.get("location_name") or "").strip().lower()
                    for r in location_recipes
                    if r.get("location_name")
                }
                featured_locations = [
                    loc for loc in featured_locations
                    if (loc.get("name") or "").strip().lower() in matching_loc_names
                    or all(w in (f"{loc.get('featured_dish', '')} {loc.get('name', '')}").lower() for w in words)
                ]

        # Nav bar tabs: 6 featured locations + selected location if different
        tab_ids = {1, 2, 3, 4, 5, 6}
        if selected_location:
            tab_ids.add(selected_location["id"])
        nav_locations = sorted(
            [loc for loc in raw_locations if loc["id"] in tab_ids],
            key=lambda x: (0 if x["id"] in {1, 2, 3, 4, 5, 6} else 1, x["id"]),
        )

        # Alphabetical order (A -> Z) for the Location Dropdown Selector
        dropdown_locations = sorted(raw_locations, key=lambda loc: (loc.get("name") or "").lower())

        return {
            "locations": dropdown_locations,
            "dropdown_locations": dropdown_locations,
            "nav_locations": nav_locations,
            "featured_locations": featured_locations,
            "selected_location": selected_location,
            "location_recipes": location_recipes,
            "query": query_clean,
        }
