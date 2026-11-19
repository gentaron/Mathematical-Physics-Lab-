"""Command line for the deep-tech radar (standard library only).

  python -m research.radar fetch    --config CONFIG --out DIR [--site] [--fixtures DIR]
  python -m research.radar rebuild  --config CONFIG --out DIR [--site]   # rescore, no network
  python -m research.radar search   "query" --data DIR/radar.json [--limit N] [--sort date] [--json]
  python -m research.radar validate --config CONFIG

Exit codes: 0 ok, 1 nothing reachable (archive kept), 2 bad input.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

try:  # imported as a package (research.radar / radar) or run from this directory
    from . import engine
except ImportError:  # pragma: no cover
    import engine  # type: ignore[no-redef]

HERE = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="radar", description="Hardened frontier-research feed searcher")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, text in (("fetch", "Fetch all sources and update the archive and feeds"),
                       ("rebuild", "Rescore the archive with the current config (no network)")):
        command = commands.add_parser(name, help=text)
        command.add_argument("--config", type=Path, default=HERE / "sources.json")
        command.add_argument("--out", type=Path, required=True)
        command.add_argument("--site", action="store_true", help="Also write the static index.html")
        if name == "fetch":
            command.add_argument("--fixtures", type=Path, help="Read <source-id>.xml files instead of the network")
    find = commands.add_parser("search", help="Search the archive")
    find.add_argument("query", nargs="?", default="")
    find.add_argument("--data", type=Path, required=True)
    find.add_argument("--limit", type=int, default=20)
    find.add_argument("--sort", choices=("rank", "date"), default="rank")
    find.add_argument("--json", action="store_true")
    check = commands.add_parser("validate", help="Validate a config file")
    check.add_argument("--config", type=Path, default=HERE / "sources.json")
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            config = engine.load_config(args.config)
            print(f"ok: {config['id']} — {len(config['sources'])} sources, {len(config['topics'])} topics, "
                  f"{len(config['allow_hosts'])} allowed hosts")
            return 0
        if args.command in ("fetch", "rebuild"):
            radar = engine.run(args.config, args.out, fixtures=getattr(args, "fixtures", None),
                               site=args.site, offline=args.command == "rebuild")
            health = radar["health"]
            print(f"{radar['radar']}: {len(radar['items'])} items, sources {health['ok']}/{health['sources']} ok "
                  f"-> {args.out}")
            if args.command == "fetch" and health["sources"] and health["ok"] == 0:
                print("no source was reachable; the previous archive was kept", file=sys.stderr)
                return 1
            return 0
        if args.command == "search":
            if not 1 <= args.limit <= 500:
                raise engine.RadarError("--limit must be in 1..500")
            radar = engine.load_archive_full(args.data)
            found = engine.search(radar, args.query, args.limit, sort=args.sort)
            if args.json:
                print(json.dumps({"query": args.query, "trust": engine.TRUST_LABEL, "items": found},
                                 ensure_ascii=False, indent=1))
            else:
                for item in found:
                    print(f"{item['date'][:10]}  {item['rank']:6.2f}  [{','.join(item['topics'])}]  {item['title']}")
                    print(f"            {item['url']}  ({' / '.join(item.get('source_names', []))})")
                print(f"-- {len(found)} result(s)")
            return 0
    except (engine.RadarError, ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
