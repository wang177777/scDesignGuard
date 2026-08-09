"""Stable command-line interface."""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .compiler import canonical_json, compile_contract, validate_contract
from .engine import evaluate_contract
from .privacy import is_safe_output_path, public_release_view
from .repair import propose_repairs
from .report import render_html


def _read(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write(path: str, content: str) -> None:
    if not is_safe_output_path(path):
        raise ValueError("output must be a safe relative POSIX path")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scdesignguard")
    parser.add_argument("--version", action="version", version=__version__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("compile", "verify", "repair", "filter-public", "validate-schema"):
        p = subs.add_parser(name)
        p.add_argument("input")
        p.add_argument("--output")
    p = subs.add_parser("report")
    p.add_argument("input")
    p.add_argument("--output", required=True)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source = _read(args.input)
        if args.command == "validate-schema":
            payload = {"valid": not validate_contract(source), "errors": validate_contract(source)}
        elif args.command == "compile":
            payload = compile_contract(source)
        elif args.command == "filter-public":
            payload = public_release_view(source)
        else:
            compiled = source if "contract" in source else compile_contract(source)
            result = evaluate_contract(compiled["contract"])
            if args.command == "verify":
                payload = result
            elif args.command == "repair":
                payload = propose_repairs(result)
            elif args.command == "report":
                _write(args.output, render_html(compiled, result))
                return 0
            else:
                raise AssertionError(args.command)
        text = canonical_json(payload)
        if getattr(args, "output", None):
            _write(args.output, text)
        else:
            sys.stdout.write(text)
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        sys.stderr.write(json.dumps({"error": type(exc).__name__, "message": str(exc)}, sort_keys=True) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
