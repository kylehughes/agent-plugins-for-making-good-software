#!/usr/bin/env python3
"""Validate the plugin marketplace structure documented in AGENTS.md.

This script checks, across the whole repository:

1. JSON validity of the two marketplace manifests and every plugin manifest.
2. Consistency between the Claude marketplace, the Codex marketplace, and
   each plugin's own `plugin.json` files (name, version, description, and
   that the referenced source directories exist).
3. That every non-empty `plugins/*/skills/*/` directory has a `SKILL.md`
   whose frontmatter `name` matches the directory name and whose
   `description` is a valid, one-line JSON-compatible double-quoted scalar.
4. That a skill's identity fields (frontmatter `name`, the body's `# ` H1,
   and the leading clause of `description`) stay free of OS/SDK version
   numbers, per AGENTS.md's "Version-free identity" rule.
5. That every skill ships `agents/openai.yaml` with the Codex interface
   fields AGENTS.md requires.
6. Link integrity of relative Markdown links and backticked
   references/scripts/examples/assets/evals paths inside each SKILL.md.
7. That every agent under `plugins/<p>/agents/*.md` has frontmatter whose
   `name` matches its filename stem, whose `skills:` entries exist as
   sibling skill directories, and whose optional `model:`/`effort:` values
   are non-empty and documented by a non-empty `## Model Selection` section
   when either is present.
8. That every file under a skill's `references/` directory is mentioned
   somewhere in that skill's SKILL.md (no orphan reference files).
9. That each plugin's skill and agent names appear in the top-level
   README.md, and that kebab-case names found in README tables correspond
   to real skills or agents on disk.
10. That any plugin whose content changed since the git base ref also had
    its `version` bumped, and that the new version did not go backwards or
    sideways.
11. That skill and agent descriptions use one-line JSON-compatible strings
    and stay within the repository's editorial character budgets.

Caveat: this repository intentionally avoids third-party dependencies, so
there is no PyYAML available. Frontmatter (in SKILL.md and agent files) and
`agents/openai.yaml` are parsed with small hand-written, line-oriented
parsers rather than a real YAML parser. The openai.yaml check in particular
is substring-based: it only confirms the required keys and the
`$<skill-name>` token appear somewhere in the file, not that the YAML is
well-formed.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Extend this pattern to teach every check about new platform/SDK version
# vocabulary (for example a new OS name or toolchain). It matches tokens
# like "iOS 17", "Xcode 16.0", or a bare "6.3.2" version number.
VERSION_TOKEN_RE = re.compile(
    r"(?:iOS|iPadOS|macOS|watchOS|tvOS|visionOS|Swift|Xcode|SDK)\s*\d[\d.]*"
    r"|\b\d+\.\d+(?:\.\d+)?\b"
)

REPO_ROOT = Path(__file__).resolve().parent.parent

Finding = tuple[str, str]


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> tuple[object | None, str | None]:
    if not path.exists():
        return None, "file does not exist"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as error:
        return None, f"invalid JSON ({error})"


def _split_frontmatter(text: str) -> tuple[list[str], str] | None:
    """Split leading `---` frontmatter lines from the rest of the body."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], "\n".join(lines[index + 1 :])
    return None


def _parse_frontmatter_fields(frontmatter_lines: list[str]) -> dict[str, str]:
    """Parse a flat set of `key: value` frontmatter fields.

    Supports plain scalars, single/double-quoted scalars, and YAML folded
    (`>`/`>-`) or literal (`|`/`|-`) block scalars whose continuation lines
    are more indented than the key line. Good enough for this repository's
    SKILL.md and agent frontmatter; not a general YAML parser.
    """
    fields: dict[str, str] = {}
    index = 0
    while index < len(frontmatter_lines):
        line = frontmatter_lines[index]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in (">", ">-", ">+", "|", "|-", "|+"):
            folded = value.startswith(">")
            block_lines: list[str] = []
            index += 1
            while index < len(frontmatter_lines):
                next_line = frontmatter_lines[index]
                if next_line.strip() == "" or next_line.startswith((" ", "\t")):
                    block_lines.append(next_line.strip() if folded else next_line)
                    index += 1
                else:
                    break
            fields[key] = " ".join(block_lines) if folded else "\n".join(block_lines)
            continue
        if value.startswith('"'):
            # Descriptions are validated separately, but parsing must still
            # decode JSON escapes so catalog measurements reflect authored text.
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError:
                decoded = value[1:-1] if value.endswith('"') else value[1:]
            if isinstance(decoded, str):
                value = decoded
        elif len(value) >= 2 and value[0] == value[-1] and value[0] == "'":
            value = value[1:-1].replace("''", "'")
        else:
            # In YAML, an unquoted `#` starts a comment only at a whitespace
            # boundary. An embedded hash such as `C#` stays in the scalar.
            value = re.split(r"(?:^|\s+)#", value, maxsplit=1)[0].rstrip()
        fields[key] = value
        index += 1
    return fields


def _description_format_issue(frontmatter_lines: list[str]) -> str | None:
    """Return why a description is not an authored one-line JSON string."""
    for line in frontmatter_lines:
        match = re.match(r"^description:\s*(.*)$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if value == "" or value in (">", ">-", ">+", "|", "|-", "|+"):
            return "description must be a one-line double-quoted JSON string"
        if not value.startswith('"'):
            return "description must be a one-line double-quoted JSON string"
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return "description is not a valid JSON string"
        if not isinstance(decoded, str) or "\n" in decoded or "\r" in decoded:
            return "description must be a one-line double-quoted JSON string"
        return None
    return "description must be a one-line double-quoted JSON string"


def check_json_validity() -> list[Finding]:
    findings: list[Finding] = []
    paths = [
        REPO_ROOT / ".claude-plugin" / "marketplace.json",
        REPO_ROOT / ".agents" / "plugins" / "marketplace.json",
    ]
    for plugin_dir in sorted((REPO_ROOT / "plugins").glob("*")):
        if not plugin_dir.is_dir():
            continue
        paths.append(plugin_dir / ".claude-plugin" / "plugin.json")
        paths.append(plugin_dir / ".codex-plugin" / "plugin.json")
    for path in paths:
        _, error = _load_json(path)
        if error:
            findings.append((_rel(path), error))
    return findings


def check_marketplace_consistency() -> list[Finding]:
    findings: list[Finding] = []
    claude_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
    codex_path = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
    claude_data, claude_error = _load_json(claude_path)
    codex_data, codex_error = _load_json(codex_path)
    if claude_error or not isinstance(claude_data, dict):
        return findings  # Already reported by check_json_validity.
    if codex_error or not isinstance(codex_data, dict):
        return findings

    claude_entries = claude_data.get("plugins", [])
    if not isinstance(claude_entries, list):
        findings.append((_rel(claude_path), "'plugins' is not a list"))
        claude_entries = []

    claude_names: set[str] = set()
    for entry in claude_entries:
        if not isinstance(entry, dict):
            findings.append((_rel(claude_path), f"plugin entry is not an object: {entry!r}"))
            continue
        name = entry.get("name")
        source = entry.get("source")
        if not isinstance(name, str):
            findings.append((_rel(claude_path), f"plugin entry missing 'name': {entry!r}"))
            continue
        claude_names.add(name)

        if not isinstance(source, str):
            findings.append((_rel(claude_path), f"{name}: 'source' is not a string"))
            continue
        source_dir = (REPO_ROOT / source).resolve()
        if not source_dir.is_dir():
            findings.append((_rel(claude_path), f"{name}: source directory {source!r} does not exist"))
            continue

        for manifest_rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            manifest_path = source_dir / manifest_rel
            manifest_data, manifest_error = _load_json(manifest_path)
            if manifest_error or not isinstance(manifest_data, dict):
                continue  # Already reported by check_json_validity.
            for field in ("name", "version", "description"):
                claude_value = entry.get(field)
                manifest_value = manifest_data.get(field)
                if claude_value != manifest_value:
                    findings.append((
                        _rel(claude_path),
                        f"{name}: '{field}' ({claude_value!r}) does not match "
                        f"{_rel(manifest_path)} ({manifest_value!r})",
                    ))

    codex_entries = codex_data.get("plugins", [])
    if not isinstance(codex_entries, list):
        findings.append((_rel(codex_path), "'plugins' is not a list"))
        codex_entries = []

    codex_names: set[str] = set()
    for entry in codex_entries:
        if not isinstance(entry, dict):
            findings.append((_rel(codex_path), f"plugin entry is not an object: {entry!r}"))
            continue
        name = entry.get("name")
        if isinstance(name, str):
            codex_names.add(name)
        source = entry.get("source")
        if not isinstance(source, dict):
            findings.append((_rel(codex_path), f"{name}: 'source' is not an object"))
            continue
        path_value = source.get("path")
        if not isinstance(path_value, str):
            findings.append((_rel(codex_path), f"{name}: 'source.path' is not a string"))
            continue
        source_dir = (REPO_ROOT / path_value).resolve()
        if not source_dir.is_dir():
            findings.append((_rel(codex_path), f"{name}: source.path {path_value!r} does not exist"))

    if claude_names != codex_names:
        only_claude = sorted(claude_names - codex_names)
        only_codex = sorted(codex_names - claude_names)
        detail_parts = []
        if only_claude:
            detail_parts.append(f"only in Claude marketplace: {only_claude}")
        if only_codex:
            detail_parts.append(f"only in Codex marketplace: {only_codex}")
        findings.append((_rel(codex_path), "plugin name set does not match Claude marketplace (" + "; ".join(detail_parts) + ")"))

    return findings


def _iter_skill_dirs() -> list[Path]:
    skill_dirs = []
    for plugin_dir in sorted((REPO_ROOT / "plugins").glob("*")):
        skills_dir = plugin_dir / "skills"
        if not skills_dir.is_dir():
            continue
        for skill_dir in sorted(skills_dir.glob("*")):
            if skill_dir.is_dir() and any(skill_dir.iterdir()):
                skill_dirs.append(skill_dir)
    return skill_dirs


def _skill_frontmatter(skill_dir: Path) -> tuple[Path, dict[str, str] | None, str | None]:
    """Return (path, fields, body) for a skill's SKILL.md, or (path, None, None) if unusable."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return skill_md, None, None
    text = skill_md.read_text(encoding="utf-8")
    split = _split_frontmatter(text)
    if split is None:
        return skill_md, None, None
    frontmatter_lines, body = split
    return skill_md, _parse_frontmatter_fields(frontmatter_lines), body


def check_skill_shape() -> list[Finding]:
    findings: list[Finding] = []
    for skill_dir in _iter_skill_dirs():
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            findings.append((_rel(skill_dir), "missing SKILL.md"))
            continue
        text = skill_md.read_text(encoding="utf-8")
        split = _split_frontmatter(text)
        if split is None:
            findings.append((_rel(skill_md), "missing or malformed '---' frontmatter block"))
            continue
        frontmatter_lines, _body = split
        fields = _parse_frontmatter_fields(frontmatter_lines)
        name = fields.get("name", "")
        if name != skill_dir.name:
            findings.append((_rel(skill_md), f"frontmatter name {name!r} does not match directory name {skill_dir.name!r}"))
        description = fields.get("description", "")
        if not description.strip():
            findings.append((_rel(skill_md), "frontmatter 'description' is empty or missing"))
        format_issue = _description_format_issue(frontmatter_lines)
        if format_issue:
            findings.append((_rel(skill_md), format_issue))
    return findings


def check_version_free_identity() -> list[Finding]:
    findings: list[Finding] = []
    for skill_dir in _iter_skill_dirs():
        skill_md, fields, body = _skill_frontmatter(skill_dir)
        if fields is None or body is None:
            continue  # Already reported by check_skill_shape.

        name = fields.get("name", "")
        if VERSION_TOKEN_RE.search(name):
            findings.append((_rel(skill_md), f"frontmatter 'name' contains a version token: {name!r}"))

        h1 = ""
        for line in body.splitlines():
            if line.startswith("# "):
                h1 = line[2:].strip()
                break
        if h1 and VERSION_TOKEN_RE.search(h1):
            findings.append((_rel(skill_md), f"body H1 contains a version token: {h1!r}"))

        description = fields.get("description", "")
        leading_clause = description.split(". ", 1)[0]
        if VERSION_TOKEN_RE.search(leading_clause):
            findings.append((
                _rel(skill_md),
                f"description's leading clause contains a version token: {leading_clause!r}",
            ))
    return findings


def check_openai_yaml() -> list[Finding]:
    findings: list[Finding] = []
    for skill_dir in _iter_skill_dirs():
        openai_yaml = skill_dir / "agents" / "openai.yaml"
        if not openai_yaml.exists():
            findings.append((_rel(skill_dir), "missing agents/openai.yaml"))
            continue
        text = openai_yaml.read_text(encoding="utf-8")
        required_substrings = [
            "display_name:",
            "short_description:",
            "default_prompt:",
            f"${skill_dir.name}",
        ]
        for substring in required_substrings:
            if substring not in text:
                findings.append((_rel(openai_yaml), f"missing required content: {substring!r}"))
    return findings


_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_BACKTICK_PATH_RE = re.compile(
    r"`((?:references|scripts|examples|assets|evals)/[^`]+\.[A-Za-z0-9]+)`"
)


def check_link_integrity() -> list[Finding]:
    findings: list[Finding] = []
    for skill_dir in _iter_skill_dirs():
        skill_md, fields, body = _skill_frontmatter(skill_dir)
        if fields is None or body is None:
            continue  # Already reported by check_skill_shape.

        targets: list[str] = []
        for match in _MARKDOWN_LINK_RE.finditer(body):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            targets.append(target)
        for match in _BACKTICK_PATH_RE.finditer(body):
            targets.append(match.group(1))

        for target in targets:
            target_without_fragment = target.split("#", 1)[0]
            if not target_without_fragment:
                continue
            if "*" in target_without_fragment:
                continue  # Glob-style documentation reference, not a literal path.
            resolved = (skill_dir / target_without_fragment).resolve()
            if not resolved.exists():
                findings.append((_rel(skill_md), f"link target does not exist: {target!r}"))
    return findings


def check_agent_frontmatter() -> list[Finding]:
    findings: list[Finding] = []
    for plugin_dir in sorted((REPO_ROOT / "plugins").glob("*")):
        agents_dir = plugin_dir / "agents"
        skills_dir = plugin_dir / "skills"
        if not agents_dir.is_dir():
            continue
        for agent_md in sorted(agents_dir.glob("*.md")):
            text = agent_md.read_text(encoding="utf-8")
            split = _split_frontmatter(text)
            if split is None:
                findings.append((_rel(agent_md), "missing or malformed '---' frontmatter block"))
                continue
            frontmatter_lines, body = split
            fields = _parse_frontmatter_fields(frontmatter_lines)

            format_issue = _description_format_issue(frontmatter_lines)
            if format_issue:
                findings.append((_rel(agent_md), format_issue))
            if not fields.get("description", "").strip():
                findings.append((_rel(agent_md), "frontmatter 'description' is empty or missing"))

            name = fields.get("name", "")
            if name != agent_md.stem:
                findings.append((_rel(agent_md), f"frontmatter name {name!r} does not match filename stem {agent_md.stem!r}"))

            skills_value = fields.get("skills", "")
            for skill_name in (s.strip() for s in skills_value.split(",") if s.strip()):
                if not (skills_dir / skill_name).is_dir():
                    findings.append((_rel(agent_md), f"skills entry {skill_name!r} has no matching plugins/{plugin_dir.name}/skills/{skill_name} directory"))

            for message in _agent_model_selection_issues(frontmatter_lines, fields, body):
                findings.append((_rel(agent_md), message))
    return findings


def _agent_model_selection_issues(
    frontmatter_lines: list[str], fields: dict[str, str], body: str
) -> list[str]:
    """Validate optional model/effort overrides and their shared rationale."""
    declared = {
        key: any(re.match(rf"^\s*{key}\s*:", line) for line in frontmatter_lines)
        for key in ("model", "effort")
    }
    issues = [
        f"frontmatter '{key}' is empty"
        for key, present in declared.items()
        if present and not fields.get(key, "").strip()
    ]
    if any(declared.values()):
        section = re.search(r"(?ms)^##\s+Model Selection\s*$\n(.*?)(?=^##\s|\Z)", body)
        if section is None or not section.group(1).strip():
            issues.append("explicit 'model' or 'effort' requires a non-empty '## Model Selection' section")
    return issues


# These are repository editorial budgets for keeping discovery metadata useful
# in crowded host context windows. They are character counts, not vendor token
# or window limits, and do not claim that a host's budget will fit.
MAX_SKILL_DESCRIPTION_CHARS = 320
MAX_TOTAL_SKILL_DESCRIPTION_CHARS = 7000
MAX_AGENT_DESCRIPTION_CHARS = 300
MAX_TOTAL_AGENT_DESCRIPTION_CHARS = 2200


def check_description_budgets() -> list[Finding]:
    findings: list[Finding] = []
    skill_total = 0
    agent_total = 0
    for skill_dir in _iter_skill_dirs():
        _path, fields, _body = _skill_frontmatter(skill_dir)
        if fields is None:
            continue
        description = fields.get("description", "")
        skill_total += len(description)
        if len(description) > MAX_SKILL_DESCRIPTION_CHARS:
            findings.append((_rel(skill_dir / "SKILL.md"), f"description is {len(description)} characters; limit is {MAX_SKILL_DESCRIPTION_CHARS}"))

    for plugin_dir in sorted((REPO_ROOT / "plugins").glob("*")):
        for agent_md in sorted((plugin_dir / "agents").glob("*.md")):
            split = _split_frontmatter(agent_md.read_text(encoding="utf-8"))
            if split is None:
                continue
            fields = _parse_frontmatter_fields(split[0])
            description = fields.get("description", "")
            agent_total += len(description)
            if len(description) > MAX_AGENT_DESCRIPTION_CHARS:
                findings.append((_rel(agent_md), f"description is {len(description)} characters; limit is {MAX_AGENT_DESCRIPTION_CHARS}"))

    if skill_total > MAX_TOTAL_SKILL_DESCRIPTION_CHARS:
        findings.append((_rel(REPO_ROOT / "plugins"), f"skill descriptions total {skill_total} characters; limit is {MAX_TOTAL_SKILL_DESCRIPTION_CHARS}"))
    if agent_total > MAX_TOTAL_AGENT_DESCRIPTION_CHARS:
        findings.append((_rel(REPO_ROOT / "plugins"), f"agent descriptions total {agent_total} characters; limit is {MAX_TOTAL_AGENT_DESCRIPTION_CHARS}"))
    return findings


def check_reference_map_completeness() -> list[Finding]:
    findings: list[Finding] = []
    for skill_dir in _iter_skill_dirs():
        references_dir = skill_dir / "references"
        if not references_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        skill_text = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""
        for reference_md in sorted(references_dir.glob("*.md")):
            relative_path = f"references/{reference_md.name}"
            if relative_path not in skill_text and reference_md.name not in skill_text:
                findings.append((_rel(reference_md), "not mentioned anywhere in SKILL.md (orphan reference file)"))
    return findings


_KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)+$")


def _extract_readme_table_names(readme_text: str) -> set[str]:
    names: set[str] = set()
    for line in readme_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells:
            continue
        first_cell = cells[0].strip("`").strip()
        if _KEBAB_CASE_RE.match(first_cell):
            names.add(first_cell)
    return names


def check_readme_consistency() -> list[Finding]:
    findings: list[Finding] = []
    readme_path = REPO_ROOT / "README.md"
    if not readme_path.exists():
        return [(_rel(readme_path), "README.md does not exist")]
    readme_text = readme_path.read_text(encoding="utf-8")
    readme_names = _extract_readme_table_names(readme_text)

    disk_names: set[str] = set()
    for plugin_dir in sorted((REPO_ROOT / "plugins").glob("*")):
        for skill_dir in _iter_skill_dirs():
            if skill_dir.parent.parent == plugin_dir:
                disk_names.add(skill_dir.name)
                if skill_dir.name not in readme_text:
                    findings.append((_rel(readme_path), f"skill {skill_dir.name!r} is not mentioned in README.md"))
        agents_dir = plugin_dir / "agents"
        if agents_dir.is_dir():
            for agent_md in sorted(agents_dir.glob("*.md")):
                disk_names.add(agent_md.stem)
                if agent_md.stem not in readme_text:
                    findings.append((_rel(readme_path), f"agent {agent_md.stem!r} is not mentioned in README.md"))

    for name in sorted(readme_names - disk_names):
        findings.append((_rel(readme_path), f"README.md mentions {name!r}, which has no matching skill or agent on disk"))

    return findings


def _run_git(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def _git_base_ref() -> str | None:
    if os.environ.get("GITHUB_BASE_REF"):
        return f"origin/{os.environ['GITHUB_BASE_REF']}"
    if os.environ.get("GITHUB_ACTIONS"):
        return "HEAD~1"
    return None


def _git_changed_paths(base: str | None) -> list[str] | None:
    if base is None:
        # Local run: union of working-tree changes against HEAD.
        outputs = [
            _run_git(["diff", "--name-only"]),
            _run_git(["diff", "--cached", "--name-only"]),
            _run_git(["ls-files", "--others", "--exclude-standard"]),
        ]
        if any(output is None for output in outputs):
            return None
        paths: set[str] = set()
        for output in outputs:
            paths.update(line for line in output.splitlines() if line)
        return sorted(paths)

    output = _run_git(["diff", "--name-only", f"{base}...HEAD"])
    if output is None:
        output = _run_git(["diff", "--name-only", f"{base}..HEAD"])
    if output is None:
        return None
    return [line for line in output.splitlines() if line]


def check_version_bumped_on_change() -> list[Finding]:
    findings: list[Finding] = []
    if _run_git(["rev-parse", "--is-inside-work-tree"]) is None:
        return findings  # No git available; skip silently.

    base = _git_base_ref()
    if base is not None and _run_git(["rev-parse", "--verify", base]) is None:
        return findings  # Base ref does not resolve (e.g. shallow clone).

    changed_paths = _git_changed_paths(base)
    if changed_paths is None:
        return findings

    git_base = base if base is not None else "HEAD"
    for plugin_dir in sorted((REPO_ROOT / "plugins").glob("*")):
        if not plugin_dir.is_dir():
            continue
        plugin_name = plugin_dir.name
        prefix = f"plugins/{plugin_name}/"
        if not any(path.startswith(prefix) for path in changed_paths):
            continue

        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        manifest_rel = _rel(manifest_path)
        old_text = _run_git(["show", f"{git_base}:{manifest_rel}"])
        if old_text is None:
            continue  # New plugin (no old manifest to compare against).

        try:
            old_version = json.loads(old_text).get("version")
        except json.JSONDecodeError:
            continue

        current_data, current_error = _load_json(manifest_path)
        if current_error or not isinstance(current_data, dict):
            continue  # Already reported by check_json_validity.
        new_version = current_data.get("version")

        if not isinstance(old_version, str) or not isinstance(new_version, str):
            continue

        if old_version == new_version:
            findings.append((
                manifest_rel,
                f"content under plugins/{plugin_name}/ changed but version was not "
                f"bumped (run scripts/bump.py)",
            ))
            continue

        old_match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", old_version)
        new_match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", new_version)
        if old_match and new_match:
            old_tuple = tuple(int(part) for part in old_match.groups())
            new_tuple = tuple(int(part) for part in new_match.groups())
            if new_tuple <= old_tuple:
                findings.append((
                    manifest_rel,
                    f"version went backwards/sideways: {old_version!r} -> {new_version!r}",
                ))
    return findings


CHECKS = [
    ("JSON validity", check_json_validity),
    ("Marketplace consistency", check_marketplace_consistency),
    ("Skill shape", check_skill_shape),
    ("Version-free identity", check_version_free_identity),
    ("openai.yaml metadata", check_openai_yaml),
    ("Link integrity", check_link_integrity),
    ("Agent frontmatter", check_agent_frontmatter),
    ("Description budgets", check_description_budgets),
    ("Reference-map completeness", check_reference_map_completeness),
    ("README consistency", check_readme_consistency),
    ("Version bumped on change", check_version_bumped_on_change),
]


def main() -> int:
    all_findings: list[Finding] = []
    for _name, check in CHECKS:
        all_findings.extend(check())

    for path, message in all_findings:
        print(f"{path}: {message}")

    if all_findings:
        print(f"\n{len(all_findings)} finding(s).")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
