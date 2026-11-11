/**
 * RecipeShare - Home Module (home.js)
 * Handles interactions on the homepage:
 * - Hero keyword search bar
 * - Category discovery cards navigation
 */

(() => {
  const initializeHeroSearch = (root = document) => {
    const heroSearchForm = root.querySelector('.hero-search');
    if (!heroSearchForm || heroSearchForm.dataset.heroInitialized === 'true') return;
    heroSearchForm.dataset.heroInitialized = 'true';

    heroSearchForm.addEventListener('submit', event => {
      event.preventDefault();
      const input = heroSearchForm.querySelector('input[name="q"], input[type="search"], input[type="text"]');
      const query = (input?.value || '').trim();
      const targetUrl = query ? `/recipes?q=${encodeURIComponent(query)}` : '/recipes';

      if (window.spaRouter) {
        window.spaRouter.navigate(targetUrl);
      } else {
        window.location.href = targetUrl;
      }
    });
  };

  const initializeCategoryCards = (root = document) => {
    root.querySelectorAll('.category-card').forEach(card => {
      if (card.dataset.categoryInitialized === 'true') return;
      card.dataset.categoryInitialized = 'true';

      card.addEventListener('click', event => {
        const link = card.getAttribute('href');
        if (!link || !window.spaRouter) return;
        event.preventDefault();
        window.spaRouter.navigate(link);
      });
    });
  };

  const initHome = (root = document) => {
    initializeHeroSearch(root);
    initializeCategoryCards(root);
  };

  window.recipeShareHome = { init: initHome };

  document.addEventListener('DOMContentLoaded', () => initHome(document));
  document.addEventListener('recipe-share:page-loaded', () => initHome(document));
})();

