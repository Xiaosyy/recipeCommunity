/**
 * RecipeShare - Admin Module (admin.js)
 * Handles admin console operations:
 * - User search and role/status filtering
 * - Activity log filtering
 * - System settings tab switching
 * - Community logo and brand image upload preview
 */

(() => {
  const initializeAdminFilters = (root = document) => {
    const userSearch = root.querySelector('#admin-user-search');
    const userRole = root.querySelector('#admin-user-role-filter');
    const userStatus = root.querySelector('#admin-user-status-filter');
    const userRows = Array.from(root.querySelectorAll('.admin-user-table tbody tr[data-user-name]'));

    const filterUsers = () => {
      const query = (userSearch?.value || '').toLowerCase();
      userRows.forEach(row => {
        const nameMatch = row.dataset.userName.toLowerCase().includes(query) ||
                          row.dataset.userEmail.toLowerCase().includes(query);
        const roleMatch = !userRole?.value || row.dataset.userRole === userRole.value;
        const statusMatch = !userStatus?.value || row.dataset.userStatus === userStatus.value;
        row.hidden = !(nameMatch && roleMatch && statusMatch);
      });
    };

    userSearch?.addEventListener('input', filterUsers);
    userRole?.addEventListener('change', filterUsers);
    userStatus?.addEventListener('change', filterUsers);

    const activitySearch = root.querySelector('#admin-activity-search');
    const activityAction = root.querySelector('#admin-activity-action-filter');
    const activityRows = Array.from(root.querySelectorAll('.admin-activity-table tbody tr[data-activity-search]'));
    const filterActivity = () => {
      const query = (activitySearch?.value || '').toLowerCase();
      const actionVal = (activityAction?.value || '').toLowerCase();
      activityRows.forEach(row => {
        const matchesSearch = !query || (row.dataset.activitySearch || '').toLowerCase().includes(query);
        const matchesAction = !actionVal || (row.dataset.activityAction || '').toLowerCase() === actionVal;
        row.hidden = !(matchesSearch && matchesAction);
      });
    };
    activitySearch?.addEventListener('input', filterActivity);
    activityAction?.addEventListener('change', filterActivity);

    const categorySearch = root.querySelector('#admin-category-search');
    const categoryStatus = root.querySelector('#admin-category-status-filter');
    const categoryRows = Array.from(root.querySelectorAll('.admin-category-table tbody tr[data-category-name]'));
    const filterCategories = () => {
      const query = (categorySearch?.value || '').toLowerCase().trim();
      const statusVal = (categoryStatus?.value || '').toLowerCase();
      categoryRows.forEach(row => {
        const nameMatch = !query ||
                          (row.dataset.categoryName || '').includes(query) ||
                          (row.dataset.categoryDesc || '').includes(query);
        const statusMatch = !statusVal || row.dataset.categoryStatus === statusVal;
        row.hidden = !(nameMatch && statusMatch);
      });
    };
    categorySearch?.addEventListener('input', filterCategories);
    categoryStatus?.addEventListener('change', filterCategories);
  };

  const initializeSettings = (root = document) => {
    const page = root.querySelector('.system-settings-page');
    if (!page || page.dataset.initialized === 'true') return;
    page.dataset.initialized = 'true';

    const description = page.querySelector('[name="community_description"]');
    const counter = page.querySelector('[data-description-count]');
    description?.addEventListener('input', () => {
      if (counter) counter.textContent = description.value.length;
    });

    const logoInput = page.querySelector('[data-logo-input]');
    const logoPreview = page.querySelector('[data-logo-preview]');
    logoInput?.addEventListener('change', () => {
      const file = logoInput.files?.[0];
      if (!file || !logoPreview) return;
      logoPreview.src = URL.createObjectURL(file);
    });
  };

  const initAdmin = (root = document) => {
    initializeAdminFilters(root);
    initializeSettings(root);
  };

  window.recipeShareAdmin = { init: initAdmin };

  document.addEventListener('DOMContentLoaded', () => initAdmin(document));
  document.addEventListener('recipe-share:page-loaded', () => initAdmin(document));
})();

