"""Background avatar fetcher — launched by generate command."""
import sys
from datetime import date
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.enricher import enrich_profiles
from app.parser import ExportParser


def main():
    import_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/import")

    parser = ExportParser(import_dir)
    snapshot = parser.parse()
    snapshot.date = date.today()

    enrich_profiles(snapshot, delay=2.0)


if __name__ == "__main__":
    main()
