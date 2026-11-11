/**
 * RecipeShare - Core Application Orchestrator (app.js)
 * Initializes global navigation, notification tray, mobile menus,
 * and coordinates domain-specific modules.
 */

document.addEventListener('DOMContentLoaded', () => {
  window.spaRouter?.init();
  window.recipeShareAnimations?.lockDrag(document.querySelector('[data-spa-main]'));

  document.addEventListener('dragstart', event => event.preventDefault());
  document.addEventListener('selectstart', event => {
    if (!(event.target instanceof Element)) return;
    if (!event.target.closest('input, textarea, select, [contenteditable="true"]')) event.preventDefault();
  });
  document.querySelectorAll('img, [draggable]').forEach(element => element.setAttribute('draggable', 'false'));

  // Mobile App Sidebar & Public Mobile Menu
  const initializeMobileMenus = (root = document) => {
    const sidebar = root.querySelector('.app-sidebar') || document.querySelector('.app-sidebar');
    root.querySelectorAll('.mobile-menu-button, .app-mobile-menu-button').forEach(menuButton => {
      if (menuButton.dataset.menuInitialized === 'true') return;
      menuButton.dataset.menuInitialized = 'true';
      menuButton.addEventListener('click', () => {
        const open = sidebar?.classList.toggle('is-open');
        menuButton.setAttribute('aria-expanded', String(Boolean(open)));
        document.querySelector('.app-primary-nav')?.classList.toggle('is-open', Boolean(open));
      });
    });

    root.querySelectorAll('.public-mobile-menu').forEach(publicMenuButton => {
      if (publicMenuButton.dataset.menuInitialized === 'true') return;
      publicMenuButton.dataset.menuInitialized = 'true';
      publicMenuButton.addEventListener('click', () => {
        const navigation = document.querySelector('.public-header nav');
        const open = navigation?.classList.toggle('is-open');
        publicMenuButton.setAttribute('aria-expanded', String(Boolean(open)));
      });
    });
  };
  initializeMobileMenus();

  // Navigation Highlights
  const setPublicActiveNavigation = () => {
    document.querySelectorAll('.public-header nav a').forEach(link => {
      link.classList.toggle('active', link.pathname === location.pathname);
    });
  };
  setPublicActiveNavigation();

  const setSidebarActiveNavigation = () => {
    document.querySelectorAll('.app-sidebar .sidebar-nav a[href="/admin/settings"], .app-sidebar .sidebar-nav a[href="/admin/system"]').forEach(link => link.remove());
    document.querySelectorAll('.app-sidebar .sidebar-nav a').forEach(link => {
      link.classList.toggle('is-active', link.pathname === location.pathname);
    });
  };
  setSidebarActiveNavigation();

  // Notification Dropdown Center
  const initializeNotifications = (root = document) => {
    root.querySelectorAll('[data-notification-menu]').forEach(menu => {
      if (menu.dataset.initialized === 'true') return;
      menu.dataset.initialized = 'true';
      const button = menu.querySelector('[data-notification-button]');
      const panel = menu.querySelector('[data-notification-panel]');
      const list = menu.querySelector('[data-notification-list]');
      const count = menu.querySelector('[data-notification-count]');

      const renderCount = value => {
        if (!count) return;
        count.textContent = String(value);
        count.hidden = value === 0;
      };

      const loadNotifications = async () => {
        try {
          const data = await window.recipeShareApi.request('/api/v1/ui/notifications');
          renderCount(data.unread_count);
          list.replaceChildren();
          if (!data.items.length) {
            const empty = document.createElement('p');
            empty.className = 'notification-empty';
            empty.textContent = 'No notifications yet.';
            list.append(empty);
            return;
          }
          data.items.forEach(notification => {
            const payload = notification.payload || {};
            const link = document.createElement('a');
            link.className = 'notification-item';
            link.href = payload.recipe_slug ? `/recipes/${payload.recipe_slug}` : (payload.link || '/settings');
            link.setAttribute('data-spa-link', '');

            let icon = '🔔';
            let message = '';

            if (notification.type === 'otp_sent') {
              icon = '🛡️';
              message = payload.message || `Security: 6-digit verification code sent to ${payload.email || 'your email'}.`;
            } else if (notification.type === 'account_verified') {
              icon = '✅';
              message = payload.message || 'Security: Your account email is officially verified.';
            } else if (notification.type === 'user_followed') {
              icon = '👤';
              message = payload.message || `${payload.actor_name || 'A community member'} started following you.`;
            } else if (notification.type === 'recipe_saved') {
              icon = '🔖';
              message = `${payload.actor_name || 'A member'} saved your recipe “${payload.recipe_title || 'Recipe'}”`;
            } else {
              icon = '❤️';
              message = `${payload.actor_name || 'A member'} liked your recipe “${payload.recipe_title || 'Recipe'}”`;
            }

            link.innerHTML = `<span class="notification-item__icon">${icon}</span><span class="notification-item__text">${message}</span>`;
            list.append(link);
          });
        } catch (_) {
          list.innerHTML = '<p class="notification-empty">Notifications are unavailable.</p>';
        }
      };

      button?.addEventListener('click', async event => {
        event.stopPropagation();
        const opening = panel.hidden;
        panel.hidden = !opening;
        button.setAttribute('aria-expanded', String(opening));
        if (opening) await loadNotifications();
      });

      document.addEventListener('click', event => {
        if (panel && !panel.hidden && !menu.contains(event.target)) {
          panel.hidden = true;
          button?.setAttribute('aria-expanded', 'false');
        }
      });

      menu.querySelector('[data-notifications-read]')?.addEventListener('click', async () => {
        await window.recipeShareApi.request('/api/v1/ui/notifications/read', { method: 'POST' });
        renderCount(0);
      });
    });
  };
  initializeNotifications();

  // Post / Recipe Status Toggle
  const initializePostCreate = (root = document) => {
    root.querySelectorAll('[data-post-status-input]').forEach(input => {
      if (input.dataset.initialized === 'true') return;
      input.dataset.initialized = 'true';
      const form = input.closest('form');
      form?.querySelector('[data-post-draft]')?.addEventListener('click', () => { input.value = 'draft'; });
      form?.querySelector('[data-post-publish]')?.addEventListener('click', () => { input.value = 'published'; });
    });
  };
  initializePostCreate();

  // Re-run handlers on SPA page load
  document.addEventListener('recipe-share:page-loaded', () => {
    initializeMobileMenus(document);
    setPublicActiveNavigation();
    setSidebarActiveNavigation();
    initializeNotifications(document);
    initializePostCreate(document);
  });
});
