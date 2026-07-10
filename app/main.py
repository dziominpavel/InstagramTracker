from datetime import date
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from app.clients.mock_client import MockClient
from app.clients.official_export_client import OfficialExportClient
from app.config import Settings, setup_logger
from app.repositories.json_repository import JsonRepository
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService
from app.services.sync_service import SyncService

app = typer.Typer(help="Instagram Tracker CLI")
console = Console()

CONFIG_PATH = Path("config/config.json")
IMPORT_DIR = Path("data/import")


def _load_settings() -> Settings:
    return Settings.load(CONFIG_PATH)


def _setup_logger(settings: Settings) -> None:
    setup_logger(settings.log_level)


def _parse_date(value: Optional[str]) -> Optional[date]:
    return date.fromisoformat(value) if value else None


@app.command()
def sync(
    mock: bool = typer.Option(False, "--mock", help="Use mock files for testing"),
    import_dir: Optional[Path] = typer.Option(
        None, "--import-dir", help="Path to folder with Instagram export JSON files"
    ),
    snapshot_date: Optional[str] = typer.Option(
        None, "--date", help="Snapshot date (YYYY-MM-DD)"
    ),
) -> None:
    """Import followers/following from Instagram export files in data/import."""
    settings = _load_settings()
    _setup_logger(settings)

    repo = JsonRepository(Path(settings.data_dir))
    report_service = ReportService(Path(settings.data_dir))

    if mock:
        client = MockClient(
            Path("data/mock/followers.json"), Path("data/mock/following.json")
        )
        source = "mock"
    else:
        import_path = import_dir or IMPORT_DIR
        client = OfficialExportClient(import_path)
        source = "official_export"

    service = SyncService(client, repo, report_service, settings.target_username)
    snapshot = service.run(snapshot_date=_parse_date(snapshot_date), source=source)

    console.print(f"[green]Snapshot saved: {snapshot.date}[/green]")
    console.print(f"  Followers: {len(snapshot.followers)}")
    console.print(f"  Following: {len(snapshot.following)}")


@app.command()
def status() -> None:
    """Show latest snapshot status."""
    settings = _load_settings()
    repo = JsonRepository(Path(settings.data_dir))
    snapshot = repo.get_latest_snapshot()

    if not snapshot:
        console.print("[red]No snapshots found.[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]Latest snapshot:[/bold] {snapshot.date}")
    console.print(f"  Followers: {len(snapshot.followers)}")
    console.print(f"  Following: {len(snapshot.following)}")
    console.print(f"  Source: {snapshot.source}")


@app.command()
def stats() -> None:
    """Show statistics for all snapshots."""
    settings = _load_settings()
    repo = JsonRepository(Path(settings.data_dir))
    snapshots = repo.list_snapshots()

    if not snapshots:
        console.print("[red]No snapshots found.[/red]")
        raise typer.Exit(1)

    table = Table(title="Snapshot Statistics")
    table.add_column("Date")
    table.add_column("Followers", justify="right")
    table.add_column("Following", justify="right")

    for snapshot in snapshots:
        table.add_row(
            str(snapshot.date),
            str(len(snapshot.followers)),
            str(len(snapshot.following)),
        )

    console.print(table)


@app.command()
def history(
    from_date: Optional[str] = typer.Option(None, "--from"),
    to_date: Optional[str] = typer.Option(None, "--to"),
) -> None:
    """Show changes between snapshots."""
    settings = _load_settings()
    repo = JsonRepository(Path(settings.data_dir))
    snapshots = repo.list_snapshots()

    if len(snapshots) < 2:
        console.print("[red]Need at least two snapshots for history.[/red]")
        raise typer.Exit(1)

    parsed_from = _parse_date(from_date)
    parsed_to = _parse_date(to_date)
    if parsed_from:
        snapshots = [s for s in snapshots if s.date >= parsed_from]
    if parsed_to:
        snapshots = [s for s in snapshots if s.date <= parsed_to]

    if len(snapshots) < 2:
        console.print("[red]Not enough snapshots in the selected range.[/red]")
        raise typer.Exit(1)

    prev, curr = snapshots[-2], snapshots[-1]
    events = AnalyticsService.diff(prev, curr)

    if not events:
        console.print("[green]No changes found.[/green]")
        return

    table = Table(title=f"Changes from {prev.date} to {curr.date}")
    table.add_column("Type")
    table.add_column("User")
    table.add_column("Old")
    table.add_column("New")

    for event in events:
        table.add_row(
            event.event_type,
            event.user.username,
            event.old_value or "",
            event.new_value or "",
        )

    console.print(table)


@app.command()
def report(
    report_date: Optional[str] = typer.Option(None, "--date"),
) -> None:
    """Show report for a given date."""
    settings = _load_settings()
    report_service = ReportService(Path(settings.data_dir))
    date_str = (_parse_date(report_date) or date.today()).isoformat()

    try:
        data = report_service.load(date_str)
    except FileNotFoundError:
        console.print(f"[red]Report not found for {date_str}.[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]Report for {data['date']}[/bold]")
    console.print(f"  Followers: {data['followers_count']}")
    console.print(f"  Following: {data['following_count']}")
    console.print(f"  Events: {len(data['events'])}")


@app.command()
def export(
    export_date: Optional[str] = typer.Option(None, "--date"),
    fmt: str = typer.Option("json", "--format"),
) -> None:
    """Export a snapshot to JSON or CSV."""
    settings = _load_settings()
    repo = JsonRepository(Path(settings.data_dir))
    date_str = (_parse_date(export_date) or date.today()).isoformat()
    snapshot = repo.load_snapshot(date_str)

    if not snapshot:
        console.print(f"[red]Snapshot not found for {date_str}.[/red]")
        raise typer.Exit(1)

    if fmt == "json":
        import json

        out = Path(f"snapshot_{date_str}.json")
        out.write_text(
            json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        console.print(f"[green]Exported to {out}[/green]")
    elif fmt == "csv":
        import csv

        out = Path(f"snapshot_{date_str}.csv")
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["type", "id", "username", "full_name"])
            for user in snapshot.followers:
                writer.writerow(["follower", user.id, user.username, user.full_name])
            for user in snapshot.following:
                writer.writerow(["following", user.id, user.username, user.full_name])
        console.print(f"[green]Exported to {out}[/green]")
    else:
        console.print("[red]Unsupported format. Use json or csv.[/red]")
        raise typer.Exit(1)


@app.command(name="config")
def show_config() -> None:
    """Show current configuration."""
    settings = _load_settings()
    console.print("[bold]Configuration[/bold]")
    console.print(f"  target_username: {settings.target_username}")
    console.print(f"  data_dir: {settings.data_dir}")
    console.print(f"  log_level: {settings.log_level}")
