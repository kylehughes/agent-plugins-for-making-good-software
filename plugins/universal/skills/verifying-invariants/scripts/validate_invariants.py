#!/usr/bin/env python3
"""Validate an invariant manifest without running any declared checks.

This is intentionally a schema and local-reference validator.  Commands are
treated as opaque text so validating an untrusted manifest cannot execute it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any


KINDS = {"structural", "refined-value", "transition", "external"}
METHODS = {
    "static-analysis", "compiler-rejection", "boundary-test", "property-test",
    "transition-test", "integration-test", "artifact-inspection", "manual-review",
    "bounded-exploration", "formal-proof",
}
ROOT_FIELDS = {"schema_version", "invariants"}
INVARIANT_FIELDS = {"id", "statement", "kind", "scope", "authority", "boundaries", "assumptions", "checks"}
SCOPE_FIELDS = {"references"}
AUTHORITY_FIELDS = {"description", "references"}
REFERENCE_FIELDS = {"path", "symbol"}
CHECK_FIELDS = {"id", "method", "command", "artifact", "implementation", "limitations", "bounds"}
BOUNDARY_FIELDS = {"surfaces", "exclusions"}
BOUNDARY_SURFACES = {"construction", "decoding", "mutation", "transition", "external"}
BOUNDS_FIELDS = {"domain", "resource_limits"}
RESOURCE_LIMIT_FIELDS = {"max_states", "max_depth", "max_seconds"}


class DuplicateKeyError(ValueError):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


class Validator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.diagnostics: list[dict[str, str]] = []

    def error(self, path: str, code: str, message: str) -> None:
        self.diagnostics.append({"code": code, "message": message, "path": path})

    def object(self, value: Any, path: str) -> dict[str, Any] | None:
        if not isinstance(value, dict):
            self.error(path, "schema.type", "must be an object")
            return None
        return value

    def array(self, value: Any, path: str, *, allow_empty: bool = False) -> list[Any] | None:
        if not isinstance(value, list):
            self.error(path, "schema.type", "must be an array")
            return None
        if not allow_empty and not value:
            self.error(path, "schema.empty", "must not be empty")
        return value

    def string(self, value: Any, path: str, *, allow_empty: bool = False) -> str | None:
        if not isinstance(value, str):
            self.error(path, "schema.type", "must be a string")
            return None
        if not allow_empty and not value.strip():
            self.error(path, "schema.empty", "must not be empty")
        return value

    def fields(self, obj: dict[str, Any], allowed: set[str], required: set[str], path: str) -> None:
        for key in sorted(set(obj) - allowed):
            self.error(f"{path}/{key}", "schema.unknown-field", "is not allowed")
        for key in sorted(required - set(obj)):
            self.error(path, "schema.missing-field", f"missing required field '{key}'")

    def reference(self, value: Any, path: str) -> None:
        obj = self.object(value, path)
        if obj is None:
            return
        self.fields(obj, REFERENCE_FIELDS, {"path"}, path)
        raw_path = self.string(obj.get("path"), f"{path}/path")
        if "symbol" in obj:
            self.string(obj["symbol"], f"{path}/symbol")
        if raw_path is None or not raw_path.strip():
            return
        candidate = PurePosixPath(raw_path)
        if candidate.is_absolute() or ".." in candidate.parts:
            self.error(f"{path}/path", "reference.path", "must be a relative path contained by --root")
            return
        target = self.root.joinpath(*candidate.parts)
        if not target.exists():
            self.error(f"{path}/path", "reference.missing", f"does not exist under --root: {raw_path}")
            return
        try:
            target.resolve().relative_to(self.root)
        except ValueError:
            self.error(f"{path}/path", "reference.escape", "resolves outside --root")

    def references(self, value: Any, path: str, *, allow_empty: bool = False) -> None:
        values = self.array(value, path, allow_empty=allow_empty)
        if values is not None:
            for index, reference in enumerate(values):
                self.reference(reference, f"{path}/{index}")

    def text_list(self, value: Any, path: str, *, allow_empty: bool) -> None:
        values = self.array(value, path, allow_empty=allow_empty)
        if values is not None:
            for index, item in enumerate(values):
                self.string(item, f"{path}/{index}")

    def check(self, value: Any, path: str) -> str | None:
        obj = self.object(value, path)
        if obj is None:
            return None
        self.fields(obj, CHECK_FIELDS, {"id", "method", "limitations"}, path)
        check_id = self.string(obj.get("id"), f"{path}/id")
        method = self.string(obj.get("method"), f"{path}/method")
        if method is not None and method not in METHODS:
            self.error(f"{path}/method", "schema.value", f"must be one of: {', '.join(sorted(METHODS))}")
        has_command = "command" in obj
        has_artifact = "artifact" in obj
        if not has_command and not has_artifact:
            self.error(path, "check.evidence", "requires command and/or artifact")
        if has_command:
            self.string(obj["command"], f"{path}/command")
        if has_artifact:
            self.reference(obj["artifact"], f"{path}/artifact")
        if "implementation" in obj:
            self.reference(obj["implementation"], f"{path}/implementation")
        self.text_list(obj.get("limitations"), f"{path}/limitations", allow_empty=True)
        if method == "bounded-exploration":
            bounds = self.object(obj.get("bounds"), f"{path}/bounds")
            if bounds is not None:
                self.fields(bounds, BOUNDS_FIELDS, {"domain"}, f"{path}/bounds")
                self.string(bounds.get("domain"), f"{path}/bounds/domain")
                if "resource_limits" in bounds:
                    limits = self.object(bounds["resource_limits"], f"{path}/bounds/resource_limits")
                    if limits is not None:
                        self.fields(limits, RESOURCE_LIMIT_FIELDS, set(), f"{path}/bounds/resource_limits")
                        if not limits:
                            self.error(f"{path}/bounds/resource_limits", "schema.empty", "must not be empty when present")
                        for name in sorted(limits):
                            item = limits[name]
                            if not isinstance(item, int) or isinstance(item, bool) or item <= 0:
                                self.error(f"{path}/bounds/resource_limits/{name}", "bounds.value", "must be a positive integer")
        elif "bounds" in obj:
            self.error(f"{path}/bounds", "schema.unexpected-field", "is only allowed for bounded-exploration")
        if method == "formal-proof" and "implementation" not in obj:
            self.error(path, "formal-proof.implementation", "requires an implementation reference")
        return check_id

    def invariant(self, value: Any, path: str) -> str | None:
        obj = self.object(value, path)
        if obj is None:
            return None
        self.fields(obj, INVARIANT_FIELDS, INVARIANT_FIELDS, path)
        invariant_id = self.string(obj.get("id"), f"{path}/id")
        self.string(obj.get("statement"), f"{path}/statement")
        kind = self.string(obj.get("kind"), f"{path}/kind")
        if kind is not None and kind not in KINDS:
            self.error(f"{path}/kind", "schema.value", f"must be one of: {', '.join(sorted(KINDS))}")
        scope = self.object(obj.get("scope"), f"{path}/scope")
        if scope is not None:
            self.fields(scope, SCOPE_FIELDS, SCOPE_FIELDS, f"{path}/scope")
            self.references(scope.get("references"), f"{path}/scope/references")
        authority = self.object(obj.get("authority"), f"{path}/authority")
        if authority is not None:
            self.fields(authority, AUTHORITY_FIELDS, AUTHORITY_FIELDS, f"{path}/authority")
            self.string(authority.get("description"), f"{path}/authority/description")
            self.references(authority.get("references"), f"{path}/authority/references")
        boundaries = self.object(obj.get("boundaries"), f"{path}/boundaries")
        if boundaries is not None:
            self.fields(boundaries, BOUNDARY_FIELDS, BOUNDARY_FIELDS, f"{path}/boundaries")
            surfaces = self.array(boundaries.get("surfaces"), f"{path}/boundaries/surfaces")
            if surfaces is not None:
                for index, surface in enumerate(surfaces):
                    surface_path = f"{path}/boundaries/surfaces/{index}"
                    text = self.string(surface, surface_path)
                    if text is not None and text not in BOUNDARY_SURFACES:
                        self.error(surface_path, "schema.value", f"must be one of: {', '.join(sorted(BOUNDARY_SURFACES))}")
            self.text_list(boundaries.get("exclusions"), f"{path}/boundaries/exclusions", allow_empty=True)
        assumptions = obj.get("assumptions")
        self.text_list(assumptions, f"{path}/assumptions", allow_empty=True)
        checks = self.array(obj.get("checks"), f"{path}/checks")
        check_ids: set[str] = set()
        formal_proof = False
        if checks is not None:
            for index, item in enumerate(checks):
                item_path = f"{path}/checks/{index}"
                check_id = self.check(item, item_path)
                if check_id:
                    if check_id in check_ids:
                        self.error(f"{item_path}/id", "identity.duplicate-check", f"duplicate check id '{check_id}'")
                    check_ids.add(check_id)
                if isinstance(item, dict) and item.get("method") == "formal-proof":
                    formal_proof = True
        if formal_proof and isinstance(assumptions, list) and not assumptions:
            self.error(f"{path}/assumptions", "formal-proof.assumptions", "must be non-empty when a formal-proof check is declared")
        return invariant_id

    def validate(self, document: Any) -> list[dict[str, str]]:
        root = self.object(document, "")
        if root is None:
            return self.sorted_diagnostics()
        self.fields(root, ROOT_FIELDS, ROOT_FIELDS, "")
        if type(root.get("schema_version")) is not int or root.get("schema_version") != 1:
            self.error("/schema_version", "schema.version", "must equal 1")
        invariants = self.array(root.get("invariants"), "/invariants")
        invariant_ids: set[str] = set()
        if invariants is not None:
            for index, item in enumerate(invariants):
                item_path = f"/invariants/{index}"
                invariant_id = self.invariant(item, item_path)
                if invariant_id:
                    if invariant_id in invariant_ids:
                        self.error(f"{item_path}/id", "identity.duplicate-invariant", f"duplicate invariant id '{invariant_id}'")
                    invariant_ids.add(invariant_id)
        return self.sorted_diagnostics()

    def sorted_diagnostics(self) -> list[dict[str, str]]:
        return sorted(self.diagnostics, key=lambda item: (item["path"], item["code"], item["message"]))


def load_manifest(path: Path) -> tuple[Any, list[dict[str, str]]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys), []
    except FileNotFoundError:
        return None, [{"code": "manifest.missing", "message": f"file does not exist: {path}", "path": ""}]
    except IsADirectoryError:
        return None, [{"code": "manifest.not-file", "message": f"not a regular file: {path}", "path": ""}]
    except UnicodeDecodeError:
        return None, [{"code": "manifest.invalid-encoding", "message": "must be UTF-8", "path": ""}]
    except DuplicateKeyError as error:
        return None, [{"code": "manifest.duplicate-key", "message": f"duplicate JSON object key: {error}", "path": ""}]
    except json.JSONDecodeError as error:
        return None, [{"code": "manifest.invalid-json", "message": f"invalid JSON: {error.msg}", "path": ""}]
    except OSError as error:
        return None, [{"code": "manifest.unreadable", "message": f"cannot read manifest: {error.strerror or error}", "path": ""}]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an invariant manifest; declared commands are never executed.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, required=True, help="project root used to resolve manifest references")
    parser.add_argument("--json", action="store_true", help="write deterministic JSON diagnostics")
    args = parser.parse_args(argv)
    if not args.root.exists():
        diagnostics = [{"code": "root.missing", "message": f"root does not exist: {args.root}", "path": ""}]
    elif not args.root.is_dir():
        diagnostics = [{"code": "root.not-directory", "message": f"root is not a directory: {args.root}", "path": ""}]
    else:
        document, diagnostics = load_manifest(args.manifest)
    if not diagnostics:
        diagnostics = Validator(args.root).validate(document)
    valid = not diagnostics
    if args.json:
        print(json.dumps({"diagnostics": diagnostics, "valid": valid}, sort_keys=True, separators=(",", ":")))
    elif valid:
        print("Invariant manifest is well-formed. No declared checks were executed.")
    else:
        for diagnostic in diagnostics:
            location = diagnostic["path"] or "/"
            print(f"{location}: {diagnostic['code']}: {diagnostic['message']}", file=sys.stderr)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
