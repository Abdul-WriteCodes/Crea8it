/* Crea8it supporter registry.
   Add only confirmed partnerships with permission to show their name/logo.
   Example:
   { name: 'Example Organisation', category: 'Scholarship Sponsor', logo: 'assets/sponsors/example.svg', url: 'https://example.org', contribution: 'Supported 10 learners' }
   Place assets in assets/sponsors/. Never store untrusted HTML in this registry. */
window.CREA8IT_SPONSORS = [];
(function () {
  'use strict';
  var items = window.CREA8IT_SPONSORS;
  var wall = document.getElementById('sponsor-wall');
  var empty = document.getElementById('sponsor-empty');
  if (!wall || !empty) return;
  if (!Array.isArray(items) || !items.length) { wall.hidden = true; empty.hidden = false; return; }
  items.forEach(function (s) {
    if (!s || !s.name || !s.logo) return;
    var card = document.createElement('article'); card.className = 'sponsor-logo-card';
    var picture = document.createElement('img'); picture.src = s.logo; picture.alt = s.name + ' logo'; picture.loading = 'lazy'; picture.decoding = 'async';
    var name = document.createElement('h3'); name.textContent = s.name;
    var cat = document.createElement('p'); cat.textContent = s.category || 'Crea8it Supporter';
    var body = document.createElement('div'); body.appendChild(name); body.appendChild(cat);
    if (s.contribution) { var note = document.createElement('small'); note.textContent = s.contribution; body.appendChild(note); }
    if (typeof s.url === 'string' && /^https:\/\//i.test(s.url)) {
      var link = document.createElement('a'); link.href = s.url; link.target = '_blank'; link.rel = 'noopener noreferrer'; link.setAttribute('aria-label', 'Visit ' + s.name + ' website'); link.appendChild(picture); link.appendChild(body); card.appendChild(link);
    } else { card.appendChild(picture); card.appendChild(body); }
    wall.appendChild(card);
  });
  if (!wall.children.length) { wall.hidden = true; empty.hidden = false; }
})();
