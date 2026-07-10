import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import typer

from app.config import Settings
from app.dashboard import save_dashboard
from app.enricher import get_profiles, get_stale_count
from app.parser import ExportParser
from app.storage import list_snapshots, save_snapshot

app = typer.Typer(help="Instagram Tracker")

CONFIG_PATH = Path("config/config.json")
IMPORT_DIR = Path("data/import")


def _load_settings() -> Settings:
    return Settings.load(CONFIG_PATH)


def _start_background_fetch(import_dir: Path) -> None:
    """Start avatar fetching in a detached background process."""
    # Use absolute path so the background process finds files regardless of cwd
    abs_import = import_dir.resolve()
    bg_script = str(Path(__file__).parent / "background_fetch.py")

    # Log file for the background process
    log_file = (Path(__file__).parent.parent / "data" / "fetch.log").open("a", encoding="utf-8")

    subprocess.Popen(
        [sys.executable, bg_script, str(abs_import)],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        close_fds=True,
        cwd=str(Path(__file__).parent.parent),
    )


@app.command()
def generate(
    import_dir: Optional[Path] = typer.Option(
        None, "--import-dir", help="Path to folder with Instagram export JSON files"
    ),
    snapshot_date: Optional[str] = typer.Option(
        None, "--date", help="Snapshot date (YYYY-MM-DD)"
    ),
    output: Path = typer.Option(Path("index.html"), "--output", help="HTML output path"),
    no_fetch: bool = typer.Option(False, "--no-fetch", help="Skip background avatar fetching"),
) -> None:
    """Parse Instagram export JSON files and generate an HTML dashboard."""
    settings = _load_settings()
    target_date = date.fromisoformat(snapshot_date) if snapshot_date else date.today()
    import_path = import_dir or IMPORT_DIR

    parser = ExportParser(import_path)
    snapshot = parser.parse()
    snapshot.date = target_date

    save_snapshot(snapshot)
    all_snapshots = list_snapshots()
    profiles = get_profiles()

    save_dashboard(snapshot, all_snapshots, settings.target_username, output, profiles)
    typer.echo(f"Dashboard saved to {output}")
    typer.echo(f"Followers: {len(snapshot.followers)}")
    typer.echo(f"Following: {len(snapshot.following)}")
    if profiles:
        with_avatars = sum(1 for p in profiles.values() if p.get("avatar_local"))
        typer.echo(f"Profiles cache: {len(profiles)} ({with_avatars} with avatars)")

    # Start background avatar fetching
    if not no_fetch:
        stale = get_stale_count(snapshot)
        if stale > 0:
            typer.echo(f"Starting background fetch for {stale} profiles...")
            _start_background_fetch(import_path)
            typer.echo("Avatars will be downloaded in the background.")
            typer.echo("Run 'generate' again later to update the dashboard.")
        else:
            typer.echo("All avatars are up to date.")


@app.command()
def fetch(
    import_dir: Optional[Path] = typer.Option(
        None, "--import-dir", help="Path to folder with Instagram export JSON files"
    ),
    delay: float = typer.Option(2.0, "--delay", help="Delay between requests in seconds"),
    limit: Optional[int] = typer.Option(
        None, "--limit", help="Max profiles to fetch (for testing)"
    ),
    force: bool = typer.Option(False, "--force", help="Re-fetch all profiles, even cached ones"),
) -> None:
    """Fetch avatars and full names from Instagram profiles (foreground)."""
    from app.enricher import enrich_profiles

    parser = ExportParser(import_dir or IMPORT_DIR)
    snapshot = parser.parse()
    snapshot.date = date.today()

    total_users = len({u.username for u in snapshot.followers + snapshot.following})
    typer.echo(f"Fetching profile data for {total_users} users...")
    typer.echo("")

    result = enrich_profiles(snapshot, delay=delay, limit=limit, force=force)

    typer.echo("")
    typer.echo(f"Done! Total: {result['total']}, Fetched: {result['fetched']}, "
               f"Skipped: {result['skipped']}, Failed: {result['failed']}")
    typer.echo("Run 'generate' to update the dashboard with avatars.")


@app.command()
def history() -> None:
    """List saved snapshots."""
    snapshots = list_snapshots()
    if not snapshots:
        typer.echo("No snapshots found.")
        raise typer.Exit(1)
    for snapshot in snapshots:
        typer.echo(f"{snapshot.date}: {len(snapshot.followers)} followers, {len(snapshot.following)} following")


@app.command(name="config")
def show_config() -> None:
    """Show current configuration."""
    settings = _load_settings()
    typer.echo(f"target_username: {settings.target_username}")
