"""Classic dashboard UI (V1)."""
import json
from typing import Any, Dict


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instagram Dashboard</title>
<style>
  :root {
    --bg: #0f1117;
    --bg-soft: #161a23;
    --card: #1c2130;
    --card-hover: #232a3b;
    --text: #e5e9f0;
    --muted: #8b93a7;
    --border: #2a3142;
    --accent: #6366f1;
    --accent-2: #a855f7;
    --success: #22c55e;
    --danger: #ef4444;
    --warning: #f59e0b;
    --info: #38bdf8;
    --radius: 16px;
    --shadow: 0 10px 30px rgba(0,0,0,0.35);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: radial-gradient(1200px 600px at 80% -10%, rgba(168,85,247,0.12), transparent 60%),
                radial-gradient(1000px 500px at -10% 0%, rgba(99,102,241,0.12), transparent 55%),
                var(--bg);
    color: var(--text);
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }
  .layout { display: flex; min-height: 100vh; }

  /* Sidebar */
  .sidebar {
    width: 264px; flex-shrink: 0;
    background: var(--bg-soft); border-right: 1px solid var(--border);
    padding: 1.5rem 1rem; position: sticky; top: 0; height: 100vh; overflow-y: auto;
  }
  .brand { display: flex; align-items: center; gap: 0.65rem; padding: 0 0.5rem 1.25rem; }
  .brand .logo {
    width: 40px; height: 40px; border-radius: 12px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    display: grid; place-items: center; font-size: 1.25rem;
  }
  .brand .title { font-weight: 700; font-size: 1.05rem; line-height: 1.1; }
  .brand .subtitle { color: var(--muted); font-size: 0.75rem; }
  .nav { display: flex; flex-direction: column; gap: 0.15rem; margin-top: 0.5rem; }
  .nav-group-label {
    color: var(--muted); font-size: 0.7rem; text-transform: uppercase;
    letter-spacing: 0.08em; padding: 1rem 0.75rem 0.4rem;
  }
  .nav-item {
    display: flex; align-items: center; gap: 0.7rem;
    padding: 0.6rem 0.75rem; border-radius: 10px;
    color: var(--muted); cursor: pointer; border: none; background: none;
    width: 100%; text-align: left; font-size: 0.9rem; transition: all 0.15s;
  }
  .nav-item:hover { background: var(--card); color: var(--text); }
  .nav-item.active { background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(168,85,247,0.25)); color: #fff; }
  .nav-item .ico { font-size: 1.05rem; width: 1.4rem; text-align: center; }
  .nav-item .badge {
    margin-left: auto; background: var(--card-hover); color: var(--muted);
    font-size: 0.72rem; padding: 0.1rem 0.5rem; border-radius: 999px; min-width: 1.6rem; text-align: center;
  }
  .nav-item.active .badge { background: rgba(255,255,255,0.2); color: #fff; }

  /* Main */
  .main { flex: 1; padding: 1.75rem 2rem 4rem; max-width: 1200px; }
  .topbar { display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; }
  .topbar h1 { font-size: 1.6rem; font-weight: 700; }
  .topbar .meta { color: var(--muted); font-size: 0.9rem; margin-top: 0.25rem; }
  .pill { display: inline-flex; align-items: center; gap: 0.4rem; background: var(--card); border: 1px solid var(--border); padding: 0.4rem 0.8rem; border-radius: 999px; font-size: 0.85rem; color: var(--muted); }

  /* Period selector */
  .period-bar {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 0.85rem 1.1rem; margin-bottom: 1.75rem; display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;
  }
  .period-bar .label { color: var(--muted); font-size: 0.85rem; font-weight: 600; }
  .period-btn {
    background: var(--bg-soft); border: 1px solid var(--border); color: var(--muted);
    padding: 0.4rem 0.85rem; border-radius: 8px; cursor: pointer; font-size: 0.85rem; transition: all 0.15s;
  }
  .period-btn:hover { color: var(--text); border-color: var(--accent); }
  .period-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }
  .period-select {
    background: var(--bg-soft); border: 1px solid var(--border); color: var(--text);
    border-radius: 8px; padding: 0.4rem 0.6rem; font-size: 0.85rem; cursor: pointer; outline: none;
  }
  .period-select:focus { border-color: var(--accent); }
  .period-info { color: var(--muted); font-size: 0.82rem; margin-left: auto; }
  .period-bar.hidden { display: none; }

  /* Stat cards */
  .stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.75rem; }
  .stat {
    background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.1rem 1.2rem; cursor: pointer; transition: all 0.18s; position: relative; overflow: hidden;
  }
  .stat:hover { transform: translateY(-3px); background: var(--card-hover); border-color: var(--accent); box-shadow: var(--shadow); }
  .stat .ico { font-size: 1.3rem; opacity: 0.9; }
  .stat .value { font-size: 2rem; font-weight: 800; margin-top: 0.4rem; line-height: 1; }
  .stat .label { color: var(--muted); font-size: 0.85rem; margin-top: 0.35rem; }
  .stat .delta { font-size: 0.78rem; margin-top: 0.5rem; display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.1rem 0.45rem; border-radius: 999px; }
  .delta.up { color: var(--success); background: rgba(34,197,94,0.12); }
  .delta.down { color: var(--danger); background: rgba(239,68,68,0.12); }
  .stat.accent { background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(168,85,247,0.14)); border-color: rgba(129,140,248,0.4); }

  /* Changes banner */
  .changes { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.75rem; }
  .change-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.1rem; }
  .change-card .value { font-size: 1.5rem; font-weight: 700; }
  .change-card .label { color: var(--muted); font-size: 0.82rem; margin-top: 0.2rem; }
  .change-card.up { border-left: 3px solid var(--success); }
  .change-card.down { border-left: 3px solid var(--danger); }
  .change-card.clickable { cursor: pointer; transition: all 0.15s; }
  .change-card.clickable:hover { background: var(--card-hover); }

  /* Panel */
  .panel { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
  .panel-head { padding: 1.1rem 1.25rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
  .panel-head h2 { font-size: 1.15rem; display: flex; align-items: center; gap: 0.6rem; }
  .panel-head .desc { color: var(--muted); font-size: 0.85rem; width: 100%; margin-top: 0.15rem; }
  .search { margin-left: auto; position: relative; }
  .search input {
    background: var(--bg-soft); border: 1px solid var(--border); color: var(--text);
    border-radius: 10px; padding: 0.55rem 0.8rem 0.55rem 2.1rem; font-size: 0.9rem; width: 240px; outline: none;
  }
  .search input:focus { border-color: var(--accent); }
  .search .ico { position: absolute; left: 0.7rem; top: 50%; transform: translateY(-50%); color: var(--muted); }

  .list { max-height: 640px; overflow-y: auto; }
  .row {
    display: flex; align-items: center; gap: 0.9rem; padding: 0.7rem 1.25rem;
    border-bottom: 1px solid var(--border); transition: background 0.12s;
  }
  .row:hover { background: var(--card-hover); }
  .row:last-child { border-bottom: none; }
  .avatar {
    width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0;
    display: grid; place-items: center; font-weight: 700; color: #fff; font-size: 0.95rem;
  }
  .avatar-img {
    width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0; object-fit: cover;
  }
  .user-stats { color: var(--muted); font-size: 0.75rem; margin-left: 0.4rem; }
  .row .info { min-width: 0; }
  .row .uname { color: var(--muted); font-size: 0.82rem; }
  .row .fname { font-weight: 600; font-size: 0.92rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .row .idx { color: var(--muted); font-size: 0.8rem; width: 2rem; text-align: right; flex-shrink: 0; }
  .row.deactivated { opacity: 0.55; }
  .row.deactivated .avatar-img { filter: grayscale(1); }
  .dead-badge {
    display: inline-block; background: rgba(248,81,73,0.15); color: #f85149;
    font-size: 0.7rem; font-weight: 600; padding: 0.1rem 0.4rem;
    border-radius: 4px; margin-left: 0.3rem; white-space: nowrap;
  }
  .row .open {
    margin-left: auto; flex-shrink: 0; text-decoration: none; color: var(--accent);
    border: 1px solid var(--border); border-radius: 8px; padding: 0.35rem 0.7rem; font-size: 0.82rem; transition: all 0.15s;
  }
  .row .open:hover { background: var(--accent); color: #fff; border-color: var(--accent); }
  .empty { padding: 3rem 1.25rem; text-align: center; color: var(--muted); }
  .empty .big { font-size: 2.5rem; margin-bottom: 0.5rem; }

  .view { display: none; }
  .view.active { display: block; }

  .mobile-nav { display: none; }

  @media (max-width: 860px) {
    .sidebar { display: none; }
    .main { padding: 1rem 1rem 3rem; }
    .search input { width: 160px; }
    .mobile-nav { display: flex; gap: 0.5rem; overflow-x: auto; padding-bottom: 0.75rem; margin-bottom: 1rem; }
    .mobile-nav .nav-item { width: auto; white-space: nowrap; background: var(--card); }
  }

  .topbar-actions { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
  .version-switch {
    display: inline-flex; align-items: center; text-decoration: none;
    background: var(--card); border: 1px solid var(--border); color: var(--muted);
    padding: 0.4rem 0.8rem; border-radius: 999px; font-size: 0.85rem; transition: all 0.15s;
  }
  .version-switch:hover { color: #fff; border-color: var(--accent); background: var(--accent); }
  ::-webkit-scrollbar { width: 10px; height: 10px; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
  ::-webkit-scrollbar-thumb:hover { background: #3a4256; }
</style>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <div class="brand">
      <div class="logo">📸</div>
      <div>
        <div class="title">Instagram</div>
        <div class="subtitle">Tracker Dashboard</div>
      </div>
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
        <div class="pill">📅 <span id="date-pill"></span></div>
        <a class="version-switch" href="index.html">Новый вид →</a>
      </div>
    </div>

    <div class="period-bar" id="period-bar">
      <span class="label">Сравнить с:</span>
      <button class="period-btn" data-days="7">Неделя</button>
      <button class="period-btn" data-days="30">Месяц</button>
      <button class="period-btn" data-days="90">3 месяца</button>
      <button class="period-btn" data-days="180">6 месяцев</button>
      <button class="period-btn" data-days="365">Год</button>
      <button class="period-btn" data-days="99999">Всё время</button>
      <select class="period-select" id="period-select"><option value="">— конкретный снимок —</option></select>
      <span class="period-info" id="period-info"></span>
    </div>

    <div class="mobile-nav" id="mobile-nav"></div>
    <div id="views"></div>
  </main>
</div>

<script>
const DATA = __DATA__;

const TABS = [
  { key: "overview", label: "Обзор", ico: "📊", group: "Главное" },
  { key: "not_following_back", label: "Не подписаны на меня", ico: "💔", group: "Анализ", desc: "Вы подписаны на них, но они не подписаны на вас." },
  { key: "fans", label: "Фанаты", ico: "⭐", group: "Анализ", desc: "Подписаны на вас, но вы не подписаны на них." },
  { key: "mutual", label: "Взаимные", ico: "🤝", group: "Анализ", desc: "Вы подписаны друг на друга." },
  { key: "new_followers", label: "Новые подписчики", ico: "🆕", group: "Изменения", desc: "Подписались на вас за выбранный период.", requiresChanges: true },
  { key: "lost_followers", label: "Отписались от меня", ico: "📉", group: "Изменения", desc: "Отписались от вас за выбранный период.", requiresChanges: true },
  { key: "new_following", label: "Новые подписки", ico: "➕", group: "Изменения", desc: "Вы подписались на них за выбранный период.", requiresChanges: true },
  { key: "lost_following", label: "Вы отписались", ico: "➖", group: "Изменения", desc: "Вы отписались от них за выбранный период.", requiresChanges: true },
  { key: "followers", label: "Подписчики", ico: "👥", group: "Списки" },
  { key: "following", label: "Подписки", ico: "➕", group: "Списки" },
  { key: "recently_unfollowed", label: "Недавно отписаны", ico: "🚪", group: "Списки", desc: "Профили, от которых вы недавно отписались." },
  { key: "recent_follow_requests", label: "Заявки", ico: "📨", group: "Списки", desc: "Отправленные заявки в подписчики." },
  { key: "hide_story_from", label: "Скрыты истории", ico: "🙈", group: "Списки", desc: "Люди, от которых скрыты ваши истории." },
  { key: "blocked", label: "Заблокированы", ico: "🚫", group: "Списки" },
];

const AVATAR_COLORS = ["#6366f1","#a855f7","#ec4899","#f43f5e","#f59e0b","#10b981","#14b8a6","#38bdf8","#8b5cf6","#0ea5e9"];
function avatarColor(name){ let h=0; for(let i=0;i<name.length;i++) h=name.charCodeAt(i)+((h<<5)-h); return AVATAR_COLORS[Math.abs(h)%AVATAR_COLORS.length]; }
function initials(user){ return (user.full_name||user.username||"?").trim().charAt(0).toUpperCase(); }
function esc(s){ return (s||"").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

let searchState = {};
let currentCompare = null;  // snapshot object or null
let currentTab = "overview";

/* ---- Change computation (client-side) ---- */
function computeChanges(compareSnap){
  if (!compareSnap) return null;
  const curF = new Set(DATA.lists.followers.map(u => u.username));
  const curG = new Set(DATA.lists.following.map(u => u.username));
  const prevF = new Set(compareSnap.followers.map(u => u.username));
  const prevG = new Set(compareSnap.following.map(u => u.username));
  const newFollowers = DATA.lists.followers.filter(u => !prevF.has(u.username));
  const lostFollowers = compareSnap.followers.filter(u => !curF.has(u.username));
  const newFollowing = DATA.lists.following.filter(u => !prevG.has(u.username));
  const lostFollowing = compareSnap.following.filter(u => !curG.has(u.username));
  return {
    previous_date: compareSnap.date,
    new_followers: newFollowers,
    lost_followers: lostFollowers,
    new_following: newFollowing,
    lost_following: lostFollowing,
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

/* ---- Period selection ---- */
function findSnapshotByDays(days){
  const cur = new Date(DATA.date);
  const target = new Date(cur); target.setDate(target.getDate() - days);
  // find snapshot closest to target date but before current
  const candidates = DATA.snapshots.filter(s => s.date < DATA.date);
  if (candidates.length === 0) return null;
  let best = candidates[0], bestDiff = Infinity;
  for (const s of candidates){
    const sd = new Date(s.date);
    const diff = Math.abs(sd - target);
    if (diff < bestDiff){ bestDiff = diff; best = s; }
  }
  return best;
}

function setCompareByDays(days){
  const snap = findSnapshotByDays(days);
  currentCompare = snap;
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
  el.textContent = "Снимок от " + currentCompare.date + " (" + days + " дн.)";
}

/* ---- Rendering ---- */
function renderRows(key, users, filter){
  const q = (filter||"").toLowerCase().trim();
  const filtered = q
    ? users.filter(u => u.username.toLowerCase().includes(q) || (u.full_name||"").toLowerCase().includes(q))
    : users;
  if (filtered.length === 0){
    if (users.length === 0) return '<div class="empty"><div class="big">🎉</div>Список пуст</div>';
    return '<div class="empty"><div class="big">🔍</div>Ничего не найдено</div>';
  }
  return filtered.map((u, i) => {
    const dead = u.status === 'deactivated';
    const rowClass = dead ? 'row deactivated' : 'row';
    const avatar = u.avatar_url
      ? `<img class="avatar-img" src="${esc(u.avatar_url)}" alt="" onerror="this.style.display='none';this.nextElementSibling.style.display='grid'"><div class="avatar" style="background:${avatarColor(u.username)};display:none">${esc(initials(u))}</div>`
      : `<div class="avatar" style="background:${avatarColor(u.username)}">${esc(initials(u))}</div>`;
    const stats = (u.followers_count || u.following_count || u.posts_count)
      ? `<span class="user-stats">${u.followers_count||'—'} подп. · ${u.posts_count||'—'} пост.</span>`
      : '';
    const badge = dead ? ' <span class="dead-badge">⚠ деактивирован</span>' : '';
    return `
    <div class="${rowClass}">
      <div class="idx">${i+1}</div>
      ${avatar}
      <div class="info">
        <div class="fname">${esc(u.full_name) || '&nbsp;'} ${stats}${badge}</div>
        <div class="uname">@${esc(u.username)}</div>
      </div>
      <a class="open" href="https://www.instagram.com/${encodeURIComponent(u.username)}/" target="_blank" rel="noopener">Открыть ↗</a>
    </div>`;
  }).join("");
}

function listView(tab){
  const source = tab.requiresChanges ? changeLists() : DATA.lists;
  const users = source[tab.key] || [];
  const desc = tab.desc ? `<div class="desc">${tab.desc}</div>` : "";
  return `
    <div class="panel">
      <div class="panel-head">
        <h2>${tab.ico} ${tab.label} <span class="pill">${users.length}</span></h2>
        <div class="search">
          <span class="ico">🔍</span>
          <input type="text" placeholder="Поиск..." oninput="onSearch('${tab.key}', this.value)" value="${esc(searchState[tab.key]||'')}">
        </div>
        ${desc}
      </div>
      <div class="list" id="list-${tab.key}">${renderRows(tab.key, users, searchState[tab.key])}</div>
    </div>`;
}

function onSearch(key, value){
  searchState[key] = value;
  const tab = TABS.find(t => t.key === key);
  const source = tab && tab.requiresChanges ? changeLists() : DATA.lists;
  const el = document.getElementById("list-"+key);
  if (el) el.innerHTML = renderRows(key, source[key]||[], value);
}

function statCard(key, label, ico, value, opts={}){
  const cls = opts.accent ? "stat accent" : "stat";
  let delta = "";
  if (opts.delta !== undefined && opts.delta !== null){
    const up = opts.delta >= 0;
    delta = `<div class="delta ${up?'up':'down'}">${up?'▲':'▼'} ${Math.abs(opts.delta)}</div>`;
  }
  return `<div class="${cls}" onclick="go('${key}')">
    <div class="ico">${ico}</div>
    <div class="value">${value}</div>
    <div class="label">${label}</div>
    ${delta}
  </div>`;
}

function overviewView(){
  const c = DATA.counts;
  const ch = currentCompare ? computeChanges(currentCompare) : null;
  const fDelta = ch ? ch.new_followers.length - ch.lost_followers.length : null;
  const gDelta = ch ? ch.new_following.length - ch.lost_following.length : null;

  let changesHtml = "";
  if (ch){
    changesHtml = `
      <h3 style="margin:0.5rem 0 0.75rem;color:var(--muted);font-size:0.9rem;text-transform:uppercase;letter-spacing:0.06em;">
        Изменения с ${ch.previous_date}
      </h3>
      <div class="changes">
        <div class="change-card up clickable" onclick="go('new_followers')"><div class="value">+${ch.new_followers.length}</div><div class="label">Новые подписчики →</div></div>
        <div class="change-card down clickable" onclick="go('lost_followers')"><div class="value">−${ch.lost_followers.length}</div><div class="label">Отписались от вас →</div></div>
        <div class="change-card up clickable" onclick="go('new_following')"><div class="value">+${ch.new_following.length}</div><div class="label">Новые подписки →</div></div>
        <div class="change-card down clickable" onclick="go('lost_following')"><div class="value">−${ch.lost_following.length}</div><div class="label">Вы отписались →</div></div>
      </div>`;
  } else {
    changesHtml = `<div class="panel" style="padding:1.1rem 1.25rem;margin-bottom:1.75rem;color:var(--muted);">
      ℹ️ Нет снимка для сравнения. Сделайте новый экспорт позже, чтобы увидеть, кто подписался и отписался.
    </div>`;
  }

  const stats = [
    statCard("followers","Подписчики","👥",c.followers,{delta:fDelta}),
    statCard("following","Подписки","➕",c.following,{delta:gDelta}),
    statCard("mutual","Взаимные","🤝",c.mutual),
    statCard("not_following_back","Не подписаны на меня","💔",c.not_following_back,{accent:true}),
    statCard("fans","Фанаты","⭐",c.fans,{accent:true}),
    statCard("recently_unfollowed","Недавно отписаны","🚪",c.recently_unfollowed),
    statCard("recent_follow_requests","Заявки","📨",c.recent_follow_requests),
    statCard("hide_story_from","Скрыты истории","🙈",c.hide_story_from),
    statCard("blocked","Заблокированы","🚫",c.blocked),
  ].join("");

  return `<div class="stats">${stats}</div>${changesHtml}`;
}

function visibleTabs(){
  return TABS.filter(t => !t.requiresChanges || hasChanges());
}

function renderNav(){
  const nav = document.getElementById("nav");
  const mnav = document.getElementById("mobile-nav");
  let lastGroup = null, navHtml = "";
  visibleTabs().forEach(tab => {
    if (tab.group !== lastGroup){ navHtml += `<div class="nav-group-label">${tab.group}</div>`; lastGroup = tab.group; }
    const source = tab.requiresChanges ? changeLists() : DATA.lists;
    const badge = tab.key === "overview" ? "" : `<span class="badge">${(source[tab.key]||[]).length}</span>`;
    navHtml += `<button class="nav-item" data-tab="${tab.key}" onclick="go('${tab.key}')"><span class="ico">${tab.ico}</span>${tab.label}${badge}</button>`;
  });
  nav.innerHTML = navHtml;
  mnav.innerHTML = visibleTabs().map(tab =>
    `<button class="nav-item" data-tab="${tab.key}" onclick="go('${tab.key}')"><span class="ico">${tab.ico}</span>${tab.label}</button>`
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
  // restore active tab if still visible, else overview
  if (!visibleTabs().find(t => t.key === currentTab)) currentTab = "overview";
  go(currentTab, true);
}

function go(key, skipScroll){
  if (!visibleTabs().find(t => t.key === key)) key = "overview";
  currentTab = key;
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  const view = document.getElementById("view-"+key);
  if (view) view.classList.add("active");
  document.querySelectorAll(".nav-item").forEach(n => n.classList.toggle("active", n.dataset.tab === key));
  history.replaceState(null, "", "#"+key);
  if (!skipScroll) window.scrollTo({top:0, behavior:"smooth"});
}

/* ---- Init ---- */
function initPeriodBar(){
  const bar = document.getElementById("period-bar");
  const select = document.getElementById("period-select");

  if (DATA.snapshots.length === 0){
    bar.classList.add("hidden");
    return;
  }

  // populate dropdown
  DATA.snapshots.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.date;
    opt.textContent = s.date + " (" + s.followers.length + " подп., " + s.following.length + " подписок)";
    select.appendChild(opt);
  });

  // period buttons
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

  // default: previous snapshot
  const prev = DATA.snapshots.filter(s => s.date < DATA.date).pop();
  if (prev){
    currentCompare = prev;
    // activate "Всё время" if prev is the oldest, else just set dropdown
    select.value = prev.date;
    updatePeriodInfo();
  }
}

function init(){
  document.getElementById("account").textContent = "Аккаунт: @" + DATA.username;
  document.getElementById("meta").textContent = `${DATA.counts.followers} подписчиков · ${DATA.counts.following} подписок`;
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
