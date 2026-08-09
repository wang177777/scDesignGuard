import copy
import html
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scdesignguard_nm03.blocker import AnalysisBlockedError, require_proceed
from scdesignguard_nm03.catalog import REASONS
from scdesignguard_nm03.compiler import canonical_json, compile_contract, validate_contract
from scdesignguard_nm03.engine import contrast_is_estimable, evaluate_contract
from scdesignguard_nm03.privacy import is_safe_output_path, public_release_view
from scdesignguard_nm03.repair import propose_repairs
from scdesignguard_nm03.report import render_html


def fixture():
    return json.loads((ROOT / "tests/fixtures/valid.json").read_text())


class CompilerTests(unittest.TestCase):
    def test_deterministic_compile(self):
        one = compile_contract(fixture())
        two = compile_contract(json.loads(json.dumps(fixture(), sort_keys=True)))
        self.assertEqual(canonical_json(one), canonical_json(two))

    def test_schema_and_path_fail_closed(self):
        value = fixture()
        value["sources"][0]["relative_path"] = "../private.txt"
        self.assertEqual(validate_contract(value)[0]["code"], "PATH_UNSAFE")
        with self.assertRaises(ValueError):
            compile_contract(value)

    def test_missing_nested_field_and_unknown_field_fail_closed(self):
        value = fixture()
        del value["evidence"]["model_estimable"]
        value["unexpected"] = True
        codes = {row["code"] for row in validate_contract(value)}
        self.assertIn("REQUIRED", codes)
        self.assertIn("ADDITIONAL_PROPERTY", codes)

    def test_exact_estimability(self):
        self.assertTrue(contrast_is_estimable([[1, 0], [1, 1]], [0, 1]))
        self.assertFalse(contrast_is_estimable([[1, 1], [1, 1]], [0, 1]))


class StateTests(unittest.TestCase):
    def test_proceed_and_authorization_boundary(self):
        result = evaluate_contract(fixture())
        self.assertEqual(result["terminal_state"], "PROCEED")
        self.assertEqual(result["estimability_proof"]["design_rank"], result["estimability_proof"]["augmented_with_contrast_rank"])
        self.assertFalse(result["estimability_proof"]["floating_tolerance_used"])
        with self.assertRaises(AnalysisBlockedError):
            require_proceed(result)
        require_proceed(result, {"authorized": True, "task_id": "FIXTURE-VALID", "contract_sha256": result["contract_sha256"], "scope": "SCIENTIFIC_EXECUTION", "authorization_id": "FIXTURE-AUTH"})

    def test_block_precedes_other_states(self):
        value = fixture()
        value["governance"]["role_leakage"] = True
        value["evidence"]["target_support_sufficient"] = False
        value["robustness"]["lodo_stable"] = False
        result = evaluate_contract(value)
        self.assertEqual(result["terminal_state"], "BLOCK")
        self.assertEqual(result["reason_codes"][0], "GOV.ROLE.LEAKAGE")

    def test_non_evaluable_precedes_abstain(self):
        value = fixture()
        value["evidence"]["target_support_sufficient"] = False
        value["robustness"]["lodo_stable"] = False
        self.assertEqual(evaluate_contract(value)["terminal_state"], "NON_EVALUABLE")

    def test_abstain(self):
        value = fixture()
        value["uncertainty"]["coverage_pass"] = False
        self.assertEqual(evaluate_contract(value)["terminal_state"], "ABSTAIN")

    def test_all_21_reason_codes_reachable(self):
        observed = {"OUTPUT.SAFE_TO_PROCEED"}
        mutations = [
            ("identity", "binding_status", "UNBOUND"), ("governance", "license_status", "UNRESOLVED"),
            ("governance", "role_leakage", True), ("claims", 0, {"claim_id": "x", "mapped_to_passed_gate": False}),
            ("design", "biological_unit", "cell"), ("design", "donor_condition_conflict", True),
            ("design", "complete_confounding", True), ("count_source", "valid", False),
            ("evidence", "target_support_sufficient", False), ("design", "matrix", [[1, 1], [1, 1]]),
            ("evidence", "independence_sufficient", False), ("evidence", "reference_present", False),
            ("evidence", "model_estimable", False), ("robustness", "lodo_stable", False),
            ("robustness", "direction_stable", False), ("robustness", "filtering_stable", False),
            ("robustness", "annotation_stable", False), ("robustness", "confounding_stable", False),
            ("uncertainty", "clustered_uncertainty_resolved", False), ("uncertainty", "coverage_pass", False),
        ]
        for section, key, new in mutations:
            value = fixture()
            value[section][key] = new
            observed.update(evaluate_contract(value)["reason_codes"])
        self.assertEqual(observed, set(REASONS))


class SafetyTests(unittest.TestCase):
    def test_private_filter_is_recursive_and_nonmutating(self):
        source = {"task_id": "T1", "terminal_state": "BLOCK", "nested": {"donor_id": "D1", "ok": 2}, "sample_name": "S1"}
        filtered = public_release_view(source)
        self.assertEqual(filtered["artifact"], {"task_id": "T1", "terminal_state": "BLOCK"})
        self.assertEqual(source["nested"]["donor_id"], "D1")
        self.assertFalse(filtered["private_values_copied"])

    def test_cli_public_filter_does_not_parse_private_input_as_contract(self):
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            path = Path(tmp) / "private.json"
            path.write_text(json.dumps({"task_id": "T", "donor_id": "D1"}))
            proc = subprocess.run([sys.executable, "-m", "scdesignguard_nm03.cli", "filter-public", str(path)], cwd=ROOT, env=env, check=True, text=True, capture_output=True)
            self.assertEqual(json.loads(proc.stdout)["artifact"], {"task_id": "T"})

    def test_output_path_safety(self):
        for bad in ("", "/tmp/a", "../a", "a/../b", "./a", "a\\b", "a\x00b"):
            self.assertFalse(is_safe_output_path(bad), bad)
        self.assertTrue(is_safe_output_path("reports/result.json"))

    def test_html_escapes_untrusted_task(self):
        value = fixture()
        value["task_id"] = "<script>alert(1)</script>"
        compiled = compile_contract(value)
        report = render_html(compiled, evaluate_contract(value))
        self.assertNotIn("<script>alert(1)</script>", report)
        self.assertIn("&lt;script&gt;", report)

    def test_repair_oracle_never_mutates(self):
        value = fixture()
        value["evidence"]["target_support_sufficient"] = False
        before = copy.deepcopy(value)
        repairs = propose_repairs(evaluate_contract(value))
        self.assertEqual(value, before)
        self.assertFalse(repairs["automatic_repair_performed"])


class IntegrationTests(unittest.TestCase):
    def test_cli_compile_verify_report(self):
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            rel = str(Path(tmp).relative_to(ROOT))
            compiled = f"{rel}/compiled.json"
            report = f"{rel}/report.html"
            subprocess.run([sys.executable, "-m", "scdesignguard_nm03.cli", "compile", "tests/fixtures/valid.json", "--output", compiled], cwd=ROOT, env=env, check=True)
            proc = subprocess.run([sys.executable, "-m", "scdesignguard_nm03.cli", "verify", compiled], cwd=ROOT, env=env, check=True, text=True, capture_output=True)
            self.assertEqual(json.loads(proc.stdout)["terminal_state"], "PROCEED")
            subprocess.run([sys.executable, "-m", "scdesignguard_nm03.cli", "report", compiled, "--output", report], cwd=ROOT, env=env, check=True)
            self.assertTrue((ROOT / report).read_text().startswith("<!doctype html>"))

    def test_cli_rejects_absolute_output(self):
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
        proc = subprocess.run([sys.executable, "-m", "scdesignguard_nm03.cli", "compile", "tests/fixtures/valid.json", "--output", "/tmp/forbidden.json"], cwd=ROOT, env=env)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
