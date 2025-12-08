"""Typer CLI for Workout Tracker operator tasks.

Provides command-line utilities for seeding data, resetting the database,
exporting exercises, and generating reports.
"""

from typing import Optional
import json

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from services.frontend.src.client import (
    list_exercises,
    create_exercise,
    delete_exercise,
    get_exercise,
)

app = typer.Typer(
    name="workout-cli",
    help="🏋️ Workout Tracker CLI - Operator utilities for managing exercises",
    add_completion=False,
)

console = Console()


@app.command()
def list(
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, json, or csv"
    )
) -> None:
    """List all exercises in various formats.

    Args:
        format (str): Output format (table, json, or csv).
    """
    try:
        exercises = list_exercises()

        if not exercises:
            console.print("[yellow]No exercises found.[/yellow]")
            return

        if format == "json":
            print(json.dumps(exercises, indent=2))
        elif format == "csv":
            # Print CSV header
            print("id,name,sets,reps,weight")
            for ex in exercises:
                weight = ex.get("weight") or ""
                print(f"{ex['id']},{ex['name']},{ex['sets']},{ex['reps']},{weight}")
        else:  # table
            table = Table(title="💪 Workout Exercises", show_lines=True)
            table.add_column("ID", style="cyan", width=6)
            table.add_column("Exercise", style="green", width=20)
            table.add_column("Sets", style="yellow", width=8)
            table.add_column("Reps", style="yellow", width=8)
            table.add_column("Weight", style="magenta", width=10)

            for ex in exercises:
                weight_str = f"{ex.get('weight', 'N/A')} kg" if ex.get("weight") else "Bodyweight"
                table.add_row(
                    str(ex["id"]),
                    ex["name"],
                    str(ex["sets"]),
                    str(ex["reps"]),
                    weight_str,
                )

            console.print(table)
            console.print(f"\n[bold]Total:[/bold] {len(exercises)} exercises")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def add(
    name: str = typer.Argument(..., help="Exercise name"),
    sets: int = typer.Option(3, "--sets", "-s", help="Number of sets"),
    reps: int = typer.Option(10, "--reps", "-r", help="Number of reps"),
    weight: Optional[float] = typer.Option(None, "--weight", "-w", help="Weight in kg"),
) -> None:
    """Add a new exercise to the tracker.

    Args:
        name (str): The name of the exercise.
        sets (int): Number of sets (default: 3).
        reps (int): Number of reps (default: 10).
        weight (Optional[float]): Weight in kg (optional).
    """
    try:
        exercise = create_exercise(
            name=name,
            sets=sets,
            reps=reps,
            weight=weight,
        )
        console.print(
            f"[green]✓[/green] Created exercise: [bold]{exercise['name']}[/bold] "
            f"({exercise['sets']} sets × {exercise['reps']} reps)"
        )
        if exercise.get("weight"):
            console.print(f"  Weight: {exercise['weight']} kg")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def show(
    exercise_id: int = typer.Argument(..., help="Exercise ID to display")
) -> None:
    """Show details of a specific exercise.

    Args:
        exercise_id (int): The ID of the exercise to display.
    """
    try:
        exercise = get_exercise(exercise_id)

        table = Table(title=f"Exercise #{exercise_id}", show_header=False)
        table.add_column("Field", style="cyan", width=15)
        table.add_column("Value", style="green")

        table.add_row("ID", str(exercise["id"]))
        table.add_row("Name", exercise["name"])
        table.add_row("Sets", str(exercise["sets"]))
        table.add_row("Reps", str(exercise["reps"]))

        weight = exercise.get("weight")
        weight_str = f"{weight} kg" if weight else "Bodyweight"
        table.add_row("Weight", weight_str)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def remove(
    exercise_id: int = typer.Argument(..., help="Exercise ID to delete"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt"
    )
) -> None:
    """Delete an exercise from the tracker.

    Args:
        exercise_id (int): The ID of the exercise to delete.
        force (bool): Skip confirmation if True.
    """
    try:
        # Fetch exercise details first
        exercise = get_exercise(exercise_id)

        if not force:
            confirm = typer.confirm(
                f"Delete exercise '{exercise['name']}'?",
                default=False
            )
            if not confirm:
                console.print("[yellow]Cancelled.[/yellow]")
                return

        delete_exercise(exercise_id)
        console.print(f"[green]✓[/green] Deleted exercise: [bold]{exercise['name']}[/bold]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def seed(
    count: int = typer.Option(5, "--count", "-c", help="Number of sample exercises to create")
) -> None:
    """Seed the database with sample exercises.

    Args:
        count (int): Number of sample exercises to create (default: 5).
    """
    sample_exercises = [
        {"name": "Bench Press", "sets": 4, "reps": 8, "weight": 80.0},
        {"name": "Squat", "sets": 4, "reps": 10, "weight": 100.0},
        {"name": "Deadlift", "sets": 3, "reps": 5, "weight": 120.0},
        {"name": "Pull-ups", "sets": 3, "reps": 12, "weight": None},
        {"name": "Overhead Press", "sets": 3, "reps": 10, "weight": 50.0},
        {"name": "Barbell Row", "sets": 4, "reps": 10, "weight": 70.0},
        {"name": "Dips", "sets": 3, "reps": 15, "weight": None},
        {"name": "Lunges", "sets": 3, "reps": 12, "weight": 30.0},
        {"name": "Push-ups", "sets": 3, "reps": 20, "weight": None},
        {"name": "Bicep Curls", "sets": 3, "reps": 12, "weight": 15.0},
    ]

    try:
        with console.status(f"[bold green]Creating {count} sample exercises..."):
            for i in range(min(count, len(sample_exercises))):
                exercise_data = sample_exercises[i]
                create_exercise(**exercise_data)

        console.print(f"[green]✓[/green] Created {min(count, len(sample_exercises))} sample exercises")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def stats() -> None:
    """Display workout statistics and summary metrics."""
    try:
        exercises = list_exercises()

        if not exercises:
            console.print("[yellow]No exercises found.[/yellow]")
            return

        # Calculate stats
        total_exercises = len(exercises)
        total_sets = sum(ex.get("sets", 0) for ex in exercises)
        total_reps = sum(ex.get("sets", 0) * ex.get("reps", 0) for ex in exercises)

        weighted = [ex for ex in exercises if ex.get("weight") is not None]
        bodyweight = [ex for ex in exercises if ex.get("weight") is None]

        total_volume = sum(
            ex.get("sets", 0) * ex.get("reps", 0) * ex.get("weight", 0)
            for ex in weighted
        )

        avg_weight = (
            sum(ex.get("weight", 0) for ex in weighted) / len(weighted)
            if weighted else 0
        )

        # Display stats table
        table = Table(title="📊 Workout Statistics", show_header=False)
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="green", width=20)

        table.add_row("Total Exercises", str(total_exercises))
        table.add_row("Total Sets", str(total_sets))
        table.add_row("Total Reps", str(total_reps))
        table.add_row("", "")
        table.add_row("Weighted Exercises", str(len(weighted)))
        table.add_row("Bodyweight Exercises", str(len(bodyweight)))
        table.add_row("", "")
        table.add_row("Total Volume", f"{total_volume:.1f} kg")
        table.add_row("Avg Weight", f"{avg_weight:.1f} kg")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def export(
    output: str = typer.Option(
        "exercises.json",
        "--output",
        "-o",
        help="Output filename"
    )
) -> None:
    """Export all exercises to a JSON file.

    Args:
        output (str): Output filename (default: exercises.json).
    """
    try:
        exercises = list_exercises()

        with open(output, "w") as f:
            json.dump(exercises, f, indent=2)

        console.print(f"[green]✓[/green] Exported {len(exercises)} exercises to [bold]{output}[/bold]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

