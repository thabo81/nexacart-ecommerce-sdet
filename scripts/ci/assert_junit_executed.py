"""Fail CI when a pytest JUnit report shows tests were skipped, errored or never collected.

A green pytest exit code alone can hide skipped PostgreSQL tests (they skip when no database URL
is set). TEST-001 requires that tests are never represented as passing without execution evidence.
"""

import argparse
import sys
import xml.etree.ElementTree as ET


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assert a pytest JUnit XML report really ran tests."
    )
    parser.add_argument("report")
    parser.add_argument("--min-tests", type=int, default=1, help="minimum executed tests required")
    args = parser.parse_args(argv)

    root = ET.parse(args.report).getroot()  # noqa: S314 - input is our own pytest output, not untrusted
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    totals = {
        key: sum(int(s.get(key, 0)) for s in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    executed = totals["tests"] - totals["skipped"]
    print(f"{args.report}: {totals} executed={executed}")
    problems = []
    if totals["skipped"]:
        problems.append(f"{totals['skipped']} test(s) skipped")
    if totals["failures"] or totals["errors"]:
        problems.append(f"{totals['failures']} failure(s), {totals['errors']} error(s)")
    if executed < args.min_tests:
        problems.append(f"only {executed} executed (minimum {args.min_tests})")
    if problems:
        print("FAIL: " + "; ".join(problems))
        return 1
    print("PASS: tests were actually executed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
