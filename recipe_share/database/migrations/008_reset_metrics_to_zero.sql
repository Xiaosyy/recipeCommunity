-- Migration: Reset all recipe views, ratings, and likes back to zero
UPDATE recipes SET view_count = 0;
DELETE FROM ratings;
DELETE FROM likes;

