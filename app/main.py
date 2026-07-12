import sys
from datetime import date
from pathlib import Path
from typing import Optional

import typer

from app.config import Settings
from app.dashboard import save_dashboard
from app.enricher import enrich_profiles, get_profiles, get_stale_count
from app.parser import ExportParser
from app.storage import list_snapshots, save_snapshot

app = typer.Typer(help="Instagram Tracker")

CONFIG_PATH = Path("config/config.json")
IMPORT_DIR = Path("data/import")


def _load_settings() -> Settings:
    return Settings.load(CONFIG_PATH)


@app.command()
def generate(
    import_dir: Optional[Path] = typer.Option(
        None, "--import-dir", help="Path to folder with Instagram export JSON files"
    ),
    snapshot_date: Optional[str] = typer.Option(
        None, "--date", help="Snapshot date (YYYY-MM-DD)"
    ),
    output: Path = typer.Option(Path("index.html"), "--output", help="HTML output path"),
    no_fetch: bool = typer.Option(False, "--no-fetch", help="Skip avatar fetching"),
    delay: float = typer.Option(2.0, "--delay", help="Delay between avatar requests (seconds)"),
) -> None:
    """Parse Instagram export, generate dashboard, and fetch avatars."""
    settings = _load_settings()
    target_date = date.fromisoformat(snapshot_date) if snapshot_date else date.today()
    import_path = import_dir or IMPORT_DIR

    # 1. Parse export and save snapshot
    parser = ExportParser(import_path)
    snapshot = parser.parse()
    snapshot.date = target_date

    save_snapshot(snapshot)
    all_snapshots = list_snapshots()
    profiles = get_profiles()

    # 2. Generate initial dashboards V2 + V1 (with whatever avatars we already have)
    save_dashboard(snapshot, all_snapshots, settings.target_username, output, profiles)
    v1_path = output.parent / "index-v1.html"
    typer.echo(f"Dashboard V2 saved to {output}")
    typer.echo(f"Dashboard V1 saved to {v1_path}")
    typer.echo(f"Followers: {len(snapshot.followers)}")
    typer.echo(f"Following: {len(snapshot.following)}")
    if profiles:
        with_avatars = sum(1 for p in profiles.values() if p.get("avatar_local"))
        typer.echo(f"Profiles cache: {len(profiles)} ({with_avatars} with avatars)")

    # 3. Fetch avatars sequentially (same process, same console)
    if not no_fetch:
        stale = get_stale_count(snapshot)
        if stale > 0:
            typer.echo("")
            typer.echo(f"Fetching avatars for {stale} profiles (delay={delay}s)...")
            typer.echo("Dashboards will update every 10 profiles. Press Ctrl+C to stop.")
            typer.echo("")

            def on_progress(done: int, total: int) -> None:
                # Regenerate both dashboards so user can see avatars appearing
                fresh_profiles = get_profiles()
                save_dashboard(snapshot, all_snapshots, settings.target_username, output, fresh_profiles)
                typer.echo(f"  [{done}/{total}] Dashboards updated")

            try:
                result = enrich_profiles(snapshot, delay=delay, on_progress=on_progress)
                typer.echo("")
                typer.echo(f"Avatars: {result['fetched']} fetched, {result['failed']} failed, "
                           f"{result['skipped']} cached")

                # Final dashboard regeneration with all fresh avatars
                fresh_profiles = get_profiles()
                save_dashboard(snapshot, all_snapshots, settings.target_username, output, fresh_profiles)
                typer.echo(f"Dashboards regenerated with {len(fresh_profiles)} profiles.")
            except KeyboardInterrupt:
                typer.echo("")
                typer.echo("Interrupted! Saving what we have...")
                fresh_profiles = get_profiles()
                save_dashboard(snapshot, all_snapshots, settings.target_username, output, fresh_profiles)
                typer.echo("Dashboards saved with partial results.")
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
    """Fetch avatars and full names from Instagram profiles."""
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
