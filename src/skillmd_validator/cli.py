"""CLI for skillmd-validator."""

from __future__ import annotations

import argparse
import json

from .core import validate_skill_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skillmd-check", description="Validate SKILL.md frontmatter, relative links, portability, and token budget.")
    parser.add_argument("skill_md", help="Path to SKILL.md")
    parser.add_argument("--max-tokens", type=int, default=4500)
    args = parser.parse_args(argv)

    res = validate_skill_file(args.skill_md, max_recommended_tokens=args.max_tokens)
    print(json.dumps(res.to_dict(), indent=2))
    return 0 if res.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
