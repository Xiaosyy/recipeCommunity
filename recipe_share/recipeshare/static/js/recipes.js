/**
 * RecipeShare - Recipes Module (recipes.js)
 * Handles:
 * - Explore recipes sort dropdown toggle
 * - Grid / List view mode switcher
 * - Explore card heart toggles
 * - Recipe detail actions (Like, Save, Rating, Share, Follow)
 */

(() => {
  const initializeExploreControls = (root = document) => {
    // 1. Sort Dropdown Toggle
    const sortDropdown = root.getElementById('recipe-sort-dropdown') || document.getElementById('recipe-sort-dropdown');
    const sortTrigger = root.getElementById('recipe-sort-trigger') || document.getElementById('recipe-sort-trigger');

    if (sortTrigger && sortDropdown && sortTrigger.dataset.initialized !== 'true') {
      sortTrigger.dataset.initialized = 'true';

      sortTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = sortDropdown.classList.toggle('is-open');
        sortTrigger.setAttribute('aria-expanded', String(isOpen));
      });

      // Close when clicking outside
      document.addEventListener('click', (e) => {
        if (!sortDropdown.contains(e.target)) {
          sortDropdown.classList.remove('is-open');
          sortTrigger.setAttribute('aria-expanded', 'false');
        }
      });

      // Close on escape
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sortDropdown.classList.contains('is-open')) {
          sortDropdown.classList.remove('is-open');
          sortTrigger.setAttribute('aria-expanded', 'false');
          sortTrigger.focus();
        }
      });
    }

    // 2. View Mode Switcher (Grid / List)
    const gridEl = root.getElementById('recipe-explore-grid') || document.getElementById('recipe-explore-grid');
    const viewButtons = root.querySelectorAll('.recipe-view-btn');

    if (gridEl && viewButtons.length) {
      // Restore saved view mode preference
      const savedMode = localStorage.getItem('recipe_view_mode') || 'grid';
      if (savedMode === 'list') {
        gridEl.classList.add('is-list-view');
        viewButtons.forEach(btn => btn.classList.toggle('is-active', btn.dataset.viewMode === 'list'));
      }

      viewButtons.forEach(btn => {
        if (btn.dataset.initialized === 'true') return;
        btn.dataset.initialized = 'true';

        btn.addEventListener('click', () => {
          const mode = btn.dataset.viewMode;
          viewButtons.forEach(b => b.classList.remove('is-active'));
          btn.classList.add('is-active');

          if (mode === 'list') {
            gridEl.classList.add('is-list-view');
            localStorage.setItem('recipe_view_mode', 'list');
          } else {
            gridEl.classList.remove('is-list-view');
            localStorage.setItem('recipe_view_mode', 'grid');
          }
        });
      });
    }

    // 3. Explore Recipe Card Heart Like/Save Toggle
    root.querySelectorAll('.recipe-card-explore__heart').forEach(heartBtn => {
      if (heartBtn.dataset.initialized === 'true') return;
      heartBtn.dataset.initialized = 'true';

      heartBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        const slug = heartBtn.dataset.slug;
        if (!slug) return;

        // Optimistic UI toggle
        const willBeActive = !heartBtn.classList.contains('is-active');
        heartBtn.classList.toggle('is-active', willBeActive);

        try {
          if (window.recipeShareApi) {
            const res = await window.recipeShareApi.request('/api/v1/ui/recipe-actions/like', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ slug }),
            });
            heartBtn.classList.toggle('is-active', Boolean(res.active));
            document.querySelectorAll('[data-profile-badge="likes"], [data-profile-stat="likes"]').forEach(el => {
              const cur = parseInt(el.textContent, 10);
              if (!isNaN(cur)) {
                el.textContent = String(Math.max(0, cur + (res.active ? 1 : -1)));
              }
            });
          }
        } catch (_) {
          // If not logged in, revert or keep visual feedback
        }
      });
    });

    // 4. Live Keyword Search Filter by Recipe Name / Word
    const catalogSearchInput = root.getElementById('recipes-catalog-search') || document.getElementById('recipes-catalog-search');
    const liveEmptyState = root.getElementById('recipe-live-empty-state') || document.getElementById('recipe-live-empty-state');

    const applyKeywordFilter = (rawQuery) => {
      const cards = document.querySelectorAll('#recipe-explore-grid .recipe-card-explore');
      if (!cards.length) return;

      const words = String(rawQuery || '')
        .trim()
        .toLowerCase()
        .split(/\s+/)
        .filter(Boolean);

      let visibleCount = 0;
      cards.forEach(card => {
        const title = (
          card.dataset.title ||
          card.querySelector('.recipe-card-explore__title')?.textContent ||
          ''
        ).toLowerCase();
        const matches = words.length === 0 || words.every(word => title.includes(word));
        card.hidden = !matches;
        card.style.display = matches ? '' : 'none';
        if (matches) visibleCount += 1;
      });

      if (liveEmptyState) {
        const emptyTitle = liveEmptyState.querySelector('[data-live-empty-title]');
        if (emptyTitle && rawQuery && rawQuery.trim()) {
          emptyTitle.textContent = `No recipes found matching “${rawQuery.trim()}”`;
        }
        liveEmptyState.hidden = !(words.length > 0 && visibleCount === 0);
      }
    };

    if (catalogSearchInput && catalogSearchInput.dataset.liveSearchInitialized !== 'true') {
      catalogSearchInput.dataset.liveSearchInitialized = 'true';
      catalogSearchInput.addEventListener('input', () => {
        const val = catalogSearchInput.value;
        document.querySelectorAll('[data-global-recipe-search-input]').forEach(inp => {
          if (inp !== catalogSearchInput) inp.value = val;
        });
        applyKeywordFilter(val);
      });
    }

    document.querySelectorAll('[data-global-recipe-search-input]').forEach(globalInput => {
      if (globalInput.dataset.liveRecipeBound === 'true') return;
      globalInput.dataset.liveRecipeBound = 'true';
      globalInput.addEventListener('input', () => {
        const activeCatalogInput = document.getElementById('recipes-catalog-search');
        if (activeCatalogInput) {
          activeCatalogInput.value = globalInput.value;
          applyKeywordFilter(globalInput.value);
        }
      });
    });
  };

  const initializeRecipeActions = (root = document) => {
    root.querySelectorAll('[data-recipe-actions]').forEach(actions => {
      if (actions.dataset.initialized === 'true') return;
      actions.dataset.initialized = 'true';

      const slug = actions.dataset.slug;
      const status = actions.closest('.recipe-detail-summary')?.querySelector('[data-recipe-status]');

      actions.addEventListener('click', async event => {
        const button = event.target.closest('[data-action]');
        if (!button) return;

        const action = button.dataset.action;
        if (action === 'share') {
          try {
            await navigator.clipboard.writeText(window.location.href);
            if (status) status.textContent = 'Recipe link copied to clipboard.';
          } catch (_) {
            if (status) status.textContent = 'Copy the recipe link from your address bar.';
          }
          return;
        }

        try {
          const result = await window.recipeShareApi.request(`/api/v1/ui/recipe-actions/${action}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slug }),
          });
          button.classList.toggle('is-active', Boolean(result.active));
          if (action === 'like') {
            const countEl = button.querySelector('strong');
            if (countEl) countEl.textContent = result.like_count;
            document.querySelectorAll('[data-profile-badge="likes"], [data-profile-stat="likes"]').forEach(el => {
              const cur = parseInt(el.textContent, 10);
              if (!isNaN(cur)) {
                el.textContent = String(Math.max(0, cur + (result.active ? 1 : -1)));
              }
            });
          }
          if (status) {
            status.textContent = action === 'like'
              ? (result.active ? 'Recipe liked.' : 'Like removed.')
              : (result.active ? 'Recipe saved.' : 'Recipe removed from saved items.');
          }
        } catch (error) {
          if (error.message && error.message.includes('(401)') && status) {
            status.textContent = 'Please log in to use this action.';
          }
        }
      });
    });

    root.querySelectorAll('.recipe-rating-input').forEach(rating => {
      if (rating.dataset.initialized === 'true') return;
      rating.dataset.initialized = 'true';

      rating.addEventListener('click', async event => {
        const button = event.target.closest('[data-rating]');
        if (!button) return;
        const stars = Number(button.dataset.rating);

        try {
          const result = await window.recipeShareApi.request('/api/v1/ui/recipe-actions/rate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slug: rating.dataset.slug, rating: stars }),
          });
          rating.querySelectorAll('[data-rating]').forEach(star => {
            star.classList.toggle('is-active', Number(star.dataset.rating) <= stars);
          });
          const reviewCount = rating.closest('.recipe-detail-summary')?.querySelector('.recipe-detail-rating small');
          if (reviewCount) reviewCount.textContent = `${result.review_count} reviews`;
          const average = rating.parentElement?.querySelector(':scope > strong');
          if (average) average.textContent = Number(result.average_rating).toFixed(1);
          const status = rating.closest('.recipe-detail-summary')?.querySelector('[data-recipe-status]');
          if (status) status.textContent = `You rated this recipe ${stars} stars.`;
        } catch (_) {
          const status = rating.closest('.recipe-detail-summary')?.querySelector('[data-recipe-status]');
          if (status) status.textContent = 'Please log in to rate this recipe.';
        }
      });
    });
  };

  const initializeRecipeFollow = (root = document) => {
    root.querySelectorAll('.recipe-follow-action').forEach(button => {
      if (button.dataset.initialized === 'true') return;
      button.dataset.initialized = 'true';

      button.addEventListener('click', async () => {
        try {
          const result = await window.recipeShareApi.request('/api/v1/ui/recipe-actions/follow', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slug: button.dataset.slug }),
          });
          button.classList.toggle('is-active', Boolean(result.active));
          button.textContent = result.active ? 'Following' : 'Follow';

          if (typeof result.follower_count !== 'undefined') {
            const authorId = button.dataset.authorId || result.author_id;
            if (authorId) {
              document.querySelectorAll(`[data-author-follower-count="${authorId}"]`).forEach(el => {
                el.textContent = String(result.follower_count);
              });
            }
            document.querySelectorAll('[data-profile-stat="members"], [data-profile-stat="followers"]').forEach(el => {
              el.textContent = String(result.follower_count);
            });
          }
        } catch (err) {
          if (err && err.status === 401) {
            window.location.href = '/login';
            return;
          }
          const status = document.querySelector('[data-recipe-status]');
          if (status) status.textContent = 'Please log in to follow this creator.';
        }
      });
    });
  };

  const initializeRecipeOwnerControls = (root = document) => {
    root.querySelectorAll('[data-recipe-owner-menu]').forEach(menuWrap => {
      if (menuWrap.dataset.initialized === 'true') return;
      menuWrap.dataset.initialized = 'true';

      const trigger = menuWrap.querySelector('[data-recipe-owner-menu-trigger]');
      const dropdown = menuWrap.querySelector('[data-recipe-owner-dropdown]');
      const shareBtn = menuWrap.querySelector('[data-owner-share-btn]');
      const deleteBtn = menuWrap.querySelector('[data-recipe-delete-btn]');

      trigger?.addEventListener('click', event => {
        event.stopPropagation();
        if (!dropdown) return;
        const willOpen = dropdown.hidden;
        dropdown.hidden = !willOpen;
        trigger.setAttribute('aria-expanded', String(willOpen));
      });

      document.addEventListener('click', event => {
        if (dropdown && !dropdown.hidden && !menuWrap.contains(event.target)) {
          dropdown.hidden = true;
          trigger?.setAttribute('aria-expanded', 'false');
        }
      });

      shareBtn?.addEventListener('click', async () => {
        const status = document.querySelector('[data-recipe-status]');
        try {
          await navigator.clipboard.writeText(window.location.href);
          if (status) status.textContent = 'Recipe link copied to clipboard.';
        } catch (_) {
          if (status) status.textContent = 'Copy the recipe link from your address bar.';
        }
        if (dropdown) dropdown.hidden = true;
        trigger?.setAttribute('aria-expanded', 'false');
      });

      deleteBtn?.addEventListener('click', event => {
        if (!window.confirm('Are you sure you want to delete this recipe?')) {
          event.preventDefault();
        }
      });
    });

    root.querySelectorAll('[data-toggle-steps]').forEach(toggleBtn => {
      if (toggleBtn.dataset.initialized === 'true') return;
      toggleBtn.dataset.initialized = 'true';

      toggleBtn.addEventListener('click', () => {
        const panel = toggleBtn.closest('.recipe-instructions');
        if (!panel) return;
        const extraSteps = panel.querySelectorAll('[data-extra-step]');
        const expanding = extraSteps[0]?.hidden ?? false;
        extraSteps.forEach(item => {
          item.hidden = !expanding;
        });
        const labelSpan = toggleBtn.querySelector('span:first-child');
        const arrowSpan = toggleBtn.querySelector('span:last-child');
        if (labelSpan) labelSpan.textContent = expanding ? 'Show Fewer Steps' : 'View More Steps';
        if (arrowSpan) arrowSpan.textContent = expanding ? '⌃' : '⌄';
      });
    });
  };

  const initRecipes = (root = document) => {
    initializeExploreControls(root);
    initializeRecipeActions(root);
    initializeRecipeFollow(root);
    initializeRecipeOwnerControls(root);
  };

  window.recipeShareRecipes = { init: initRecipes };

  document.addEventListener('DOMContentLoaded', () => initRecipes(document));
  document.addEventListener('recipe-share:page-loaded', () => initRecipes(document));
})();
