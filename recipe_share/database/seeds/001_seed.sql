INSERT IGNORE INTO roles (id, name) VALUES
  (1, 'user'),
  (2, 'admin');

INSERT IGNORE INTO categories (id, name, slug, description, image_url) VALUES
  (1, 'Filipino', 'filipino', 'Filipino community recipes', 'https://images.unsplash.com/photo-1541544741938-0af808871cc0?auto=format&fit=crop&w=800&q=80'),
  (2, 'Italian', 'italian', 'Italian community recipes', 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80'),
  (3, 'Asian', 'asian', 'Asian community recipes', 'https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80'),
  (4, 'Desserts', 'desserts', 'Sweet recipes and desserts', 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80'),
  (5, 'Vegetarian', 'vegetarian', 'Vegetarian recipes', 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80'),
  (14, 'Appetizers', 'appetizers', 'Starters, finger foods, and small plates', 'https://images.unsplash.com/photo-1541529086526-db283c563270?auto=format&fit=crop&w=800&q=80'),
  (16, 'Cakes & Pastries', 'cakes-pastries', 'Layer cakes, flaky pastries, and baked confections', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80'),
  (17, 'Chicken', 'chicken', 'Roasted, grilled, and homestyle poultry dishes', 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&w=800&q=80'),
  (18, 'Drinks & Beverages', 'drinks-beverages', 'Refreshing coolers, hot drinks, and specialty beverages', 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80'),
  (25, 'Fried Foods', 'fried-foods', 'Golden-crispy fried specialties and crunch-packed favorites', 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=800&q=80'),
  (28, 'Low-Carb Meals', 'low-carb-meals', 'Keto-friendly, protein-rich, and low-carbohydrate plates', 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=800&q=80'),
  (32, 'Pork', 'pork', 'Savory pork belly, chops, roasts, and braised favorites', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80'),
  (34, 'Salads', 'salads', 'Crisp greens, grain salads, and vibrant dressings', 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80'),
  (39, 'Street Food', 'street-food', 'Global night-market snacks, skewers, and handheld bites', 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80'),
  (40, 'Vegan', 'vegan', '100% plant-based dishes free from animal products', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80'),
  (54, 'Lamb', 'lamb', 'Tender braised lamb shanks, chops, and roasted specialties', 'https://images.unsplash.com/photo-1603360946369-dc9bb6258143?auto=format&fit=crop&w=800&q=80'),
  (55, 'Fish', 'fish', 'Fresh grilled, pan-seared, and steamed fish favorites', 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80'),
  (66, 'Gluten-Free', 'gluten-free', 'Naturally wheat-free and gluten-friendly recipes', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80'),
  (67, 'Vegetables', 'vegetables', 'Fresh garden vegetables, stir-fries, and healthy greens', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80'),
  (68, 'Snacks', 'snacks', 'Quick finger foods, savory bites, and afternoon snacks', 'https://images.unsplash.com/photo-1621996346565-e3d5d6281781?auto=format&fit=crop&w=800&q=80'),
  (69, 'Baking', 'baking', 'Oven-baked breads, cookies, pies, and artisan pastries', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80'),
  (70, 'Quick & Easy', 'quick-easy', 'Simple, delicious meals ready in 30 minutes or less', 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80'),
  (71, 'Others', 'others', 'Unique fusion dishes, specialty recipes, and homemade creations', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80'),
  (72, 'Rice Meals', 'rice-meals', 'Fried rice, silog plates, biryani, paella, and flavorful rice bowls', 'https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?auto=format&fit=crop&w=800&q=80'),
  (73, 'Grilled & BBQ', 'grilled-bbq', 'Charcoal-grilled meats, skewers, barbecue, and smoky favorites', 'https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?auto=format&fit=crop&w=800&q=80'),
  (74, 'Sandwiches', 'sandwiches', 'Stacked club sandwiches, paninis, subs, and handheld wraps', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80'),
  (75, 'Dairy-Free', 'dairy-free', 'Delicious lactose-free and dairy-free wholesome recipes', 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=800&q=80'),
  (76, 'Smoothies', 'smoothies', 'Blended fruit smoothies, protein shakes, and acai bowls', 'https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=800&q=80'),
  (77, 'Sauces & Dips', 'sauces-dips', 'Savory dips, salsas, marinades, and homemade dressings', 'https://images.unsplash.com/photo-1472476443507-c7a5948772fc?auto=format&fit=crop&w=800&q=80'),
  (78, 'Traditional Filipino Food', 'traditional-filipino-food', 'Authentic Filipino heirloom recipes, adobo, sinigang, and regional heritage dishes', 'https://images.unsplash.com/photo-1541544741938-0af808871cc0?auto=format&fit=crop&w=800&q=80');

INSERT IGNORE INTO locations (id, name, region, country_code, image_path) VALUES
  (1, 'Philippines', 'Asia', 'PH', 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80'),
  (2, 'Italy', 'Europe', 'IT', 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=900&q=80'),
  (3, 'Japan', 'Asia', 'JP', 'https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?auto=format&fit=crop&w=900&q=80'),
  (4, 'Mexico', 'North America', 'MX', 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=900&q=80'),
  (5, 'Thailand', 'Asia', 'TH', 'https://images.unsplash.com/photo-1559314809-0d155014e29e?auto=format&fit=crop&w=900&q=80'),
  (6, 'Mediterranean', 'Europe', 'XX', 'https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=900&q=80');

INSERT IGNORE INTO users (id, role_id, username, email, password_hash, status, email_verified_at) VALUES
  (1, 1, 'testuser', 'testuser@example.com', 'scrypt:32768:8:1$ADfShMvLtFsnW9wt$167e4427fef65ebc0663585f369316068f8af823adb90ee1c680904f76c41fbc59c789a0af90ed0b5095f5ef30e9922d11e1d82bde05621a9b5ade10e40f8044', 'active', NOW()),
  (2, 1, 'maria_santos', 'maria@example.com', 'scrypt:32768:8:1$ADfShMvLtFsnW9wt$167e4427fef65ebc0663585f369316068f8af823adb90ee1c680904f76c41fbc59c789a0af90ed0b5095f5ef30e9922d11e1d82bde05621a9b5ade10e40f8044', 'active', NOW()),
  (3, 1, 'juan_cruz', 'juan@example.com', 'scrypt:32768:8:1$ADfShMvLtFsnW9wt$167e4427fef65ebc0663585f369316068f8af823adb90ee1c680904f76c41fbc59c789a0af90ed0b5095f5ef30e9922d11e1d82bde05621a9b5ade10e40f8044', 'active', NOW()),
  (4, 1, 'ana_reyes', 'ana@example.com', 'scrypt:32768:8:1$ADfShMvLtFsnW9wt$167e4427fef65ebc0663585f369316068f8af823adb90ee1c680904f76c41fbc59c789a0af90ed0b5095f5ef30e9922d11e1d82bde05621a9b5ade10e40f8044', 'active', NOW()),
  (5, 1, 'rico_samba', 'rico@example.com', 'scrypt:32768:8:1$ADfShMvLtFsnW9wt$167e4427fef65ebc0663585f369316068f8af823adb90ee1c680904f76c41fbc59c789a0af90ed0b5095f5ef30e9922d11e1d82bde05621a9b5ade10e40f8044', 'active', NOW()),
  (6, 1, 'pipeto', 'pipeto@example.com', 'scrypt:32768:8:1$ADfShMvLtFsnW9wt$167e4427fef65ebc0663585f369316068f8af823adb90ee1c680904f76c41fbc59c789a0af90ed0b5095f5ef30e9922d11e1d82bde05621a9b5ade10e40f8044', 'active', NOW()),
  (7, 2, 'recipe_admin', 'admin@example.com', 'scrypt:32768:8:1$ADfShMvLtFsnW9wt$167e4427fef65ebc0663585f369316068f8af823adb90ee1c680904f76c41fbc59c789a0af90ed0b5095f5ef30e9922d11e1d82bde05621a9b5ade10e40f8044', 'active', NOW());

UPDATE users SET email_verified_at = COALESCE(email_verified_at, created_at) WHERE id IN (1, 2, 3, 4, 5, 6, 7);

INSERT IGNORE INTO user_profiles (user_id, display_name, bio, location_id) VALUES
  (6, 'Pipeto', 'Home cook sharing Filipino favorites and family recipes.', 1);

INSERT IGNORE INTO recipes (id, author_id, category_id, location_id, title, slug, description, servings, prep_minutes, cook_minutes, instructions, status, view_count, published_at) VALUES
  (1, 2, 1, 1, 'Chicken Adobo', 'chicken-adobo', 'Classic Filipino chicken adobo simmered in soy, vinegar, garlic, and bay leaves.', 4, 10, 35, '["Pat the chicken dry and cut it into even serving pieces. Mix the soy sauce, vinegar, crushed garlic, bay leaves, and peppercorns in a large bowl.", "Place the chicken in the marinade and turn each piece until coated. Cover and refrigerate for 30 minutes, reserving the marinade for cooking.", "Heat the oil in a heavy pot over medium heat. Remove the chicken from the marinade, brown the pieces for 3 to 4 minutes on each side, then set aside.", "Pour the reserved marinade into the pot and scrape up the browned bits. Return the chicken, cover, and simmer over low heat for 25 minutes.", "Uncover and add 1/2 cup water if the sauce is too thick. Increase the heat slightly and simmer for 5 to 8 minutes until the sauce is glossy and the chicken reaches 74°C (165°F) internally.", "Taste the sauce and adjust with a little water or soy sauce if needed. Rest for 5 minutes, then serve hot with steamed rice."]', 'published', 0, NOW()),
  (2, 3, 2, 3, 'Pancit Canton', 'pancit-canton', 'Savory stir-fried noodles with vegetables and chicken.', 5, 15, 20, '["Slice the chicken into thin strips and cut the carrots, cabbage, and bell pepper into uniform pieces. Mix the soy sauce and oyster sauce with 3 cups of broth.", "Heat 1 tablespoon of oil in a wok over medium-high heat. Stir-fry the chicken for 4 to 5 minutes until cooked through, then transfer it to a plate.", "Add the remaining oil to the wok and sauté the garlic for 30 seconds. Add the carrots and bell pepper, cooking for 2 minutes before adding the cabbage for another minute.", "Pour in the sauce mixture and bring it to a gentle boil. Add the noodles and toss continuously for 3 to 4 minutes, folding them through the vegetables as the liquid is absorbed.", "Return the chicken to the wok and cook for 2 more minutes. Season with pepper and add the remaining broth a splash at a time if the noodles are firm.", "Transfer to a serving platter, top with sliced green onions, and serve immediately with calamansi or lemon wedges."]', 'published', 0, NOW()),
  (3, 4, 1, 1, 'Adobo sa Gata', 'adobo-sa-gata', 'Creamy chicken adobo enriched with coconut milk.', 4, 15, 40, '["Cut the chicken into even pieces and season lightly with pepper. Stir the soy sauce, vinegar, crushed garlic, and bay leaves together in a bowl.", "Heat the oil in a wide pot over medium heat. Brown the chicken in batches for 3 to 4 minutes per side so the pieces do not overcrowd the pot.", "Return all the chicken to the pot, add the marinade, and bring it to a gentle simmer. Cover and cook over low heat for 20 minutes.", "Pour in the coconut milk while stirring slowly. Keep the pot below a strong boil to prevent the sauce from separating, and simmer uncovered for 15 minutes.", "Add the sugar and continue cooking until the sauce thickens enough to coat a spoon. Check that the chicken reaches an internal temperature of 74°C (165°F).",
  "Taste and add pepper or a splash of water to balance the sauce. Garnish with chili if desired and serve with steamed rice."]', 'published', 0, NOW()),
  (4, 5, 2, 2, 'Spaghetti Bolognese', 'spaghetti-bolognese', 'A hearty tomato and meat pasta for the whole family.', 4, 20, 35, '["Bring 4 liters of salted water to a rolling boil. Finely chop the onion, carrot, and celery, and grate the Parmesan before starting the sauce.", "Heat the olive oil in a deep skillet over medium heat. Add the chopped vegetables and cook for 6 to 8 minutes until softened, then add the garlic for 30 seconds.", "Add the ground beef and break it apart with a spoon. Cook for 7 to 8 minutes until browned, then stir in the tomato paste for 1 minute.", "Pour in the crushed tomatoes and simmer uncovered over low heat for 20 minutes. Stir occasionally and add a splash of water if the sauce becomes too thick.", "Meanwhile, cook the spaghetti 1 minute less than the package directions. Reserve 1 cup of pasta water, then drain the pasta without rinsing.", "Add the spaghetti to the sauce and toss for 1 to 2 minutes, adding reserved pasta water until glossy. Finish with Parmesan, basil, salt, and pepper, then serve immediately."]', 'published', 0, NOW()),
  (5, 2, 4, 3, 'Mango Graham Float', 'mango-graham-float', 'A chilled layered dessert with cream, graham, and fresh mango.', 6, 20, 0, '["Peel and slice the mangoes into thin, even pieces. Set aside a few attractive slices for decorating the top of the dessert.", "Whip the chilled cream in a cold bowl until soft peaks form. Add the condensed milk gradually and continue whipping just until the mixture holds its shape.", "Arrange a single layer of graham crackers in an 8-inch square dish, breaking crackers as needed to cover gaps.", "Spread one-third of the cream mixture over the crackers and cover it with one-third of the mango slices. Repeat with crackers, cream, and mango twice more.", "Finish with the reserved mango slices and press a piece of plastic wrap directly against the surface. Refrigerate for at least 4 hours, preferably overnight, so the crackers soften.", "Lift and cleanly slice the float into portions. Serve chilled and refrigerate any leftovers within 2 hours."]', 'published', 0, NOW());

INSERT IGNORE INTO recipe_images (recipe_id, storage_path, original_name, mime_type, is_primary) VALUES
  (1, 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=800&q=80', 'chicken-adobo.jpg', 'image/jpeg', TRUE),
  (2, 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80', 'pancit-canton.jpg', 'image/jpeg', TRUE),
  (3, 'https://images.unsplash.com/photo-1601050690117-94f5f6fa8bd7?auto=format&fit=crop&w=800&q=80', 'adobo-sa-gata.jpg', 'image/jpeg', TRUE),
  (4, 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80', 'spaghetti-bolognese.jpg', 'image/jpeg', TRUE),
  (5, 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80', 'mango-graham-float.jpg', 'image/jpeg', TRUE);

UPDATE recipe_images SET storage_path = CASE recipe_id
  WHEN 1 THEN 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=800&q=80'
  WHEN 2 THEN 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80'
  WHEN 3 THEN 'https://images.unsplash.com/photo-1601050690117-94f5f6fa8bd7?auto=format&fit=crop&w=800&q=80'
  WHEN 4 THEN 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80'
  WHEN 5 THEN 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80'
END, original_name = CASE recipe_id
  WHEN 1 THEN 'chicken-adobo.jpg'
  WHEN 2 THEN 'pancit-canton.jpg'
  WHEN 3 THEN 'adobo-sa-gata.jpg'
  WHEN 4 THEN 'spaghetti-bolognese.jpg'
  WHEN 5 THEN 'mango-graham-float.jpg'
END
WHERE recipe_id IN (1,2,3,4,5);

INSERT IGNORE INTO ratings (recipe_id, user_id, score) VALUES (1,1,5),(1,2,5),(1,3,4),(2,1,5),(2,3,4),(3,1,5),(3,2,5),(4,1,4),(4,4,4),(5,1,5),(5,3,5);

-- Keep richer instruction and measurement data synchronized when this seed is rerun.
UPDATE recipes SET location_id = 2, category_id = 2, status = 'published' WHERE slug = 'spaghetti-bolognese';
UPDATE recipes SET location_id = 3 WHERE slug = 'pancit-canton';
UPDATE recipes SET instructions = '["Pat the chicken dry and cut it into even serving pieces. Mix the soy sauce, vinegar, crushed garlic, bay leaves, and peppercorns in a large bowl.","Place the chicken in the marinade and turn each piece until coated. Cover and refrigerate for 30 minutes, reserving the marinade for cooking.","Heat the oil in a heavy pot over medium heat. Remove the chicken from the marinade, brown the pieces for 3 to 4 minutes on each side, then set aside.","Pour the reserved marinade into the pot and scrape up the browned bits. Return the chicken, cover, and simmer over low heat for 25 minutes.","Uncover and add 1/2 cup water if the sauce is too thick. Increase the heat slightly and simmer for 5 to 8 minutes until the sauce is glossy and the chicken reaches 74°C (165°F) internally.","Taste the sauce and adjust with a little water or soy sauce if needed. Rest for 5 minutes, then serve hot with steamed rice."]' WHERE id = 1;
UPDATE recipes SET instructions = '["Slice the chicken into thin strips and cut the carrots, cabbage, and bell pepper into uniform pieces. Mix the soy sauce and oyster sauce with 3 cups of broth.","Heat 1 tablespoon of oil in a wok over medium-high heat. Stir-fry the chicken for 4 to 5 minutes until cooked through, then transfer it to a plate.","Add the remaining oil to the wok and sauté the garlic for 30 seconds. Add the carrots and bell pepper, cooking for 2 minutes before adding the cabbage for another minute.","Pour in the sauce mixture and bring it to a gentle boil. Add the noodles and toss continuously for 3 to 4 minutes, folding them through the vegetables as the liquid is absorbed.","Return the chicken to the wok and cook for 2 more minutes. Season with pepper and add the remaining broth a splash at a time if the noodles are firm.","Transfer to a serving platter, top with sliced green onions, and serve immediately with calamansi or lemon wedges."]' WHERE id = 2;
UPDATE recipes SET instructions = '["Cut the chicken into even pieces and season lightly with pepper. Stir the soy sauce, vinegar, crushed garlic, and bay leaves together in a bowl.","Heat the oil in a wide pot over medium heat. Brown the chicken in batches for 3 to 4 minutes per side so the pieces do not overcrowd the pot.","Return all the chicken to the pot, add the marinade, and bring it to a gentle simmer. Cover and cook over low heat for 20 minutes.","Pour in the coconut milk while stirring slowly. Keep the pot below a strong boil to prevent the sauce from separating, and simmer uncovered for 15 minutes.","Add the sugar and continue cooking until the sauce thickens enough to coat a spoon. Check that the chicken reaches an internal temperature of 74°C (165°F).","Taste and add pepper or a splash of water to balance the sauce. Garnish with chili if desired and serve with steamed rice."]' WHERE id = 3;
UPDATE recipes SET instructions = '["Bring 4 liters of salted water to a rolling boil. Finely chop the onion, carrot, and celery, and grate the Parmesan before starting the sauce.","Heat the olive oil in a deep skillet over medium heat. Add the chopped vegetables and cook for 6 to 8 minutes until softened, then add the garlic for 30 seconds.","Add the ground beef and break it apart with a spoon. Cook for 7 to 8 minutes until browned, then stir in the tomato paste for 1 minute.","Pour in the crushed tomatoes and simmer uncovered over low heat for 20 minutes. Stir occasionally and add a splash of water if the sauce becomes too thick.","Meanwhile, cook the spaghetti 1 minute less than the package directions. Reserve 1 cup of pasta water, then drain the pasta without rinsing.","Add the spaghetti to the sauce and toss for 1 to 2 minutes, adding reserved pasta water until glossy. Finish with Parmesan, basil, salt, and pepper, then serve immediately."]' WHERE id = 4;
UPDATE recipes SET instructions = '["Peel and slice the mangoes into thin, even pieces. Set aside a few attractive slices for decorating the top of the dessert.","Whip the chilled cream in a cold bowl until soft peaks form. Add the condensed milk gradually and continue whipping just until the mixture holds its shape.","Arrange a single layer of graham crackers in an 8-inch square dish, breaking crackers as needed to cover gaps.","Spread one-third of the cream mixture over the crackers and cover it with one-third of the mango slices. Repeat with crackers, cream, and mango twice more.","Finish with the reserved mango slices and press a piece of plastic wrap directly against the surface. Refrigerate for at least 4 hours, preferably overnight, so the crackers soften.","Lift and cleanly slice the float into portions. Serve chilled and refrigerate any leftovers within 2 hours."]' WHERE id = 5;

INSERT IGNORE INTO ingredients (name, normalized_name) VALUES
  ('Chicken', 'chicken'), ('Soy Sauce', 'soy_sauce'), ('Cane Vinegar', 'cane_vinegar'), ('Garlic', 'garlic'), ('Bay Leaves', 'bay_leaves'), ('Black Peppercorns', 'black_peppercorns'), ('Cooking Oil', 'cooking_oil'), ('Water', 'water'), ('Steamed Rice', 'steamed_rice'),
  ('Pancit Canton Noodles', 'pancit_canton_noodles'), ('Carrots', 'carrots'), ('Cabbage', 'cabbage'), ('Bell Pepper', 'bell_pepper'), ('Oyster Sauce', 'oyster_sauce'), ('Chicken Broth', 'chicken_broth'), ('Green Onions', 'green_onions'), ('Calamansi', 'calamansi'),
  ('Coconut Milk', 'coconut_milk'), ('Brown Sugar', 'brown_sugar'), ('Chili', 'chili'),
  ('Spaghetti', 'spaghetti'), ('Ground Beef', 'ground_beef'), ('Onion', 'onion'), ('Celery', 'celery'), ('Crushed Tomatoes', 'crushed_tomatoes'), ('Tomato Paste', 'tomato_paste'), ('Olive Oil', 'olive_oil'), ('Parmesan', 'parmesan'), ('Basil', 'basil'), ('Salt', 'salt'), ('Black Pepper', 'black_pepper'),
  ('Mangoes', 'mangoes'), ('All-Purpose Cream', 'all_purpose_cream'), ('Condensed Milk', 'condensed_milk'), ('Graham Crackers', 'graham_crackers');

INSERT IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order)
SELECT 1, id, quantity, unit, sort_order FROM (
  SELECT 'chicken' normalized_name, 800 quantity, 'g' unit, 1 sort_order UNION ALL SELECT 'soy_sauce', 0.5, 'cup', 2 UNION ALL SELECT 'cane_vinegar', 0.5, 'cup', 3 UNION ALL SELECT 'garlic', 8, 'cloves', 4 UNION ALL SELECT 'bay_leaves', 3, 'pieces', 5 UNION ALL SELECT 'black_peppercorns', 1, 'tsp', 6 UNION ALL SELECT 'cooking_oil', 2, 'tbsp', 7 UNION ALL SELECT 'steamed_rice', 4, 'cups', 8
) amounts JOIN ingredients ON ingredients.normalized_name = amounts.normalized_name;

INSERT IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order)
SELECT 2, id, quantity, unit, sort_order FROM (
  SELECT 'pancit_canton_noodles' normalized_name, 500 quantity, 'g' unit, 1 sort_order UNION ALL SELECT 'chicken', 300, 'g', 2 UNION ALL SELECT 'chicken_broth', 3.5, 'cups', 3 UNION ALL SELECT 'carrots', 1, 'piece', 4 UNION ALL SELECT 'cabbage', 250, 'g', 5 UNION ALL SELECT 'bell_pepper', 1, 'piece', 6 UNION ALL SELECT 'cooking_oil', 2, 'tbsp', 7 UNION ALL SELECT 'garlic', 5, 'cloves', 8 UNION ALL SELECT 'soy_sauce', 0.25, 'cup', 9 UNION ALL SELECT 'oyster_sauce', 3, 'tbsp', 10 UNION ALL SELECT 'green_onions', 4, 'stalks', 11 UNION ALL SELECT 'calamansi', 2, 'pieces', 12
) amounts JOIN ingredients ON ingredients.normalized_name = amounts.normalized_name;

INSERT IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order)
SELECT 3, id, quantity, unit, sort_order FROM (
  SELECT 'chicken' normalized_name, 800 quantity, 'g' unit, 1 sort_order UNION ALL SELECT 'coconut_milk', 400, 'ml', 2 UNION ALL SELECT 'soy_sauce', 0.33, 'cup', 3 UNION ALL SELECT 'cane_vinegar', 0.25, 'cup', 4 UNION ALL SELECT 'garlic', 8, 'cloves', 5 UNION ALL SELECT 'bay_leaves', 3, 'pieces', 6 UNION ALL SELECT 'cooking_oil', 2, 'tbsp', 7 UNION ALL SELECT 'brown_sugar', 1, 'tbsp', 8 UNION ALL SELECT 'black_pepper', 0.5, 'tsp', 9 UNION ALL SELECT 'chili', 1, 'piece', 10
) amounts JOIN ingredients ON ingredients.normalized_name = amounts.normalized_name;

INSERT IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order)
SELECT 4, id, quantity, unit, sort_order FROM (
  SELECT 'spaghetti' normalized_name, 400 quantity, 'g' unit, 1 sort_order UNION ALL SELECT 'ground_beef', 500, 'g', 2 UNION ALL SELECT 'onion', 1, 'piece', 3 UNION ALL SELECT 'carrots', 1, 'piece', 4 UNION ALL SELECT 'celery', 2, 'stalks', 5 UNION ALL SELECT 'garlic', 4, 'cloves', 6 UNION ALL SELECT 'crushed_tomatoes', 800, 'g', 7 UNION ALL SELECT 'tomato_paste', 2, 'tbsp', 8 UNION ALL SELECT 'olive_oil', 3, 'tbsp', 9 UNION ALL SELECT 'parmesan', 0.5, 'cup', 10 UNION ALL SELECT 'basil', 0.25, 'cup', 11 UNION ALL SELECT 'salt', 1, 'tsp', 12 UNION ALL SELECT 'black_pepper', 0.5, 'tsp', 13
) amounts JOIN ingredients ON ingredients.normalized_name = amounts.normalized_name;

INSERT IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order)
SELECT 5, id, quantity, unit, sort_order FROM (
  SELECT 'mangoes' AS normalized_name, 4 AS quantity, 'pieces' AS unit, 1 AS sort_order UNION ALL
  SELECT 'all_purpose_cream', 500, 'ml', 2 UNION ALL
  SELECT 'condensed_milk', 300, 'ml', 3 UNION ALL
  SELECT 'graham_crackers', 24, 'pieces', 4
) amounts JOIN ingredients ON ingredients.normalized_name = amounts.normalized_name;

-- Additional Filipino recipes for the community catalog.
INSERT IGNORE INTO recipes (id, author_id, category_id, location_id, title, slug, description, servings, prep_minutes, cook_minutes, instructions, status, view_count, published_at) VALUES
  (6, 2, 1, 1, 'Pork Sisig', 'pork-sisig', 'A sizzling, tangy pork dish with chopped onions, calamansi, and chili.', 4, 20, 45, '["Boil the pork belly and mask with ginger until tender, then drain and cool completely.","Chop the cooked pork and chicken liver into small, even pieces.","Sear the pork in a hot skillet until browned and crisp at the edges.","Add onion, chili, soy sauce, vinegar, and chopped liver; toss over high heat for 5 minutes.","Season with calamansi juice, salt, and pepper, then serve on a sizzling plate with optional egg."]', 'published', 0, NOW()),
  (7, 3, 1, 1, 'Batangas Lomi', 'batangas-lomi', 'Hearty Batangas noodle soup thickened with egg and topped with pork and vegetables.', 4, 20, 35, '["Combine chicken or pork stock and water in a pot; bring it to a gentle boil.","Cook the sliced pork until firm, then add garlic, onions, fish balls, and vegetables.","Add the lomi noodles and stir constantly so they do not stick to the bottom of the pot.","Whisk eggs and slowly pour them in while stirring until the soup thickens.","Season with soy sauce and pepper, then serve hot with calamansi and crushed pork cracklings."]', 'published', 0, NOW()),
  (8, 4, 1, 1, 'Ginataang Gulay', 'ginataang-gulay', 'Mixed squash and green vegetables simmered in savory coconut milk.', 5, 15, 30, '["Prepare the squash, eggplant, sitaw, and chili by cutting them into even pieces.","Saute garlic, onion, and ginger until fragrant; add shrimp paste and cook for 1 minute.","Pour in coconut milk and bring to a gentle simmer without boiling rapidly.","Add squash and eggplant first, followed by sitaw after 5 minutes.","Cook until all vegetables are tender, then season with salt and serve with rice."]', 'published', 0, NOW()),
  (9, 5, 1, 1, 'Pork Sinigang', 'pork-sinigang', 'A comforting Filipino sour soup with pork and garden vegetables.', 6, 20, 55, '["Rinse the pork ribs and place them in a large pot with water, onion, and tomato.","Bring to a simmer and cook for 45 minutes, skimming foam as needed.","Add radish, long beans, eggplant, and green chili; cook until the radish is tender.","Stir in sinigang mix and adjust the sourness to taste.","Add kangkong just before turning off the heat; season and serve hot."]', 'published', 0, NOW()),
  (10, 2, 1, 1, 'Beef Nilaga', 'beef-nilaga', 'A clean, comforting beef broth with tender meat, cabbage, potatoes, and corn.', 6, 15, 90, '["Place beef shank and water in a large pot, bring to a boil, then reduce to a steady simmer.","Skim the surface and simmer covered until the beef is tender, about 75 minutes.","Add corn and potatoes; cook for 10 minutes until the potatoes are almost tender.","Add pechay or cabbage and simmer for another 5 minutes.","Season with fish sauce and pepper, then serve with calamansi and dipping sauce."]', 'published', 0, NOW()),
  (11, 3, 1, 1, 'Chicken Kare-Kare', 'chicken-kare-kare', 'A mellow peanut and toasted rice stew served with bagoong.', 5, 20, 50, '["Simmer the chicken with onion, garlic, and water until tender, reserving the broth.","Soak annatto seeds in warm broth, then strain the colored liquid into the pot.","Add peanut butter, ground roasted rice, and annatto broth; stir until smooth.","Add eggplant, sitaw, and bok choy, cooking each vegetable until tender-crisp.","Season lightly and serve with bagoong on the side."]', 'published', 0, NOW());

INSERT IGNORE INTO recipe_images (recipe_id, storage_path, original_name, mime_type, is_primary) VALUES
  (6, 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=800&q=80', 'pork-sisig.jpg', 'image/jpeg', TRUE),
  (7, 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80', 'batangas-lomi.jpg', 'image/jpeg', TRUE),
  (8, 'https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80', 'ginataang-gulay.jpg', 'image/jpeg', TRUE),
  (9, 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=800&q=80', 'pork-sinigang.jpg', 'image/jpeg', TRUE),
  (10, 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=800&q=80', 'beef-nilaga.jpg', 'image/jpeg', TRUE),
  (11, 'https://images.unsplash.com/photo-1601050690117-94f5f6fa8bd7?auto=format&fit=crop&w=800&q=80', 'chicken-kare-kare.jpg', 'image/jpeg', TRUE);

INSERT IGNORE INTO ingredients (name, normalized_name) VALUES
  ('Pork Belly', 'pork_belly'), ('Chicken Liver', 'chicken_liver'), ('Ginger', 'ginger'), ('Fish Balls', 'fish_balls'), ('Lomi Noodles', 'lomi_noodles'), ('Squash', 'squash'), ('Eggplant', 'eggplant'), ('Sitaw', 'sitaw'), ('Shrimp Paste', 'shrimp_paste'), ('Pork Ribs', 'pork_ribs'), ('Radish', 'radish'), ('Long Beans', 'long_beans'), ('Sinigang Mix', 'sinigang_mix'), ('Kangkong', 'kangkong'), ('Beef Shank', 'beef_shank'), ('Potatoes', 'potatoes'), ('Corn', 'corn'), ('Pechay', 'pechay'), ('Annatto Seeds', 'annatto_seeds'), ('Peanut Butter', 'peanut_butter'), ('Ground Roasted Rice', 'ground_roasted_rice'), ('Bagoong', 'bagoong'), ('Crushed Pork Cracklings', 'crushed_pork_cracklings'), ('Fish Sauce', 'fish_sauce');

INSERT IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order)
SELECT recipe_id, id, quantity, unit, sort_order FROM (
  SELECT 6 AS recipe_id, 'pork_belly' AS normalized_name, 800 AS quantity, 'g' AS unit, 1 AS sort_order UNION ALL
  SELECT 6, 'chicken_liver', 150, 'g', 2 UNION ALL SELECT 6, 'onion', 1, 'piece', 3 UNION ALL SELECT 6, 'chili', 2, 'pieces', 4 UNION ALL SELECT 6, 'soy_sauce', 3, 'tbsp', 5 UNION ALL SELECT 6, 'cane_vinegar', 2, 'tbsp', 6 UNION ALL SELECT 6, 'calamansi', 4, 'pieces', 7 UNION ALL
  SELECT 7, 'pork_belly', 300, 'g', 1 UNION ALL SELECT 7, 'lomi_noodles', 500, 'g', 2 UNION ALL SELECT 7, 'chicken_broth', 8, 'cups', 3 UNION ALL SELECT 7, 'fish_balls', 8, 'pieces', 4 UNION ALL SELECT 7, 'carrots', 1, 'piece', 5 UNION ALL SELECT 7, 'cabbage', 1, 'cup', 6 UNION ALL SELECT 7, 'garlic', 4, 'cloves', 7 UNION ALL
  SELECT 8, 'squash', 500, 'g', 1 UNION ALL SELECT 8, 'eggplant', 2, 'pieces', 2 UNION ALL SELECT 8, 'sitaw', 12, 'pieces', 3 UNION ALL SELECT 8, 'coconut_milk', 400, 'ml', 4 UNION ALL SELECT 8, 'shrimp_paste', 1, 'tbsp', 5 UNION ALL SELECT 8, 'ginger', 1, 'tbsp', 6 UNION ALL
  SELECT 9, 'pork_ribs', 1, 'kg', 1 UNION ALL SELECT 9, 'radish', 1, 'piece', 2 UNION ALL SELECT 9, 'long_beans', 12, 'pieces', 3 UNION ALL SELECT 9, 'eggplant', 2, 'pieces', 4 UNION ALL SELECT 9, 'sinigang_mix', 40, 'g', 5 UNION ALL SELECT 9, 'kangkong', 2, 'cups', 6 UNION ALL SELECT 9, 'onion', 1, 'piece', 7 UNION ALL
  SELECT 10, 'beef_shank', 1, 'kg', 1 UNION ALL SELECT 10, 'corn', 2, 'cobs', 2 UNION ALL SELECT 10, 'potatoes', 3, 'pieces', 3 UNION ALL SELECT 10, 'pechay', 1, 'bundle', 4 UNION ALL SELECT 10, 'fish_sauce', 2, 'tbsp', 5 UNION ALL SELECT 10, 'onion', 1, 'piece', 6 UNION ALL
  SELECT 11, 'chicken', 800, 'g', 1 UNION ALL SELECT 11, 'peanut_butter', 1, 'cup', 2 UNION ALL SELECT 11, 'ground_roasted_rice', 0.25, 'cup', 3 UNION ALL SELECT 11, 'annatto_seeds', 1, 'tbsp', 4 UNION ALL SELECT 11, 'eggplant', 2, 'pieces', 5 UNION ALL SELECT 11, 'sitaw', 12, 'pieces', 6 UNION ALL SELECT 11, 'cabbage', 1, 'cup', 7 UNION ALL SELECT 11, 'bagoong', 3, 'tbsp', 8
) amounts JOIN ingredients ON ingredients.normalized_name = amounts.normalized_name;

INSERT IGNORE INTO ratings (recipe_id, user_id, score) VALUES (6,1,5),(6,2,5),(6,4,4),(7,1,5),(7,3,4),(8,2,5),(8,5,4),(9,1,5),(9,2,5),(9,4,5),(10,3,4),(10,5,5),(11,1,5),(11,3,4),(11,5,5);

-- Pipeto's published recipe collection.
INSERT IGNORE INTO recipes (id, author_id, category_id, location_id, title, slug, description, servings, prep_minutes, cook_minutes, instructions, status, view_count, published_at) VALUES
  (12, 6, 1, 1, 'Pipeto Tinola', 'pipeto-tinola', 'Warming chicken soup with green papaya, ginger, and chili leaves.', 4, 15, 35, '["Sauté the ginger, onion, and garlic until fragrant.","Add the chicken pieces and cook until lightly browned.","Pour in water and simmer until the chicken is tender.","Add green papaya and cook until soft but not mushy.","Finish with chili leaves and season with fish sauce."]', 'published', 0, NOW()),
  (13, 6, 1, 1, 'Pipeto Pork Menudo', 'pipeto-pork-menudo', 'Filipino pork stew with tomato sauce, potatoes, carrots, and raisins.', 6, 20, 45, '["Sauté garlic and onion in oil until fragrant.","Brown the pork cubes, then add tomato sauce and water.","Cover and simmer until the pork is tender.","Add potatoes and carrots and cook until tender.","Fold in raisins and peas, then season before serving."]', 'published', 0, NOW()),
  (14, 6, 1, 1, 'Pipeto Ginisang Munggo', 'pipeto-ginisang-munggo', 'Savory mung bean stew with pork and leafy greens.', 5, 15, 50, '["Boil mung beans until tender, then set aside.","Sauté garlic, onion, and tomato in a pot.","Add pork and cook until browned.","Pour in the mung beans with their broth and simmer.","Add malunggay leaves and season with fish sauce."]', 'published', 0, NOW()),
  (15, 6, 1, 1, 'Pipeto Buko Pandan', 'pipeto-buko-pandan', 'Refreshing coconut and pandan jelly dessert with cream and condensed milk.', 6, 20, 10, '["Prepare and chill the pandan jelly, then cut it into small cubes.","Combine shredded young coconut, cream, and condensed milk in a bowl.","Fold the pandan jelly into the coconut mixture.","Chill for at least two hours before serving."]', 'published', 0, NOW());

INSERT IGNORE INTO recipe_images (recipe_id, storage_path, original_name, mime_type, is_primary) VALUES
  (12, 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=800&q=80', 'pipeto-tinola.jpg', 'image/jpeg', TRUE),
  (13, 'https://images.unsplash.com/photo-1601050690117-94f5f6fa8bd7?auto=format&fit=crop&w=800&q=80', 'pipeto-pork-menudo.jpg', 'image/jpeg', TRUE),
  (14, 'https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80', 'pipeto-ginisang-munggo.jpg', 'image/jpeg', TRUE),
  (15, 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80', 'pipeto-buko-pandan.jpg', 'image/jpeg', TRUE);

INSERT IGNORE INTO ingredients (name, normalized_name) VALUES
  ('Green Papaya', 'green_papaya'), ('Chili Leaves', 'chili_leaves'), ('Fish Sauce', 'fish_sauce'), ('Pork Cubes', 'pork_cubes'), ('Tomato Sauce', 'tomato_sauce'), ('Potatoes', 'potatoes'), ('Peas', 'peas'), ('Raisins', 'raisins'), ('Mung Beans', 'mung_beans'), ('Malunggay Leaves', 'malunggay_leaves'), ('Shredded Young Coconut', 'shredded_young_coconut'), ('Pandan Jelly', 'pandan_jelly'), ('All-Purpose Cream', 'all_purpose_cream'), ('Condensed Milk', 'condensed_milk');

INSERT IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, sort_order)
SELECT recipe_id, id, quantity, unit, sort_order FROM (
  SELECT 12 AS recipe_id, 'chicken' AS normalized_name, 800 AS quantity, 'g' AS unit, 1 AS sort_order UNION ALL
  SELECT 12, 'green_papaya', 1, 'piece', 2 UNION ALL SELECT 12, 'ginger', 1, 'tbsp', 3 UNION ALL SELECT 12, 'chili_leaves', 2, 'cups', 4 UNION ALL SELECT 12, 'fish_sauce', 2, 'tbsp', 5 UNION ALL
  SELECT 13, 'pork_cubes', 800, 'g', 1 UNION ALL SELECT 13, 'tomato_sauce', 250, 'ml', 2 UNION ALL SELECT 13, 'potatoes', 2, 'pieces', 3 UNION ALL SELECT 13, 'carrots', 2, 'pieces', 4 UNION ALL SELECT 13, 'peas', 0.5, 'cup', 5 UNION ALL SELECT 13, 'raisins', 0.25, 'cup', 6 UNION ALL
  SELECT 14, 'mung_beans', 500, 'g', 1 UNION ALL SELECT 14, 'pork_belly', 300, 'g', 2 UNION ALL SELECT 14, 'garlic', 5, 'cloves', 3 UNION ALL SELECT 14, 'malunggay_leaves', 2, 'cups', 4 UNION ALL SELECT 14, 'fish_sauce', 2, 'tbsp', 5 UNION ALL
  SELECT 15, 'shredded_young_coconut', 300, 'g', 1 UNION ALL SELECT 15, 'pandan_jelly', 250, 'g', 2 UNION ALL SELECT 15, 'all_purpose_cream', 250, 'ml', 3 UNION ALL SELECT 15, 'condensed_milk', 150, 'ml', 4
) amounts JOIN ingredients ON ingredients.normalized_name = amounts.normalized_name;

INSERT IGNORE INTO ratings (recipe_id, user_id, score) VALUES (12,1,5),(12,4,4),(13,3,5),(13,5,4),(14,1,5),(14,2,4),(15,2,5),(15,4,5);
