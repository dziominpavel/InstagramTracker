"""Modern dashboard UI (V2) — Dark Refined."""
import json
from typing import Any, Dict

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instagram Tracker</title>
<style>
  :root {
    --bg: #101114;
    --bg-soft: #0c0d10;
    --card: #171a21;
    --card-2: #14161c;
    --card-hover: #1c212b;
    --text: #eceef2;
    --muted: #8b93a7;
    --faint: #6b7280;
    --border: #2a2f3a;
    --border-soft: #232833;
    --accent: #2dd4bf;
    --accent-dim: rgba(45, 212, 191, 0.14);
    --accent-border: rgba(45, 212, 191, 0.35);
    --danger: #f87171;
    --danger-dim: rgba(248, 113, 113, 0.12);
    --radius: 12px;
    --radius-lg: 14px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }
  .layout { display: flex; min-height: 100vh; }

  .sidebar {
    width: 248px; flex-shrink: 0;
    background: var(--bg-soft); border-right: 1px solid var(--border);
    padding: 1.25rem 0.85rem; position: sticky; top: 0; height: 100vh; overflow-y: auto;
    display: flex; flex-direction: column;
  }
  .brand { padding: 0.25rem 0.65rem 1.25rem; }
  .brand .title { font-weight: 700; font-size: 0.95rem; }
  .brand .subtitle { color: var(--muted); font-size: 0.75rem; margin-top: 0.1rem; }
  .nav { display: flex; flex-direction: column; gap: 0.1rem; }
  .nav-group-label {
    color: var(--faint); font-size: 0.68rem; text-transform: uppercase;
    letter-spacing: 0.08em; padding: 0.95rem 0.7rem 0.35rem;
  }
  .nav-group-label.collapsible {
    cursor: pointer; display: flex; align-items: center; justify-content: space-between;
    user-select: none;
  }
  .nav-group-label.collapsible:hover { color: var(--muted); }
  .nav-group-label .chevron { font-size: 0.65rem; transition: transform 0.15s; }
  .nav-group-label.collapsed .chevron { transform: rotate(-90deg); }
  .nav-group-body.collapsed { display: none; }
  .nav-item {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.55rem 0.7rem; border-radius: 8px;
    color: var(--muted); cursor: pointer; border: none; background: none;
    width: 100%; text-align: left; font-size: 0.88rem; transition: background 0.12s, color 0.12s;
  }
  .nav-item:hover { background: var(--card); color: var(--text); }
  .nav-item.active { background: var(--accent-dim); color: var(--text); }
  .nav-item .badge {
    margin-left: auto; background: var(--card); color: var(--faint);
    font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 999px; min-width: 1.5rem; text-align: center;
  }
  .nav-item.active .badge { background: rgba(45,212,191,0.18); color: var(--accent); }

  .main { flex: 1; padding: 1.5rem 1.75rem 3.5rem; min-width: 0; width: 100%; }
  .topbar { display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem; }
  .topbar h1 { font-size: 1.45rem; font-weight: 800; letter-spacing: -0.02em; }
  .topbar .meta { color: var(--muted); font-size: 0.88rem; margin-top: 0.2rem; }
  .topbar-actions { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
  .pill {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: var(--card); border: 1px solid var(--border);
    padding: 0.4rem 0.75rem; border-radius: 8px; font-size: 0.82rem; color: var(--muted);
  }
  .version-switch {
    display: inline-flex; align-items: center; text-decoration: none;
    background: transparent; border: 1px solid var(--border); color: var(--muted);
    padding: 0.4rem 0.75rem; border-radius: 8px; font-size: 0.82rem; transition: all 0.15s;
  }
  .version-switch:hover { color: var(--text); border-color: var(--accent); background: var(--accent-dim); }

  .period-bar {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg);
    padding: 0.75rem 1rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;
  }
  .period-bar .label { color: var(--muted); font-size: 0.82rem; margin-right: 0.25rem; }
  .period-btn {
    background: transparent; border: 1px solid var(--border); color: var(--muted);
    padding: 0.35rem 0.7rem; border-radius: 6px; cursor: pointer; font-size: 0.82rem; transition: all 0.12s;
  }
  .period-btn:hover { color: var(--text); border-color: var(--accent-border); }
  .period-btn.active { background: var(--accent-dim); color: var(--accent); border-color: var(--accent-border); }
  .period-select {
    background: var(--bg-soft); border: 1px solid var(--border); color: var(--text);
    border-radius: 6px; padding: 0.35rem 0.5rem; font-size: 0.82rem; cursor: pointer; outline: none;
  }
  .period-select:focus { border-color: var(--accent); }
  .period-info { color: var(--faint); font-size: 0.78rem; margin-left: auto; }
  .period-bar.hidden { display: none; }

  .section-label {
    color: var(--faint); font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 0.06em; margin-bottom: 0.55rem;
  }
  .hero-delta {
    font-size: 2rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 1rem; line-height: 1.1;
  }
  .hero-delta .up { color: var(--accent); }
  .hero-delta .down { color: var(--danger); }
  .hero-delta .sep { color: #4b5563; font-weight: 400; }
  .hero-delta .hint { font-size: 0.85rem; color: var(--muted); font-weight: 500; margin-left: 0.5rem; }

  .changes { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem; }
  .change-card {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1rem 1.1rem; cursor: pointer; transition: background 0.12s, border-color 0.12s;
  }
  .change-card:hover { background: var(--card-hover); border-color: var(--accent-border); }
  .change-card .value { font-size: 1.45rem; font-weight: 700; }
  .change-card .label { color: var(--muted); font-size: 0.8rem; margin-top: 0.25rem; }
  .change-card.up .value { color: var(--accent); }
  .change-card.down .value { color: var(--danger); }

  .stats { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.65rem; margin-bottom: 0.5rem; }
  .stat {
    background: var(--card-2); border: 1px solid var(--border-soft); border-radius: 10px;
    padding: 0.85rem 1rem; cursor: pointer; transition: background 0.12s, border-color 0.12s;
  }
  .stat:hover { background: var(--card-hover); border-color: var(--border); }
  .stat .value { font-size: 1.2rem; font-weight: 700; margin-top: 0.2rem; }
  .stat .label { color: var(--faint); font-size: 0.75rem; }
  .stat .delta { font-size: 0.72rem; margin-top: 0.35rem; color: var(--accent); }
  .stat .delta.down { color: var(--danger); }

  .empty-compare {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1rem 1.15rem; margin-bottom: 1.5rem; color: var(--muted); font-size: 0.9rem;
  }

  .panel { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; }
  .panel-head { padding: 1rem 1.15rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
  .panel-head h2 { font-size: 1.1rem; font-weight: 700; }
  .panel-head .count {
    color: var(--faint); font-size: 0.8rem; background: var(--bg-soft);
    border: 1px solid var(--border); padding: 0.15rem 0.55rem; border-radius: 999px;
  }
  .panel-head .desc { color: var(--muted); font-size: 0.82rem; width: 100%; margin-top: 0.1rem; }
  .toolbar { display: flex; gap: 0.5rem; margin-left: auto; flex-wrap: wrap; align-items: center; }
  .search { position: relative; }
  .search input {
    background: var(--bg-soft); border: 1px solid var(--border); color: var(--text);
    border-radius: 8px; padding: 0.5rem 0.75rem 0.5rem 2rem; font-size: 0.85rem; width: 240px; outline: none;
  }
  .search input:focus { border-color: var(--accent); }
  .search .ico { position: absolute; left: 0.65rem; top: 50%; transform: translateY(-50%); color: var(--faint); font-size: 0.8rem; }
  .sort-select {
    background: var(--bg-soft); border: 1px solid var(--border); color: var(--muted);
    border-radius: 8px; padding: 0.5rem 0.65rem; font-size: 0.82rem; outline: none; cursor: pointer;
  }

  .list { max-height: 720px; overflow-y: auto; }
  .row {
    display: flex; align-items: center; gap: 0.9rem; padding: 0.85rem 1.15rem;
    border-bottom: 1px solid var(--border); transition: background 0.1s;
  }
  .row:hover { background: var(--card-hover); }
  .row:last-child { border-bottom: none; }
  .avatar {
    width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0;
    display: grid; place-items: center; font-weight: 700; color: #fff; font-size: 1rem;
  }
  .avatar-img {
    width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0; object-fit: cover;
  }
  .row .info { min-width: 0; flex: 1; }
  .row .fname { font-weight: 700; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .row .uname { color: var(--muted); font-size: 0.82rem; margin-top: 0.15rem; }
  .user-stats { color: var(--faint); }
  .row.deactivated { opacity: 0.55; }
  .row.deactivated .avatar-img { filter: grayscale(1); }
  .dead-badge {
    display: inline-block; background: var(--danger-dim); color: var(--danger);
    font-size: 0.68rem; font-weight: 600; padding: 0.1rem 0.4rem;
    border-radius: 4px; margin-left: 0.35rem; white-space: nowrap; vertical-align: middle;
  }
  .row .open {
    margin-left: auto; flex-shrink: 0; text-decoration: none; color: var(--accent);
    border: 1px solid var(--border); border-radius: 8px; padding: 0.4rem 0.75rem; font-size: 0.82rem; transition: all 0.12s;
  }
  .row .open:hover { background: var(--accent-dim); border-color: var(--accent-border); }
  .empty { padding: 3rem 1.25rem; text-align: center; color: var(--muted); font-size: 0.95rem; }

  .view { display: none; }
  .view.active { display: block; }
  .mobile-nav { display: none; }

  @media (max-width: 1100px) {
    .changes { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .stats { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  }
  @media (max-width: 860px) {
    .sidebar { display: none; }
    .main { padding: 1rem 1rem 3rem; }
    .search input { width: 160px; }
    .mobile-nav { display: flex; gap: 0.4rem; overflow-x: auto; padding-bottom: 0.75rem; margin-bottom: 0.75rem; }
    .mobile-nav .nav-item { width: auto; white-space: nowrap; background: var(--card); border: 1px solid var(--border); }
    .changes, .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }
  ::-webkit-scrollbar { width: 8px; height: 8px; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 8px; }
  ::-webkit-scrollbar-thumb:hover { background: #3a4256; }
</style>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <div class="brand">
      <div class="title">Tracker</div>
      <div class="subtitle">Instagram</div>
    </div>
    <nav class="nav" id="nav"></nav>
  </aside>

  <main class="main">
    <div class="topbar">
      <div>
        <h1 id="account"></h1>
        <div class="meta" id="meta"></div>
      </div>
      <div class="topbar-actions">
        <div class="pill"><span id="date-pill"></span></div>
        <a class="version-switch" href="index-v1.html">← Классический вид</a>
      </div>
    </div>

    <div class="period-bar" id="period-bar">
      <span class="label">Сравнить с</span>
      <button class="period-btn" data-days="7">Неделя</button>
      <button class="period-btn" data-days="30">Месяц</button>
      <button class="period-btn" data-days="90">3 мес</button>
      <button class="period-btn" data-days="180">6 мес</button>
      <button class="period-btn" data-days="365">Год</button>
      <button class="period-btn" data-days="99999">Всё время</button>
      <select class="period-select" id="period-select"><option value="">— снимок —</option></select>
      <span class="period-info" id="period-info"></span>
    </div>

    <div class="mobile-nav" id="mobile-nav"></div>
    <div id="views"></div>
  </main>
</div>

<script>
const DATA = __DATA__;

const TABS = [
  { key: "overview", label: "Обзор", group: "Главное" },
  { key: "not_following_back", label: "Не подписаны", group: "Анализ", desc: "Вы подписаны на них, но они не подписаны на вас." },
  { key: "fans", label: "Фанаты", group: "Анализ", desc: "Подписаны на вас, но вы не подписаны на них." },
  { key: "mutual", label: "Взаимные", group: "Анализ", desc: "Вы подписаны друг на друга." },
  { key: "new_followers", label: "Новые подписчики", group: "Изменения", desc: "Подписались на вас за выбранный период.", requiresChanges: true },
  { key: "lost_followers", label: "Отписались от меня", group: "Изменения", desc: "Отписались от вас за выбранный период.", requiresChanges: true },
  { key: "new_following", label: "Новые подписки", group: "Изменения", desc: "Вы подписались на них за выбранный период.", requiresChanges: true },
  { key: "lost_following", label: "Вы отписались", group: "Изменения", desc: "Вы отписались от них за выбранный период.", requiresChanges: true },
  { key: "followers", label: "Подписчики", group: "Списки" },
  { key: "following", label: "Подписки", group: "Списки" },
  { key: "recent_follow_requests", label: "Заявки", group: "Списки", desc: "Заявки в подписчики, которые ещё не приняты." },
  { key: "hide_story_from", label: "Скрыты истории", group: "Списки", desc: "Люди, от которых скрыты ваши истории." },
  { key: "blocked", label: "Заблокированы", group: "Списки" },
];

const AVATAR_COLORS = ["#0d9488","#115e59","#334155","#475569","#1e293b","#0f766e","#164e63","#3f3f46"];
function avatarColor(name){ let h=0; for(let i=0;i<name.length;i++) h=name.charCodeAt(i)+((h<<5)-h); return AVATAR_COLORS[Math.abs(h)%AVATAR_COLORS.length]; }
function initials(user){ return (user.full_name||user.username||"?").trim().charAt(0).toUpperCase(); }
function esc(s){ return (s||"").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function fmtCount(n){
  if (n === undefined || n === null || n === "") return "—";
  const x = Number(n);
  if (Number.isNaN(x)) return String(n);
  if (x >= 1000000) return (x/1000000).toFixed(1).replace(/\.0$/,"") + "M";
  if (x >= 1000) return (x/1000).toFixed(1).replace(/\.0$/,"") + "k";
  return String(x);
}

let searchState = {};
let sortState = {};
let currentCompare = null;
let currentTab = "overview";
let listsCollapsed = true;

function computeChanges(compareSnap){
  if (!compareSnap) return null;
  const curF = new Set(DATA.lists.followers.map(u => u.username));
  const curG = new Set(DATA.lists.following.map(u => u.username));
  const prevF = new Set(compareSnap.followers.map(u => u.username));
  const prevG = new Set(compareSnap.following.map(u => u.username));
  return {
    previous_date: compareSnap.date,
    new_followers: DATA.lists.followers.filter(u => !prevF.has(u.username)),
    lost_followers: compareSnap.followers.filter(u => !curF.has(u.username)),
    new_following: DATA.lists.following.filter(u => !prevG.has(u.username)),
    lost_following: compareSnap.following.filter(u => !curG.has(u.username)),
  };
}

function changeLists(){
  if (!currentCompare) return {};
  const ch = computeChanges(currentCompare);
  return {
    new_followers: ch.new_followers,
    lost_followers: ch.lost_followers,
    new_following: ch.new_following,
    lost_following: ch.lost_following,
  };
}

function hasChanges(){ return !!currentCompare; }

function findSnapshotByDays(days){
  const cur = new Date(DATA.date);
  const target = new Date(cur); target.setDate(target.getDate() - days);
  const candidates = DATA.snapshots.filter(s => s.date < DATA.date);
  if (candidates.length === 0) return null;
  let best = candidates[0], bestDiff = Infinity;
  for (const s of candidates){
    const diff = Math.abs(new Date(s.date) - target);
    if (diff < bestDiff){ bestDiff = diff; best = s; }
  }
  return best;
}

function setCompareByDays(days){
  currentCompare = findSnapshotByDays(days);
  updatePeriodInfo();
  refreshUI();
}

function setCompareByDate(dateStr){
  if (!dateStr){ currentCompare = null; updatePeriodInfo(); refreshUI(); return; }
  currentCompare = DATA.snapshots.find(s => s.date === dateStr) || null;
  updatePeriodInfo();
  refreshUI();
}

function updatePeriodInfo(){
  const el = document.getElementById("period-info");
  if (!currentCompare){ el.textContent = ""; return; }
  const days = Math.round((new Date(DATA.date) - new Date(currentCompare.date)) / 86400000);
  el.textContent = "снимок от " + currentCompare.date + " · " + days + " дн.";
}

function sortUsers(users, mode){
  const arr = users.slice();
  if (mode === "username") arr.sort((a,b) => a.username.localeCompare(b.username));
  else arr.sort((a,b) => (a.full_name||a.username).localeCompare(b.full_name||b.username, "ru"));
  return arr;
}

function renderRows(key, users, filter, sortMode){
  const q = (filter||"").toLowerCase().trim();
  let filtered = q
    ? users.filter(u => u.username.toLowerCase().includes(q) || (u.full_name||"").toLowerCase().includes(q))
    : users.slice();
  filtered = sortUsers(filtered, sortMode || "name");
  if (filtered.length === 0){
    if (users.length === 0) return '<div class="empty">Список пуст</div>';
    return '<div class="empty">Ничего не найдено</div>';
  }
  return filtered.map(u => {
    const dead = u.status === "deactivated";
    const rowClass = dead ? "row deactivated" : "row";
    const avatar = u.avatar_url
      ? `<img class="avatar-img" src="${esc(u.avatar_url)}" alt="" onerror="this.style.display='none';this.nextElementSibling.style.display='grid'"><div class="avatar" style="background:${avatarColor(u.username)};display:none">${esc(initials(u))}</div>`
      : `<div class="avatar" style="background:${avatarColor(u.username)}">${esc(initials(u))}</div>`;
    const statsParts = [];
    if (u.followers_count || u.following_count || u.posts_count){
      statsParts.push(fmtCount(u.followers_count) + " подп.");
      if (u.posts_count) statsParts.push(fmtCount(u.posts_count) + " пост.");
    }
    const stats = statsParts.length ? ` · <span class="user-stats">${statsParts.join(" · ")}</span>` : "";
    const badge = dead ? ' <span class="dead-badge">деактивирован</span>' : "";
    return `
    <div class="${rowClass}">
      ${avatar}
      <div class="info">
        <div class="fname">${esc(u.full_name) || esc(u.username)}${badge}</div>
        <div class="uname">@${esc(u.username)}${stats}</div>
      </div>
      <a class="open" href="https://www.instagram.com/${encodeURIComponent(u.username)}/" target="_blank" rel="noopener">Открыть</a>
    </div>`;
  }).join("");
}

function listView(tab){
  const source = tab.requiresChanges ? changeLists() : DATA.lists;
  const users = source[tab.key] || [];
  const desc = tab.desc ? `<div class="desc">${tab.desc}</div>` : "";
  const sort = sortState[tab.key] || "name";
  return `
    <div class="panel">
      <div class="panel-head">
        <h2>${tab.label}</h2>
        <span class="count">${users.length}</span>
        <div class="toolbar">
          <div class="search">
            <span class="ico">⌕</span>
            <input type="text" placeholder="Поиск по имени или @username" oninput="onSearch('${tab.key}', this.value)" value="${esc(searchState[tab.key]||'')}">
          </div>
          <select class="sort-select" onchange="onSort('${tab.key}', this.value)">
            <option value="name" ${sort==="name"?"selected":""}>Сортировка: имя</option>
            <option value="username" ${sort==="username"?"selected":""}>Сортировка: username</option>
          </select>
        </div>
        ${desc}
      </div>
      <div class="list" id="list-${tab.key}">${renderRows(tab.key, users, searchState[tab.key], sort)}</div>
    </div>`;
}

function onSearch(key, value){
  searchState[key] = value;
  const tab = TABS.find(t => t.key === key);
  const source = tab && tab.requiresChanges ? changeLists() : DATA.lists;
  const el = document.getElementById("list-"+key);
  if (el) el.innerHTML = renderRows(key, source[key]||[], value, sortState[key]||"name");
}

function onSort(key, value){
  sortState[key] = value;
  onSearch(key, searchState[key]||"");
}

function overviewView(){
  const c = DATA.counts;
  const ch = currentCompare ? computeChanges(currentCompare) : null;
  const fDelta = ch ? ch.new_followers.length - ch.lost_followers.length : null;
  const gDelta = ch ? ch.new_following.length - ch.lost_following.length : null;

  let changesBlock = "";
  if (ch){
    changesBlock = `
      <div class="section-label">Изменения за период</div>
      <div class="hero-delta">
        <span class="up">+${ch.new_followers.length}</span>
        <span class="sep"> / </span>
        <span class="down">−${ch.lost_followers.length}</span>
        <span class="hint">подписчики · с ${ch.previous_date}</span>
      </div>
      <div class="changes">
        <div class="change-card up" onclick="go('new_followers')"><div class="value">${ch.new_followers.length}</div><div class="label">Новые подписчики →</div></div>
        <div class="change-card down" onclick="go('lost_followers')"><div class="value">${ch.lost_followers.length}</div><div class="label">Отписались от меня →</div></div>
        <div class="change-card up" onclick="go('new_following')"><div class="value">${ch.new_following.length}</div><div class="label">Новые подписки →</div></div>
        <div class="change-card down" onclick="go('lost_following')"><div class="value">${ch.lost_following.length}</div><div class="label">Вы отписались →</div></div>
      </div>`;
  } else {
    changesBlock = `<div class="empty-compare">Нет снимка для сравнения. Сделайте новый экспорт позже, чтобы увидеть, кто подписался и отписался.</div>`;
  }

  function deltaHtml(d){
    if (d === null || d === undefined) return "";
    const up = d >= 0;
    return `<div class="delta ${up?"":"down"}">${up?"▲":"▼"} ${Math.abs(d)}</div>`;
  }

  const stats = `
    <div class="section-label">Сейчас</div>
    <div class="stats">
      <div class="stat" onclick="go('followers')"><div class="label">Подписчики</div><div class="value">${c.followers}</div>${deltaHtml(fDelta)}</div>
      <div class="stat" onclick="go('following')"><div class="label">Подписки</div><div class="value">${c.following}</div>${deltaHtml(gDelta)}</div>
      <div class="stat" onclick="go('mutual')"><div class="label">Взаимные</div><div class="value">${c.mutual}</div></div>
      <div class="stat" onclick="go('not_following_back')"><div class="label">Не подписаны</div><div class="value">${c.not_following_back}</div></div>
      <div class="stat" onclick="go('fans')"><div class="label">Фанаты</div><div class="value">${c.fans}</div></div>
    </div>`;

  return changesBlock + stats;
}

function visibleTabs(){
  return TABS.filter(t => !t.requiresChanges || hasChanges());
}

function toggleListsGroup(){
  listsCollapsed = !listsCollapsed;
  renderNav();
  document.querySelectorAll(".nav-item").forEach(n => n.classList.toggle("active", n.dataset.tab === currentTab));
}

function renderNav(){
  const nav = document.getElementById("nav");
  const mnav = document.getElementById("mobile-nav");
  const tabs = visibleTabs();
  const groups = [];
  tabs.forEach(tab => {
    if (!groups.length || groups[groups.length-1].name !== tab.group)
      groups.push({ name: tab.group, tabs: [] });
    groups[groups.length-1].tabs.push(tab);
  });

  let navHtml = "";
  groups.forEach(g => {
    const isLists = g.name === "Списки";
    if (isLists){
      const collapsed = listsCollapsed;
      navHtml += `<div class="nav-group-label collapsible ${collapsed?"collapsed":""}" onclick="toggleListsGroup()">Списки <span class="chevron">▾</span></div>`;
      navHtml += `<div class="nav-group-body ${collapsed?"collapsed":""}">`;
      g.tabs.forEach(tab => {
        const source = tab.requiresChanges ? changeLists() : DATA.lists;
        const badge = `<span class="badge">${(source[tab.key]||[]).length}</span>`;
        navHtml += `<button class="nav-item" data-tab="${tab.key}" onclick="go('${tab.key}')">${tab.label}${badge}</button>`;
      });
      navHtml += `</div>`;
    } else {
      navHtml += `<div class="nav-group-label">${g.name}</div>`;
      g.tabs.forEach(tab => {
        const source = tab.requiresChanges ? changeLists() : DATA.lists;
        const badge = tab.key === "overview" ? "" : `<span class="badge">${(source[tab.key]||[]).length}</span>`;
        navHtml += `<button class="nav-item" data-tab="${tab.key}" onclick="go('${tab.key}')">${tab.label}${badge}</button>`;
      });
    }
  });
  nav.innerHTML = navHtml;
  mnav.innerHTML = tabs.map(tab =>
    `<button class="nav-item" data-tab="${tab.key}" onclick="go('${tab.key}')">${tab.label}</button>`
  ).join("");
}

function renderViews(){
  const views = document.getElementById("views");
  views.innerHTML = visibleTabs().map(tab =>
    `<div class="view" id="view-${tab.key}">${tab.key === "overview" ? overviewView() : listView(tab)}</div>`
  ).join("");
}

function refreshUI(){
  renderNav();
  renderViews();
  if (!visibleTabs().find(t => t.key === currentTab)) currentTab = "overview";
  go(currentTab, true);
}

function go(key, skipScroll){
  if (!visibleTabs().find(t => t.key === key)) key = "overview";
  // auto-expand lists if navigating into a list tab
  const tab = TABS.find(t => t.key === key);
  if (tab && tab.group === "Списки" && listsCollapsed){
    listsCollapsed = false;
    renderNav();
  }
  currentTab = key;
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  const view = document.getElementById("view-"+key);
  if (view) view.classList.add("active");
  document.querySelectorAll(".nav-item").forEach(n => n.classList.toggle("active", n.dataset.tab === key));
  history.replaceState(null, "", "#"+key);
  if (!skipScroll) window.scrollTo({top:0, behavior:"smooth"});
}

function initPeriodBar(){
  const bar = document.getElementById("period-bar");
  const select = document.getElementById("period-select");
  if (DATA.snapshots.length === 0){
    bar.classList.add("hidden");
    return;
  }
  DATA.snapshots.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.date;
    opt.textContent = s.date + " (" + s.followers.length + " подп.)";
    select.appendChild(opt);
  });
  document.querySelectorAll(".period-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".period-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      select.value = "";
      setCompareByDays(parseInt(btn.dataset.days));
    });
  });
  select.addEventListener("change", () => {
    document.querySelectorAll(".period-btn").forEach(b => b.classList.remove("active"));
    setCompareByDate(select.value);
  });
  const prev = DATA.snapshots.filter(s => s.date < DATA.date).pop();
  if (prev){
    currentCompare = prev;
    select.value = prev.date;
    updatePeriodInfo();
  }
}

function init(){
  document.getElementById("account").textContent = "@" + DATA.username;
  document.getElementById("meta").textContent = "Снимок · " + DATA.date + " · " + DATA.counts.followers + " подп. · " + DATA.counts.following + " подписок";
  document.getElementById("date-pill").textContent = DATA.date;
  initPeriodBar();
  refreshUI();
  go(location.hash ? location.hash.slice(1) : "overview");
}

init();
</script>
</body>
</html>"""


def render_html(payload: Dict[str, Any]) -> str:
    data_json = json.dumps(payload, ensure_ascii=False)
    return HTML_TEMPLATE.replace("__DATA__", data_json)
