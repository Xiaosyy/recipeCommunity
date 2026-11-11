/**
 * RecipeShare - Locations Module (locations.js)
 * Handles location discovery interactions:
 * - Location navigation filter tabs
 * - Custom dropdown selector with search filter
 * - Clickable location cards with smooth SPA navigation
 * - Heart / save toggle on location cards
 */

(() => {
  const initializeLocationTabs = (root = document) => {
    root.querySelectorAll('.location-nav-tab').forEach(tab => {
      if (tab.dataset.locationsInitialized === 'true') return;
      tab.dataset.locationsInitialized = 'true';

      tab.addEventListener('click', event => {
        const href = tab.getAttribute('href');
        if (!href || !window.spaRouter) return;
        event.preventDefault();

        root.querySelectorAll('.location-nav-tab').forEach(t => t.classList.remove('is-active'));
        tab.classList.add('is-active');

        window.spaRouter.navigate(href);
      });
    });
  };

  const initializeLocationDropdown = (root = document) => {
    root.querySelectorAll('[data-location-dropdown]').forEach(dropdown => {
      if (dropdown.dataset.dropdownInitialized === 'true') return;
      dropdown.dataset.dropdownInitialized = 'true';

      const toggleBtn = dropdown.querySelector('[data-location-dropdown-btn]');
      const menu = dropdown.querySelector('[data-location-dropdown-menu]');
      const searchInput = dropdown.querySelector('[data-location-search-input]');
      const items = dropdown.querySelectorAll('.location-dropdown-item');

      if (!toggleBtn || !menu) return;

      const openDropdown = () => {
        menu.removeAttribute('hidden');
        toggleBtn.setAttribute('aria-expanded', 'true');
        searchInput?.focus();
      };

      const closeDropdown = () => {
        menu.setAttribute('hidden', '');
        toggleBtn.setAttribute('aria-expanded', 'false');
      };

      toggleBtn.addEventListener('click', event => {
        event.stopPropagation();
        const isOpen = !menu.hasAttribute('hidden');
        if (isOpen) {
          closeDropdown();
        } else {
          openDropdown();
        }
      });

      // Filter options as user types
      searchInput?.addEventListener('input', () => {
        const query = searchInput.value.trim().toLowerCase();
        items.forEach(item => {
          const name = (item.dataset.locationName || item.textContent || '').toLowerCase();
          item.hidden = !name.includes(query);
        });
      });

      // Close when clicking outside
      document.addEventListener('click', event => {
        if (!dropdown.contains(event.target)) {
          closeDropdown();
        }
      });

      // Handle item selection
      items.forEach(item => {
        item.addEventListener('click', () => {
          closeDropdown();
        });
      });
    });
  };

  const initializeLocationCards = (root = document) => {
    root.querySelectorAll('.location-card').forEach(card => {
      if (card.dataset.cardInitialized === 'true') return;
      card.dataset.cardInitialized = 'true';

      card.addEventListener('click', event => {
        // If the user clicked the heart button inside the card, don't navigate
        if (event.target.closest('[data-save-location]')) return;

        const href = card.getAttribute('href');
        if (!href || !window.spaRouter) return;
        event.preventDefault();
        window.spaRouter.navigate(href);
      });
    });

    root.querySelectorAll('[data-save-location]').forEach(heart => {
      if (heart.dataset.heartInitialized === 'true') return;
      heart.dataset.heartInitialized = 'true';

      heart.addEventListener('click', event => {
        event.preventDefault();
        event.stopPropagation();
        const isSaved = heart.classList.toggle('is-saved');
        const icon = heart.querySelector('.heart-icon');
        if (icon) {
          icon.textContent = isSaved ? '♥' : '♡';
        }
      });
    });
  };

  const initializeLocationGenerator = (root = document) => {
    root.querySelectorAll('[data-location-generate-form]').forEach(form => {
      if (form.dataset.generatorInitialized === 'true') return;
      form.dataset.generatorInitialized = 'true';

      form.addEventListener('submit', async event => {
        if (!window.recipeShareApi || !window.spaRouter) return;
        event.preventDefault();

        const formData = new FormData(form);
        const locationId = Number(formData.get('location_id') || 1);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : '';

        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = '✨ Generating Recipe...';
        }

        try {
          await window.recipeShareApi.request('/api/v1/ui/locations/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location_id: locationId }),
          });
          window.spaRouter.navigate(`/locations?location_id=${locationId}`);
        } catch (_) {
          form.submit();
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
          }
        }
      });
    });
  };

  const initializeLocationKeywordSearch = (root = document) => {
    const searchInput = root.querySelector('[data-location-recipe-search-input]') || document.getElementById('location-recipe-search-input');
    const liveEmpty = root.querySelector('#location-live-empty-state') || document.getElementById('location-live-empty-state');

    const filterLocationRecipesByKeyword = (rawQuery) => {
      const recipeCards = document.querySelectorAll('[data-location-recipe-card]');
      if (!recipeCards.length) return;

      const words = String(rawQuery || '')
        .trim()
        .toLowerCase()
        .split(/\s+/)
        .filter(Boolean);

      const matchingLocations = new Set();
      let visibleCount = 0;

      recipeCards.forEach(card => {
        const title = (
          card.dataset.title ||
          card.querySelector('h2')?.textContent ||
          ''
        ).toLowerCase();
        const locName = (card.dataset.locationName || '').toLowerCase();
        const matches = words.length === 0 || words.every(word => title.includes(word));
        card.hidden = !matches;
        card.style.display = matches ? '' : 'none';
        if (matches) {
          visibleCount += 1;
          if (locName) matchingLocations.add(locName);
        }
      });

      const locationCards = document.querySelectorAll('[data-location-card-item]');
      locationCards.forEach(locWrapper => {
        if (words.length === 0) {
          locWrapper.hidden = false;
          locWrapper.style.display = '';
          return;
        }
        const locTitle = (locWrapper.dataset.title || '').toLowerCase();
        const locName = (locWrapper.dataset.locationName || '').toLowerCase();
        const matchesCardOrRecipe =
          words.every(word => locTitle.includes(word)) || matchingLocations.has(locName);
        locWrapper.hidden = !matchesCardOrRecipe;
        locWrapper.style.display = matchesCardOrRecipe ? '' : 'none';
      });

      if (liveEmpty) {
        liveEmpty.hidden = !(words.length > 0 && visibleCount === 0);
      }
    };

    if (searchInput && searchInput.dataset.liveSearchInitialized !== 'true') {
      searchInput.dataset.liveSearchInitialized = 'true';
      searchInput.addEventListener('input', () => {
        filterLocationRecipesByKeyword(searchInput.value);
      });
    }

    document.querySelectorAll('[data-global-recipe-search-input]').forEach(globalInput => {
      if (globalInput.dataset.liveLocationBound === 'true') return;
      globalInput.dataset.liveLocationBound = 'true';
      globalInput.addEventListener('input', () => {
        const activeLocInput = document.getElementById('location-recipe-search-input');
        if (activeLocInput) {
          activeLocInput.value = globalInput.value;
          filterLocationRecipesByKeyword(globalInput.value);
        }
      });
    });
  };

  const initLocations = (root = document) => {
    initializeLocationTabs(root);
    initializeLocationDropdown(root);
    initializeLocationCards(root);
    initializeLocationGenerator(root);
    initializeLocationKeywordSearch(root);
  };

  window.recipeShareLocations = { init: initLocations };

  document.addEventListener('DOMContentLoaded', () => initLocations(document));
  document.addEventListener('recipe-share:page-loaded', () => initLocations(document));
})();
