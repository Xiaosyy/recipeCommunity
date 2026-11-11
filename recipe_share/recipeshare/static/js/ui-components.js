document.addEventListener('DOMContentLoaded', () => {
  const setupComponents = () => {
    document.querySelectorAll('img, [draggable]').forEach(element => element.setAttribute('draggable', 'false'));
    document.querySelectorAll('[data-ui-dropdown]').forEach(dropdown => {
      if (dropdown.dataset.dropdownInitialized) return;
      dropdown.dataset.dropdownInitialized = 'true';
      dropdown.querySelector(':scope > summary')?.addEventListener('click', event => {
        event.preventDefault();
        if (dropdown.open) {
          dropdown.classList.add('is-closing');
          window.setTimeout(() => { dropdown.removeAttribute('open'); dropdown.classList.remove('is-closing'); }, 160);
        } else {
          document.querySelectorAll('[data-ui-dropdown][open]').forEach(openDropdown => {
            if (openDropdown !== dropdown) openDropdown.removeAttribute('open');
          });
          dropdown.setAttribute('open', '');
        }
      });
    });
    const scroller = document.querySelector('[data-content-scroll]');
    const scrollButton = document.querySelector('[data-scroll-to-top]');
    if (scroller && scrollButton && scroller.dataset.scrollInitialized !== 'true') {
      scroller.dataset.scrollInitialized = 'true';
      scroller.addEventListener('scroll', () => scrollButton.classList.toggle('is-visible', scroller.scrollTop > 300), { passive: true });
      scrollButton.addEventListener('click', () => scroller.scrollTo({ top: 0, behavior: 'smooth' }));
    }
    document.querySelectorAll('.ui-tabs').forEach(tabs => tabs.addEventListener('click', event => {
      const tab = event.target.closest('.ui-tab');
      if (!tab) return;
      tabs.querySelectorAll('.ui-tab').forEach(item => { item.classList.toggle('is-active', item === tab); item.setAttribute('aria-selected', String(item === tab)); });
    }));
    document.querySelectorAll('[data-location-action]').forEach(button => button.addEventListener('click', () => {
      if (!navigator.geolocation) return;
      navigator.geolocation.getCurrentPosition(() => {
        button.textContent = 'Location enabled';
        button.disabled = true;
      }, () => { button.textContent = 'Allow location or enter manually'; });
    }));
  };
  setupComponents();
  document.addEventListener('recipe-share:page-loaded', setupComponents);
  document.addEventListener('click', event => {
    if (event.target instanceof Element && event.target.closest('[data-ui-dropdown]')) return;
    document.querySelectorAll('[data-ui-dropdown][open]').forEach(dropdown => dropdown.removeAttribute('open'));
  });
});
