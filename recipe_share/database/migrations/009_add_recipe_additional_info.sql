-- Migration: Add additional information fields to recipes
ALTER TABLE recipes
  ADD COLUMN cooking_tips VARCHAR(500) NULL AFTER instructions,
  ADD COLUMN serving_suggestion VARCHAR(255) NULL AFTER cooking_tips,
  ADD COLUMN food_type VARCHAR(100) NULL AFTER serving_suggestion,
  ADD COLUMN taste VARCHAR(100) NULL AFTER food_type,
  ADD COLUMN best_served VARCHAR(100) NULL AFTER taste;

