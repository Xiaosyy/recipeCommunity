/**
 * RecipeShare - Dashboard Module (dashboard.js)
 * Handles dashboard inventory management, metric updates,
 * real-time statistics polling, dynamic charts, and user follow actions.
 */

(() => {
  let dashboardPollTimer = null;
  let activePeriod = 'all';

  const formatNumber = num => {
    const val = Number(num || 0);
    return val.toLocaleString();
  };

  const renderChartColumns = (container, items, fieldName) => {
    if (!container) return;
    if (!items || !items.length) {
      container.innerHTML = '<p class="chart-empty" style="margin: auto; color: #7b8580; font-size: 0.75rem;">No recipes recorded yet for this view.</p>';
      return;
    }

    let highest = 1;
    items.forEach(item => {
      const score = Number(fieldName === 'view_count' ? item.view_count : item.like_count || item.score || 0);
      if (score > highest) highest = score;
    });

    container.innerHTML = '';
    items.forEach(item => {
      const score = Number(fieldName === 'view_count' ? item.view_count : item.like_count || item.score || 0);
      const displayScore = item.display_score || (score >= 1000 ? `${(score / 1000).toFixed(1)}K` : String(score));
      const heightPct = score > 0 ? Math.min(100, Math.round(15 + (score / highest) * 80)) : 4;

      const words = (item.title || 'Recipe').trim().split(/\s+/);
      const firstWord = words[0] || '';
      const restWords = words.slice(1).join(' ');

      const col = document.createElement('div');
      col.className = 'chart-column';
      col.innerHTML = `
        <strong>${displayScore}</strong>
        <div class="chart-bar-wrap">
          <div class="chart-bar" style="height: ${heightPct}%"></div>
        </div>
        <small>${firstWord}<br>${restWords}</small>
      `;
      container.appendChild(col);
    });
  };

  const refreshDashboardRealtime = async (period = activePeriod) => {
    const hasDashboard = Boolean(document.querySelector('[data-dashboard-metrics]'));
    const hasHome = Boolean(document.querySelector('[data-home-stats]'));
    if (!hasDashboard && !hasHome) return;
    if (!window.recipeShareApi) return;

    try {
      const data = await window.recipeShareApi.request(`/api/v1/ui/dashboard-stats?period=${encodeURIComponent(period)}`);
      if (!data || !data.metrics) return;

      const m = data.metrics;

      // Update Dashboard Metric Cards
      document.querySelectorAll('[data-metric-key="total_views"]').forEach(el => {
        el.textContent = formatNumber(m.total_views);
      });
      document.querySelectorAll('[data-metric-key="total_likes"]').forEach(el => {
        el.textContent = formatNumber(m.total_likes);
      });
      document.querySelectorAll('[data-metric-key="recipe_count"]').forEach(el => {
        el.textContent = formatNumber(m.recipe_count);
      });
      document.querySelectorAll('[data-metric-key="active_chefs"]').forEach(el => {
        el.textContent = formatNumber(m.active_chefs);
      });

      // Update Home Screen Stat Cards
      document.querySelectorAll('[data-home-stat="total_views"]').forEach(el => {
        el.textContent = formatNumber(m.total_views);
      });
      document.querySelectorAll('[data-home-stat="total_likes"]').forEach(el => {
        el.textContent = formatNumber(m.total_likes);
      });
      document.querySelectorAll('[data-home-stat="my_recipes"]').forEach(el => {
        if (data.user_metrics && data.user_metrics.recipe_count !== undefined) {
          el.textContent = formatNumber(data.user_metrics.recipe_count);
        }
      });
      document.querySelectorAll('[data-home-stat="recent"]').forEach(el => {
        const recentCount = (data.inventory && data.inventory.length) ? data.inventory.length : (m.recipe_count || 0);
        el.textContent = formatNumber(recentCount);
      });

      // Update Charts
      if (hasDashboard) {
        const viewChart = document.querySelector('[data-chart-container="view_count"]');
        if (viewChart && data.chart_views) {
          renderChartColumns(viewChart, data.chart_views, 'view_count');
        }

        const likeChart = document.querySelector('[data-chart-container="like_count"]');
        if (likeChart && data.chart_likes) {
          renderChartColumns(likeChart, data.chart_likes, 'like_count');
        }

        // Update Side Panel Rankings
        const renderRanking = (containerSelector, items, statFormatter) => {
          const container = document.querySelector(containerSelector);
          if (!container || !items) return;
          container.innerHTML = '';
          items.forEach((item, idx) => {
            const rank = idx + 1;
            const link = document.createElement('a');
            link.className = 'dashboard-ranking';
            link.href = `/recipes/${item.slug}`;
            link.dataset.spaLink = '';
            const imgStyle = item.image_path ? `style="background-image:url('${item.image_path}')"` : '';
            link.innerHTML = `
              <strong class="ranking-place ranking-place--${rank}">${rank}</strong>
              <div class="ranking-image" ${imgStyle}></div>
              <div><b>${item.title}</b><small>♟ ${item.author_name || 'Community Chef'}</small></div>
              <span class="ranking-stat">${statFormatter(item)}</span>
            `;
            container.appendChild(link);
          });
        };

        if (data.top_views) {
          renderRanking('[data-ranking-container="view_count"]', data.top_views, r => `◉ ${formatNumber(r.view_count)}`);
        }
        if (data.top_likes) {
          renderRanking('[data-ranking-container="like_count"]', data.top_likes, r => `♡ ${r.like_count}`);
        }
        if (data.top_rated) {
          renderRanking('[data-ranking-container="rating"]', data.top_rated, r => `★ ${Number(r.average_rating || 0).toFixed(1)}`);
        }

        // Update Recipe Inventory Grid with live statistics & latest recipes
        if (data.inventory && data.inventory.length) {
          const grid = document.querySelector('.dashboard-recipe-grid');
          if (grid) {
            data.inventory.forEach(item => {
              let card = grid.querySelector(`[data-slug="${item.slug}"]`);
              if (card) {
                // Update live statistics
                card.dataset.views = item.view_count || 0;
                card.dataset.likes = item.like_count || 0;
                if (item.id) card.dataset.latest = item.id;

                const viewsEl = card.querySelector('[data-recipe-views]');
                if (viewsEl) viewsEl.textContent = `◉ ${formatNumber(item.view_count || 0)}`;

                const likesEl = card.querySelector('[data-recipe-likes]');
                if (likesEl) likesEl.textContent = `♡ ${item.like_count || 0}`;

                const ratingEl = card.querySelector('[data-recipe-rating]');
                if (ratingEl) {
                  const avgRating = Number(item.average_rating || 0).toFixed(1);
                  ratingEl.innerHTML = `★ ${avgRating} <small>(${item.review_count || 0})</small>`;
                }
              } else {
                // Newly posted recipe ("latest recipes") — add to inventory
                const emptyMsg = grid.querySelector('.empty-dashboard');
                if (emptyMsg) emptyMsg.remove();

                const newCard = document.createElement('article');
                newCard.className = 'dashboard-recipe-card ui-card';
                newCard.dataset.inventoryCard = '';
                newCard.dataset.index = grid.children.length + 1;
                newCard.dataset.latest = item.id || Date.now();
                newCard.dataset.slug = item.slug;
                newCard.dataset.title = (item.title || '').toLowerCase();
                newCard.dataset.category = item.category_name || '';
                newCard.dataset.location = item.location_name || '';
                newCard.dataset.views = item.view_count || 0;
                newCard.dataset.likes = item.like_count || 0;

                const avgRating = Number(item.average_rating || 0).toFixed(1);
                const imgStyle = item.image_path ? `style="background-image:url('${item.image_path}')"` : '';

                newCard.innerHTML = `
                  <a href="/recipes/${item.slug}" data-spa-link>
                    <div class="dashboard-recipe-image" ${imgStyle}>
                      <span class="recipe-location">⌖ ${item.location_name || 'Community'}</span>
                      <span class="recipe-save" data-save-recipe="${item.slug}" role="button" tabindex="0" aria-label="Save ${item.title}">♡</span>
                    </div>
                    <div class="dashboard-recipe-body">
                      <h3>${item.title}</h3>
                      <p>♟ ${item.author_name || 'Community Chef'}</p>
                      <div class="dashboard-recipe-meta">
                        <strong data-recipe-rating>★ ${avgRating} <small>(${item.review_count || 0})</small></strong>
                        <span data-recipe-views>◉ ${formatNumber(item.view_count || 0)}</span>
                        <b data-recipe-likes>♡ ${item.like_count || 0}</b>
                      </div>
                      <div class="recipe-tags"><span>${item.category_name || 'Recipe'}</span></div>
                    </div>
                  </a>
                `;

                // Bind save button on newly added card
                const saveBtn = newCard.querySelector('[data-save-recipe]');
                if (saveBtn) {
                  saveBtn.addEventListener('click', async event => {
                    event.preventDefault();
                    event.stopPropagation();
                    const slug = saveBtn.dataset.saveRecipe;
                    const willSave = !saveBtn.classList.contains('is-active');
                    saveBtn.classList.toggle('is-active', willSave);
                    saveBtn.textContent = willSave ? '♥' : '♡';
                    if (slug && window.recipeShareApi) {
                      try {
                        const res = await window.recipeShareApi.request('/api/v1/ui/recipe-actions/save', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ slug }),
                        });
                        saveBtn.classList.toggle('is-active', Boolean(res.active));
                        saveBtn.textContent = res.active ? '♥' : '♡';
                        refreshDashboardRealtime();
                      } catch (_) {}
                    }
                  });
                }
                grid.appendChild(newCard);
              }
            });

            // Re-sort cards according to the currently active inventory tab
            const activeTab = document.querySelector('.inventory-tabs button.is-active');
            if (activeTab) {
              const sortKey = activeTab.dataset.inventoryTab || '';
              const allCards = Array.from(grid.querySelectorAll('[data-inventory-card]'));
              if (sortKey === 'views' || sortKey === 'likes' || sortKey === 'latest') {
                allCards.sort((a, b) => Number(b.dataset[sortKey] || 0) - Number(a.dataset[sortKey] || 0))
                  .forEach(c => grid.appendChild(c));
              } else if (sortKey === 'all') {
                allCards.sort((a, b) => Number(a.dataset.index || 0) - Number(b.dataset.index || 0))
                  .forEach(c => grid.appendChild(c));
              }
            }
          }
        }
      }
    } catch (_) {}
  };

  const initializeChartControls = (root = document) => {
    root.querySelectorAll('[data-chart-period]').forEach(select => {
      if (select.dataset.chartInitialized === 'true') return;
      select.dataset.chartInitialized = 'true';

      select.addEventListener('change', () => {
        activePeriod = select.value;
        // Keep sibling dropdowns in sync
        root.querySelectorAll('[data-chart-period]').forEach(s => {
          if (s !== select) s.value = activePeriod;
        });
        refreshDashboardRealtime(activePeriod);
      });
    });
  };

  const initializeInventory = (root = document) => {
    root.querySelectorAll('.dashboard-inventory:not([data-inventory-initialized])').forEach(inventory => {
      inventory.dataset.inventoryInitialized = 'true';
      const grid = inventory.querySelector('.dashboard-recipe-grid');
      const cards = Array.from(grid?.querySelectorAll('[data-inventory-card]') || []);
      const search = inventory.querySelector('.inventory-search input');
      const category = inventory.querySelector('.inventory-category');
      const location = inventory.querySelector('.inventory-location');

      const applyFilters = () => {
        const query = search?.value.trim().toLowerCase() || '';
        const currentCards = Array.from(grid?.querySelectorAll('[data-inventory-card]') || []);
        currentCards.forEach(card => {
          const cardTitle = (card.dataset.title || '').toLowerCase();
          const cardCategory = (card.dataset.category || '').toLowerCase();
          const cardLocation = (card.dataset.location || '').toLowerCase();

          const matchesSearch = !query || cardTitle.includes(query) || cardCategory.includes(query) || cardLocation.includes(query);
          const matchesCategory = !category?.value || category.value === 'All Categories' || card.dataset.category === category.value || (card.dataset.category || '').toLowerCase() === category.value.toLowerCase();
          const matchesLocation = !location?.value || location.value === '⌖ Filter by Location' || card.dataset.location === location.value || (card.dataset.location || '').toLowerCase() === location.value.toLowerCase();

          card.hidden = !(matchesSearch && matchesCategory && matchesLocation);
        });

        const visibleCount = currentCards.filter(card => !card.hidden).length;
        let emptyNotice = grid?.querySelector('.inventory-filter-empty');
        if (visibleCount === 0 && currentCards.length > 0) {
          if (!emptyNotice) {
            emptyNotice = document.createElement('div');
            emptyNotice.className = 'inventory-filter-empty';
            emptyNotice.style.gridColumn = '1 / -1';
            emptyNotice.style.textAlign = 'center';
            emptyNotice.style.padding = '36px 16px';
            emptyNotice.innerHTML = '<p style="font-size: 1rem; font-weight: 600; color: #405149; margin-bottom: 6px;">No recipes found for this selection</p><p style="font-size: 0.85rem; color: #748078;">Try selecting another location or category.</p>';
            grid.appendChild(emptyNotice);
          }
          emptyNotice.hidden = false;
        } else if (emptyNotice) {
          emptyNotice.hidden = true;
        }
      };

      inventory.querySelectorAll('.inventory-tabs button').forEach(button => {
        button.addEventListener('click', () => {
          inventory.querySelectorAll('.inventory-tabs button').forEach(tab => tab.classList.remove('is-active'));
          button.classList.add('is-active');

          const tabKey = button.dataset.inventoryTab || '';
          const text = (button.textContent || '').toLowerCase();
          const sortKey = tabKey || (text.includes('viewed') ? 'views' : text.includes('liked') ? 'likes' : text.includes('latest') ? 'latest' : 'all');

          if (grid) {
            const currentCards = Array.from(grid.querySelectorAll('[data-inventory-card]'));
            if (sortKey === 'all') {
              currentCards.sort((a, b) => Number(a.dataset.index || 0) - Number(b.dataset.index || 0)).forEach(card => grid.appendChild(card));
            } else {
              currentCards.sort((a, b) => Number(b.dataset[sortKey] || 0) - Number(a.dataset[sortKey] || 0)).forEach(card => grid.appendChild(card));
            }
          }
          applyFilters();
        });
      });

      inventory.querySelectorAll('[data-save-recipe]').forEach(saveBtn => {
        saveBtn.addEventListener('click', async event => {
          event.preventDefault();
          event.stopPropagation();
          const slug = saveBtn.dataset.saveRecipe;
          const willSave = !saveBtn.classList.contains('is-active');
          saveBtn.classList.toggle('is-active', willSave);
          saveBtn.textContent = willSave ? '♥' : '♡';
          if (slug && window.recipeShareApi) {
            try {
              const res = await window.recipeShareApi.request('/api/v1/ui/recipe-actions/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slug }),
              });
              saveBtn.classList.toggle('is-active', Boolean(res.active));
              saveBtn.textContent = res.active ? '♥' : '♡';
              refreshDashboardRealtime();
            } catch (_) {}
          }
        });
      });

      search?.addEventListener('input', applyFilters);
      category?.addEventListener('change', applyFilters);
      location?.addEventListener('change', applyFilters);
    });
  };

  const refreshProfileStatistics = async (root = document) => {
    if (!root.querySelector('[data-profile-stat]') || !window.recipeShareApi) return;
    try {
      const result = await window.recipeShareApi.request('/api/v1/ui/profile-statistics');
      root.querySelector('[data-profile-stat="recipes"]')?.replaceChildren(document.createTextNode(String(result.recipe_count)));
      root.querySelectorAll('[data-profile-stat="members"], [data-profile-stat="followers"]').forEach(el => {
        el.replaceChildren(document.createTextNode(String(result.follower_count)));
      });
      root.querySelector('[data-profile-stat="likes"]')?.replaceChildren(document.createTextNode(String(result.like_count)));
      root.querySelectorAll('[data-profile-badge="likes"]').forEach(el => {
        el.replaceChildren(document.createTextNode(String(result.like_count)));
      });
      root.querySelectorAll('[data-profile-badge="followers"]').forEach(el => {
        el.replaceChildren(document.createTextNode(String(result.follower_count)));
      });
      root.querySelectorAll('[data-profile-badge="following"]').forEach(el => {
        el.replaceChildren(document.createTextNode(String(result.following_count)));
      });
    } catch (_) {}
  };

  const initializeUserFollow = (root = document) => {
    // User profile follow button (e.g. on /users/<username>)
    root.querySelectorAll('.profile-follow-action').forEach(btn => {
      if (btn.dataset.initialized === 'true') return;
      btn.dataset.initialized = 'true';

      btn.addEventListener('click', async () => {
        const userId = btn.dataset.userId;
        if (!userId || !window.recipeShareApi) return;

        try {
          const res = await window.recipeShareApi.request(`/api/v1/ui/users/${userId}/follow`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
          });

          btn.classList.toggle('is-active', Boolean(res.active));
          btn.textContent = res.active ? 'Following' : 'Follow';

          if (typeof res.follower_count !== 'undefined') {
            document.querySelectorAll('[data-profile-stat="members"], [data-profile-stat="followers"]').forEach(stat => {
              stat.textContent = String(res.follower_count);
            });
            document.querySelectorAll(`[data-author-follower-count="${userId}"]`).forEach(stat => {
              stat.textContent = String(res.follower_count);
            });
          }
        } catch (err) {
          if (err && err.status === 401) {
            window.location.href = '/login';
          }
        }
      });
    });
  };

  const initializeProfilePicturePreview = (root = document) => {
    root.querySelectorAll('[data-profile-avatar-input]').forEach(input => {
      if (input.dataset.previewInitialized === 'true') return;
      input.dataset.previewInitialized = 'true';

      const card = input.closest('.profile-picture-card');
      const form = input.closest('form');
      const statusText = card?.querySelector('[data-profile-avatar-status]');
      const avatarBox = card?.querySelector('.profile-settings-avatar');

      if (avatarBox) {
        avatarBox.style.cursor = 'pointer';
        avatarBox.title = 'Click to choose a profile picture';
        avatarBox.addEventListener('click', () => input.click());
      }

      form?.addEventListener('submit', event => {
        if (!input.files || !input.files.length) {
          event.preventDefault();
          input.click();
        }
      });

      input.addEventListener('change', () => {
        const file = input.files?.[0];
        if (!file) return;

        if (statusText) {
          statusText.textContent = `Selected: ${file.name} — uploading...`;
        }

        const preview = card?.querySelector('[data-profile-avatar-preview]');
        if (preview) {
          if (preview.tagName === 'IMG') {
            preview.src = URL.createObjectURL(file);
          } else {
            const image = document.createElement('img');
            image.src = URL.createObjectURL(file);
            image.alt = 'Profile picture preview';
            image.dataset.profileAvatarPreview = '';
            preview.replaceWith(image);
          }
        }

        if (form) {
          form.submit();
        }
      });
    });
  };

  const startRealtimePolling = () => {
    if (dashboardPollTimer) clearInterval(dashboardPollTimer);
    // Poll every 12 seconds when the page has dashboard metrics or home stats
    dashboardPollTimer = setInterval(() => {
      if (!document.hidden) {
        refreshDashboardRealtime();
      }
    }, 12000);
  };

  const initDashboard = (root = document) => {
    initializeInventory(root);
    initializeChartControls(root);
    initializeUserFollow(root);
    refreshProfileStatistics(root);
    initializeProfilePicturePreview(root);

    // Initial real-time fetch if on dashboard or home
    if (root.querySelector('[data-dashboard-metrics]') || root.querySelector('[data-home-stats]')) {
      refreshDashboardRealtime();
      startRealtimePolling();
    }
  };

  // Re-fetch when user switches back to this tab
  window.addEventListener('focus', () => {
    refreshDashboardRealtime();
  });

  window.recipeShareDashboard = {
    init: initDashboard,
    refreshRealtime: refreshDashboardRealtime,
  };

  document.addEventListener('DOMContentLoaded', () => initDashboard(document));
  document.addEventListener('recipe-share:page-loaded', () => initDashboard(document));
})();
