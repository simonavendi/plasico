/**
 * Shared auth modal (Здравей! / email / Продължи / social).
 * Opens via [data-open-auth-modal]. Injects markup + CSS when missing.
 */
(function initAuthModal() {
  if (window.__plasicoAuthModalInit) return;
  window.__plasicoAuthModalInit = true;

  const scriptEl = document.currentScript;
  const assetBase = scriptEl?.src ? scriptEl.src.replace(/[^/]+$/, '') : '';

  const MODAL_HTML = `
  <div class="auth-modal" id="auth-modal" hidden aria-hidden="true">
    <div class="auth-modal__backdrop" data-auth-close tabindex="-1"></div>
    <div class="auth-modal__dialog" role="dialog" aria-modal="true" aria-labelledby="auth-modal-title" tabindex="-1">
      <button type="button" class="auth-modal__close" data-auth-close aria-label="Затвори">
        <span class="material-symbols-outlined" aria-hidden="true">close</span>
      </button>
      <h2 class="auth-modal__greeting" id="auth-modal-title">Здравей!</h2>
      <form class="auth-modal__form" id="auth-modal-form" novalidate>
        <label class="auth-modal__label" for="auth-email">Моля въведи имейл адрес</label>
        <input id="auth-email" name="auth_email" type="email" class="auth-modal__input" autocomplete="email" placeholder="name@email.com" required/>
        <button type="submit" class="auth-modal__continue">Продължи</button>
      </form>
      <p class="auth-modal__help">Нямаш акаунт? Не се тревожи! Можеш да си създадеш в следващата стъпка.</p>
      <div class="auth-modal__divider" role="separator">
        <span class="auth-modal__divider-line" aria-hidden="true"></span>
        <span class="auth-modal__divider-or">или</span>
        <span class="auth-modal__divider-line" aria-hidden="true"></span>
      </div>
      <p class="auth-modal__social-hint">използвайте твоя социален акаунт</p>
      <div class="auth-modal__socials">
        <button type="button" class="auth-social auth-social--facebook" data-auth-social="Facebook">
          <span class="auth-social__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H7v3h3v7h3v-7h3l1-3h-4v-2c0-.6.4-1 1-1z"/></svg>
          </span>
          <span class="auth-social__label">Facebook</span>
        </button>
        <button type="button" class="auth-social auth-social--google" data-auth-social="Google">
          <span class="auth-social__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 11v2.4h5.5c-.2 1.3-1.6 3.9-5.5 3.9-3.3 0-6-2.7-6-6s2.7-6 6-6c1.9 0 3.1.8 3.8 1.5l2.6-2.5C16.7 2.7 14.6 1.7 12 1.7 6.9 1.7 2.7 5.9 2.7 11S6.9 20.3 12 20.3c6.9 0 8.5-4.8 8.5-7.3 0-.5 0-.8-.1-1.2H12z"/></svg>
          </span>
          <span class="auth-social__label">Google</span>
        </button>
        <button type="button" class="auth-social auth-social--apple" data-auth-social="Apple">
          <span class="auth-social__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M16.4 12.6c0-1.7.9-3.2 2.3-4.1-.9-1.3-2.3-2.1-3.9-2.2-1.6-.2-3.3.9-3.9.9-.7 0-2.1-.9-3.4-.8-1.8.1-3.4 1-4.3 2.6-1.8 3.2-.5 7.9 1.3 10.5.9 1.3 1.9 2.7 3.3 2.6 1.3-.1 1.8-.8 3.4-.8s2 .8 3.4.8c1.4 0 2.3-1.3 3.2-2.6.6-.9 1.1-1.9 1.4-2.9-1.7-.6-2.8-2.3-2.8-4zM13.9 5.1c.7-.9 1.2-2.1 1.1-3.3-1.1.1-2.4.7-3.1 1.6-.7.8-1.3 2.1-1.1 3.3 1.2.1 2.4-.6 3.1-1.6z"/></svg>
          </span>
          <span class="auth-social__label">Apple</span>
        </button>
      </div>
    </div>
  </div>`;

  function ensureStyles() {
    if (document.querySelector('link[data-auth-modal-css], link[href*="auth-modal.css"]')) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `${assetBase}auth-modal.css`;
    link.setAttribute('data-auth-modal-css', '');
    document.head.appendChild(link);
  }

  function ensureModal() {
    let modal = document.getElementById('auth-modal');
    if (modal) return modal;
    const wrap = document.createElement('div');
    wrap.innerHTML = MODAL_HTML.trim();
    modal = wrap.firstElementChild;
    document.body.appendChild(modal);
    return modal;
  }

  ensureStyles();
  const authModal = ensureModal();
  const authEmail = document.getElementById('auth-email');
  const authForm = document.getElementById('auth-modal-form');
  let authLastFocus = null;
  let wired = false;

  function openAuthModal() {
    if (!authModal) return;
    window.__closeHeaderCategories?.();
    window.__closeHeaderCategoriesPanel?.();
    window.__closeCartDrawer?.();
    authLastFocus = document.activeElement;
    authModal.hidden = false;
    authModal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('auth-modal-open');
    window.setTimeout(() => {
      (authEmail || authModal.querySelector('.auth-modal__dialog'))?.focus?.();
    }, 20);
  }

  function closeAuthModal() {
    if (!authModal || authModal.hidden) return;
    authModal.hidden = true;
    authModal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('auth-modal-open');
    if (authLastFocus && typeof authLastFocus.focus === 'function') {
      authLastFocus.focus();
    }
  }

  function wireOnce() {
    if (wired || !authModal) return;
    wired = true;

    authModal.querySelectorAll('[data-auth-close]').forEach((el) => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        closeAuthModal();
      });
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !authModal.hidden) {
        e.preventDefault();
        closeAuthModal();
      }
    });

    authForm?.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = (authEmail?.value || '').trim();
      window.alert(email ? `Продължи с ${email} (демо)` : 'Моля въведи имейл адрес (демо)');
    });

    authModal.querySelectorAll('[data-auth-social]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const provider = btn.getAttribute('data-auth-social') || 'социален акаунт';
        window.alert(`Вход с ${provider} (демо)`);
      });
    });
  }

  wireOnce();

  document.addEventListener('click', (e) => {
    const trigger = e.target?.closest?.('[data-open-auth-modal]');
    if (!trigger) return;
    e.preventDefault();
    openAuthModal();
  });

  window.__openAuthModal = openAuthModal;
  window.__closeAuthModal = closeAuthModal;
})();
