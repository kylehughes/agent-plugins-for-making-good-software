#!/usr/bin/env python3
"""Bump a plugin's version across the three files that must stay in sync.

Usage: `python3 scripts/bump.py <plugin> <patch|minor|major>`

Updates, in place, without re-serializing the surrounding JSON:

- `plugins/<plugin>/.claude-plugin/plugin.json`
- `plugins/<plugin>/.codex-plugin/plugin.json`
- the matching `plugins` entry (matched by `name`) in
  `.claude-plugin/marketplace.json`

`.agents/plugins/marketplace.json` has no version fields and is left alone.
Run `python3 scripts/validate.py` after bumping to confirm consistency.
"""

from __future__ import annotations

import re
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _valid_plugin_names() -> list[str]:
    plugins_dir = REPO_ROOT / "plugins"
    return sorted(p.name for p in plugins_dir.glob("*") if p.is_dir())


def _parse_version(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"version {version!r} is not in X.Y.Z form")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _bump(version: tuple[int, int, int], part: str) -> tuple[int, int, int]:
    major, minor, patch = version
    if part == "patch":
        return major, minor, patch + 1
    if part == "minor":
        return major, minor + 1, 0
    if part == "major":
        return major + 1, 0, 0
    raise ValueError(f"unknown bump part {part!r}")


def _replace_single_version(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    needle = f'"version": "{old}"'
    count = text.count(needle)
    if count != 1:
        raise ValueError(f"expected exactly one {needle!r} in {path}, found {count}")
    path.write_text(text.replace(needle, f'"version": "{new}"', 1), encoding="utf-8")


def _replace_marketplace_version(path: Path, plugin: str, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    name_needle = f'"name": "{plugin}"'
    name_index = text.find(name_needle)
    if name_index == -1:
        raise ValueError(f"could not find {name_needle!r} in {path}")

    # Bound the search window to before the next "name": entry, so a
    # shared version string on another plugin is never touched.
    next_name_index = text.find('"name":', name_index + len(name_needle))
    window_end = next_name_index if next_name_index != -1 else len(text)
    window = text[name_index:window_end]

    version_needle = f'"version": "{old}"'
    version_index = window.find(version_needle)
    if version_index == -1:
        raise ValueError(
            f"could not find {version_needle!r} for plugin {plugin!r} in {path} "
            f"before the next 'name' entry"
        )

    absolute_index = name_index + version_index
    new_text = (
        text[:absolute_index]
        + f'"version": "{new}"'
        + text[absolute_index + len(version_needle) :]
    )
    path.write_text(new_text, encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: python3 scripts/bump.py <plugin> <patch|minor|major>", file=sys.stderr)
        return 2

    plugin, part = sys.argv[1], sys.argv[2]
    valid_names = _valid_plugin_names()
    if plugin not in valid_names:
        print(
            f"error: unknown plugin {plugin!r}. Valid plugins: {', '.join(valid_names)}",
            file=sys.stderr,
        )
        return 2
    if part not in ("patch", "minor", "major"):
        print(f"error: unknown bump part {part!r}. Expected patch, minor, or major.", file=sys.stderr)
        return 2

    claude_plugin_path = REPO_ROOT / "plugins" / plugin / ".claude-plugin" / "plugin.json"
    codex_plugin_path = REPO_ROOT / "plugins" / plugin / ".codex-plugin" / "plugin.json"
    marketplace_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"

    try:
        current_data = json.loads(claude_plugin_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: could not read {claude_plugin_path}: {error}", file=sys.stderr)
        return 1

    old_version = current_data.get("version")
    if not isinstance(old_version, str):
        print(f"error: {claude_plugin_path} has no string 'version' field", file=sys.stderr)
        return 1

    try:
        old_tuple = _parse_version(old_version)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    new_tuple = _bump(old_tuple, part)
    new_version = f"{new_tuple[0]}.{new_tuple[1]}.{new_tuple[2]}"

    try:
        _replace_single_version(claude_plugin_path, old_version, new_version)
        _replace_single_version(codex_plugin_path, old_version, new_version)
        _replace_marketplace_version(marketplace_path, plugin, old_version, new_version)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    # Re-parse and assert the three versions now agree.
    touched_paths = [claude_plugin_path, codex_plugin_path, marketplace_path]
    for path in touched_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            print(f"error: {path} is not valid JSON after edit: {error}", file=sys.stderr)
            return 1

    claude_data = json.loads(claude_plugin_path.read_text(encoding="utf-8"))
    codex_data = json.loads(codex_plugin_path.read_text(encoding="utf-8"))
    marketplace_data = json.loads(marketplace_path.read_text(encoding="utf-8"))

    marketplace_version = None
    for entry in marketplace_data.get("plugins", []):
        if isinstance(entry, dict) and entry.get("name") == plugin:
            marketplace_version = entry.get("version")
            break

    versions = {
        _rel(claude_plugin_path): claude_data.get("version"),
        _rel(codex_plugin_path): codex_data.get("version"),
        _rel(marketplace_path): marketplace_version,
    }
    if any(version != new_version for version in versions.values()):
        print(f"error: version mismatch after bump: {versions}", file=sys.stderr)
        return 1

    print(f"{plugin}: {old_version} -> {new_version}")
    for path in touched_paths:
        print(f"  updated {_rel(path)}")
    print("Run python3 scripts/validate.py to confirm consistency.")
    return 0


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
