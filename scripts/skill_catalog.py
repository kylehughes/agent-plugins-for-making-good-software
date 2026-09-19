#!/usr/bin/env python3
"""Report repository skill and agent discovery metadata costs.

All measurements are Unicode characters or source lines, never tokens. The
report describes this repository's editorial costs and does not claim that any
particular Claude or Codex host window will fit them.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import validate


def _catalog_from_files(files: dict[str, str]) -> dict[str, Any]:
    """Build one catalog shape from canonical repository-relative files."""
    skills: list[dict[str, Any]] = []
    agents: list[dict[str, Any]] = []
    for path, text in sorted(files.items()):
        parts = Path(path).parts
        if len(parts) == 5 and parts[0] == "plugins" and parts[2] == "skills" and parts[4] == "SKILL.md":
            split = validate._split_frontmatter(text)
            if split is None:
                continue
            frontmatter, body = split
            fields = validate._parse_frontmatter_fields(frontmatter)
            description = fields.get("description", "")
            skills.append({"plugin": parts[1], "name": fields.get("name", parts[3]), "description": description, "description_chars": len(description), "body_chars": len(body), "body_lines": len(body.splitlines()), "path": path})

    skill_by_plugin_name = {(s["plugin"], s["name"]): s for s in skills}
    for path, text in sorted(files.items()):
        parts = Path(path).parts
        if len(parts) != 4 or parts[0] != "plugins" or parts[2] != "agents" or not parts[3].endswith(".md"):
            continue
        split = validate._split_frontmatter(text)
        if split is None:
            continue
        frontmatter, body = split
        fields = validate._parse_frontmatter_fields(frontmatter)
        description = fields.get("description", "")
        preload = [s.strip() for s in fields.get("skills", "").split(",") if s.strip()]
        preloaded = sum(skill_by_plugin_name.get((parts[1], name), {}).get("body_chars", 0) for name in preload)
        agents.append({"plugin": parts[1], "name": fields.get("name", Path(parts[3]).stem), "description": description, "description_chars": len(description), "path": path, "preload": preload, "preloaded_body_chars": preloaded, "body_chars": len(body), "body_lines": len(body.splitlines())})
    plugins = {plugin: {"skills": [s for s in skills if s["plugin"] == plugin], "agents": [a for a in agents if a["plugin"] == plugin]} for plugin in sorted({s["plugin"] for s in skills} | {a["plugin"] for a in agents})}
    return {
        "skills": skills,
        "agents": agents,
        "totals": {
            "skill_count": len(skills),
            "skill_description_chars": sum(s["description_chars"] for s in skills),
            "skill_body_chars": sum(s["body_chars"] for s in skills),
            "skill_body_lines": sum(s["body_lines"] for s in skills),
            "agent_count": len(agents),
            "agent_description_chars": sum(a["description_chars"] for a in agents),
            "agent_preloaded_body_chars": sum(a["preloaded_body_chars"] for a in agents),
        },
        "plugins": plugins,
    }


def _catalog(root: Path | None = None) -> dict[str, Any]:
    root = root or validate.REPO_ROOT
    files: dict[str, str] = {}
    for path in sorted((root / "plugins").glob("*/skills/*/SKILL.md")):
        files[str(path.relative_to(root))] = path.read_text(encoding="utf-8")
    for path in sorted((root / "plugins").glob("*/agents/*.md")):
        files[str(path.relative_to(root))] = path.read_text(encoding="utf-8")
    return _catalog_from_files(files)


def _git_files(ref: str) -> dict[str, str]:
    try:
        listing_result = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref], cwd=validate.REPO_ROOT, text=True, capture_output=True, check=False)
    except OSError as error:
        raise ValueError(f"could not read git baseline {ref!r}: {error}") from error
    if listing_result.returncode:
        raise ValueError(f"could not read git baseline {ref!r}: {listing_result.stderr.strip()}")
    result: dict[str, str] = {}
    for path in listing_result.stdout.splitlines():
        parts = Path(path).parts
        is_skill = len(parts) == 5 and parts[0] == "plugins" and parts[2] == "skills" and parts[4] == "SKILL.md"
        is_agent = len(parts) == 4 and parts[0] == "plugins" and parts[2] == "agents" and parts[3].endswith(".md")
        if not (is_skill or is_agent):
            continue
        try:
            blob = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=validate.REPO_ROOT, text=True, capture_output=True, check=False)
        except OSError as error:
            raise ValueError(f"could not read baseline file {path!r}: {error}") from error
        if blob.returncode:
            raise ValueError(f"could not read baseline file {path!r}: {blob.stderr.strip()}")
        result[path] = blob.stdout
    return result


def _catalog_from_git(ref: str) -> dict[str, Any]:
    return _catalog_from_files(_git_files(ref))


def _text_report(data: dict[str, Any], baseline: dict[str, Any] | None = None) -> str:
    totals = data["totals"]
    lines = [f"Skills: {totals['skill_count']} | description chars: {totals['skill_description_chars']} | body chars: {totals['skill_body_chars']} | body lines: {totals['skill_body_lines']}", f"Agents: {totals['agent_count']} | description chars: {totals['agent_description_chars']} | preloaded skill body chars: {totals['agent_preloaded_body_chars']}"]
    for plugin in sorted(data["plugins"]):
        p = data["plugins"][plugin]
        lines.append(f"{plugin}: {len(p['skills'])} skills, {sum(s['description_chars'] for s in p['skills'])} description chars, {len(p['agents'])} agents, {sum(a['description_chars'] for a in p['agents'])} agent description chars")
    longest_descriptions = sorted(data["skills"], key=lambda x: (-x["description_chars"], x["path"]))[:5]
    longest_bodies = sorted(data["skills"], key=lambda x: (-x["body_chars"], x["path"]))[:5]
    lines.append("Longest skill descriptions: " + ", ".join(f"{s['path']} ({s['description_chars']})" for s in longest_descriptions))
    lines.append("Longest skill bodies: " + ", ".join(f"{s['path']} ({s['body_chars']} chars/{s['body_lines']} lines)" for s in longest_bodies))
    if baseline:
        old = baseline["totals"]
        lines.append("Baseline delta: " + ", ".join(f"{key} {old.get(key, 0)} -> {totals.get(key, 0)}" for key in ("skill_count", "skill_description_chars", "skill_body_chars", "agent_count", "agent_description_chars", "agent_preloaded_body_chars")))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--base", metavar="REF", help="compare current measurements with tracked files at REF")
    args = parser.parse_args(argv)
    data = _catalog()
    try:
        baseline = _catalog_from_git(args.base) if args.base else None
    except ValueError as error:
        parser.error(str(error))
    if args.json:
        payload = dict(data)
        if baseline is not None:
            payload["baseline"] = baseline
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(_text_report(data, baseline))
    return 0


if __name__ == "__main__":
    sys.exit(main())
