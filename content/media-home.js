(function () {
  'use strict';
  var data = window.POI_DAYS_MEDIA;
  var panel = document.getElementById('ranking-panel');
  var tablist = document.querySelector('.ranking-tabs');
  var disclosure = document.getElementById('ranking-disclosure');
  function element(tag, className, text) {
    var node = document.createElement(tag); node.className = className || '';
    if (text != null) node.textContent = String(text);
    return node;
  }
  function safeLocal(value) {
    if (typeof value !== 'string' || !value || /^[\s/#?]/.test(value) || /[\\:]|\.\./.test(value)) return null;
    try { var url = new URL(value, location.href); return url.origin === location.origin ? value : null; } catch (_) { return null; }
  }
  function empty(message) { return element('p', 'empty-state', message || '現在準備中です。'); }
  function rankingMeta(siteId) {
    return data && data.rankingMeta && data.rankingMeta[siteId] ? data.rankingMeta[siteId] : {};
  }
  function updateDisclosure(siteId) {
    if (!disclosure) return;
    var meta = rankingMeta(siteId);
    if (meta.checkedAt) {
      disclosure.textContent = meta.checkedAt + ' 取得 · 各ポイントサイトの公開ランキング';
      if (meta.stale) disclosure.textContent += '（前回取得分）';
    } else {
      disclosure.textContent = 'サンプル表示 · 自動取得は本番反映前です。';
    }
  }
  function selectSite(button) {
    var buttons = tablist.querySelectorAll('button');
    for (var j = 0; j < buttons.length; j++) {
      var selected = buttons[j] === button;
      buttons[j].setAttribute('aria-selected', String(selected)); buttons[j].tabIndex = selected ? 0 : -1;
    }
    var siteId = button.getAttribute('data-site');
    panel.setAttribute('aria-labelledby', button.id); panel.removeAttribute('aria-label');
    updateDisclosure(siteId);
    var rows = data.rankings && data.rankings[siteId];
    panel.textContent = '';
    if (!Array.isArray(rows) || !rows.length) { panel.appendChild(empty()); return; }
    var list = element('ol', 'ranking-list');
    rows.slice(0, 5).forEach(function (row, index) {
      if (!row || typeof row.title !== 'string' || !row.title.trim()) return;
      var li = element('li', 'ranking-row');
      li.appendChild(element('span', 'rank-number', index + 1));
      var img = element('img', 'rank-thumb'); img.width = 42; img.height = 42;
      img.alt = 'ランキング掲載案件のイメージ'; img.src = safeLocal(row.image) || 'visuals/about.svg'; li.appendChild(img);
      var description = element('div', 'rank-description');
      description.appendChild(element('h3', '', row.title));
      description.appendChild(element('span', 'rank-category', row.category || '公式ランキング')); li.appendChild(description);
      var verified = row.sample === false && row.verified === true && /^\d{4}-\d{2}-\d{2}$/.test(row.checkedAt || '') && typeof row.rewardText === 'string' && row.rewardText.trim();
      var amount = element('div', 'rank-amount', verified ? row.rewardText : 'サンプル');
      amount.appendChild(element('small', '', verified ? row.checkedAt + ' 確認' : '金額未掲載')); li.appendChild(amount);
      var href = verified && safeLocal(row.href);
      if (href) { var link = element('a', '', row.title); link.href = href; description.firstChild.textContent = ''; description.firstChild.appendChild(link); }
      list.appendChild(li);
    });
    panel.appendChild(list.children.length ? list : empty());
  }
  if (data && data.rankings && tablist && panel) {
    tablist.hidden = false;
    tablist.addEventListener('click', function (event) {
      var button = event.target.closest('button[data-site]'); if (button) selectSite(button);
    });
    tablist.addEventListener('keydown', function (event) {
      var buttons = Array.prototype.slice.call(tablist.querySelectorAll('button'));
      var index = buttons.indexOf(document.activeElement);
      if (index < 0 || ['ArrowLeft','ArrowRight','Home','End'].indexOf(event.key) < 0) return;
      event.preventDefault();
      index = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
      buttons[index].focus(); selectSite(buttons[index]);
    });
    selectSite(tablist.querySelector('button'));
  }
  document.addEventListener('error', function (event) {
    var img = event.target;
    if (img.tagName !== 'IMG') return;
    if (img.getAttribute('data-fallback') === 'true') { img.removeAttribute('src'); img.alt = '画像準備中'; return; }
    img.setAttribute('data-fallback', 'true'); img.classList.add('image-fallback'); img.src = 'visuals/about.svg';
  }, true);
  Array.prototype.forEach.call(document.images, function (img) { if (img.complete && !img.naturalWidth) img.dispatchEvent(new Event('error')); });
  var menus = document.querySelectorAll('.header-disclosure');
  Array.prototype.forEach.call(menus, function (menu) {
    menu.addEventListener('toggle', function () { if (menu.open) Array.prototype.forEach.call(menus, function (other) { if (other !== menu) other.open = false; }); });
    menu.addEventListener('click', function (event) { if (event.target.closest('a')) menu.open = false; });
  });
  document.addEventListener('keydown', function (event) { if (event.key === 'Escape') Array.prototype.forEach.call(menus, function (menu) { if (menu.open) { menu.open = false; menu.querySelector('summary').focus(); } }); });
  document.addEventListener('click', function (event) { if (!event.target.closest('.media-header')) Array.prototype.forEach.call(menus, function (menu) { menu.open = false; }); });
  var form = document.getElementById('site-search');
  if (data && Array.isArray(data.articles) && form) form.addEventListener('submit', function (event) {
    event.preventDefault();
    var query = document.getElementById('search-query').value.trim().toLowerCase();
    var results = document.getElementById('search-results'); results.textContent = '';
    var matches = data.articles.filter(function (a) { return a && typeof a.title === 'string' && safeLocal(a.href) && a.title.toLowerCase().indexOf(query) >= 0; });
    if (!matches.length) { results.appendChild(empty('該当する記事がありません。別の言葉で検索してください。')); return; }
    results.appendChild(element('p', '', matches.length + '件の記事'));
    matches.forEach(function (a) { var link = element('a', '', a.title); link.href = a.href; results.appendChild(link); });
  });
})();
