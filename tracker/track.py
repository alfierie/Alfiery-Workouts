#!/usr/bin/env python3
"""Minimal workout tracker: log sets, then watch the numbers go up.

Data lives in log.csv next to this script.

    python3 track.py log bench 60 8 4
    python3 track.py progress
    python3 track.py history bench
    python3 track.py summary
    python3 track.py undo
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA = Path(__file__).resolve().parent / "log.csv"
FIELDS = ["date", "exercise", "weight_kg", "reps", "sets", "notes"]


@dataclass(frozen=True)
class Row:
    date: dt.date
    exercise: str
    weight: float
    reps: int
    sets: int
    notes: str = ""

    @property
    def volume(self) -> float:
        """Total kg moved: weight x reps x sets."""
        return self.weight * self.reps * self.sets

    @property
    def e1rm(self) -> float:
        """Estimated one-rep max (Epley)."""
        return self.weight * (1 + self.reps / 30)


def norm(name: str) -> str:
    return " ".join(name.lower().split())


def fmt(value: float, decimals: int = 1) -> str:
    """175.0 -> '175', 72.5 -> '72.5'."""
    rounded = round(value, decimals)
    return str(int(rounded)) if rounded == int(rounded) else f"{rounded:.{decimals}f}"


def load(path: Path) -> list[Row]:
    if not path.exists():
        return []
    rows: list[Row] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for line_no, record in enumerate(csv.DictReader(handle), start=2):
            if not record.get("exercise", "").strip():
                continue
            try:
                rows.append(
                    Row(
                        date=dt.date.fromisoformat(record["date"].strip()),
                        exercise=norm(record["exercise"]),
                        weight=float(record["weight_kg"]),
                        reps=int(record["reps"]),
                        sets=int(record["sets"]),
                        notes=(record.get("notes") or "").strip(),
                    )
                )
            except (ValueError, KeyError, TypeError):
                print(f"  ! skipping malformed row at line {line_no}", file=sys.stderr)
    return rows


def append(path: Path, row: Row) -> None:
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(
            {
                "date": row.date.isoformat(),
                "exercise": row.exercise,
                "weight_kg": fmt(row.weight),
                "reps": row.reps,
                "sets": row.sets,
                "notes": row.notes,
            }
        )


def rewrite(path: Path, rows: list[Row]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "date": row.date.isoformat(),
                    "exercise": row.exercise,
                    "weight_kg": fmt(row.weight),
                    "reps": row.reps,
                    "sets": row.sets,
                    "notes": row.notes,
                }
            )


def group_by_exercise(rows: list[Row]) -> dict[str, list[Row]]:
    grouped: dict[str, list[Row]] = defaultdict(list)
    for row in rows:
        grouped[row.exercise].append(row)
    return dict(grouped)


def sessions(rows: list[Row]) -> dict[dt.date, list[Row]]:
    """Best row per exercise, per calendar day."""
    per_day: dict[dt.date, dict[str, Row]] = defaultdict(dict)
    for row in rows:
        current = per_day[row.date].get(row.exercise)
        if current is None or row.e1rm > current.e1rm:
            per_day[row.date][row.exercise] = row
    return {day: list(by_ex.values()) for day, by_ex in sorted(per_day.items())}


# --------------------------------------------------------------------------- commands


def cmd_log(args: argparse.Namespace) -> int:
    if args.weight < 0:
        print("Weight can't be negative.", file=sys.stderr)
        return 1
    if args.reps < 1 or args.sets < 1:
        print("Reps and sets must be at least 1.", file=sys.stderr)
        return 1

    row = Row(
        date=args.date or dt.date.today(),
        exercise=norm(args.exercise),
        weight=args.weight,
        reps=args.reps,
        sets=args.sets,
        notes=args.notes or "",
    )
    append(args.data, row)

    previous = [r for r in load(args.data) if r.exercise == row.exercise][:-1]
    best = max((r.e1rm for r in previous), default=None)

    print(f"Logged  {row.date}  {row.exercise}: {fmt(row.weight)} kg x {row.reps} x {row.sets}")
    if best is not None:
        delta = row.e1rm - best
        if delta > 0.05:
            print(f"  New best set for {row.exercise}! e1RM {fmt(best)} -> {fmt(row.e1rm)} (+{fmt(delta)})")
        else:
            print(f"  e1RM {fmt(row.e1rm)}  (best so far: {fmt(best)})")
    return 0


def cmd_progress(args: argparse.Namespace) -> int:
    rows = load(args.data)
    if not rows:
        print("No entries yet. Start with:\n  python3 track.py log bench 60 8 4")
        return 0

    header = f"{'exercise':<22}{'sets':>5}{'best e1RM':>11}{'best set':>14}{'last':>12}  trend"
    print(header)
    print("-" * len(header))

    for name, entries in sorted(group_by_exercise(rows).items()):
        by_day = sessions(entries)
        days = sorted(by_day)
        best_e1rm = max(r.e1rm for r in entries)
        best_row = max(entries, key=lambda r: r.e1rm)
        last_day = days[-1]
        last_e1rm = max(r.e1rm for r in by_day[last_day])

        earlier = [max(r.e1rm for r in by_day[d]) for d in days[:-1]]
        if earlier:
            if last_e1rm > max(earlier) + 0.05:
                trend = "up"
            elif last_e1rm < max(earlier) - 0.05:
                trend = "down"
            else:
                trend = "flat"
        else:
            trend = "-"

        best_set = f"{fmt(best_row.weight)}x{best_row.reps}"
        print(
            f"{name:<22}{len(entries):>5}{fmt(best_e1rm):>11}"
            f"{best_set:>14}{last_day.isoformat():>12}  {trend}"
        )
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    rows = [r for r in load(args.data) if r.exercise == norm(args.exercise)]
    if not rows:
        print(f"No entries for '{norm(args.exercise)}'.")
        return 0

    header = f"{'date':<12}{'weight':>8}{'reps':>6}{'sets':>6}{'volume':>10}{'e1RM':>8}  notes"
    print(f"{norm(args.exercise)}\n{header}")
    print("-" * len(header))
    for row in sorted(rows, key=lambda r: r.date):
        print(
            f"{row.date.isoformat():<12}{fmt(row.weight):>8}{row.reps:>6}{row.sets:>6}"
            f"{fmt(row.volume, 0):>10}{fmt(row.e1rm):>8}  {row.notes}"
        )
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    rows = load(args.data)
    if not rows:
        print("No entries yet.")
        return 0

    header = f"{'date':<12}{'lifts':>6}{'sets':>6}{'volume (kg)':>13}   top lift"
    print(header)
    print("-" * len(header))
    for day, entries in sessions(rows).items():
        volume = sum(r.volume for r in entries)
        top = max(entries, key=lambda r: r.volume)
        print(
            f"{day.isoformat():<12}{len(entries):>6}{sum(r.sets for r in entries):>6}"
            f"{fmt(volume, 0):>13}   {top.exercise} ({fmt(top.weight)}x{top.reps}x{top.sets})"
        )
    return 0


def cmd_undo(args: argparse.Namespace) -> int:
    rows = load(args.data)
    if not rows:
        print("Nothing to undo.")
        return 0
    removed = rows.pop()
    rewrite(args.data, rows)
    print(f"Removed  {removed.date}  {removed.exercise}: {fmt(removed.weight)} kg x {removed.reps} x {removed.sets}")
    return 0


# --------------------------------------------------------------------------- cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="track.py",
        description="Log workouts and track progress.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(sub: argparse.ArgumentParser) -> argparse.ArgumentParser:
        sub.add_argument(
            "-d",
            "--data",
            type=Path,
            default=DEFAULT_DATA,
            help="path to the CSV log (default: %(default)s)",
        )
        return sub

    log = add_common(subparsers.add_parser("log", help="add an entry"))
    log.add_argument("exercise", help='exercise name, e.g. "bench press"')
    log.add_argument("weight", type=float, help="weight in kg")
    log.add_argument("reps", type=int, help="reps performed")
    log.add_argument("sets", type=int, nargs="?", default=3, help="number of sets (default: 3)")
    log.add_argument("--date", type=dt.date.fromisoformat, metavar="YYYY-MM-DD", help="defaults to today")
    log.add_argument("--notes", help="optional free-text note")
    log.set_defaults(func=cmd_log)

    progress = add_common(subparsers.add_parser("progress", help="best e1RM + trend per exercise"))
    progress.set_defaults(func=cmd_progress)

    history = add_common(subparsers.add_parser("history", help="every entry for one exercise"))
    history.add_argument("exercise")
    history.set_defaults(func=cmd_history)

    summary = add_common(subparsers.add_parser("summary", help="volume per session"))
    summary.set_defaults(func=cmd_summary)

    undo = add_common(subparsers.add_parser("undo", help="delete the most recent entry"))
    undo.set_defaults(func=cmd_undo)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
