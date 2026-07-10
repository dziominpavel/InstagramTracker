from pathlib import Path
from typing import List, Optional, Tuple

from app.models import Snapshot, User


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Instagram Dashboard — {username}</title>
  <style>
    :root {{
      --bg: #f5f7fa;
      --card: #ffffff;
      --text: #1f2937;
      --muted: #6b7280;
      --accent: #4f46e5;
      --accent-light: #eef2ff;
      --danger: #ef4444;
      --warning: #f59e0b;
      --success: #10b981;
      --border: #e5e7eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    header {{
      background: var(--card);
      border-bottom: 1px solid var(--border);
      padding: 2rem 1rem;
      text-align: center;
    }}
    header h1 {{ margin: 0; font-size: 1.75rem; }}
    header p {{ margin: 0.5rem 0 0; color: var(--muted); }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 1rem;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1rem;
      margin: 1.5rem 0;
    }}
    .stat {{
      background: var(--card);
      border-radius: 12px;
      padding: 1.25rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      text-align: center;
    }}
    .stat .value {{
      font-size: 2rem;
      font-weight: 700;
      color: var(--accent);
    }}
    .stat .label {{
      color: var(--muted);
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }}
    .changes {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
      margin: 1.5rem 0;
    }}
    .change {{
      background: var(--card);
      border-radius: 12px;
      padding: 1rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      border-left: 4px solid var(--border);
    }}
    .change.gain {{ border-left-color: var(--success); }}
    .change.loss {{ border-left-color: var(--danger); }}
    .change .value {{
      font-size: 1.5rem;
      font-weight: 700;
    }}
    .change .label {{
      color: var(--muted);
      font-size: 0.875rem;
    }}
    .section {{
      background: var(--card);
      border-radius: 12px;
      padding: 1.25rem;
      margin: 1.5rem 0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .section h2 {{
      margin: 0 0 1rem;
      font-size: 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .section h2 .count {{
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--muted);
      background: var(--accent-light);
      padding: 0.25rem 0.75rem;
      border-radius: 999px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      padding: 0.75rem;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    a {{
      color: var(--accent);
      text-decoration: none;
    }}
    a:hover {{ text-decoration: underline; }}
    .empty {{
      color: var(--muted);
      font-style: italic;
      padding: 1rem 0;
    }}
    footer {{
      text-align: center;
      color: var(--muted);
      font-size: 0.875rem;
      padding: 2rem 1rem;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Instagram Dashboard</h1>
    <p>Аккаунт: <strong>{username}</strong> · Снимок: <strong>{date}</strong></p>
  </header>

  <div class="container">
    <div class="stats">
      <div class="stat"><div class="value">{followers}</div><div class="label">Подписчики</div></div>
      <div class="stat"><div class="value">{following}</div><div class="label">Подписки</div></div>
      <div class="stat"><div class="value">{blocked}</div><div class="label">Заблокированы</div></div>
      <div class="stat"><div class="value">{hidden}</div><div class="label">Скрыты из историй</div></div>
      <div class="stat"><div class="value">{recent_unfollows}</div><div class="label">Недавно отписаны</div></div>
      <div class="stat"><div class="value">{follow_requests}</div><div class="label">Заявки в подписчики</div></div>
    </div>

    {changes}

    {sections}
  </div>

  <footer>
    Сгенерировано Instagram Tracker
  </footer>
</body>
</html>"""


def _user_rows(users: List[User]) -> str:
    if not users:
        return '<tr><td colspan="2" class="empty">Список пуст</td></tr>'
    rows = []
    for user in users:
        link = f'<a href="https://www.instagram.com/{user.username}/" target="_blank">@{user.username}</a>'
        rows.append(f"<tr><td>{link}</td><td>{user.full_name or '—'}</td></tr>")
    return "\n".join(rows)


def _section(title: str, count: int, users: List[User]) -> str:
    return f"""<div class="section">
  <h2>{title} <span class="count">{count}</span></h2>
  <table>
    <thead><tr><th>Username</th><th>Имя</th></tr></thead>
    <tbody>
      {_user_rows(users)}
    </tbody>
  </table>
</div>"""


def _diff_text(current_ids: set, previous_ids: set) -> Tuple[int, int]:
    gained = len(current_ids - previous_ids)
    lost = len(previous_ids - current_ids)
    return gained, lost


def _changes_html(snapshot: Snapshot, previous: Optional[Snapshot]) -> str:
    if not previous:
        return ""
    f_gain, f_loss = _diff_text({u.id for u in snapshot.followers}, {u.id for u in previous.followers})
    g_gain, g_loss = _diff_text({u.id for u in snapshot.following}, {u.id for u in previous.following})
    return f"""<div class="changes">
  <div class="change gain"><div class="value">+{f_gain}</div><div class="label">Новых подписчиков</div></div>
  <div class="change loss"><div class="value">-{f_loss}</div><div class="label">Потерянных подписчиков</div></div>
  <div class="change gain"><div class="value">+{g_gain}</div><div class="label">Новых подписок</div></div>
  <div class="change loss"><div class="value">-{g_loss}</div><div class="label">Отписанных</div></div>
</div>"""


def generate_html(snapshot: Snapshot, previous: Optional[Snapshot], username: str) -> str:
    sections = [
        _section("Подписчики", len(snapshot.followers), snapshot.followers),
        _section("Подписки", len(snapshot.following), snapshot.following),
        _section("Заблокированные профили", len(snapshot.blocked), snapshot.blocked),
        _section("Скрыты из историй", len(snapshot.hide_story_from), snapshot.hide_story_from),
        _section("Недавно отписанные", len(snapshot.recently_unfollowed), snapshot.recently_unfollowed),
        _section("Заявки в подписчики", len(snapshot.recent_follow_requests), snapshot.recent_follow_requests),
    ]
    return HTML_TEMPLATE.format(
        username=username,
        date=snapshot.date.isoformat(),
        followers=len(snapshot.followers),
        following=len(snapshot.following),
        blocked=len(snapshot.blocked),
        hidden=len(snapshot.hide_story_from),
        recent_unfollows=len(snapshot.recently_unfollowed),
        follow_requests=len(snapshot.recent_follow_requests),
        changes=_changes_html(snapshot, previous),
        sections="\n".join(sections),
    )


def save_dashboard(snapshot: Snapshot, previous: Optional[Snapshot], username: str, out: Path = Path("index.html")) -> None:
    html = generate_html(snapshot, previous, username)
    out.write_text(html, encoding="utf-8")
