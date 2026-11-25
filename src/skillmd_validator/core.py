"""Validator, link checker, path/secret scanner, and token estimator for SKILL.md agent packages."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HARDCODED_HOME_RE = re.compile(r"(?:[A-Za-z]:[\\/]Users[\\/]|/Users/|/home/)")
SECRET_RE = re.compile(r"(?:sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,})")


@dataclass(frozen=True)
class SkillAuditResult:
    valid: bool
    estimated_tokens: int
    errors: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4.0))


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw_fm, body = parts[1], parts[2]
    meta: dict[str, str] = {}
    current_key: str | None = None
    for line in raw_fm.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            k, v = line.split(":", 1)
            current_key = k.strip()
            val = v.strip().strip('"').strip("'")
            meta[current_key] = "" if val in (">-", "|", ">") else val
        elif current_key is not None:
            meta[current_key] = (meta[current_key] + " " + line.strip()).strip()
    return meta, body


def validate_skill_file(skill_md_path: str | Path, max_recommended_tokens: int = 4500) -> SkillAuditResult:
    p = Path(skill_md_path).resolve()
    text = p.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    meta, body = parse_frontmatter(text)
    if not meta:
        errors.append("Missing YAML frontmatter (`--- ... ---`) at top of SKILL.md.")
    else:
        name = meta.get("name", "")
        desc = meta.get("description", "")
        if not name or not KEBAB_RE.match(name):
            errors.append("Frontmatter 'name' must be non-empty kebab-case (e.g. 'edit-video').")
        if len(desc) < 25:
            errors.append("Frontmatter 'description' must be at least 25 characters explaining when to trigger the skill.")

    if HARDCODED_HOME_RE.search(text):
        errors.append("Hardcoded OS user home path detected; use portable $HOME or relative skill paths.")
    if SECRET_RE.search(text):
        errors.append("Potential hardcoded API key token detected inside SKILL.md.")

    for match in MD_LINK_RE.finditer(body):
        target = match.group(1).split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "conversation://", "file://")):
            continue
        resolved = (p.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"Broken relative link target: '{target}'")

    tokens = estimate_tokens(text)
    if tokens > max_recommended_tokens:
        warnings.append(f"SKILL.md is ~{tokens} tokens (> {max_recommended_tokens}); consider moving reference tables into references/.")

    return SkillAuditResult(valid=len(errors) == 0, estimated_tokens=tokens, errors=errors, warnings=warnings)
