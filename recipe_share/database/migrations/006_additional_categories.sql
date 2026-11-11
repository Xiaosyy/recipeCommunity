-- Migration 006: Add meat, international cuisine, special diets, and additional food categories
INSERT INTO categories (name, slug, description, is_active) VALUES
  -- Meat & Protein additions
  ('Lamb', 'lamb', 'Tender braised lamb shanks, chops, and roasted specialties', TRUE),
  ('Fish', 'fish', 'Fresh grilled, pan-seared, and steamed fish favorites', TRUE),
  ('Eggs', 'eggs', 'Omelets, frittatas, deviled eggs, and savory egg dishes', TRUE),

  -- International Cuisine additions
  ('Chinese', 'chinese', 'Dim sum, stir-fries, Peking duck, and regional Chinese cuisine', TRUE),
  ('Japanese', 'japanese', 'Sushi, ramen, teriyaki, and traditional Japanese cuisine', TRUE),
  ('Korean', 'korean', 'Kimchi stews, Korean barbecue, bibimbap, and savory pancakes', TRUE),
  ('Mexican', 'mexican', 'Tacos, enchiladas, salsas, and vibrant Mexican dishes', TRUE),
  ('American', 'american', 'Classic barbecue, burgers, comfort pies, and diner favorites', TRUE),
  ('French', 'french', 'Classic bistro fare, pastries, and French culinary traditions', TRUE),
  ('Mediterranean', 'mediterranean', 'Sun-drenched coastal salads, olive oil, and seafood specialties', TRUE),
  ('Thai', 'thai', 'Pad thai, aromatic curries, and spicy Thai classics', TRUE),
  ('Indian', 'indian', 'Fragrant curries, tandoori specialties, biryanis, and naan', TRUE),

  -- Special Diets additions
  ('Gluten-Free', 'gluten-free', 'Naturally wheat-free and gluten-friendly recipes', TRUE)
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  description = COALESCE(categories.description, VALUES(description)),
  is_active = TRUE;

