// Just Water Solution: page behaviour (no dependencies)
(function () {
  var BUSINESS_EMAIL = 'justwatersolution@yahoo.com';

  // Header shadow once the page scrolls
  var header = document.querySelector('.header');
  function onScroll() { header.classList.toggle('is-scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  var menuBtn = document.querySelector('.menu-btn');
  var menuIcon = menuBtn.querySelector('use');
  function setMenu(open) {
    header.classList.toggle('is-open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    menuIcon.setAttribute('href', open ? '#i-x' : '#i-menu');
  }
  menuBtn.addEventListener('click', function () { setMenu(!header.classList.contains('is-open')); });
  document.querySelectorAll('.mobile-nav a').forEach(function (a) {
    a.addEventListener('click', function () { setMenu(false); });
  });

  // Reveal on scroll
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealEls.forEach(function (el, i) {
      // stagger siblings inside the same grid
      var idx = Array.prototype.indexOf.call(el.parentNode.children, el);
      el.style.transitionDelay = Math.min(idx, 5) * 70 + 'ms';
      io.observe(el);
    });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-in'); });
  }

  // How it works: link pins on the photo with the numbered steps
  var pins = document.querySelectorAll('.pin');
  var steps = document.querySelectorAll('.step');
  function activate(n) {
    pins.forEach(function (p) { p.classList.toggle('is-active', p.dataset.step === n); });
    steps.forEach(function (s) { s.classList.toggle('is-active', s.dataset.step === n); });
  }
  pins.forEach(function (p) {
    p.addEventListener('click', function () { activate(p.dataset.step); });
    p.addEventListener('mouseenter', function () { activate(p.dataset.step); });
  });
  steps.forEach(function (s) {
    s.addEventListener('mouseenter', function () { activate(s.dataset.step); });
    s.addEventListener('click', function () { activate(s.dataset.step); });
  });
  activate('1');

  // Gallery lightbox
  var shots = Array.prototype.slice.call(document.querySelectorAll('.shot'));
  var lb = document.getElementById('lightbox');
  var lbImg = lb.querySelector('img');
  var lbCount = lb.querySelector('.lb-count');
  var current = 0;
  function show(i) {
    current = (i + shots.length) % shots.length;
    var shot = shots[current];
    lbImg.src = shot.dataset.full;
    lbImg.alt = shot.querySelector('img').alt;
    lbCount.textContent = (current + 1) + ' / ' + shots.length;
  }
  shots.forEach(function (shot, i) {
    shot.addEventListener('click', function () {
      show(i);
      if (typeof lb.showModal === 'function') lb.showModal(); else window.open(shot.dataset.full, '_blank');
    });
  });
  lb.querySelector('.lb-close').addEventListener('click', function () { lb.close(); });
  lb.querySelector('.lb-prev').addEventListener('click', function () { show(current - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function () { show(current + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) lb.close(); });
  lb.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });

  // Quote form: until a form service is connected, compose the request as an email
  var form = document.getElementById('quote-form');
  var status = form.querySelector('.form-status');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var missing = Array.prototype.filter.call(form.querySelectorAll('[required]'), function (f) {
      return !f.value.trim();
    });
    if (missing.length) {
      status.textContent = 'Please fill in your name, phone and address.';
      missing[0].focus();
      return;
    }
    var d = new FormData(form);
    var name = (d.get('first') + ' ' + d.get('last')).trim();
    var body = [
      'Name: ' + name,
      'Phone: ' + d.get('phone'),
      'Email: ' + (d.get('email') || ''),
      'Address: ' + d.get('address'),
      'Water source: ' + d.get('source'),
      '',
      d.get('message') || ''
    ].join('\n');
    var href = 'mailto:' + BUSINESS_EMAIL +
      '?subject=' + encodeURIComponent('Quote request from ' + name) +
      '&body=' + encodeURIComponent(body);
    status.textContent = 'Opening your email app...';
    window.location.href = href;
  });

  document.getElementById('year').textContent = new Date().getFullYear();
})();
