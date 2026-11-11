class RecipeShareAnimations {
  constructor() { this.duration = 360; }
  async slide(element, direction = 'forward') {
    if (!element || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const fromLeft = direction === 'back';
    await element.animate([
      { opacity: 0, transform: `translateX(${fromLeft ? '-32px' : '32px'})` },
      { opacity: 1, transform: 'translateX(0)' }
    ], { duration: this.duration, easing: 'cubic-bezier(.2,.75,.25,1)' }).finished.catch(() => {});
  }
  async leave(element, direction = 'forward') {
    if (!element || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const toLeft = direction === 'forward';
    await element.animate([
      { opacity: 1, transform: 'translateX(0)' },
      { opacity: 0, transform: `translateX(${toLeft ? '-24px' : '24px'})` }
    ], { duration: this.duration, easing: 'cubic-bezier(.4,0,.8,.2)' }).finished.catch(() => {});
  }
  async pageTransition(element, direction = 'forward') {
    await this.leave(element, direction);
    await this.slide(element, direction);
  }
  lockDrag(root) {
    if (!root) return;
    root.setAttribute('draggable', 'false');
    root.querySelectorAll('img, a').forEach(node => node.setAttribute('draggable', 'false'));
    if (root.dataset.dragLocked !== 'true') {
      root.dataset.dragLocked = 'true';
      root.addEventListener('dragstart', event => event.preventDefault(), { passive: false });
    }
  }
}
window.recipeShareAnimations = new RecipeShareAnimations();
