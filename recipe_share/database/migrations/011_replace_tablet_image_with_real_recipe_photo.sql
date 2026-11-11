-- Migration 011: Replace tablet photos with real food recipe photos and ensure all recipes have recipe images
UPDATE recipe_images
SET storage_path = 'https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=800&q=80'
WHERE storage_path LIKE '%1495521821757%';

-- Assign noodles category and palabok photo to Special Pancit Palabok recipes
UPDATE recipes
SET category_id = (SELECT id FROM categories WHERE slug = 'noodles-pasta' LIMIT 1)
WHERE (title LIKE '%Pancit Palabok%' OR title LIKE '%Palabok%') AND category_id IS NULL;

INSERT INTO recipe_images (recipe_id, storage_path, is_primary)
SELECT r.id, 'https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=800&q=80', TRUE
FROM recipes r
WHERE (SELECT COUNT(*) FROM recipe_images ri WHERE ri.recipe_id = r.id) = 0;

