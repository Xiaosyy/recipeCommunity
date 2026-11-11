/**
 * RecipeShare - Login Module (login.js)
 * Handles login screen password visibility toggle, client-side validation,
 * social auth buttons, and remember-me persistence.
 */

(() => {
  const initializePasswordToggles = (root = document) => {
    root.querySelectorAll('.auth-screen-login .password-toggle, .auth-screen .password-toggle, .forgot-password-stage .password-toggle').forEach(button => {
      if (button.dataset.loginInitialized === 'true') return;
      button.dataset.loginInitialized = 'true';

      button.addEventListener('click', event => {
        event.preventDefault();
        const targetId = button.getAttribute('aria-controls');
        const input = document.getElementById(targetId) || button.previousElementSibling;
        if (!input) return;

        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        button.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
        button.textContent = isPassword ? '○' : '◉';
        input.focus();
      });
    });
  };

  const initializeSocialAuthButtons = (root = document) => {
    root.querySelectorAll('.auth-screen [data-provider]').forEach(button => {
      if (button.dataset.providerInitialized === 'true') return;
      button.dataset.providerInitialized = 'true';

      button.addEventListener('click', event => {
        event.preventDefault();
        const provider = button.dataset.provider || 'Social';
        const formattedProvider = provider.charAt(0).toUpperCase() + provider.slice(1);
        window.alert(`${formattedProvider} sign-in is not configured yet.`);
      });
    });
  };

  const initializeLoginFormValidation = (root = document) => {
    const loginForm = root.querySelector('.auth-screen-login .auth-form');
    if (!loginForm || loginForm.dataset.validationInitialized === 'true') return;
    loginForm.dataset.validationInitialized = 'true';

    loginForm.addEventListener('submit', event => {
      const emailOrUser = loginForm.querySelector('[name="email_or_username"]');
      const password = loginForm.querySelector('[name="password"]');

      let hasError = false;
      [emailOrUser, password].forEach(field => {
        if (!field) return;
        const parent = field.closest('.input-with-icon');
        if (!field.value.trim()) {
          parent?.classList.add('has-error');
          hasError = true;
        } else {
          parent?.classList.remove('has-error');
        }
      });

      if (hasError) {
        event.preventDefault();
      }
    });

    loginForm.querySelectorAll('input').forEach(input => {
      input.addEventListener('input', () => {
        const parent = input.closest('.input-with-icon');
        if (input.value.trim()) {
          parent?.classList.remove('has-error');
        }
      });
    });
  };

  const initLogin = (root = document) => {
    initializePasswordToggles(root);
    initializeSocialAuthButtons(root);
    initializeLoginFormValidation(root);
  };

  window.recipeShareLogin = { init: initLogin };

  document.addEventListener('DOMContentLoaded', () => initLogin(document));
  document.addEventListener('recipe-share:page-loaded', () => initLogin(document));
})();

