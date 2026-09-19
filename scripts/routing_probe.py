#!/usr/bin/env python3
"""Export skill-routing prompts and grade model selections without invoking a model."""

import argparse
import json
import sys
from pathlib import Path


def load_json(path):
    try:
        with Path(path).open(encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON {path}: {error}") from error


def cases_from(value):
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError("cases must be an object with schema_version 1")
    cases = value.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty array")
    seen = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise ValueError("every case needs a string id")
        if case["id"] in seen:
            raise ValueError(f"duplicate case id: {case['id']}")
        seen.add(case["id"])
        if not isinstance(case.get("prompt"), str):
            raise ValueError(f"{case['id']}: prompt must be a string")
        for key in ("required", "forbidden"):
            if not isinstance(case.get(key), list) or not all(isinstance(x, str) for x in case[key]):
                raise ValueError(f"{case['id']}: {key} must be a string array")
        if "no_skills" in case and not isinstance(case["no_skills"], bool):
            raise ValueError(f"{case['id']}: no_skills must be boolean")
    return cases


def catalog_skills(value):
    if not isinstance(value, dict) or not isinstance(value.get("plugins"), dict):
        raise ValueError("catalog must contain a plugins object")
    skills = {}
    for plugin in value["plugins"].values():
        if not isinstance(plugin, dict):
            raise ValueError("catalog plugin must be an object")
        for skill in plugin.get("skills", []):
            if not isinstance(skill, dict) or not isinstance(skill.get("name"), str) or not isinstance(skill.get("description"), str):
                raise ValueError("catalog skills need name and description")
            if skill["name"] in skills:
                raise ValueError(f"duplicate catalog skill: {skill['name']}")
            skills[skill["name"]] = skill["description"]
    if not skills:
        raise ValueError("catalog contains no skills")
    return skills


def export_prompt(catalog, cases):
    lines = [
        "Select the smallest helpful set of applicable skills for each user request.",
        "Include legitimate companion skills when the request clearly needs them.",
        "Return JSON only in this shape: {\"selections\":[{\"id\":\"case-id\",\"skills\":[\"skill-name\"]}]}",
        "Do not answer the requests, use tools, or explain selections.",
        "",
        "Available skills (name and description):",
    ]
    for name, description in catalog.items():
        lines.append(f"- {name}: {description}")
    lines.append("")
    lines.append("Requests:")
    for case in cases:
        lines.append(f"[{case['id']}] {case['prompt']}")
    return "\n".join(lines) + "\n"


def grade(cases, response, known=None):
    errors = []
    if not isinstance(response, dict) or not isinstance(response.get("selections"), list):
        return {"score": 0, "missing": [], "forbidden": [], "errors": ["response must contain a selections array"]}
    expected = {case["id"]: case for case in cases}
    got = {}
    for item in response["selections"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(item.get("skills"), list) or not all(isinstance(x, str) for x in item["skills"]):
            errors.append("each selection needs string id and skills array")
            continue
        case_id = item["id"]
        if case_id in got:
            errors.append(f"duplicate response id: {case_id}")
        got[case_id] = item["skills"]
        if case_id not in expected:
            errors.append(f"unexpected response id: {case_id}")
        if known is not None:
            errors.extend(f"{case_id}: unknown skill {skill}" for skill in item["skills"] if skill not in known)
    missing_cases = [case["id"] for case in cases if case["id"] not in got]
    errors.extend(f"missing response id: {case_id}" for case_id in missing_cases)
    missing = []
    forbidden = []
    correct = 0
    for case in cases:
        selected = set(got.get(case["id"], []))
        absent = sorted(set(case["required"]) - selected)
        banned = sorted(set(case["forbidden"]) & selected)
        if case.get("no_skills") and selected:
            banned = sorted(selected)
        if absent:
            missing.append({"id": case["id"], "skills": absent})
        if banned:
            forbidden.append({"id": case["id"], "skills": banned})
        if case["id"] in got and not absent and not banned:
            correct += 1
    if errors:
        score = 0
    else:
        score = correct / len(cases) if cases else 0
    return {"score": score, "correct": correct, "total": len(cases), "missing": missing, "forbidden": forbidden, "errors": errors}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export")
    export.add_argument("--catalog", required=True)
    export.add_argument("--cases", required=True)
    export.add_argument("--output", required=True)
    grade_parser = sub.add_parser("grade")
    grade_parser.add_argument("--cases", required=True)
    grade_parser.add_argument("--responses", required=True)
    grade_parser.add_argument("--catalog")
    args = parser.parse_args()
    try:
        cases = cases_from(load_json(args.cases))
        if args.command == "export":
            prompt = export_prompt(catalog_skills(load_json(args.catalog)), cases)
            Path(args.output).write_text(prompt, encoding="utf-8")
        else:
            known = catalog_skills(load_json(args.catalog)) if args.catalog else None
            result = grade(cases, load_json(args.responses), known)
            print(json.dumps(result, indent=2, sort_keys=True))
            if result["errors"] or result["missing"] or result["forbidden"]:
                return 1
    except ValueError as error:
        print(f"routing_probe: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
