/**
 * RecipeShare - Auth Module Entrypoint (auth.js)
 * Backward-compatible coordinator for authentication screens.
 */

const initializeAuthControls = () => {
  window.recipeShareLogin?.init();
  window.recipeShareRegister?.init();
};

document.addEventListener('DOMContentLoaded', initializeAuthControls);
document.addEventListener('recipe-share:page-loaded', initializeAuthControls);
