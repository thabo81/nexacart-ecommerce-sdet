"""CLI: python -m app.seed {seed|reset|verify|assets|fixtures}. Never prints secrets."""

import argparse
import sys
import time
from collections.abc import Sequence

from sqlalchemy import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings
from app.persistence.session import create_db_engine
from app.seed import assets, catalogue
from app.seed.guard import SeedGuardError, assert_safe_environment
from app.seed.loader import apply_plan
from app.seed.plan import build_plan
from app.seed.reset import clear_scope
from app.seed.settings import SeedSettings
from app.seed.validate import validate_dataset
from app.seed.verify import (
    baseline_report,
    dumps,
    invariant_failures,
    seed_baseline_failures,
    seed_baseline_report,
    snapshot,
)


def _engine(settings: SeedSettings) -> tuple[Engine, str]:
    database = assert_safe_environment(settings)  # fails closed before any connection
    return create_db_engine(Settings()), database


def _static_checks() -> None:
    errors = validate_dataset()
    if errors:
        raise SeedGuardError("Dataset self-check failed: " + "; ".join(errors))


def _database_failures(conn: Connection) -> list[str]:
    """Combine expected-record completeness checks with relational/data invariants."""
    return seed_baseline_failures(seed_baseline_report(conn)) + invariant_failures(conn)


def cmd_seed(settings: SeedSettings) -> int:
    engine, database = _engine(settings)
    _static_checks()
    started = time.perf_counter()
    with engine.begin() as conn:
        inserted = apply_plan(conn, build_plan(), settings)
        failures = _database_failures(conn)
        if failures:
            raise SeedGuardError("Verification failed, rolled back: " + "; ".join(failures))
    print(
        f"seed ok (env={settings.app_env}, database={database}, "
        f"{time.perf_counter() - started:.2f}s)"
    )
    for table, count in inserted.items():
        print(f"  inserted {count:>4} {table}")
    return 0


def cmd_reset(settings: SeedSettings, confirmed: bool) -> int:
    if not confirmed:
        raise SeedGuardError(
            "reset is destructive within the seed/qa boundary; re-run with --confirm."
        )
    engine, database = _engine(settings)
    _static_checks()
    started = time.perf_counter()
    plan = build_plan()
    with engine.begin() as conn:
        deleted = clear_scope(conn, plan)
        inserted = apply_plan(conn, plan, settings)
        failures = _database_failures(conn)
        if failures:
            raise SeedGuardError(
                "Verification failed after reset, rolled back: " + "; ".join(failures)
            )
    elapsed = time.perf_counter() - started
    print(
        f"reset ok (env={settings.app_env}, database={database}) in {elapsed:.2f}s "
        "(NFR-027 target <= 30s)"
    )
    print("  deleted: " + ", ".join(f"{t}={n}" for t, n in deleted.items() if n))
    print("  reinserted: " + ", ".join(f"{t}={n}" for t, n in inserted.items() if n))
    return 0


def cmd_verify(settings: SeedSettings, with_snapshot: bool) -> int:
    engine, _ = _engine(settings)
    with engine.connect() as conn:
        seed_report = seed_baseline_report(conn)
        seed_failures = seed_baseline_failures(seed_report)
        relational_failures = invariant_failures(conn)
        out: dict[str, object] = {
            "report": baseline_report(conn),
            "seed_baseline": seed_report,
            "seed_baseline_failures": seed_failures,
            "invariant_failures": relational_failures,
        }
        if with_snapshot:
            out["snapshot"] = snapshot(conn)
    print(dumps(out))
    return 1 if seed_failures or relational_failures else 0


def cmd_assets(check: bool) -> int:
    if check:
        problems = assets.check_assets()
        print("assets ok" if not problems else "assets problems:\n  " + "\n  ".join(problems))
        return 1 if problems else 0
    print(f"wrote assets and manifest ({assets.write_assets()} entries)")
    return 0


def cmd_fixtures() -> int:
    print(
        "| Fixture | Product slug | Base SKU | Active | Variants (price minor : stock) |\n"
        "|---|---|---|---|---|"
    )
    for p in catalogue.all_products():
        if p.fixture:
            variants = "; ".join(
                f"{dict(v.options) or 'default'} {v.price_minor}:{v.stock}" for v in p.variants
            )
            print(f"| {p.fixture} | `{p.slug}` | `{p.base_sku}` | {p.active} | {variants} |")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m app.seed", description="NexaCart deterministic seed data (local/test only)."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed", help="idempotently insert the baseline dataset")
    reset = sub.add_parser(
        "reset", help="remove seed-owned and qa_ data inside the boundary, then re-seed"
    )
    reset.add_argument("--confirm", action="store_true", help="required acknowledgement")
    verify = sub.add_parser("verify", help="print baseline report and invariant results")
    verify.add_argument(
        "--snapshot", action="store_true", help="include per-table row counts and sha256"
    )
    asset = sub.add_parser("assets", help="(re)generate local SVG assets and provenance manifest")
    asset.add_argument(
        "--check", action="store_true", help="verify files are present and up to date"
    )
    sub.add_parser("fixtures", help="print the fixture catalogue as a Markdown table")
    args = parser.parse_args(argv)
    try:
        if args.command == "assets":
            return cmd_assets(args.check)
        if args.command == "fixtures":
            return cmd_fixtures()
        settings = SeedSettings()
        if args.command == "seed":
            return cmd_seed(settings)
        if args.command == "reset":
            return cmd_reset(settings, args.confirm)
        return cmd_verify(settings, args.snapshot)
    except SeedGuardError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except SQLAlchemyError as exc:
        # Class name only: driver messages and URLs can contain connection details.
        print(
            f"ERROR: database operation failed ({type(exc).__name__}); transaction rolled back.",
            file=sys.stderr,
        )
        return 3
