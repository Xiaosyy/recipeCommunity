-- Migration 012: Delete duplicate recipes and ensure unique recipe images
DELETE FROM reports WHERE target_type = 'recipe' AND target_id IN (
  83, 86, 88, 90, 92, 94, 96, 100, 107, 109, 113, 117, 121, 125,
  1, 9, 24, 26, 28, 25, 27, 35
);

DELETE FROM recipes WHERE id IN (
  83, 86, 88, 90, 92, 94, 96, 100, 107, 109, 113, 117, 121, 125,
  1, 9, 24, 26, 28, 25, 27, 35
);

UPDATE recipes SET author_id = 8, title = 'Special Pancit Palabok', status = 'published' WHERE id = 82;
UPDATE recipes SET title = 'Mexico Chimichurri Grilled Steak Bowl' WHERE id = 22;
UPDATE recipes SET title = 'Golden Mexico Savory Empanadas' WHERE id = 23;
UPDATE recipes SET title = 'Herb-Roasted Beef Stew' WHERE id = 30;

DELETE FROM recipes WHERE author_id = 1 AND title = 'Special Pancit Palabok';
