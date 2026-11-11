-- Migration 014: Add and update new and recommended categories
INSERT INTO categories (name, slug, description, image_url, is_active) VALUES
  ('Chicken', 'chicken', 'Roasted, grilled, and homestyle poultry dishes', 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Vegetarian', 'vegetarian', 'Vibrant plant-forward meals and garden-fresh medleys', 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Vegetables', 'vegetables', 'Fresh garden vegetables, stir-fries, and healthy greens', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Snacks', 'snacks', 'Quick finger foods, savory bites, and afternoon snacks', 'https://images.unsplash.com/photo-1621996346565-e3d5d6281781?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Baking', 'baking', 'Oven-baked breads, cookies, pies, and artisan pastries', 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Quick & Easy', 'quick-easy', 'Simple, delicious meals ready in 30 minutes or less', 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Others', 'others', 'Unique fusion dishes, specialty recipes, and homemade creations', 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Pork', 'pork', 'Savory pork belly, chops, roasts, and braised favorites', 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Lamb', 'lamb', 'Tender braised lamb shanks, chops, and roasted specialties', 'https://images.unsplash.com/photo-1603360946369-dc9bb6258143?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Fish', 'fish', 'Fresh grilled, pan-seared, and steamed fish favorites', 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Rice Meals', 'rice-meals', 'Fried rice, silog plates, biryani, paella, and flavorful rice bowls', 'https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Grilled & BBQ', 'grilled-bbq', 'Charcoal-grilled meats, skewers, barbecue, and smoky favorites', 'https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Fried Foods', 'fried-foods', 'Golden-crispy fried specialties and crunch-packed favorites', 'https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Appetizers', 'appetizers', 'Starters, finger foods, and small plates', 'https://images.unsplash.com/photo-1541529086526-db283c563270?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Salads', 'salads', 'Crisp greens, grain salads, and vibrant dressings', 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Sandwiches', 'sandwiches', 'Stacked club sandwiches, paninis, subs, and handheld wraps', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Street Food', 'street-food', 'Global night-market snacks, skewers, and handheld bites', 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Vegan', 'vegan', '100% plant-based dishes free from animal products', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Low-Carb Meals', 'low-carb-meals', 'Keto-friendly, protein-rich, and low-carbohydrate plates', 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Dairy-Free', 'dairy-free', 'Delicious lactose-free and dairy-free wholesome recipes', 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Gluten-Free', 'gluten-free', 'Naturally wheat-free and gluten-friendly recipes', 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Drinks & Beverages', 'drinks-beverages', 'Refreshing coolers, hot drinks, teas, and specialty beverages', 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Smoothies', 'smoothies', 'Blended fruit smoothies, protein shakes, and acai bowls', 'https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Cakes & Pastries', 'cakes-pastries', 'Layer cakes, flaky pastries, tarts, and baked confections', 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Sauces & Dips', 'sauces-dips', 'Savory dips, salsas, marinades, and homemade dressings', 'https://images.unsplash.com/photo-1472476443507-c7a5948772fc?auto=format&fit=crop&w=800&q=80', TRUE),
  ('Traditional Filipino Food', 'traditional-filipino-food', 'Authentic Filipino heirloom recipes, adobo, sinigang, and regional heritage dishes', 'https://images.unsplash.com/photo-1541544741938-0af808871cc0?auto=format&fit=crop&w=800&q=80', TRUE)
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  description = VALUES(description),
  image_url = VALUES(image_url),
  is_active = TRUE;

