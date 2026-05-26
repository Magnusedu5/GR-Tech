'use strict';

/* ============================================================
   GR TECH — main.js
   Shared across all pages.
============================================================ */

/* ——————————————————————————————————
   NAV: scroll state + light/dark mode + active link
—————————————————————————————————— */
const nav        = document.getElementById('nav');
const navLinks   = document.querySelectorAll('.nav-links a[data-section]');
const sections   = document.querySelectorAll('section[id]');

// Classes that mean the section has a light/cream background
const LIGHT_PANELS = ['panel-light', 'panel-light-alt'];

// Apply light/dark mode to nav based on a panel element
function applyNavTheme(el) {
  if (!nav || !el) return;
  const isLight = LIGHT_PANELS.some(c => el.classList.contains(c));
  nav.classList.toggle('light-mode', isLight);
}

// Scroll-based detection: find the panel element whose top is
// closest to (but not above) the nav's bottom edge.
function detectNavTheme() {
  if (!nav) return;
  const navBottom = nav.getBoundingClientRect().bottom;
  let best = null, bestTop = -Infinity;

  document.querySelectorAll('[class*="panel-"]').forEach(el => {
    // Skip fixed elements (e.g. mobile-menu overlay)
    if (window.getComputedStyle(el).position === 'fixed') return;
    const { top } = el.getBoundingClientRect();
    if (top <= navBottom && top > bestTop) { bestTop = top; best = el; }
  });

  applyNavTheme(best);
}

// IntersectionObserver: fires even when scroll events are throttled on mobile.
// Creates a 1px detection slice right at the nav's bottom edge.
function setupNavThemeObserver() {
  if (!nav) return;
  const h = nav.offsetHeight;
  const vp = window.innerHeight;
  const bottomMargin = Math.max(vp - h - 1, 0);
  const margin = `-${h}px 0px -${bottomMargin}px 0px`;

  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) applyNavTheme(entry.target);
    });
  }, { rootMargin: margin, threshold: 0 });

  document.querySelectorAll('[class*="panel-"]').forEach(el => {
    if (window.getComputedStyle(el).position !== 'fixed') obs.observe(el);
  });
}

// Scrolled border class + fallback scroll detection
window.addEventListener('scroll', () => {
  if (!nav) return;
  nav.classList.toggle('scrolled', window.scrollY > 40);
  detectNavTheme();
}, { passive: true });

// Run both on load
detectNavTheme();
setupNavThemeObserver();

// Active link via IntersectionObserver
if (sections.length && nav) {
  const sectionObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const id = entry.target.id;
      navLinks.forEach(a => a.classList.toggle('active', a.dataset.section === id));
    });
  }, { rootMargin: '-40% 0px -55% 0px', threshold: 0 });

  sections.forEach(s => sectionObs.observe(s));
}

/* ——————————————————————————————————
   MOBILE MENU
—————————————————————————————————— */
const hamburger  = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile-menu');

function toggleMenu(open) {
  hamburger?.classList.toggle('open', open);
  mobileMenu?.classList.toggle('open', open);
  hamburger?.setAttribute('aria-expanded', String(open));
  document.body.style.overflow = open ? 'hidden' : '';
}

hamburger?.addEventListener('click', () => {
  toggleMenu(!mobileMenu?.classList.contains('open'));
});

document.querySelectorAll('.mobile-link').forEach(a => {
  a.addEventListener('click', () => toggleMenu(false));
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && mobileMenu?.classList.contains('open')) {
    toggleMenu(false);
    hamburger?.focus();
  }
});

/* ——————————————————————————————————
   SCROLL-TRIGGERED ANIMATIONS
—————————————————————————————————— */
const animObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      animObs.unobserve(entry.target);
    }
  });
}, { rootMargin: '0px 0px -80px 0px', threshold: 0.08 });

document.querySelectorAll('.fade-up, .fade-in, .stagger').forEach(el => animObs.observe(el));

/* ——————————————————————————————————
   SMOOTH SCROLL (anchor links)
—————————————————————————————————— */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', e => {
    const href   = anchor.getAttribute('href');
    const target = href && href.length > 1 ? document.querySelector(href) : null;
    if (!target) return;
    e.preventDefault();
    const offset = nav?.offsetHeight || 72;
    const top    = target.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  });
});

/* ——————————————————————————————————
   CONTACT FORM
—————————————————————————————————— */
const API_BASE   = 'https://grtech-backend.onrender.com';
const form       = document.getElementById('contact-form');
const submitBtn  = document.getElementById('submit-btn');
const successMsg = document.getElementById('form-success');

if (form) {
  form.addEventListener('submit', async e => {
    e.preventDefault();

    const name        = form.querySelector('#name')?.value.trim();
    const email       = form.querySelector('#email')?.value.trim();
    const projectType = form.querySelector('#project-type')?.value;
    const message     = form.querySelector('#message')?.value.trim();
    const emailRe     = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!name)                           return shakeField(form.querySelector('#name'));
    if (!email || !emailRe.test(email))  return shakeField(form.querySelector('#email'));
    if (!projectType)                    return shakeField(form.querySelector('#project-type'));
    if (!message || message.length < 10) return shakeField(form.querySelector('#message'));

    if (submitBtn) {
      submitBtn.textContent   = 'Sending...';
      submitBtn.disabled      = true;
      submitBtn.style.opacity = '0.7';
    }

    try {
      const res = await fetch(`${API_BASE}/api/contact/`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          name,
          email,
          project_type: projectType,
          message,
        }),
      });

      if (res.ok) {
        if (submitBtn)  submitBtn.style.display  = 'none';
        if (successMsg) successMsg.style.display = 'block';
        form.reset();
      } else {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.errors ? JSON.stringify(data.errors) : 'Submission failed');
      }
    } catch (err) {
      if (submitBtn) {
        submitBtn.textContent   = 'Send Message';
        submitBtn.disabled      = false;
        submitBtn.style.opacity = '1';
      }
      alert('Something went wrong. Please try again or email us directly.');
      console.error(err);
    }
  });
}

function shakeField(el) {
  if (!el) return;
  el.style.borderColor = 'rgba(160, 50, 50, 0.65)';
  el.style.boxShadow   = '0 0 0 3px rgba(160,50,50,0.1)';

  const start = performance.now();
  (function step(now) {
    const p = (now - start) / 420;
    if (p < 1) {
      el.style.transform = `translateX(${Math.sin(p * Math.PI * 6) * 6 * (1 - p)}px)`;
      requestAnimationFrame(step);
    } else {
      el.style.transform = '';
    }
  })(start);

  setTimeout(() => { el.style.borderColor = ''; el.style.boxShadow = ''; }, 2200);
}

/* ——————————————————————————————————
   FAQ ACCORDION
—————————————————————————————————— */
document.querySelectorAll('.faq-item').forEach(item => {
  const q = item.querySelector('.faq-q');
  q?.addEventListener('click', () => {
    const wasOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
    if (!wasOpen) item.classList.add('open');
  });
});

/* ——————————————————————————————————
   PROJECT FILTER TABS
—————————————————————————————————— */
const filterTabs = document.querySelectorAll('.filter-tab');
const projCards  = document.querySelectorAll('.proj-card[data-cat]');

filterTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    filterTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const cat = tab.dataset.filter || 'all';
    projCards.forEach(card => {
      card.classList.toggle('hidden', cat !== 'all' && card.dataset.cat !== cat);
    });
  });
});

/* ——————————————————————————————————
   HERO PARALLAX
—————————————————————————————————— */
const heroGeo = document.querySelector('.hero-geo');
if (heroGeo) {
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y < window.innerHeight) {
      heroGeo.style.transform = `translateY(calc(-50% + ${(y / window.innerHeight) * 55}px))`;
    }
  }, { passive: true });
}

/* ——————————————————————————————————
   STAT COUNTER ANIMATION
—————————————————————————————————— */
const statNums = document.querySelectorAll('.stat-num[data-target]');
if (statNums.length) {
  const counterObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el     = entry.target;
      const target = parseInt(el.dataset.target, 10);
      const suffix = el.dataset.suffix || '';
      const dur    = 1400;
      const start  = performance.now();
      (function tick(now) {
        const p   = Math.min((now - start) / dur, 1);
        const val = Math.round(p * p * (3 - 2 * p) * target); // smooth step
        el.textContent = val + suffix;
        if (p < 1) requestAnimationFrame(tick);
      })(start);
      counterObs.unobserve(el);
    });
  }, { threshold: 0.5 });

  statNums.forEach(el => counterObs.observe(el));
}
