import json
import os
import py_compile
import shutil
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import invariant_behavior as behavior


ROOT = Path(__file__).resolve().parent.parent


CORRECT_IMPLEMENTATION = """\
import Foundation

struct Quantity: Codable, Equatable {
    let value: Int

    init?(_ value: Int) {
        guard value > 0 else { return nil }
        self.value = value
    }

    private enum CodingKeys: String, CodingKey {
        case value
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let value = try container.decode(Int.self, forKey: .value)
        guard let quantity = Quantity(value) else {
            throw DecodingError.dataCorruptedError(
                forKey: .value,
                in: container,
                debugDescription: "Quantity must be positive."
            )
        }
        self = quantity
    }
}
"""


SCALAR_REGRESSION = """\
import Foundation

struct Quantity: Codable, Equatable {
    let value: Int

    init?(_ value: Int) {
        guard value > 0 else { return nil }
        self.value = value
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let value = try container.decode(Int.self)
        guard let quantity = Quantity(value) else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Quantity must be positive."
            )
        }
        self = quantity
    }
}
"""


ROOT_DATA_CORRUPTED_IMPLEMENTATION = """\
import Foundation

struct Quantity: Codable, Equatable {
    let value: Int

    init?(_ value: Int) {
        guard value > 0 else { return nil }
        self.value = value
    }

    private enum CodingKeys: String, CodingKey { case value }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let value = try container.decode(Int.self, forKey: .value)
        guard let quantity = Quantity(value) else {
            throw DecodingError.dataCorrupted(
                .init(codingPath: decoder.codingPath, debugDescription: "Quantity must be positive.")
            )
        }
        self = quantity
    }
}
"""


ALWAYS_REJECT_IMPLEMENTATION = """\
import Foundation

enum QuantityError: Error { case rejected }

struct Quantity: Codable, Equatable {
    let value: Int

    init?(_ value: Int) {
        guard value > 0 else { return nil }
        self.value = value
    }

    init(from decoder: Decoder) throws {
        throw QuantityError.rejected
    }
}
"""


class InvariantBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def prepare(self, case_id="swift-decoding-write-apple"):
        workspace = self.root / "workspace"
        bundle_path = self.root / "bundle.json"
        bundle = behavior.prepare_case(case_id, workspace, ROOT)
        behavior.write_json(bundle_path, bundle)
        return workspace, bundle_path, bundle

    def write_outcome(self, bundle_path, bundle, *, status="completed", write_capable=True):
        response = self.root / "response.md"
        transcript = self.root / "transcript.jsonl"
        stderr = self.root / "stderr.txt"
        response.write_text("response", encoding="utf-8")
        transcript.write_text('{"type":"response"}\n', encoding="utf-8")
        stderr.write_text("", encoding="utf-8")
        outcome = {
            "schema_version": 1,
            "bundle_sha256": behavior.sha256_file(bundle_path),
            "case_id": bundle["case_id"],
            "prompt_sha256": bundle["prompt"]["sha256"],
            "plugin_snapshot_sha256": bundle["plugin_snapshot"]["sha256"],
            "runtime": {"name": "fixture", "version": "1"},
            "model": {"name": "fixture", "effort": "fixture"},
            "tools": {"available": ["Read", "Write"], "calls": [], "write_capable": write_capable},
            "execution": {"status": status, "exit_code": 0 if status == "completed" else 1, "duration_seconds": 0.1},
            "response": {"path": str(response), "sha256": behavior.sha256_file(response)},
            "transcript": {"path": str(transcript), "sha256": behavior.sha256_file(transcript)},
            "stderr": {"path": str(stderr), "sha256": behavior.sha256_file(stderr)},
        }
        outcome_path = self.root / "outcome.json"
        behavior.write_json(outcome_path, outcome)
        return outcome_path

    def write_swift_candidate(self, workspace, implementation):
        (workspace / "Sources/Quantity.swift").write_text(implementation, encoding="utf-8")
        tests = workspace / "Tests/main.swift"
        tests.write_text(
            tests.read_text(encoding="utf-8")
            + '''

let invalidSavedQuantity = Data(#"{"value":0}"#.utf8)
do {
    _ = try JSONDecoder().decode(Quantity.self, from: invalidSavedQuantity)
    fatalError("saved zero quantity must be rejected")
} catch {
    // The invalid keyed payload reached decoding and was rejected.
}
''',
            encoding="utf-8",
        )

    def python_bytecode_workspace(self, name, cached_source, current_source, test_source=None):
        self.assertEqual(len(cached_source.encode()), len(current_source.encode()))
        workspace = self.root / name
        (workspace / "Sources/__pycache__").mkdir(parents=True)
        (workspace / "Tests").mkdir()
        source = workspace / "Sources/quantity.py"
        fixed_ns = 1_700_000_000_000_000_000
        source.write_text(cached_source, encoding="utf-8")
        os.utime(source, ns=(fixed_ns, fixed_ns))
        cache = workspace / "Sources/__pycache__" / f"quantity.cpython-{behavior.sys.version_info.major}{behavior.sys.version_info.minor}.pyc"
        py_compile.compile(str(source), cfile=str(cache), doraise=True)
        source.write_text(current_source, encoding="utf-8")
        os.utime(source, ns=(fixed_ns, fixed_ns))
        (workspace / "Tests/test_fixture.py").write_text(
            test_source
            or "import unittest\n\nclass FixtureTests(unittest.TestCase):\n    def test_passes(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        return workspace, cache.read_bytes()

    def test_prepare_exports_natural_prompt_and_retains_baseline(self):
        workspace, _, bundle = self.prepare("swift-decoding-readonly-combined")
        self.assertIn("Assess whether this saved value", bundle["prompt"]["text"])
        self.assertNotIn("Behavioral acceptance", bundle["prompt"]["text"])
        self.assertNotIn("CodingKeys", bundle["prompt"]["text"])
        self.assertEqual(
            bundle["workspace"]["baseline_tree_sha256"],
            behavior.tree_sha256(behavior.relative_files(workspace)),
        )
        self.assertEqual(bundle["configuration"], "combined")

    def test_config_contains_original_native_matrix_without_rubrics_in_prompts(self):
        cases = behavior.load_cases(behavior.DEFAULT_CONFIG)
        original_ids = {
            "universal-bounded-claim-readonly",
            "universal-decoder-boundary-readonly",
            "universal-missed-mutation-readonly",
            "universal-nested-mutation-readonly",
            "universal-stale-completion-readonly",
            "apple-decoded-value-readonly",
            "combined-decoded-value-readonly",
            "near-miss-swift-test-readonly",
            "near-miss-async-readiness-readonly",
            "near-miss-api-naming-readonly",
            "near-miss-code-review-readonly",
        }
        self.assertTrue(original_ids.issubset(cases))
        for identifier in original_ids:
            case = cases[identifier]
            prompt_path = behavior.DEFAULT_CONFIG.parent / case["prompt"]
            prompt = behavior.natural_prompt(prompt_path.resolve())
            self.assertNotIn("Behavioral acceptance", prompt)
            self.assertNotIn("Award full credit", prompt)
        durable = cases["universal-durable-invariant-write"]
        self.assertEqual(durable["allowed_change_paths"], ["**"])

    def test_changed_plugin_snapshot_fails_freshness_check(self):
        _, bundle_path, bundle = self.prepare("swift-decoding-readonly-apple")
        bundle["plugin_snapshot"]["sha256"] = "0" * 64
        behavior.write_json(bundle_path, bundle)
        outcome_path = self.write_outcome(bundle_path, bundle)
        evidence = behavior.assess(bundle_path, outcome_path)
        self.assertIn(
            "plugin snapshot changed after preparation",
            evidence["deterministic_assessment"]["problems"],
        )

    def test_snapshot_hash_ignores_evals_caches_and_ds_store(self):
        snapshot = self.root / "snapshot"
        plugin = snapshot / "plugins/universal"
        (plugin / "skills/example").mkdir(parents=True)
        (plugin / "skills/example/SKILL.md").write_text("guidance\n", encoding="utf-8")
        (plugin / "skills/example/__pycache__").mkdir()
        (plugin / "skills/example/__pycache__/cached.pyc").write_bytes(b"cache")
        (plugin / "skills/example/.DS_Store").write_bytes(b"metadata")
        (plugin / "skills/example/evals/case").mkdir(parents=True)
        (plugin / "skills/example/evals/case/rubric.md").write_text("answer\n", encoding="utf-8")
        files = behavior.snapshot_files(snapshot, ["plugins/universal"])
        self.assertEqual(list(files), ["plugins/universal/skills/example/SKILL.md"])

    def test_changed_acceptance_input_binding_fails_freshness_check(self):
        _, bundle_path, bundle = self.prepare("swift-decoding-readonly-apple")
        captured = bundle["acceptance_inputs"]["rubric"]
        copied_rubric = self.root / "rubric.md"
        copied_rubric.write_text(captured["content"], encoding="utf-8")
        captured["path"] = str(copied_rubric)
        behavior.write_json(bundle_path, bundle)
        copied_rubric.write_text("replacement rubric\n", encoding="utf-8")
        outcome_path = self.write_outcome(bundle_path, bundle)
        evidence = behavior.assess(bundle_path, outcome_path)
        self.assertIn(
            "acceptance input changed after preparation: rubric",
            evidence["deterministic_assessment"]["problems"],
        )

    def test_only_selected_case_changes_stale_captured_config(self):
        _, bundle_path, bundle = self.prepare("swift-decoding-readonly-apple")
        config_input = bundle["acceptance_inputs"]["config"]
        copied_config = self.root / "cases.json"
        copied_config.write_text(config_input["content"], encoding="utf-8")
        config_input["path"] = str(copied_config)
        behavior.write_json(bundle_path, bundle)
        outcome_path = self.write_outcome(bundle_path, bundle)

        config = json.loads(copied_config.read_text(encoding="utf-8"))
        unrelated = next(item for item in config["cases"] if item["id"] == "universal-bounded-claim-readonly")
        unrelated["configuration"] = "changed-unrelated-case"
        copied_config.write_text(json.dumps(config), encoding="utf-8")
        unchanged_selected = behavior.assess(bundle_path, outcome_path)
        self.assertNotIn(
            "selected case config changed after preparation",
            unchanged_selected["deterministic_assessment"]["problems"],
        )
        self.assertEqual(unchanged_selected["overall_status"], "pending_manual_review")

        config["schema_version"] = 2
        copied_config.write_text(json.dumps(config), encoding="utf-8")
        changed_schema = behavior.assess(bundle_path, outcome_path)
        self.assertIn(
            "top-level case config schema_version changed or is invalid",
            changed_schema["deterministic_assessment"]["problems"],
        )

        config["schema_version"] = 1
        selected = next(item for item in config["cases"] if item["id"] == bundle["case_id"])
        selected["configuration"] = "changed-selected-case"
        copied_config.write_text(json.dumps(config), encoding="utf-8")
        changed_selected = behavior.assess(bundle_path, outcome_path)
        self.assertIn(
            "selected case config changed after preparation",
            changed_selected["deterministic_assessment"]["problems"],
        )

    def test_mutated_live_checker_cannot_replace_captured_checker(self):
        workspace, bundle_path, bundle = self.prepare()
        self.write_swift_candidate(workspace, CORRECT_IMPLEMENTATION)
        captured = bundle["acceptance_inputs"]["artifact_checker"]
        copied_checker = self.root / "copied-checker.swift"
        copied_checker.write_text(captured["content"], encoding="utf-8")
        captured["path"] = str(copied_checker)
        behavior.write_json(bundle_path, bundle)
        copied_checker.write_text("// permissive replacement\n", encoding="utf-8")
        outcome_path = self.write_outcome(bundle_path, bundle)

        evidence = behavior.assess(bundle_path, outcome_path)

        self.assertEqual(evidence["artifact_checks"][0]["status"], "passed")
        self.assertIn(
            "acceptance input changed after preparation: artifact_checker",
            evidence["deterministic_assessment"]["problems"],
        )

    def test_workspace_mutation_during_check_fails_while_captured_copy_is_checked(self):
        workspace, bundle_path, bundle = self.prepare()
        self.write_swift_candidate(workspace, CORRECT_IMPLEMENTATION)
        outcome_path = self.write_outcome(bundle_path, bundle)
        original_checker = behavior.run_swift_checker

        def mutate_then_check(captured_workspace, checker_content):
            (workspace / "Sources/Quantity.swift").write_text(SCALAR_REGRESSION, encoding="utf-8")
            return original_checker(captured_workspace, checker_content)

        with mock.patch.object(behavior, "run_swift_checker", side_effect=mutate_then_check):
            evidence = behavior.assess(bundle_path, outcome_path)

        self.assertEqual(evidence["artifact_checks"][0]["status"], "passed")
        self.assertIn(
            "live workspace changed after the assessed copy was captured",
            evidence["deterministic_assessment"]["problems"],
        )
        self.assertEqual(evidence["overall_status"], "failed")

    def test_correct_swift_fix_passes_deterministic_checks_but_stays_pending(self):
        workspace, bundle_path, bundle = self.prepare()
        self.write_swift_candidate(workspace, CORRECT_IMPLEMENTATION)
        outcome_path = self.write_outcome(bundle_path, bundle)

        evidence = behavior.assess(bundle_path, outcome_path)

        self.assertEqual(evidence["deterministic_assessment"]["status"], "passed")
        self.assertEqual(evidence["artifact_checks"][0]["status"], "passed")
        self.assertIn("Swift version", evidence["artifact_checks"][0]["toolchain"]["version"])
        self.assertEqual(
            [command["stage"] for command in evidence["artifact_checks"][0]["commands"]],
            ["project-test-compile", "project-test-run", "acceptance-compile", "acceptance-run"],
        )
        acceptance_compile = evidence["artifact_checks"][0]["commands"][2]["argv"]
        self.assertEqual(acceptance_compile[1:3], ["-swift-version", "6"])
        self.assertEqual(evidence["semantic_review"]["status"], "pending_manual_review")
        self.assertEqual(evidence["overall_status"], "pending_manual_review")

    def test_scalar_decoder_regression_fails_historical_keyed_payload(self):
        workspace, bundle_path, bundle = self.prepare()
        self.write_swift_candidate(workspace, SCALAR_REGRESSION)
        outcome_path = self.write_outcome(bundle_path, bundle)

        evidence = behavior.assess(bundle_path, outcome_path)

        self.assertEqual(evidence["artifact_checks"][0]["status"], "failed")
        self.assertEqual(evidence["overall_status"], "failed")

    def test_root_data_corrupted_domain_rejection_is_accepted(self):
        workspace, bundle_path, bundle = self.prepare()
        self.write_swift_candidate(workspace, ROOT_DATA_CORRUPTED_IMPLEMENTATION)
        outcome_path = self.write_outcome(bundle_path, bundle)
        evidence = behavior.assess(bundle_path, outcome_path)
        self.assertEqual(evidence["artifact_checks"][0]["status"], "passed")
        self.assertEqual(evidence["overall_status"], "pending_manual_review")

    def test_always_reject_decoder_fails_valid_historical_control(self):
        workspace, bundle_path, bundle = self.prepare()
        self.write_swift_candidate(workspace, ALWAYS_REJECT_IMPLEMENTATION)
        outcome_path = self.write_outcome(bundle_path, bundle)
        evidence = behavior.assess(bundle_path, outcome_path)
        self.assertEqual(evidence["artifact_checks"][0]["status"], "failed")
        self.assertEqual(evidence["overall_status"], "failed")

    def test_unchanged_write_case_and_out_of_scope_changes_fail(self):
        workspace, bundle_path, bundle = self.prepare()
        (workspace / ".github").mkdir()
        (workspace / ".github/workflow.yml").write_text("name: unsolicited\n", encoding="utf-8")
        outcome_path = self.write_outcome(bundle_path, bundle)

        evidence = behavior.assess(bundle_path, outcome_path)

        problems = evidence["deterministic_assessment"]["problems"]
        self.assertTrue(any("out-of-scope" in problem for problem in problems))
        self.assertEqual(evidence["overall_status"], "failed")

        shutil.rmtree(workspace / ".github")
        unchanged = behavior.assess(bundle_path, outcome_path)
        self.assertIn("write case left the implementation unchanged", unchanged["deterministic_assessment"]["problems"])

    def test_read_only_case_has_write_tools_available_and_rejects_changes(self):
        workspace, bundle_path, bundle = self.prepare("swift-decoding-readonly-apple")
        outcome_path = self.write_outcome(bundle_path, bundle, write_capable=True)
        evidence = behavior.assess(bundle_path, outcome_path)
        self.assertEqual(evidence["overall_status"], "pending_manual_review")

        self.write_swift_candidate(workspace, CORRECT_IMPLEMENTATION)
        changed = behavior.assess(bundle_path, outcome_path)
        self.assertIn("read-only case changed workspace files", changed["deterministic_assessment"]["problems"])

        no_write_outcome = self.write_outcome(bundle_path, bundle, write_capable=False)
        unavailable = behavior.assess(bundle_path, no_write_outcome)
        self.assertIn(
            "outcome does not establish that write tools were available",
            unavailable["deterministic_assessment"]["problems"],
        )

    def test_failed_runtime_and_malformed_outcome_are_retained(self):
        _, bundle_path, bundle = self.prepare("swift-decoding-readonly-apple")
        outcome_path = self.write_outcome(bundle_path, bundle, status="timeout")
        raw = json.loads(outcome_path.read_text(encoding="utf-8"))
        evidence = behavior.assess(bundle_path, outcome_path)
        self.assertEqual(evidence["raw_outcome"], raw)
        self.assertEqual(evidence["overall_status"], "failed")

        outcome_path.write_text("{", encoding="utf-8")
        malformed = behavior.assess(bundle_path, outcome_path)
        self.assertIn("unreadable_outcome", malformed["raw_outcome"])
        self.assertEqual(malformed["overall_status"], "failed")

    def test_claude_skill_metadata_diagnostic_is_bound_and_tampering_is_detected(self):
        _, bundle_path, bundle = self.prepare("swift-decoding-readonly-apple")
        outcome_path = self.write_outcome(bundle_path, bundle)
        outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
        diagnostic = self.root / "claude.debug.log"
        diagnostic.write_text("Sending 32 skills via attachment (initial)\n", encoding="utf-8")
        outcome["runtime"]["activation"] = {
            "skill_metadata_exposure": {
                "status": "passed",
                "configured_char_budget": 24000,
                "configured_by": "SLASH_COMMAND_TOOL_CHAR_BUDGET",
                "skills_sent": 32,
                "problems": [],
                "diagnostic": {
                    "path": str(diagnostic),
                    "sha256": behavior.sha256_file(diagnostic),
                },
            }
        }
        behavior.write_json(outcome_path, outcome)

        evidence = behavior.assess(bundle_path, outcome_path)
        evidence_path = self.root / "evidence.json"
        behavior.write_json(evidence_path, evidence)

        self.assertEqual(evidence["deterministic_assessment"]["status"], "passed")
        self.assertEqual(
            evidence["normalized_outcome_artifacts"]["skill_metadata_diagnostic"]["sha256"],
            behavior.sha256_file(diagnostic),
        )
        self.assertEqual(behavior.verify_evidence(evidence_path), [])

        diagnostic.write_text("tampered\n", encoding="utf-8")
        self.assertIn(
            "evidence skill metadata diagnostic artifact is stale",
            behavior.verify_evidence(evidence_path),
        )

    def test_missing_claude_skill_metadata_diagnostic_fails_outcome_validation(self):
        _, bundle_path, bundle = self.prepare("swift-decoding-readonly-apple")
        outcome_path = self.write_outcome(bundle_path, bundle)
        outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
        outcome["runtime"]["activation"] = {
            "skill_metadata_exposure": {
                "status": "failed",
                "configured_char_budget": 24000,
                "configured_by": "SLASH_COMMAND_TOOL_CHAR_BUDGET",
                "skills_sent": None,
                "problems": ["diagnostic missing"],
                "diagnostic": None,
            }
        }
        behavior.write_json(outcome_path, outcome)

        evidence = behavior.assess(bundle_path, outcome_path)

        problems = evidence["deterministic_assessment"]["problems"]
        self.assertIn("outcome Claude skill metadata exposure did not pass", problems)
        self.assertIn("outcome skill metadata diagnostic must be an object", problems)
        self.assertEqual(evidence["overall_status"], "failed")

    def test_completed_label_cannot_mask_nonzero_exit_or_empty_raw_artifacts(self):
        _, bundle_path, bundle = self.prepare("swift-decoding-readonly-apple")
        outcome_path = self.write_outcome(bundle_path, bundle)
        outcome = json.loads(outcome_path.read_text(encoding="utf-8"))
        response_path = Path(outcome["response"]["path"])
        transcript_path = Path(outcome["transcript"]["path"])
        response_path.write_text("", encoding="utf-8")
        transcript_path.write_text("\n", encoding="utf-8")
        outcome["response"]["sha256"] = behavior.sha256_file(response_path)
        outcome["transcript"]["sha256"] = behavior.sha256_file(transcript_path)
        outcome["execution"]["status"] = "completed"
        outcome["execution"]["exit_code"] = 2
        behavior.write_json(outcome_path, outcome)

        evidence = behavior.assess(bundle_path, outcome_path)

        problems = evidence["deterministic_assessment"]["problems"]
        self.assertIn("completed runtime execution must have exit_code 0", problems)
        self.assertIn("outcome response must not be empty", problems)
        self.assertIn("outcome transcript must not be empty", problems)
        self.assertEqual(evidence["overall_status"], "failed")

    def test_verify_evidence_rejects_incomplete_or_accepted_claim(self):
        evidence_path = self.root / "evidence.json"
        behavior.write_json(evidence_path, {"schema_version": 1, "overall_status": "accepted"})
        problems = behavior.verify_evidence(evidence_path)
        self.assertTrue(any("missing" in problem for problem in problems))
        self.assertIn("pending semantic review cannot claim acceptance", problems)

    def test_full_review_requires_exact_artifact_hashes_criteria_and_composition(self):
        workspace, bundle_path, bundle = self.prepare()
        self.write_swift_candidate(workspace, CORRECT_IMPLEMENTATION)
        outcome_path = self.write_outcome(bundle_path, bundle)
        evidence = behavior.assess(bundle_path, outcome_path)
        evidence_path = self.root / "evidence.json"
        behavior.write_json(evidence_path, evidence)
        evaluator = evidence["evaluator_engine"]
        retained_evaluator = Path(evaluator["path"])
        retained_bytes = retained_evaluator.read_bytes()
        self.assertEqual(evaluator["version"], behavior.EVALUATOR_ENGINE_VERSION)
        self.assertEqual(evaluator["sha256"], behavior.sha256_bytes(retained_bytes))
        self.assertEqual(behavior.verify_evidence(evidence_path), [])

        retained_evaluator.write_text("# changed retained evaluator\n", encoding="utf-8")
        self.assertIn("evaluator engine binding is stale", behavior.verify_evidence(evidence_path))
        retained_evaluator.write_bytes(retained_bytes)

        original_engine_version = behavior.EVALUATOR_ENGINE_VERSION
        try:
            behavior.EVALUATOR_ENGINE_VERSION = original_engine_version + 1
            self.assertEqual(behavior.verify_evidence(evidence_path), [])
        finally:
            behavior.EVALUATOR_ENGINE_VERSION = original_engine_version

        legacy = json.loads(json.dumps(evidence))
        legacy.pop("evaluator_engine")
        legacy["schema_version"] = 1
        legacy_path = self.root / "legacy-evidence.json"
        behavior.write_json(legacy_path, legacy)
        self.assertEqual(behavior.verify_evidence(legacy_path), [])

        stripped = json.loads(json.dumps(evidence))
        stripped.pop("evaluator_engine")
        stripped_path = self.root / "stripped-evidence.json"
        behavior.write_json(stripped_path, stripped)
        self.assertIn("evidence is missing evaluator_engine", behavior.verify_evidence(stripped_path))
        response_hash = evidence["normalized_outcome_artifacts"]["response"]["sha256"]
        transcript_hash = evidence["normalized_outcome_artifacts"]["transcript"]["sha256"]
        review = {
            "schema_version": 1,
            "case_id": bundle["case_id"],
            "rubric_sha256": evidence["semantic_review"]["rubric"]["sha256"],
            "response_sha256": response_hash,
            "transcript_sha256": transcript_hash,
            "reviewer": {"kind": "human", "name": "fixture reviewer"},
            "criteria": [
                {"id": identifier, "status": "pass", "reason": "Reviewed in full.", "evidence": ["response paragraph 1"]}
                for identifier in ("behavior", "scope", "evidence_honesty")
            ],
            "composition": {"status": "pass", "reason": "Required skills composed.", "evidence": ["trace tool call 1"]},
        }
        review_path = self.root / "review.json"
        behavior.write_json(review_path, review)

        completed = behavior.finalize_review(evidence_path, review_path)
        self.assertEqual(completed["semantic_review"]["status"], "completed")
        self.assertEqual(completed["overall_status"], "accepted")
        completed_path = self.root / "completed.json"
        behavior.write_json(completed_path, completed)
        self.assertEqual(behavior.verify_evidence(completed_path), [])

        (workspace / "Sources/Quantity.swift").write_text("// changed after review\n", encoding="utf-8")
        self.assertIn(
            "evidence post-run workspace binding is stale",
            behavior.verify_evidence(completed_path),
        )
        self.write_swift_candidate(workspace, CORRECT_IMPLEMENTATION)

        review["rubric_sha256"] = "0" * 64
        behavior.write_json(review_path, review)
        with self.assertRaises(behavior.HarnessError):
            behavior.finalize_review(evidence_path, review_path)
        review["rubric_sha256"] = evidence["semantic_review"]["rubric"]["sha256"]
        review["transcript_sha256"] = "0" * 64
        behavior.write_json(review_path, review)
        with self.assertRaises(behavior.HarnessError):
            behavior.finalize_review(evidence_path, review_path)

    def test_failed_composition_remains_a_separate_acceptance_gate(self):
        workspace, bundle_path, bundle = self.prepare()
        (workspace / "Sources/Quantity.swift").write_text(CORRECT_IMPLEMENTATION, encoding="utf-8")
        outcome_path = self.write_outcome(bundle_path, bundle)
        evidence = behavior.assess(bundle_path, outcome_path)
        evidence_path = self.root / "evidence.json"
        behavior.write_json(evidence_path, evidence)
        review = {
            "schema_version": 1,
            "case_id": bundle["case_id"],
            "rubric_sha256": evidence["semantic_review"]["rubric"]["sha256"],
            "response_sha256": evidence["normalized_outcome_artifacts"]["response"]["sha256"],
            "transcript_sha256": evidence["normalized_outcome_artifacts"]["transcript"]["sha256"],
            "reviewer": {"kind": "model", "name": "fixture reviewer"},
            "criteria": [
                {"id": identifier, "status": "pass", "reason": "Behavior passed.", "evidence": ["response"]}
                for identifier in ("behavior", "scope", "evidence_honesty")
            ],
            "composition": {"status": "fail", "reason": "Universal procedure was omitted.", "evidence": ["trace has only Apple skill"]},
        }
        review_path = self.root / "review.json"
        behavior.write_json(review_path, review)
        completed = behavior.finalize_review(evidence_path, review_path)
        self.assertEqual(completed["overall_status"], "failed")

    def test_explicit_durable_request_allows_and_requires_registry_and_ci_artifacts(self):
        workspace, bundle_path, bundle = self.prepare("universal-durable-invariant-write")
        validator = bundle["acceptance_inputs"]["artifact_support:validate_invariants.py"]
        self.assertEqual(
            validator["sha256"],
            behavior.sha256_bytes(validator["content"].encode("utf-8")),
        )
        (workspace / "Sources/quantity.py").write_text(
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if value <= 0:\n'
            '        raise ValueError("quantity must be positive")\n'
            '    return value\n',
            encoding="utf-8",
        )
        outcome_path = self.write_outcome(bundle_path, bundle)
        missing = behavior.assess(bundle_path, outcome_path)
        self.assertTrue(any("required workspace changes" in item for item in missing["deterministic_assessment"]["problems"]))

        (workspace / ".github/workflows").mkdir(parents=True)
        (workspace / ".github/workflows/invariants.yml").write_text("name: invariants\n", encoding="utf-8")
        (workspace / "Tools").mkdir()
        (workspace / "Tools/validate_invariants.py").write_text("# vendored project validator\n", encoding="utf-8")
        (workspace / "invariants.json").write_text('{"schema_version": 1, "invariants": []}\n', encoding="utf-8")
        invalid_manifest = behavior.assess(bundle_path, outcome_path)
        self.assertEqual(invalid_manifest["artifact_checks"][0]["stage"], "manifest-validation")
        self.assertEqual(invalid_manifest["overall_status"], "failed")

        manifest = {
            "schema_version": 1,
            "invariants": [{
                "id": "imported-quantity-positive",
                "statement": "Imported quantities are positive.",
                "kind": "refined-value",
                "scope": {"references": [{"path": "Sources/quantity.py", "symbol": "import_quantity"}]},
                "authority": {
                    "description": "The import boundary rejects nonpositive values.",
                    "references": [{"path": "Sources/quantity.py"}],
                },
                "boundaries": {"surfaces": ["decoding"], "exclusions": []},
                "assumptions": [],
                "checks": [{
                    "id": "boundary-tests",
                    "method": "boundary-test",
                    "artifact": {"path": "Tests/test_quantity.py"},
                    "limitations": [],
                }],
            }],
        }
        (workspace / "invariants.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        complete = behavior.assess(bundle_path, outcome_path)
        self.assertEqual(complete["artifact_checks"][0]["status"], "passed")
        self.assertIn("Python", complete["artifact_checks"][0]["toolchain"]["version"])
        self.assertEqual(
            [command["stage"] for command in complete["artifact_checks"][0]["commands"]],
            ["manifest-validation", "project-tests", "acceptance-run"],
        )
        manifest_argv = complete["artifact_checks"][0]["commands"][0]["argv"]
        self.assertTrue(any(item.endswith("validate_invariants.py") for item in manifest_argv))
        self.assertIn("-B", manifest_argv)
        self.assertTrue(any(item.startswith("pycache_prefix=") for item in manifest_argv))
        self.assertIn("--root", manifest_argv)
        self.assertEqual(manifest_argv[-1], "--json")
        self.assertEqual(complete["overall_status"], "pending_manual_review")

    def test_durable_invariant_checker_preserves_supported_positive_values_and_rejects_decimal_nonpositive_values(self):
        workspace = self.root / "durable-invariant-checker"
        fixture = ROOT / "evals/invariant-behavior/durable-invariant/workspace"
        shutil.copytree(fixture, workspace)

        minimal_guard = (
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if value <= 0:\n'
            '        raise ValueError("quantity must be positive")\n'
            '    return value\n'
        )
        finite_only_guard = (
            'import math\n\n'
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if value <= 0 or not math.isfinite(value):\n'
            '        raise ValueError("quantity must be a positive finite number")\n'
            '    return value\n'
        )
        real_only_guard = (
            'from numbers import Real\n\n'
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if isinstance(value, Real) and value <= 0:\n'
            '        raise ValueError("quantity must be positive")\n'
            '    return value\n'
        )
        bool_rejecting_guard = (
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if isinstance(value, bool):\n'
            '        raise ValueError("booleans are not quantities")\n'
            '    if value <= 0:\n'
            '        raise ValueError("quantity must be positive")\n'
            '    return value\n'
        )
        checker = (ROOT / "evals/invariant-behavior/durable-invariant/acceptance/assertions.py").read_text(
            encoding="utf-8"
        )

        (workspace / "Sources/quantity.py").write_text(minimal_guard, encoding="utf-8")
        accepted = behavior.run_python_checker(workspace, checker)
        self.assertEqual(accepted["status"], "passed")

        (workspace / "Sources/quantity.py").write_text(finite_only_guard, encoding="utf-8")
        rejected = behavior.run_python_checker(workspace, checker)
        self.assertEqual(rejected["status"], "failed")
        self.assertEqual(rejected["stage"], "run")
        self.assertIn("quantity must be a positive finite number", rejected["stderr"])

        (workspace / "Sources/quantity.py").write_text(real_only_guard, encoding="utf-8")
        category_gated = behavior.run_python_checker(workspace, checker)
        self.assertEqual(category_gated["status"], "failed")
        self.assertEqual(category_gated["stage"], "run")
        self.assertIn("invalid imported quantity was accepted: Decimal('-3')", category_gated["stderr"])

        (workspace / "Sources/quantity.py").write_text(bool_rejecting_guard, encoding="utf-8")
        bool_rejected = behavior.run_python_checker(workspace, checker)
        self.assertEqual(bool_rejected["status"], "failed")
        self.assertEqual(bool_rejected["stage"], "run")
        self.assertIn("booleans are not quantities", bool_rejected["stderr"])

    def test_scope_excludes_only_new_interpreter_cache_files(self):
        bytecode = "Sources/__pycache__/quantity.cpython-314.pyc"
        self.assertTrue(behavior.is_incidental_python_bytecode_change({"path": bytecode, "status": "added"}))
        for change in (
            {"path": bytecode, "status": "modified"},
            {"path": bytecode, "status": "deleted"},
            {"path": "Sources/__pycache__/injected.py", "status": "added"},
            {"path": "Sources/__pycache__/config.json", "status": "added"},
            {"path": "Sources/__pycache__/nested/payload.pyc", "status": "added"},
            {"path": "Sources/quantity.pyc", "status": "added"},
        ):
            with self.subTest(change=change):
                self.assertFalse(behavior.is_incidental_python_bytecode_change(change))

    def test_ordinary_invariant_case_accepts_the_scoped_fix_and_rejects_bad_repairs(self):
        workspace, bundle_path, bundle = self.prepare("universal-ordinary-invariant-write")
        self.assertEqual(bundle["allowed_change_paths"], ["Sources/quantity.py", "Tests"])
        self.assertEqual(bundle["required_change_paths"], ["Sources/quantity.py", "Tests"])
        self.assertEqual(bundle["artifact_checker"]["kind"], "python")
        self.assertNotIn("artifact_support:validate_invariants.py", bundle["acceptance_inputs"])

        focused_tests = (
            "\n    def test_rejects_nonpositive_quantities(self):\n"
            "        for value in (0, -3):\n"
            "            with self.assertRaises(ValueError):\n"
            "                import_quantity({\"value\": value})\n"
        )
        correct_guard = (
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if value <= 0:\n'
            '        raise ValueError("quantity must be positive")\n'
            '    return value\n'
        )
        (workspace / "Sources/quantity.py").write_text(correct_guard, encoding="utf-8")
        tests = workspace / "Tests/test_quantity.py"
        tests.write_text(tests.read_text(encoding="utf-8").replace("\n\nif __name__", focused_tests + "\n\nif __name__"), encoding="utf-8")
        environment = os.environ.copy()
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
        environment.pop("PYTHONPYCACHEPREFIX", None)
        test_run = behavior.subprocess.run(
            [behavior.sys.executable, "-m", "unittest", "discover", "-s", "Tests", "-v"],
            cwd=workspace,
            capture_output=True,
            text=True,
            env=environment,
        )
        self.assertEqual(test_run.returncode, 0, test_run.stderr)
        cache_directory = workspace / "Sources/__pycache__"
        cache_directory.mkdir(exist_ok=True)
        py_compile.compile(
            workspace / "Sources/quantity.py",
            cfile=cache_directory / "quantity.test.pyc",
            doraise=True,
        )
        generated_bytecode = sorted((workspace / "Sources/__pycache__").glob("quantity.*.pyc"))
        self.assertTrue(generated_bytecode)
        outcome_path = self.write_outcome(bundle_path, bundle)

        accepted = behavior.assess(bundle_path, outcome_path)
        self.assertEqual(accepted["deterministic_assessment"]["status"], "passed")
        self.assertEqual(accepted["artifact_checks"][0]["status"], "passed")
        self.assertEqual(
            [command["stage"] for command in accepted["artifact_checks"][0]["commands"]],
            ["project-tests", "acceptance-run"],
        )
        self.assertTrue(any(item["path"].endswith(".pyc") for item in accepted["tree_diff"]))
        self.assertTrue(accepted["scope_assessment"]["ignored_incidental_python_bytecode"])
        self.assertFalse(any(item["path"].endswith(".pyc") for item in accepted["scope_assessment"]["changes"]))
        evidence_path = self.root / "ordinary-evidence.json"
        behavior.write_json(evidence_path, accepted)
        self.assertEqual(behavior.verify_evidence(evidence_path), [])
        accepted["scope_assessment"]["changes"] = []
        behavior.write_json(evidence_path, accepted)
        self.assertIn(
            "evidence scope assessment does not match raw tree diff",
            behavior.verify_evidence(evidence_path),
        )
        for malformed in (
            {"status": "added"},
            {"path": "Sources/quantity.py", "status": []},
            {"path": "Sources/quantity.py", "status": {}},
        ):
            with self.subTest(malformed=malformed):
                accepted["tree_diff"] = [malformed]
                behavior.write_json(evidence_path, accepted)
                self.assertIn(
                    "evidence scope assessment contains malformed change records",
                    behavior.verify_evidence(evidence_path),
                )

        cache_neighbor = workspace / "Sources/__pycache__/injected.py"
        cache_neighbor.write_text("not bytecode\n", encoding="utf-8")
        cache_neighbor_result = behavior.assess(bundle_path, outcome_path)
        self.assertIn(
            "workspace contains out-of-scope changes: Sources/__pycache__/injected.py",
            cache_neighbor_result["deterministic_assessment"]["problems"],
        )
        cache_neighbor.unlink()

        (workspace / "invariants.json").write_text('{"schema_version": 1}\n', encoding="utf-8")
        unsolicited_registry = behavior.assess(bundle_path, outcome_path)
        self.assertIn(
            "workspace contains out-of-scope changes: invariants.json",
            unsolicited_registry["deterministic_assessment"]["problems"],
        )
        self.assertEqual(unsolicited_registry["overall_status"], "failed")

        (workspace / "invariants.json").unlink()
        unchecked = 'def import_quantity(payload):\n    return payload["value"]\n'
        (workspace / "Sources/quantity.py").write_text(unchecked, encoding="utf-8")
        unchecked_result = behavior.assess(bundle_path, outcome_path)
        self.assertEqual(unchecked_result["artifact_checks"][0]["status"], "failed")

        finite_only_guard = (
            'import math\n\n'
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if value <= 0 or not math.isfinite(value):\n'
            '        raise ValueError("quantity must be a positive finite number")\n'
            '    return value\n'
        )
        (workspace / "Sources/quantity.py").write_text(finite_only_guard, encoding="utf-8")
        finite_only_result = behavior.assess(bundle_path, outcome_path)
        self.assertEqual(finite_only_result["artifact_checks"][0]["status"], "failed")
        self.assertIn("positive finite number", finite_only_result["artifact_checks"][0]["stderr"])

    def test_toolchain_version_timeout_fails_closed(self):
        with mock.patch.object(
            behavior.subprocess,
            "run",
            side_effect=behavior.subprocess.TimeoutExpired(["swiftc", "--version"], 30),
        ):
            metadata, error = behavior.resolve_toolchain("swiftc")
        self.assertEqual(metadata["version_argv"][-1], "--version")
        self.assertIn("timed out", error)

    def test_python_project_tests_cannot_change_bytes_seen_by_oracle(self):
        workspace = self.root / "python-project-test-mutation"
        (workspace / "Sources").mkdir(parents=True)
        (workspace / "Tests").mkdir()
        source = workspace / "Sources/quantity.py"
        source.write_text("VALUE = 1\n", encoding="utf-8")
        (workspace / "Tests/test_mutation.py").write_text(
            "import pathlib\n"
            "import unittest\n\n"
            "class MutationTests(unittest.TestCase):\n"
            "    def test_mutates_source(self):\n"
            "        pathlib.Path('Sources/quantity.py').write_text('VALUE = 2\\n')\n",
            encoding="utf-8",
        )
        result = behavior.run_python_checker(workspace, "raise SystemExit(0)\n")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["stage"], "project-tests-workspace-integrity")
        self.assertEqual(result["commands"][0]["stage"], "project-tests")

    def test_python_oracle_cannot_mutate_checked_workspace(self):
        workspace = self.root / "python-oracle-mutation"
        (workspace / "Sources").mkdir(parents=True)
        (workspace / "Tests").mkdir()
        (workspace / "Sources/quantity.py").write_text("VALUE = 1\n", encoding="utf-8")
        (workspace / "Tests/test_clean.py").write_text(
            "import unittest\n\n"
            "class CleanTests(unittest.TestCase):\n"
            "    def test_passes(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        checker = (
            "import pathlib, sys\n"
            "pathlib.Path(sys.argv[1], 'Sources/quantity.py').write_text('VALUE = 3\\n')\n"
        )
        result = behavior.run_python_checker(workspace, checker)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["stage"], "acceptance-workspace-integrity")
        self.assertEqual([item["stage"] for item in result["commands"]], ["project-tests", "acceptance-run"])

    def test_project_tests_cannot_replace_independent_oracle(self):
        malicious_test = (
            "import pathlib\n"
            "import unittest\n\n"
            "class OracleReplacementTests(unittest.TestCase):\n"
            "    def test_replaces_predictable_oracle(self):\n"
            "        pathlib.Path.cwd().parent.joinpath('assertions.py').write_text('raise SystemExit(0)\\n')\n"
        )
        valid = (
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if value <= 0:\n'
            '        raise ValueError("positive quantity required")\n'
            '    return value\n'
        )
        condition = "if value <= 0:"
        invalid = valid.replace(condition, "if False:" + " " * (len(condition) - len("if False:")))
        checker = (ROOT / "evals/invariant-behavior/durable-invariant/acceptance/assertions.py").read_text(encoding="utf-8")

        invalid_workspace, _ = self.python_bytecode_workspace("replaced-oracle-invalid", invalid, invalid, malicious_test)
        invalid_result = behavior.run_python_checker(invalid_workspace, checker)
        self.assertEqual(invalid_result["status"], "failed")
        self.assertEqual(invalid_result["stage"], "run")

        valid_workspace, _ = self.python_bytecode_workspace("replaced-oracle-valid", valid, valid, malicious_test)
        valid_result = behavior.run_python_checker(valid_workspace, checker)
        self.assertEqual(valid_result["status"], "passed")

    def test_stale_valid_bytecode_cannot_make_invalid_source_pass(self):
        valid = (
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if value <= 0:\n'
            '        raise ValueError("positive quantity required")\n'
            '    return value\n'
        )
        condition = "if value <= 0:"
        invalid = valid.replace(condition, "if False:" + " " * (len(condition) - len("if False:")))
        workspace, _ = self.python_bytecode_workspace("stale-valid-cache", valid, invalid)
        checker = (ROOT / "evals/invariant-behavior/durable-invariant/acceptance/assertions.py").read_text(encoding="utf-8")
        result = behavior.run_python_checker(workspace, checker)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["stage"], "run")

    def test_stale_invalid_bytecode_cannot_make_valid_source_fail(self):
        valid = (
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if value <= 0:\n'
            '        raise ValueError("positive quantity required")\n'
            '    return value\n'
        )
        condition = "if value <= 0:"
        invalid = valid.replace(condition, "if False:" + " " * (len(condition) - len("if False:")))
        workspace, _ = self.python_bytecode_workspace("stale-invalid-cache", invalid, valid)
        checker = (ROOT / "evals/invariant-behavior/durable-invariant/acceptance/assertions.py").read_text(encoding="utf-8")
        result = behavior.run_python_checker(workspace, checker)
        self.assertEqual(result["status"], "passed")

    def test_project_test_poisoned_cache_cannot_change_oracle_result(self):
        import base64

        valid = (
            'def import_quantity(payload):\n'
            '    value = payload["value"]\n'
            '    if value <= 0:\n'
            '        raise ValueError("positive quantity required")\n'
            '    return value\n'
        )
        condition = "if value <= 0:"
        invalid = valid.replace(condition, "if False:" + " " * (len(condition) - len("if False:")))
        _, valid_cache = self.python_bytecode_workspace("cache-seed", valid, invalid)
        poison_test = (
            "import base64\nimport importlib.util\nimport pathlib\nimport unittest\n\n"
            f"CACHE = base64.b64decode({base64.b64encode(valid_cache).decode()!r})\n\n"
            "class PoisonTests(unittest.TestCase):\n"
            "    def test_writes_cache(self):\n"
            "        target = pathlib.Path(importlib.util.cache_from_source('Sources/quantity.py'))\n"
            "        target.parent.mkdir(parents=True, exist_ok=True)\n"
            "        target.write_bytes(CACHE)\n"
        )
        checker = (ROOT / "evals/invariant-behavior/durable-invariant/acceptance/assertions.py").read_text(encoding="utf-8")

        invalid_workspace, _ = self.python_bytecode_workspace("poisoned-invalid", invalid, invalid, poison_test)
        invalid_result = behavior.run_python_checker(invalid_workspace, checker)
        self.assertEqual(invalid_result["status"], "failed")
        self.assertEqual(invalid_result["stage"], "run")

        valid_workspace, _ = self.python_bytecode_workspace("poisoned-valid", valid, valid, poison_test)
        valid_result = behavior.run_python_checker(valid_workspace, checker)
        self.assertEqual(valid_result["status"], "passed")


if __name__ == "__main__":
    unittest.main()
