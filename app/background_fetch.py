"""Background avatar fetcher — launched by generate command."""
import sys
import os
import json
from datetime import date
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

LOG_PATH = PROJECT_ROOT / "data" / "fetch.log"
CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"


def log(msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    line = f"[{datetime.now().isoformat()}] {msg}"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def _load_username() -> str:
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return config.get("target_username", "unknown")
    except Exception:
        return "unknown"


def _regenerate_dashboard(snapshot, import_dir: Path) -> None:
    """Regenerate index.html with updated avatar cache."""
    from app.dashboard import save_dashboard
    from app.enricher import get_profiles
    from app.storage import list_snapshots

    all_snapshots = list_snapshots()
    profiles = get_profiles()
    username = _load_username()

    # Write to temp file first, then rename (atomic-ish on Windows)
    output = PROJECT_ROOT / "index.html"
    tmp = PROJECT_ROOT / "index.html.tmp"

    save_dashboard(snapshot, all_snapshots, username, tmp, profiles)

    # Replace original
    if output.exists():
        output.unlink()
    tmp.rename(output)


def main():
    log("Background fetch started")
    log(f"Python: {sys.executable}")
    log(f"argv: {sys.argv}")
    log(f"cwd: {os.getcwd()}")

    try:
        from app.enricher import enrich_profiles
        from app.parser import ExportParser

        # Resolve import dir — use absolute path
        if len(sys.argv) > 1:
            import_dir = Path(sys.argv[1])
        else:
            import_dir = PROJECT_ROOT / "data" / "import"

        if not import_dir.is_absolute():
            import_dir = (PROJECT_ROOT / import_dir).resolve()

        log(f"import_dir: {import_dir}")
        log(f"exists: {import_dir.exists()}")

        if not import_dir.exists():
            log(f"ERROR: import dir does not exist: {import_dir}")
            return

        parser = ExportParser(import_dir)
        snapshot = parser.parse()
        snapshot.date = date.today()

        log(f"Snapshot: {len(snapshot.followers)} followers, {len(snapshot.following)} following")

        # Find the latest saved snapshot to use for regeneration
        from app.storage import list_snapshots
        all_snaps = list_snapshots()
        latest_snap = all_snaps[-1] if all_snaps else snapshot

        def on_progress(done: int, total: int) -> None:
            log(f"Progress: {done}/{total} — regenerating dashboard...")
            _regenerate_dashboard(latest_snap, import_dir)
            log(f"Dashboard updated ({done}/{total})")

        result = enrich_profiles(snapshot, delay=2.0, on_progress=on_progress)

        # Final regeneration
        log("Final dashboard regeneration...")
        _regenerate_dashboard(latest_snap, import_dir)

        log(f"Done: {result}")
        log("Background fetch finished")

    except Exception as e:
        import traceback
        log(f"FATAL: {e}")
        log(traceback.format_exc())


if __name__ == "__main__":
    main()
