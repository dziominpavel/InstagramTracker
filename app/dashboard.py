import json
from pathlib import Path
from typing import Dict, List, Optional

from app.models import Snapshot, User


def _users_payload(users: List[User]) -> List[Dict[str, str]]:
    return [{"username": u.username, "full_name": u.full_name or ""} for u in users]


def _build_payload(snapshot: Snapshot, previous: Optional[Snapshot], username: str) -> dict:
    follower_ids = {u.id for u in snapshot.followers}
    following_ids = {u.id for u in snapshot.following}

    not_following_back = [u for u in snapshot.following if u.id not in follower_ids]
    fans = [u for u in snapshot.followers if u.id not in following_ids]
    mutual = [u for u in snapshot.followers if u.id in following_ids]

    changes = None
    if previous:
        prev_follower_ids = {u.id for u in previous.followers}
        prev_following_ids = {u.id for u in previous.following}
        new_followers = [u for u in snapshot.followers if u.id not in prev_follower_ids]
        lost_followers = [u for u in previous.followers if u.id not in follower_ids]
        new_following = [u for u in snapshot.following if u.id not in prev_following_ids]
        lost_following = [u for u in previous.following if u.id not in following_ids]
        changes = {
            "previous_date": previous.date.isoformat(),
            "new_followers": _users_payload(new_followers),
            "lost_followers": _users_payload(lost_followers),
            "new_following": _users_payload(new_following),
            "lost_following": _users_payload(lost_following),
        }

    return {
        "username": username,
        "date": snapshot.date.isoformat(),
        "counts": {
            "followers": len(snapshot.followers),
            "following": len(snapshot.following),
            "mutual": len(mutual),
            "not_following_back": len(not_following_back),
            "fans": len(fans),
            "blocked": len(snapshot.blocked),
            "hide_story_from": len(snapshot.hide_story_from),
            "recently_unfollowed": len(snapshot.recently_unfollowed),
            "recent_follow_requests": len(snapshot.recent_follow_requests),
        },
        "lists": {
            "not_following_back": _users_payload(not_following_back),
            "fans": _users_payload(fans),
            "mutual": _users_payload(mutual),
            "followers": _users_payload(snapshot.followers),
            "following": _users_payload(snapshot.following),
            "blocked": _users_payload(snapshot.blocked),
            "hide_story_from": _users_payload(snapshot.hide_story_from),
            "recently_unfollowed": _users_payload(snapshot.recently_unfollowed),
            "recent_follow_requests": _users_payload(snapshot.recent_follow_requests),
        },
        "changes": changes,
    }


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
    width: 264px;
    flex-shrink: 0;
    background: var(--bg-soft);
    border-right: 1px solid var(--border);
    padding: 1.5rem 1rem;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
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
  .row .info { min-width: 0; }
  .row .uname { font-weight: 600; font-size: 0.92rem; }
  .row .fname { color: var(--muted); font-size: 0.82rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .row .idx { color: var(--muted); font-size: 0.8rem; width: 2rem; text-align: right; flex-shrink: 0; }
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
      <div class="pill">📅 <span id="date-pill"></span></div>
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
  { key: "followers", label: "Подписчики", ico: "👥", group: "Списки" },
  { key: "following", label: "Подписки", ico: "➕", group: "Списки" },
  { key: "recently_unfollowed", label: "Недавно отписаны", ico: "🚪", group: "Списки", desc: "Профили, от которых вы недавно отписались." },
  { key: "recent_follow_requests", label: "Заявки", ico: "📨", group: "Списки", desc: "Отправленные заявки в подписчики." },
  { key: "hide_story_from", label: "Скрыты истории", ico: "🙈", group: "Списки", desc: "Люди, от которых скрыты ваши истории." },
  { key: "blocked", label: "Заблокированы", ico: "🚫", group: "Списки" },
];

const AVATAR_COLORS = [
  "#6366f1","#a855f7","#ec4899","#f43f5e","#f59e0b",
  "#10b981","#14b8a6","#38bdf8","#8b5cf6","#0ea5e9"
];
function avatarColor(name){
  let h = 0;
  for (let i=0;i<name.length;i++) h = name.charCodeAt(i) + ((h<<5)-h);
  return AVATAR_COLORS[Math.abs(h) % AVATAR_COLORS.length];
}
function initials(user){
  const src = (user.full_name || user.username || "?").trim();
  return src.charAt(0).toUpperCase();
}
function esc(s){ return (s||"").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

let searchState = {};

function renderRows(key, users, filter){
  const q = (filter||"").toLowerCase().trim();
  const filtered = q
    ? users.filter(u => u.username.toLowerCase().includes(q) || (u.full_name||"").toLowerCase().includes(q))
    : users;
  if (filtered.length === 0){
    if (users.length === 0)
      return '<div class="empty"><div class="big">🎉</div>Список пуст</div>';
    return '<div class="empty"><div class="big">🔍</div>Ничего не найдено</div>';
  }
  return filtered.map((u, i) => `
    <div class="row">
      <div class="idx">${i+1}</div>
      <div class="avatar" style="background:${avatarColor(u.username)}">${esc(initials(u))}</div>
      <div class="info">
        <div class="uname">@${esc(u.username)}</div>
        <div class="fname">${esc(u.full_name) || '&nbsp;'}</div>
      </div>
      <a class="open" href="https://www.instagram.com/${encodeURIComponent(u.username)}/" target="_blank" rel="noopener">Открыть ↗</a>
    </div>`).join("");
}

function listView(tab){
  const users = DATA.lists[tab.key] || [];
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
  const el = document.getElementById("list-"+key);
  if (el) el.innerHTML = renderRows(key, DATA.lists[key]||[], value);
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
  const ch = DATA.changes;
  const fDelta = ch ? ch.new_followers.length - ch.lost_followers.length : null;
  const gDelta = ch ? ch.new_following.length - ch.lost_following.length : null;

  let changesHtml = "";
  if (ch){
    changesHtml = `
      <h3 style="margin:0.5rem 0 0.75rem;color:var(--muted);font-size:0.9rem;text-transform:uppercase;letter-spacing:0.06em;">
        Изменения с ${ch.previous_date}
      </h3>
      <div class="changes">
        <div class="change-card up"><div class="value">+${ch.new_followers.length}</div><div class="label">Новые подписчики</div></div>
        <div class="change-card down"><div class="value">−${ch.lost_followers.length}</div><div class="label">Отписались от вас</div></div>
        <div class="change-card up"><div class="value">+${ch.new_following.length}</div><div class="label">Новые подписки</div></div>
        <div class="change-card down"><div class="value">−${ch.lost_following.length}</div><div class="label">Вы отписались</div></div>
      </div>`;
  } else {
    changesHtml = `<div class="panel" style="padding:1.1rem 1.25rem;margin-bottom:1.75rem;color:var(--muted);">
      ℹ️ Это первый снимок. Сделайте новый экспорт позже, чтобы увидеть, кто подписался и отписался.
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

function render(){
  document.getElementById("account").textContent = "Аккаунт: @" + DATA.username;
  document.getElementById("meta").textContent = `${DATA.counts.followers} подписчиков · ${DATA.counts.following} подписок`;
  document.getElementById("date-pill").textContent = DATA.date;

  // nav
  const nav = document.getElementById("nav");
  const mnav = document.getElementById("mobile-nav");
  let lastGroup = null;
  let navHtml = "";
  TABS.forEach(tab => {
    if (tab.group !== lastGroup){ navHtml += `<div class="nav-group-label">${tab.group}</div>`; lastGroup = tab.group; }
    const badge = tab.key === "overview" ? "" : `<span class="badge">${(DATA.lists[tab.key]||[]).length}</span>`;
    navHtml += `<button class="nav-item" data-tab="${tab.key}" onclick="go('${tab.key}')"><span class="ico">${tab.ico}</span>${tab.label}${badge}</button>`;
  });
  nav.innerHTML = navHtml;
  mnav.innerHTML = TABS.map(tab =>
    `<button class="nav-item" data-tab="${tab.key}" onclick="go('${tab.key}')"><span class="ico">${tab.ico}</span>${tab.label}</button>`
  ).join("");

  // views
  const views = document.getElementById("views");
  views.innerHTML = TABS.map(tab =>
    `<div class="view" id="view-${tab.key}">${tab.key === "overview" ? overviewView() : listView(tab)}</div>`
  ).join("");

  go(location.hash ? location.hash.slice(1) : "overview");
}

function go(key){
  if (!TABS.find(t => t.key === key)) key = "overview";
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  const view = document.getElementById("view-"+key);
  if (view) view.classList.add("active");
  document.querySelectorAll(".nav-item").forEach(n => n.classList.toggle("active", n.dataset.tab === key));
  history.replaceState(null, "", "#"+key);
  window.scrollTo({top:0, behavior:"smooth"});
}

render();
</script>
</body>
</html>"""


def generate_html(snapshot: Snapshot, previous: Optional[Snapshot], username: str) -> str:
    payload = _build_payload(snapshot, previous, username)
    data_json = json.dumps(payload, ensure_ascii=False)
    return HTML_TEMPLATE.replace("__DATA__", data_json)


def save_dashboard(snapshot: Snapshot, previous: Optional[Snapshot], username: str, out: Path = Path("index.html")) -> None:
    html = generate_html(snapshot, previous, username)
    out.write_text(html, encoding="utf-8")
