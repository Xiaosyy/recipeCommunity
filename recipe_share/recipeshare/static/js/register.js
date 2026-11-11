/**
 * RecipeShare - Registration Module (register.js)
 * Handles client-side validation for account registration:
 * - Minimum password length
 * - Password confirmation match
 * - Terms of Service agreement verification
 */

(() => {
  const evaluatePasswordRules = (value = '') => ({
    length: value.length >= 8,
    case: /[A-Z]/.test(value) && /[a-z]/.test(value),
    number: /\d/.test(value),
    special: /[^A-Za-z0-9\s]/.test(value),
  });

  const getPasswordErrorMessages = (value = '') => {
    const checks = evaluatePasswordRules(value);
    const messages = [];
    if (!checks.length) messages.push('At least 8 characters.');
    if (!checks.case) messages.push('Uppercase and lowercase letters.');
    if (!checks.number) messages.push('Contains numbers.');
    if (!checks.special) messages.push('Contains special characters.');
    return messages;
  };

  const initializeRegisterValidation = (root = document) => {
    const registerForm = root.querySelector('.auth-screen-register .auth-form:not([data-otp-form])');
    if (!registerForm || registerForm.dataset.registerInitialized === 'true') return;
    registerForm.dataset.registerInitialized = 'true';

    const usernameInput = registerForm.querySelector('#username');
    const emailInput = registerForm.querySelector('#email');
    const passwordInput = registerForm.querySelector('#password');
    const confirmInput = registerForm.querySelector('#password_confirmation');
    const agreementInput = registerForm.querySelector('[name="agreement"]');
    const checklist = registerForm.querySelector('[data-password-checklist]');
    const strengthFill = checklist?.querySelector('[data-password-strength-fill]');
    const strengthTrack = checklist?.querySelector('[data-password-strength-track]');
    const strengthLabel = checklist?.querySelector('[data-password-strength-label]');

    const updatePasswordChecklist = (value = '', showUnmet = false) => {
      if (!checklist) return;
      const hasInput = value.length > 0 || showUnmet;
      const checks = evaluatePasswordRules(value);
      let metCount = 0;

      Object.entries(checks).forEach(([ruleKey, isMet]) => {
        if (isMet) metCount += 1;
        const item = checklist.querySelector(`[data-password-rule="${ruleKey}"]`);
        if (!item) return;
        const icon = item.querySelector('.password-rule-icon');
        const markUnmet = hasInput && !isMet;
        item.classList.toggle('is-met', isMet);
        item.classList.toggle('is-unmet', markUnmet);
        if (icon) {
          icon.textContent = isMet ? '✓' : markUnmet ? '✕' : '';
        }
      });

      if (strengthFill) {
        strengthFill.classList.remove('is-weak', 'is-fair', 'is-good', 'is-strong');
      }
      if (!hasInput) {
        strengthTrack?.setAttribute('aria-valuenow', '0');
        if (strengthLabel) {
          strengthLabel.textContent = '';
        }
        return;
      }

      const levels = {
        0: { cls: 'is-weak', text: 'Weak', val: 1 },
        1: { cls: 'is-weak', text: 'Weak', val: 1 },
        2: { cls: 'is-fair', text: 'Fair', val: 2 },
        3: { cls: 'is-good', text: 'Good', val: 3 },
        4: { cls: 'is-strong', text: 'Strong', val: 4 },
      };
      const currentLevel = levels[metCount] || levels[0];
      strengthFill?.classList.add(currentLevel.cls);
      strengthTrack?.setAttribute('aria-valuenow', String(currentLevel.val));
      if (strengthLabel) {
        strengthLabel.textContent = currentLevel.text;
      }
    };

    const showFieldError = (input, message) => {
      const parent = input.closest('.input-with-icon') || input.parentElement;
      parent?.classList.add('has-error');
      let errorSpan = parent?.nextElementSibling?.classList.contains('field-error')
        ? parent.nextElementSibling
        : parent?.querySelector('.field-error');
      if (!errorSpan) {
        errorSpan = document.createElement('small');
        errorSpan.className = 'field-error';
        errorSpan.setAttribute('role', 'alert');
        parent?.after(errorSpan);
      }
      errorSpan.textContent = message;
    };

    const clearFieldError = (input) => {
      const parent = input.closest('.input-with-icon') || input.parentElement;
      parent?.classList.remove('has-error');
      const errorSpan = parent?.nextElementSibling?.classList.contains('field-error')
        ? parent.nextElementSibling
        : parent?.querySelector('.field-error');
      if (errorSpan) {
        errorSpan.textContent = '';
      }
    };

    usernameInput?.addEventListener('input', () => {
      const value = usernameInput.value.trim();
      if (!value || /^[A-Za-z0-9_]{3,30}$/.test(value)) {
        clearFieldError(usernameInput);
      }
    });

    emailInput?.addEventListener('input', () => {
      const value = emailInput.value.trim();
      if (!value || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        clearFieldError(emailInput);
      }
    });

    confirmInput?.addEventListener('input', () => {
      if (passwordInput && confirmInput.value && passwordInput.value !== confirmInput.value) {
        showFieldError(confirmInput, 'Passwords do not match');
      } else {
        clearFieldError(confirmInput);
      }
    });

    passwordInput?.addEventListener('input', () => {
      const value = passwordInput.value || '';
      updatePasswordChecklist(value, false);
      const issues = getPasswordErrorMessages(value);
      if (issues.length === 0 || !value) {
        clearFieldError(passwordInput);
      }
      if (confirmInput && confirmInput.value && value !== confirmInput.value) {
        showFieldError(confirmInput, 'Passwords do not match');
      } else if (confirmInput && confirmInput.value) {
        clearFieldError(confirmInput);
      }
    });

    registerForm.addEventListener('submit', event => {
      let valid = true;

      if (usernameInput) {
        const usernameVal = usernameInput.value.trim();
        if (!usernameVal || !/^[A-Za-z0-9_]{3,30}$/.test(usernameVal)) {
          showFieldError(usernameInput, 'Use 3 to 30 letters, numbers, or underscores.');
          valid = false;
        }
      }
      if (emailInput && !emailInput.value.trim()) {
        showFieldError(emailInput, 'Email address is required');
        valid = false;
      }
      if (passwordInput) {
        const value = passwordInput.value || '';
        updatePasswordChecklist(value, true);
        const issues = getPasswordErrorMessages(value);
        if (issues.length > 0) {
          if (!checklist) {
            showFieldError(passwordInput, issues.join(' '));
          }
          valid = false;
        }
      }
      if (confirmInput && passwordInput && passwordInput.value !== confirmInput.value) {
        showFieldError(confirmInput, 'Passwords do not match');
        valid = false;
      }
      if (agreementInput && !agreementInput.checked) {
        window.alert('Please accept the Terms of Service and Privacy Policy to continue.');
        valid = false;
      }

      if (!valid) {
        event.preventDefault();
      }
    });

    if (checklist?.dataset.passwordHasError === 'true') {
      updatePasswordChecklist(passwordInput?.value || '', true);
    }
  };

  const initializeOtpVerification = (root = document) => {
    const otpForm = root.querySelector('[data-otp-form]');
    if (!otpForm || otpForm.dataset.otpInitialized === 'true') return;
    otpForm.dataset.otpInitialized = 'true';

    const digitInputs = Array.from(otpForm.querySelectorAll('[data-otp-digit]'));
    const combinedInput = otpForm.querySelector('[data-otp-combined]');
    const digitGrid = otpForm.querySelector('.otp-digit-grid');
    const countdownEl = root.querySelector('[data-otp-countdown]');

    if (countdownEl) {
      let remaining = parseInt(countdownEl.dataset.otpCountdown || '60', 10);
      const timerId = window.setInterval(() => {
        if (!document.body.contains(countdownEl)) {
          window.clearInterval(timerId);
          return;
        }
        remaining = Math.max(0, remaining - 1);
        if (remaining > 0) {
          countdownEl.textContent = `${remaining}s`;
        } else {
          countdownEl.textContent = 'Expired';
          countdownEl.classList.add('is-expired');
          window.clearInterval(timerId);
        }
      }, 1000);
    }

    const syncCombinedCode = () => {
      const code = digitInputs.map(input => input.value.replace(/\D/g, '')).join('');
      if (combinedInput) {
        combinedInput.value = code;
      }
      digitInputs.forEach(input => {
        input.classList.toggle('is-filled', Boolean(input.value));
      });
      if (code.length === 6) {
        digitGrid?.classList.remove('has-error');
        otpForm.querySelector('.otp-field-error')?.remove();
      }
      return code;
    };

    const fillDigits = (rawString) => {
      const digits = String(rawString || '').replace(/\D/g, '').slice(0, 6).split('');
      digitInputs.forEach((input, index) => {
        input.value = digits[index] || '';
      });
      syncCombinedCode();
      const focusIndex = Math.min(digits.length, digitInputs.length - 1);
      digitInputs[focusIndex]?.focus();
    };

    // Device Gmail Sync & Push Notification Auto-fill Controller
    const deviceBanner = root.querySelector('[data-device-gmail-banner]');
    const toast = root.querySelector('[data-otp-toast]');
    const targetEmail = (deviceBanner?.dataset.targetEmail || toast?.dataset.otpTargetEmail || '').trim().toLowerCase();
    const isGmailAccount = targetEmail.endsWith('@gmail.com');

    const getDeviceGmail = () => {
      try {
        const stored = (localStorage.getItem('recipe_device_gmail_account') || '').trim().toLowerCase();
        if (stored) return stored;
        const match = document.cookie.match(/(?:^|;\s*)device_gmail_account=([^;]+)/);
        return match ? decodeURIComponent(match[1]).trim().toLowerCase() : '';
      } catch (e) {
        return '';
      }
    };

    const setDeviceGmail = (email) => {
      try {
        if (email) {
          localStorage.setItem('recipe_device_gmail_account', email);
          document.cookie = `device_gmail_account=${encodeURIComponent(email)}; path=/; max-age=2592000; SameSite=Lax`;
        } else {
          localStorage.removeItem('recipe_device_gmail_account');
          document.cookie = 'device_gmail_account=; path=/; max-age=0; SameSite=Lax';
        }
      } catch (e) {}
    };

    const updateDeviceGmailUI = (isLoggedIn) => {
      if (deviceBanner) {
        const disconnectedView = deviceBanner.querySelector('[data-device-gmail-disconnected]');
        const connectedView = deviceBanner.querySelector('[data-device-gmail-connected]');
        const emailLabel = deviceBanner.querySelector('[data-device-gmail-email]');

        if (isLoggedIn) {
          if (disconnectedView) disconnectedView.hidden = true;
          if (connectedView) connectedView.hidden = false;
          if (emailLabel) emailLabel.textContent = targetEmail;
        } else {
          if (disconnectedView) disconnectedView.hidden = false;
          if (connectedView) connectedView.hidden = true;
        }
      }

      if (toast) {
        if (isLoggedIn) {
          toast.style.display = '';
          toast.classList.remove('is-hiding');
        } else {
          toast.style.display = 'none';
        }
      }
    };

    // Only active if target email is a Gmail address and logged in on this device
    const currentDeviceGmail = getDeviceGmail();
    let isDeviceGmailActive = isGmailAccount && (currentDeviceGmail === targetEmail);

    updateDeviceGmailUI(isDeviceGmailActive);

    if (deviceBanner) {
      deviceBanner.addEventListener('click', event => {
        const btn = event.target.closest('[data-device-gmail-btn]');
        if (!btn) return;
        event.preventDefault();
        const action = btn.dataset.deviceGmailBtn;
        if (action === 'login') {
          setDeviceGmail(targetEmail);
          isDeviceGmailActive = true;
          updateDeviceGmailUI(true);
        } else if (action === 'logout') {
          setDeviceGmail('');
          isDeviceGmailActive = false;
          updateDeviceGmailUI(false);
        }
      });
    }

    // OTP Push Notification Toast Controller
    if (toast) {
      const autofillBtn = toast.querySelector('[data-otp-autofill]');
      const closeBtn = toast.querySelector('[data-otp-toast-close]');
      const toastCountdown = toast.querySelector('[data-otp-toast-countdown]');
      const codeBadge = toast.querySelector('[data-otp-code]');
      const rawCode = autofillBtn?.dataset.otpAutofill || codeBadge?.dataset.otpCode || '';

      const dismissToast = () => {
        toast.classList.add('is-hiding');
        window.setTimeout(() => {
          if (toast && toast.parentNode) toast.parentNode.removeChild(toast);
        }, 260);
      };

      closeBtn?.addEventListener('click', event => {
        event.stopPropagation();
        dismissToast();
      });

      autofillBtn?.addEventListener('click', event => {
        event.preventDefault();
        event.stopPropagation();
        if (!isDeviceGmailActive) {
          window.alert('Auto-fill is only available when your Gmail account is logged in on this device.');
          return;
        }
        if (rawCode) {
          fillDigits(rawCode);
          autofillBtn.innerHTML = '<span class="otp-toast-icon">✓</span><span>Code Entered!</span>';
          autofillBtn.style.background = '#09583e';
          window.setTimeout(dismissToast, 1100);
        }
      });

      codeBadge?.addEventListener('click', event => {
        event.preventDefault();
        event.stopPropagation();
        if (rawCode) fillDigits(rawCode);
      });

      if (toastCountdown) {
        let toastRemaining = parseInt(toastCountdown.textContent || '60', 10);
        const toastTimer = window.setInterval(() => {
          if (!document.body.contains(toast)) {
            window.clearInterval(toastTimer);
            return;
          }
          toastRemaining = Math.max(0, toastRemaining - 1);
          if (toastRemaining > 0) {
            toastCountdown.textContent = `${toastRemaining}s`;
          } else {
            toastCountdown.textContent = 'Expired';
            window.clearInterval(toastTimer);
            dismissToast();
          }
        }, 1000);
      }
    }

    digitInputs.forEach((input, index) => {
      input.addEventListener('input', event => {
        const sanitized = event.target.value.replace(/\D/g, '');
        if (sanitized.length > 1) {
          fillDigits(sanitized);
          return;
        }
        event.target.value = sanitized;
        syncCombinedCode();
        if (sanitized && index < digitInputs.length - 1) {
          digitInputs[index + 1].focus();
          digitInputs[index + 1].select();
        }
      });

      input.addEventListener('keydown', event => {
        if (event.key === 'Backspace' && !input.value && index > 0) {
          digitInputs[index - 1].value = '';
          syncCombinedCode();
          digitInputs[index - 1].focus();
        } else if (event.key === 'ArrowLeft' && index > 0) {
          event.preventDefault();
          digitInputs[index - 1].focus();
        } else if (event.key === 'ArrowRight' && index < digitInputs.length - 1) {
          event.preventDefault();
          digitInputs[index + 1].focus();
        }
      });

      input.addEventListener('paste', event => {
        const pasted = event.clipboardData?.getData('text') || '';
        const digits = pasted.replace(/\D/g, '');
        if (digits) {
          event.preventDefault();
          fillDigits(digits);
        }
      });

      input.addEventListener('focus', () => input.select());
    });

    otpForm.addEventListener('submit', event => {
      const code = syncCombinedCode();
      if (code.length !== 6) {
        event.preventDefault();
        digitGrid?.classList.add('has-error');
        let errorEl = otpForm.querySelector('.otp-field-error');
        if (!errorEl) {
          errorEl = document.createElement('small');
          errorEl.className = 'field-error otp-field-error';
          errorEl.setAttribute('role', 'alert');
          digitGrid?.after(errorEl);
        }
        errorEl.textContent = 'Please enter all 6 digits of your verification code.';
        const firstEmpty = digitInputs.find(input => !input.value) || digitInputs[0];
        firstEmpty?.focus();
      }
    });

    digitInputs[0]?.focus();
  };

  const initRegister = (root = document) => {
    initializeRegisterValidation(root);
    initializeOtpVerification(root);
  };

  window.recipeShareRegister = { init: initRegister };

  document.addEventListener('DOMContentLoaded', () => initRegister(document));
  document.addEventListener('recipe-share:page-loaded', () => initRegister(document));
})();

