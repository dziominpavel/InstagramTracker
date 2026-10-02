// InstagramTracker Web — анализатор экспорта Instagram.
// Работает целиком в браузере: никаких сетевых запросов с данными экспорта.
// Разбор — порт app/parser.py (паттерны файлов, username из label_values/
// string_list_data, фикс mojibake latin-1 → utf-8); секции и счётчики —
// порт app/dashboard.py; динамика — порт dashboard_v2 (сравнение снимков).
(function () {
  'use strict';

  var SNAP_KEY = 'igtracker.snapshots';
  var SNAP_LIMIT = 50;

  var EXACT_FILES = {
    'following.json': 'following',
    'blocked_profiles.json': 'blocked',
    'hide_story_from.json': 'hide_story_from',
    'recently_unfollowed_profiles.json': 'recently_unfollowed',
    'recent_follow_requests.json': 'recent_follow_requests'
  };

  var OVERVIEW = [
    { key: 'followers', label: 'Подписчики' },
    { key: 'following', label: 'Подписки' },
    { key: 'mutual', label: 'Взаимные' },
    { key: 'not_following_back', label: 'Не подписаны', accent: true },
    { key: 'fans', label: 'Фанаты' },
    { key: 'recent_follow_requests', label: 'Заявки' },
    { key: 'hide_story_from', label: 'Скрыты истории' },
    { key: 'blocked', label: 'Заблокированы' }
  ];

  var ANALYSIS = [
    { key: 'not_following_back', label: 'Не подписаны', desc: 'Вы подписаны на них, но они не подписаны на вас.' },
    { key: 'fans', label: 'Фанаты', desc: 'Подписаны на вас, но вы не подписаны на них.' },
    { key: 'mutual', label: 'Взаимные', desc: 'Вы подписаны друг на друга.' }
  ];

  var CHANGES = [
    { key: 'new_followers', label: 'Новые подписчики', desc: 'Подписались на вас за выбранный период.' },
    { key: 'lost_followers', label: 'Отписались от меня', desc: 'Отписались от вас за выбранный период.' },
    { key: 'new_following', label: 'Новые подписки', desc: 'Вы подписались на них за выбранный период.' },
    { key: 'lost_following', label: 'Вы отписались', desc: 'Вы отписались от них за выбранный период.' }
  ];

  var LISTS = [
    { key: 'followers', label: 'Подписчики', desc: '' },
    { key: 'following', label: 'Подписки', desc: '' },
    { key: 'recent_follow_requests', label: 'Заявки', desc: 'Заявки в подписчики, которые ещё не приняты.' },
    { key: 'hide_story_from', label: 'Скрыты истории', desc: 'Люди, от которых скрыты ваши истории.' },
    { key: 'blocked', label: 'Заблокированы', desc: '' }
  ];

  /* ---------- утилиты ---------- */

  function esc(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function fmtDate(iso) {
    var p = String(iso || '').split('-');
    if (p.length !== 3) return String(iso || '—');
    return p[2] + '.' + p[1] + '.' + p[0];
  }

  function isoToday() {
    var d = new Date();
    var m = d.getMonth() + 1;
    var day = d.getDate();
    return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day;
  }

  /* ---------- парсер (порт app/parser.py) ---------- */

  // Python: text.encode('latin-1').decode('utf-8'), ошибки → исходная строка.
  function decodeMojibake(text) {
    try {
      var bytes = new Uint8Array(text.length);
      for (var i = 0; i < text.length; i++) {
        var code = text.charCodeAt(i);
        if (code > 255) return text; // UnicodeEncodeError
        bytes[i] = code;
      }
      return new TextDecoder('utf-8', { fatal: true }).decode(bytes);
    } catch (e) {
      return text; // UnicodeDecodeError → исходная строка
    }
  }

  // Python: href.rstrip('/').split('/')[-1]
  function parseUsername(href) {
    var clean = String(href || '').replace(/\/+$/, '');
    var parts = clean.split('/');
    return parts[parts.length - 1] || '';
  }

  function extractFromLabelValues(labelValues) {
    var result = {};
    for (var i = 0; i < labelValues.length; i++) {
      var item = labelValues[i] || {};
      var label = decodeMojibake(String(item.label || ''));
      var value = decodeMojibake(String(item.value || ''));
      if (label === 'URL') result.url = value;
      else if (label === 'Имя пользователя' || label === 'Username') result.username = value;
      else if (label === 'Имя' || label === 'Name') result.full_name = value;
    }
    return result;
  }

  function userFromLabelValues(labelValues) {
    var data = extractFromLabelValues(labelValues);
    var username = data.username || parseUsername(data.url || '');
    if (!username) return null;
    return { id: username, username: username, full_name: data.full_name || '' };
  }

  function readFollowers(groups) {
    var users = [];
    groups.forEach(function (group) {
      var items = Array.isArray(group.data) ? group.data : [group.data];
      items.forEach(function (item) {
        if (!item || typeof item !== 'object') return;
        var entries = Array.isArray(item.string_list_data) ? item.string_list_data : [];
        entries.forEach(function (entry) {
          if (!entry || typeof entry !== 'object') return;
          var username = entry.value || parseUsername(entry.href || '');
          if (username) users.push({ id: username, username: username, full_name: '' });
        });
      });
    });
    return users;
  }

  function readFollowing(groups) {
    var users = [];
    groups.forEach(function (group) {
      var data = group.data && typeof group.data === 'object' && !Array.isArray(group.data)
        ? group.data
        : {};
      var items = Array.isArray(data.relationships_following) ? data.relationships_following : [];
      items.forEach(function (item) {
        if (!item || typeof item !== 'object') return;
        var username = typeof item.title === 'string' ? item.title : '';
        if (!username && Array.isArray(item.string_list_data) && item.string_list_data.length) {
          var first = item.string_list_data[0] || {};
          username = parseUsername(first.href || '');
        }
        if (username) users.push({ id: username, username: username, full_name: '' });
      });
    });
    return users;
  }

  function readLabelUsers(groups) {
    var users = [];
    groups.forEach(function (group) {
      var items = Array.isArray(group.data) ? group.data : [group.data];
      items.forEach(function (item) {
        if (!item || typeof item !== 'object') return;
        var user = userFromLabelValues(Array.isArray(item.label_values) ? item.label_values : []);
        if (user) users.push(user);
      });
    });
    return users;
  }

  function parseEntries(entries) {
    var groups = {
      followers: [],
      following: [],
      blocked: [],
      hide_story_from: [],
      recently_unfollowed: [],
      recent_follow_requests: []
    };
    var matched = 0;
    var broken = [];

    entries.forEach(function (entry) {
      var base = String(entry.base || '').toLowerCase();
      var key = null;
      if (/^followers_.*\.json$/.test(base)) key = 'followers';
      else if (EXACT_FILES[base]) key = EXACT_FILES[base];
      if (!key) return;
      matched++;
      try {
        groups[key].push({ base: entry.base, data: JSON.parse(entry.text) });
      } catch (e) {
        broken.push(entry.base);
      }
    });

    var users = {
      followers: readFollowers(groups.followers),
      following: readFollowing(groups.following),
      blocked: readLabelUsers(groups.blocked),
      hide_story_from: readLabelUsers(groups.hide_story_from),
      recently_unfollowed: readLabelUsers(groups.recently_unfollowed),
      recent_follow_requests: readLabelUsers(groups.recent_follow_requests)
    };

    return { matched: matched, broken: broken, users: users };
  }

  /* ---------- аналитика (порт app/dashboard.py) ---------- */

  function buildData(users) {
    var followerIds = new Set(users.followers.map(function (u) { return u.id; }));
    var followingIds = new Set(users.following.map(function (u) { return u.id; }));
    var notFollow = users.following.filter(function (u) { return !followerIds.has(u.id); });
    var fans = users.followers.filter(function (u) { return !followingIds.has(u.id); });
    var mutual = users.followers.filter(function (u) { return followingIds.has(u.id); });
    var active = users.recent_follow_requests.filter(function (u) {
      return !followerIds.has(u.username);
    });

    return {
      counts: {
        followers: users.followers.length,
        following: users.following.length,
        mutual: mutual.length,
        not_following_back: notFollow.length,
        fans: fans.length,
        blocked: users.blocked.length,
        hide_story_from: users.hide_story_from.length,
        recent_follow_requests: active.length
      },
      analysis: {
        not_following_back: notFollow,
        fans: fans,
        mutual: mutual
      },
      lists: {
        followers: users.followers,
        following: users.following,
        recent_follow_requests: active,
        hide_story_from: users.hide_story_from,
        blocked: users.blocked
      }
    };
  }

  // Порт dashboard_v2: сравнение текущего экспорта с предыдущим снимком.
  function computeChanges(data, prev) {
    var prevF = new Set(prev.followers || []);
    var prevG = new Set(prev.following || []);
    var curF = new Set(data.lists.followers.map(function (u) { return u.username; }));
    var curG = new Set(data.lists.following.map(function (u) { return u.username; }));
    function asUser(name) { return { id: name, username: name, full_name: '' }; }

    return {
      previous_date: prev.date,
      new_followers: data.lists.followers.filter(function (u) { return !prevF.has(u.username); }),
      lost_followers: (prev.followers || [])
        .filter(function (name) { return !curF.has(name); })
        .map(asUser),
      new_following: data.lists.following.filter(function (u) { return !prevG.has(u.username); }),
      lost_following: (prev.following || [])
        .filter(function (name) { return !curG.has(name); })
        .map(asUser)
    };
  }

  /* ---------- снимки в localStorage ---------- */

  function loadSnapshots() {
    try {
      var raw = localStorage.getItem(SNAP_KEY);
      if (!raw) return [];
      var data = JSON.parse(raw);
      if (!data || !Array.isArray(data.snapshots)) return [];
      return data.snapshots.filter(function (s) {
        return s && typeof s.date === 'string' && Array.isArray(s.followers) && Array.isArray(s.following);
      });
    } catch (e) {
      return [];
    }
  }

  // 'ok' | 'trimmed' | false
  function saveSnapshots(list) {
    function write(items) {
      localStorage.setItem(SNAP_KEY, JSON.stringify({ v: 1, snapshots: items }));
    }
    try {
      write(list.slice(-SNAP_LIMIT));
      return 'ok';
    } catch (e) {
      try {
        var half = list.slice(Math.ceil(list.length / 2));
        write(half);
        list.length = 0;
        Array.prototype.push.apply(list, half);
        return 'trimmed';
      } catch (e2) {
        return false;
      }
    }
  }

  /* ---------- файлы и ZIP ---------- */

  async function hasZipMagic(file) {
    try {
      var head = new Uint8Array(await file.slice(0, 4).arrayBuffer());
      return head.length === 4 && head[0] === 0x50 && head[1] === 0x4b;
    } catch (e) {
      return false;
    }
  }

  async function collectEntries(files) {
    var entries = [];
    var errors = [];

    for (var i = 0; i < files.length; i++) {
      var file = files[i];
      var name = file.name || '';
      var isZip = /\.zip$/i.test(name) || await hasZipMagic(file);

      if (isZip) {
        try {
          var raw = new Uint8Array(await file.arrayBuffer());
          var tree = fflate.unzipSync(raw);
          Object.keys(tree).forEach(function (path) {
            // Разделители в архиве могут быть и слэшами, и обратными (Windows-архивы).
            var clean = String(path).replace(/\\/g, '/');
            if (/\.json$/i.test(clean)) {
              entries.push({
                base: clean.split('/').pop(),
                text: new TextDecoder('utf-8').decode(tree[path])
              });
            }
          });
        } catch (e) {
          errors.push('архив «' + name + '» не читается: ' + (e && e.message ? e.message : 'ошибка'));
        }
      } else if (/\.json$/i.test(name)) {
        try {
          entries.push({ base: name, text: await file.text() });
        } catch (e) {
          errors.push('файл «' + name + '» не читается');
        }
      }
      // Прочие файлы (медиа, html) молча пропускаются: папка может содержать лишнее.
    }

    return { entries: entries, errors: errors };
  }

  /* ---------- сообщения ---------- */

  function showMsg(text, kind) {
    var el = document.getElementById('it-msg');
    el.textContent = text;
    el.className = 'it-msg ' + kind;
    el.hidden = false;
  }

  function hideMsg() {
    var el = document.getElementById('it-msg');
    el.hidden = true;
    el.textContent = '';
  }

  /* ---------- рендер ---------- */

  function chipsHtml(users) {
    return users
      .slice()
      .sort(function (a, b) { return a.username.localeCompare(b.username, 'ru'); })
      .map(function (u) {
        var title = u.full_name ? ' title="' + esc(u.full_name) + '"' : '';
        return '<span class="it-chip"' + title + '>' + esc(u.username) + '</span>';
      })
      .join('');
  }

  function blockHtml(item, users, emptyText) {
    var count = users.length;
    var head =
      '<summary><span class="it-card-title">' + esc(item.label) + '</span>' +
      '<span class="it-n">' + count + '</span></summary>';
    var desc = item.desc ? '<p class="it-desc">' + esc(item.desc) + '</p>' : '';
    var body;

    if (count > 40) {
      body =
        '<input class="it-filter" type="search" placeholder="Поиск по списку…" ' +
        'aria-label="Фильтр списка ' + esc(item.label) + '">' +
        '<div class="it-list">' + chipsHtml(users) + '</div>';
    } else if (count) {
      body = '<div class="it-list">' + chipsHtml(users) + '</div>';
    } else {
      body = '<p class="it-empty">' + esc(emptyText) + '</p>';
    }

    return '<details class="it-card"' + (count > 0 && count <= 12 ? ' open' : '') + '>' +
      head + desc + body + '</details>';
  }

  function sectionHtml(title, hint, blocks) {
    return '<section class="it-sec">' +
      '<div class="it-head"><h2>' + esc(title) + '</h2>' +
      (hint ? '<p class="it-hint">' + esc(hint) + '</p>' : '') +
      '</div><div class="it-blocks">' + blocks.join('') + '</div></section>';
  }

  function renderDashboard(data, changes, meta) {
    var parts = [];

    parts.push('<section class="it-sec">');
    parts.push(
      '<div class="it-head"><h2>Обзор</h2><p class="it-hint">Экспорт от ' +
      fmtDate(meta.date) + ' · разобрано файлов: ' + meta.matched + '</p></div>'
    );
    parts.push('<div class="it-stats">');
    OVERVIEW.forEach(function (card) {
      parts.push(
        '<div class="it-stat' + (card.accent ? ' it-accent' : '') + '"><strong>' +
        data.counts[card.key] + '</strong><span>' + esc(card.label) + '</span></div>'
      );
    });
    parts.push('</div></section>');

    parts.push(sectionHtml('Анализ', '', ANALYSIS.map(function (item) {
      return blockHtml(item, data.analysis[item.key], 'Пусто');
    })));

    if (changes) {
      parts.push(sectionHtml(
        'Изменения',
        'Сравнение с снимком от ' + fmtDate(changes.previous_date),
        CHANGES.map(function (item) {
          return blockHtml(item, changes[item.key], 'Нет изменений');
        })
      ));
    }

    parts.push(sectionHtml('Списки', '', LISTS.map(function (item) {
      return blockHtml(item, data.lists[item.key], 'Пусто');
    })));

    document.getElementById('it-dash').innerHTML = parts.join('');
  }

  /* ---------- обработка загрузки ---------- */

  async function handleFiles(fileList) {
    if (!fileList || !fileList.length) return;
    hideMsg();

    var collected = await collectEntries(fileList);

    if (!collected.entries.length) {
      var detail = collected.errors.length ? ' ' + collected.errors.join('; ') + '.' : '';
      showMsg(
        'Не найдены JSON-файлы экспорта Instagram. Нужен ZIP-архив или файлы ' +
        'followers_*.json, following.json и другие из папки connections/followers_and_following/.' +
        detail,
        'is-error'
      );
      return;
    }

    var parsed = parseEntries(collected.entries);

    if (!parsed.matched) {
      showMsg(
        'В загруженных файлах нет нужных данных: ищу followers_*.json, following.json, ' +
        'blocked_profiles.json, hide_story_from.json, recently_unfollowed_profiles.json, ' +
        'recent_follow_requests.json.',
        'is-error'
      );
      return;
    }

    if (parsed.broken.length >= parsed.matched) {
      showMsg('Файлы экспорта повреждены или не являются JSON: ' + parsed.broken.join(', ') + '.', 'is-error');
      return;
    }

    var data = buildData(parsed.users);
    var snaps = loadSnapshots();
    var today = isoToday();

    var prev = null;
    for (var i = snaps.length - 1; i >= 0; i--) {
      if (snaps[i].date < today) { prev = snaps[i]; break; }
    }
    var changes = prev ? computeChanges(data, prev) : null;

    var snapshot = {
      date: today,
      counts: data.counts,
      followers: data.lists.followers.map(function (u) { return u.username; }),
      following: data.lists.following.map(function (u) { return u.username; })
    };
    var idx = snaps.map(function (s) { return s.date; }).indexOf(today);
    if (idx >= 0) snaps[idx] = snapshot; else snaps.push(snapshot);
    var stored = saveSnapshots(snaps);

    renderDashboard(data, changes, { date: today, matched: parsed.matched });

    var dash = document.getElementById('it-dash');
    dash.hidden = false;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    dash.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });

    var notes = [];
    if (collected.errors.length) notes.push(collected.errors.join('; '));
    if (parsed.broken.length) notes.push('не разобраны: ' + parsed.broken.join(', '));
    if (stored === 'trimmed') notes.push('история снимков усечена из-за нехватки места');
    if (stored === false) notes.push('не удалось сохранить снимок в браузере (нехватка места)');

    var summary = 'Готово: ' + data.counts.followers + ' подписчиков, ' +
      data.counts.following + ' подписок.';
    if (notes.length) showMsg(summary + ' Предупреждения: ' + notes.join('; ') + '.', 'is-warn');
    else showMsg(summary + ' Данные остались в браузере.', 'is-ok');
  }

  /* ---------- инициализация ---------- */

  function dropHasDirectory(dt) {
    if (!dt.items) return false;
    for (var i = 0; i < dt.items.length; i++) {
      var item = dt.items[i];
      if (item.kind === 'file' && item.webkitGetAsEntry) {
        var entry = item.webkitGetAsEntry();
        if (entry && entry.isDirectory) return true;
      }
    }
    return false;
  }

  function init() {
    var zone = document.getElementById('it-zone');
    var filesInput = document.getElementById('it-files');
    var folderInput = document.getElementById('it-folder');
    var dash = document.getElementById('it-dash');

    document.getElementById('it-pick-files').addEventListener('click', function () {
      filesInput.click();
    });
    document.getElementById('it-pick-folder').addEventListener('click', function () {
      folderInput.click();
    });

    filesInput.addEventListener('change', function () {
      handleFiles(filesInput.files);
      filesInput.value = '';
    });
    folderInput.addEventListener('change', function () {
      handleFiles(folderInput.files);
      folderInput.value = '';
    });

    ['dragenter', 'dragover'].forEach(function (name) {
      zone.addEventListener(name, function (event) {
        event.preventDefault();
        zone.classList.add('is-over');
      });
    });
    ['dragleave', 'drop'].forEach(function (name) {
      zone.addEventListener(name, function (event) {
        event.preventDefault();
        zone.classList.remove('is-over');
      });
    });

    zone.addEventListener('drop', function (event) {
      var dt = event.dataTransfer;
      if (!dt) return;
      if (dropHasDirectory(dt)) {
        showMsg('Папку перетащить не получится — используйте кнопку «Выбрать папку».', 'is-error');
        return;
      }
      handleFiles(dt.files);
    });

    dash.addEventListener('input', function (event) {
      var target = event.target;
      if (!target.classList || !target.classList.contains('it-filter')) return;
      var card = target.closest('details');
      if (!card) return;
      var query = target.value.trim().toLowerCase();
      var chips = card.querySelectorAll('.it-chip');
      for (var i = 0; i < chips.length; i++) {
        chips[i].hidden = query ? chips[i].textContent.toLowerCase().indexOf(query) === -1 : false;
      }
    });

    var snaps = loadSnapshots();
    if (snaps.length) {
      showMsg(
        'В истории ' + snaps.length + ' снимок(ов): после загрузки появится сравнение с предыдущим.',
        'is-ok'
      );
    }
  }

  init();
})();
