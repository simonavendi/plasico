(function () {
  'use strict';

  /* ── Hero carousel ── */
  function initHeroCarousel() {
    const root = document.getElementById('home-hero-carousel');
    if (!root) return;

    const slides = Array.from(root.querySelectorAll('.home-hero__slide'));
    const dots = Array.from(document.querySelectorAll('.home-hero__dot'));
    const prevBtn = document.getElementById('home-hero-prev');
    const nextBtn = document.getElementById('home-hero-next');
    if (!slides.length) return;

    let index = slides.findIndex((s) => s.classList.contains('is-active'));
    if (index < 0) index = 0;

    let timer = null;
    const INTERVAL = 5000;
    let paused = false;

    function setSlide(i) {
      index = ((i % slides.length) + slides.length) % slides.length;
      slides.forEach((slide, idx) => {
        const active = idx === index;
        slide.classList.toggle('is-active', active);
        slide.setAttribute('aria-hidden', active ? 'false' : 'true');
      });
      dots.forEach((dot, idx) => {
        const active = idx === index;
        dot.classList.toggle('is-active', active);
        dot.setAttribute('aria-selected', active ? 'true' : 'false');
      });
    }

    function next() {
      setSlide(index + 1);
    }

    function prev() {
      setSlide(index - 1);
    }

    function startAutoplay() {
      stopAutoplay();
      if (paused || slides.length < 2) return;
      timer = window.setInterval(next, INTERVAL);
    }

    function stopAutoplay() {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
    }

    prevBtn?.addEventListener('click', () => {
      prev();
      startAutoplay();
    });

    nextBtn?.addEventListener('click', () => {
      next();
      startAutoplay();
    });

    dots.forEach((dot, idx) => {
      dot.addEventListener('click', () => {
        setSlide(idx);
        startAutoplay();
      });
    });

    root.addEventListener('mouseenter', () => {
      paused = true;
      stopAutoplay();
    });

    root.addEventListener('mouseleave', () => {
      paused = false;
      startAutoplay();
    });

    root.addEventListener('focusin', () => {
      paused = true;
      stopAutoplay();
    });

    root.addEventListener('focusout', (e) => {
      if (!root.contains(e.relatedTarget)) {
        paused = false;
        startAutoplay();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (!root.matches(':hover') && document.activeElement?.closest('#home-hero') == null) return;
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prev();
        startAutoplay();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        next();
        startAutoplay();
      }
    });

    setSlide(index);
    startAutoplay();
  }

  /* ── Newsletter mock ── */
  function initNewsletter() {
    const form = document.getElementById('home-newsletter-form');
    const msg = document.getElementById('home-newsletter-msg');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = form.querySelector('input[type="email"]');
      if (msg) {
        msg.textContent = input?.value
          ? 'Благодарим! Ще ви уведомим за следващите промоции.'
          : 'Моля, въведете имейл адрес.';
      }
      if (input?.value) form.reset();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initHeroCarousel();
      initNewsletter();
    });
  } else {
    initHeroCarousel();
    initNewsletter();
  }
})();
