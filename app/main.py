from datetime import date
from pathlib import Path
from typing import Optional

import typer

from app.config import Settings
from app.dashboard import save_dashboard
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
) -> None:
    """Parse Instagram export JSON files and generate an HTML dashboard."""
    settings = _load_settings()
    target_date = date.fromisoformat(snapshot_date) if snapshot_date else date.today()

    parser = ExportParser(import_dir or IMPORT_DIR)
    snapshot = parser.parse()
    snapshot.date = target_date

    save_snapshot(snapshot)
    all_snapshots = list_snapshots()

    save_dashboard(snapshot, all_snapshots, settings.target_username, output)
    typer.echo(f"Dashboard saved to {output}")
    typer.echo(f"Followers: {len(snapshot.followers)}")
    typer.echo(f"Following: {len(snapshot.following)}")


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
