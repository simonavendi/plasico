(function forceLightTheme() {
  const STORAGE_KEY = 'plasico-theme';
  const FAV_STORAGE_KEY = 'plasico-hss2026-favs';
  const root = document.documentElement;

  function applyLight() {
    try {
      localStorage.setItem(STORAGE_KEY, 'light');
    } catch (_) {
      /* ignore quota / private mode */
    }
    root.setAttribute('data-theme', 'light');
    root.classList.remove('dark');
  }

  function syncFavBadge() {
    const badge = document.getElementById('header-fav-badge');
    if (!badge) return;
    let count = 0;
    try {
      const raw = localStorage.getItem(FAV_STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      count = Array.isArray(parsed) ? parsed.length : 0;
    } catch (_) {
      count = 0;
    }
    badge.textContent = String(count);
    badge.classList.toggle('is-empty', count === 0);
    badge.setAttribute('aria-hidden', count === 0 ? 'true' : 'false');
  }

  applyLight();
  syncFavBadge();

  window.plasicoTheme = {
    apply: () => applyLight(),
    get: () => 'light',
  };
})();
