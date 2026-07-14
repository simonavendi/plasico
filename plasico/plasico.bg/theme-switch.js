(function () {
  const STORAGE_KEY = 'plasico-theme';

  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
    if (window.matchMedia('(prefers-color-scheme: light)').matches) return 'light';
    return 'dark';
  }

  function applyTheme(theme) {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    root.classList.toggle('dark', theme === 'dark');
    const btn = document.getElementById('theme-toggle');
    if (btn) {
      const label = theme === 'dark' ? 'Светла тема' : 'Тъмна тема';
      btn.setAttribute('aria-label', label);
      btn.setAttribute('title', label);
    }
  }

  function init() {
    let theme = document.documentElement.getAttribute('data-theme');
    if (theme !== 'light' && theme !== 'dark') {
      theme = getPreferredTheme();
    }
    applyTheme(theme);

    document.getElementById('theme-toggle')?.addEventListener('click', () => {
      const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      localStorage.setItem(STORAGE_KEY, next);
      applyTheme(next);
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(STORAGE_KEY)) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.plasicoTheme = {
    apply: applyTheme,
    get: () => document.documentElement.getAttribute('data-theme'),
  };
})();
