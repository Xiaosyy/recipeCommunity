class SpaRouter {
  constructor() {
    this.main = document.querySelector('[data-spa-main]');
    this.initialized = false;
  }

  isInternal(url) {
    return (
      url.origin === location.origin &&
      !url.pathname.match(/\.(?:css|js|png|jpg|jpeg|gif|webp|svg|ico|mp4|webm|mov|ogg)$/i)
    );
  }

  init() {
    this.main = document.querySelector('[data-spa-main]');
    if (!this.main || this.initialized) return;
    this.initialized = true;

    document.addEventListener('submit', event => {
      if (event.defaultPrevented) return;

      const searchForm = event.target.closest('form[data-spa-search]');
      if (searchForm) {
        event.preventDefault();
        const query = new FormData(searchForm).get('q') || '';
        const params = new URLSearchParams({ q: String(query).trim() });
        this.navigate(`/search?${params.toString()}`, true, 'forward', false);
        return;
      }

      const locationSearchForm = event.target.closest('form[data-location-recipe-search]');
      if (locationSearchForm) {
        event.preventDefault();
        const formData = new FormData(locationSearchForm);
        const query = String(formData.get('q') || '').trim();
        const locationId = String(formData.get('location_id') || '').trim();
        const params = new URLSearchParams();
        if (locationId) params.set('location_id', locationId);
        if (query) params.set('q', query);
        const searchStr = params.toString() ? `?${params.toString()}` : '';
        this.navigate(`/locations${searchStr}`, true, 'forward', false);
        return;
      }

      const recipeSearchForm = event.target.closest('form[data-recipe-search], form.global-search');
      if (recipeSearchForm) {
        event.preventDefault();
        const formData = new FormData(recipeSearchForm);
        const query = String(formData.get('q') || '').trim();
        const currentUrl = new URL(window.location.href);
        const category = String(formData.get('category') || currentUrl.searchParams.get('category') || '').trim();
        const locParam = String(formData.get('location') || currentUrl.searchParams.get('location') || '').trim();
        const filter = String(formData.get('filter') || currentUrl.searchParams.get('filter') || '').trim();
        const params = new URLSearchParams();
        if (query) params.set('q', query);
        if (category) params.set('category', category);
        if (locParam) params.set('location', locParam);
        if (filter && filter !== 'all') params.set('filter', filter);
        const searchStr = params.toString() ? `?${params.toString()}` : '';
        this.navigate(`/recipes${searchStr}`, true, 'forward', false);
        return;
      }

      const generatorForm = event.target.closest('form[data-location-generator]');
      if (generatorForm) {
        event.preventDefault();
        const locationId = new FormData(generatorForm).get('location_id');
        if (locationId) this.navigate(`/locations?location_id=${encodeURIComponent(String(locationId))}`, true, 'forward', false);
        return;
      }

      const form = event.target.closest('form');
      if (!form || form.hasAttribute('data-no-spa') || form.hasAttribute('data-location-generate-form')) return;
      const method = (form.getAttribute('method') || 'GET').toUpperCase();
      const actionUrl = new URL(form.getAttribute('action') || location.href, location.origin);
      if (!this.isInternal(actionUrl)) return;

      if (method === 'POST') {
        event.preventDefault();
        this.submitForm(form, actionUrl, event.submitter);
      }
    });

    document.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0) return;
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (event.target instanceof Element && event.target.closest('button, [data-save-location], [data-save-recipe]')) return;

      const link = event.target instanceof Element
        ? event.target.closest('a[data-spa-link], .app-shell a[href^="/"]:not([target]):not([download]), .public-shell a[href^="/"]:not([target]):not([download])')
        : null;
      if (!link) return;

      const href = link.getAttribute('href');
      if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;

      const url = new URL(link.href, location.href);
      if (!this.isInternal(url)) return;

      event.preventDefault();
      document.querySelectorAll('[data-ui-dropdown][open]').forEach(dropdown => dropdown.removeAttribute('open'));
      const sidebarNavigation = Boolean(link.closest('.app-sidebar'));
      const direction = link.dataset.authTransition || this.transitionDirection(location.pathname, url.pathname);
      this.navigate(url.pathname + url.search, true, direction, sidebarNavigation);
    });

    window.addEventListener('popstate', () => {
      this.navigate(location.pathname + location.search, false);
    });
  }

  transitionDirection(from, to) {
    const order = [
      '/',
      '/recipes',
      '/categories',
      '/locations',
      '/login',
      '/register',
      '/verify-email',
      '/forgot-password',
      '/reset-password/verify',
      '/reset-password',
    ];
    const fromIdx = order.indexOf(from);
    const toIdx = order.indexOf(to);
    if (fromIdx !== -1 && toIdx !== -1 && fromIdx !== toIdx) {
      return toIdx > fromIdx ? 'forward' : 'back';
    }
    const authRoutes = ['/login', '/register', '/verify-email', '/forgot-password', '/reset-password/verify', '/reset-password'];
    const publicToAuth = from === '/' && authRoutes.includes(to);
    return publicToAuth || (from === '/login' && to === '/register') || to === '/verify-email' || to === '/forgot-password' || to === '/reset-password/verify' || to === '/reset-password' ? 'forward' : 'back';
  }

  syncCsrfToken(doc) {
    const nextToken = doc.querySelector('meta[name="csrf-token"]')?.content;
    if (!nextToken) return;
    const currentMeta = document.querySelector('meta[name="csrf-token"]');
    if (currentMeta) currentMeta.setAttribute('content', nextToken);
    if (window.recipeShareApi) window.recipeShareApi.csrfToken = nextToken;
  }

  async applyDocumentResponse(doc, targetPath, push = true, direction = 'forward') {
    this.syncCsrfToken(doc);
    const currentIsApp = document.body.classList.contains('app-shell');
    const nextIsApp = doc.body.classList.contains('app-shell');
    const newMain = doc.querySelector('[data-spa-main]');

    if (!newMain) {
      location.href = targetPath;
      return;
    }

    const nextUrl = new URL(targetPath, location.origin);
    const nextPathname = nextUrl.pathname === '/' ? '/' : nextUrl.pathname.replace(/\/$/, '') || '/';
    const normalizedTarget = nextPathname + nextUrl.search;
    const currentPathname = location.pathname === '/' ? '/' : location.pathname.replace(/\/$/, '') || '/';

    if (currentIsApp !== nextIsApp || !document.querySelector('[data-spa-main]')) {
      document.body.className = doc.body.className;
      Array.from(document.body.children).forEach(child => {
        if (child.tagName !== 'SCRIPT') child.remove();
      });
      const firstScript = document.body.querySelector('script');
      Array.from(doc.body.children).forEach(child => {
        if (child.tagName !== 'SCRIPT') {
          document.body.insertBefore(child.cloneNode(true), firstScript);
        }
      });
      this.main = document.querySelector('[data-spa-main]');
    } else {
      this.main = document.querySelector('[data-spa-main]');
      const shouldAnimate = currentPathname !== nextPathname && !currentIsApp;
      if (shouldAnimate) await window.recipeShareAnimations?.leave(this.main, direction);
      this.main.innerHTML = newMain.innerHTML;
      document.body.className = doc.body.className;
      const isAuth =
        doc.body.classList.contains('auth-page') ||
        ['/login', '/register', '/verify-email'].includes(nextPathname);
      document.body.classList.toggle('spa-auth-view', isAuth);
      document.body.classList.toggle('auth-page', isAuth);
      if (shouldAnimate) await window.recipeShareAnimations?.slide(this.main, direction);
    }

    if (this.main) {
      window.recipeShareAnimations?.lockDrag(this.main);
    }
    if (doc.title) {
      document.title = doc.title;
    }
    if (push && (location.pathname + location.search) !== normalizedTarget) {
      history.pushState({}, '', normalizedTarget);
    }
    const scroller = document.querySelector('[data-content-scroll], .app-main');
    scroller?.scrollTo({ top: 0, behavior: 'auto' });
    this.main?.focus({ preventScroll: true });
    document.dispatchEvent(new CustomEvent('recipe-share:page-loaded', { detail: { path: normalizedTarget } }));
  }

  async submitForm(form, actionUrl, submitter) {
    const submitBtn = submitter || form.querySelector('button[type="submit"], input[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    try {
      const formData = new FormData(form);
      if (submitter && submitter.name) {
        formData.set(submitter.name, submitter.value || '');
      }
      const csrfToken =
        formData.get('csrf_token') ||
        document.querySelector('meta[name="csrf-token"]')?.content ||
        window.recipeShareApi?.csrfToken;
      const headers = { 'X-Requested-With': 'XMLHttpRequest' };
      if (csrfToken) headers['X-CSRFToken'] = String(csrfToken);

      const response = await fetch(actionUrl.pathname + actionUrl.search, {
        method: 'POST',
        body: formData,
        headers,
        credentials: 'same-origin',
      });

      const htmlText = await response.text();
      const doc = new DOMParser().parseFromString(htmlText, 'text/html');
      const targetUrl = new URL(response.url || actionUrl.href, location.origin);
      const direction = this.transitionDirection(location.pathname, targetUrl.pathname);
      await this.applyDocumentResponse(doc, targetUrl.pathname + targetUrl.search, true, direction);
    } catch (_) {
      form.setAttribute('data-no-spa', 'true');
      form.submit();
    } finally {
      if (submitBtn && document.body.contains(submitBtn)) {
        submitBtn.disabled = false;
      }
    }
  }

  async navigate(path, push = true, direction = 'forward', sidebarNavigation = false) {
    try {
      const url = new URL(path, location.origin);
      const pathname = url.pathname === '/' ? '/' : url.pathname.replace(/\/$/, '') || '/';
      let fullPath = pathname + url.search;
      const apiPath = `/api/v1/ui/pages${pathname === '/' ? '/' : pathname}${url.search}`;
      const response = await window.recipeShareApi.request(apiPath);

      if (response.redirect_path) {
        fullPath = response.redirect_path;
      }

      const currentIsApp = document.body.classList.contains('app-shell');
      const nextIsApp = response.layout === 'app';

      if (currentIsApp !== nextIsApp) {
        const pageResp = await fetch(fullPath, { credentials: 'same-origin' });
        const htmlText = await pageResp.text();
        const doc = new DOMParser().parseFromString(htmlText, 'text/html');
        await this.applyDocumentResponse(doc, fullPath, push, direction);
        return;
      }

      this.main = document.querySelector('[data-spa-main]');
      const shouldAnimate =
        !sidebarNavigation &&
        !currentIsApp &&
        [
          '/login',
          '/register',
          '/verify-email',
          '/forgot-password',
          '/reset-password/verify',
          '/reset-password',
          '/',
          '/recipes',
          '/categories',
          '/locations',
        ].includes(pathname);
      if (shouldAnimate) await window.recipeShareAnimations?.leave(this.main, direction);
      this.main.innerHTML = response.html;
      window.recipeShareAnimations?.lockDrag(this.main);
      const isAuth = response.layout === 'auth';
      document.body.classList.toggle('spa-auth-view', isAuth);
      document.body.classList.toggle('auth-page', isAuth);
      document.title = response.title;
      if (push && (location.pathname + location.search) !== fullPath) {
        history.pushState({}, '', fullPath);
      }
      const scroller = document.querySelector('[data-content-scroll], .app-main');
      scroller?.scrollTo({ top: 0, behavior: 'auto' });
      this.main.focus({ preventScroll: true });
      if (shouldAnimate) await window.recipeShareAnimations?.slide(this.main, direction);
      document.dispatchEvent(new CustomEvent('recipe-share:page-loaded', { detail: { path: fullPath } }));
    } catch (_) {
      location.href = path;
    }
  }
}
window.spaRouter = new SpaRouter();
