"""Background avatar fetcher — launched by generate command."""
import sys
import os
from datetime import date
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

LOG_PATH = PROJECT_ROOT / "data" / "fetch.log"


def log(msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    line = f"[{datetime.now().isoformat()}] {msg}"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


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

        result = enrich_profiles(snapshot, delay=2.0)

        log(f"Done: {result}")
        log("Background fetch finished")

    except Exception as e:
        import traceback
        log(f"FATAL: {e}")
        log(traceback.format_exc())


if __name__ == "__main__":
    main()
