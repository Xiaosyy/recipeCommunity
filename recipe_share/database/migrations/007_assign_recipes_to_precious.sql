-- Migration: Assign all recipes to user 'precious' if present, otherwise default author
UPDATE recipes 
SET author_id = (SELECT id FROM users WHERE username = 'precious' LIMIT 1)
WHERE EXISTS (SELECT 1 FROM users WHERE username = 'precious');
