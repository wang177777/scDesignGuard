#!/usr/bin/env python3
"""Reconcile frozen aggregate claims from the released Source Data workbook.

This verifier uses only the Python standard library. It never accesses raw
expression data and never refits a scientific model.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List
from xml.etree import ElementTree as ET


MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def _column_index(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference).group(0)
    value = 0
    for letter in letters:
        value = value * 26 + ord(letter) - 64
    return value - 1


def _shared_strings(archive: zipfile.ZipFile) -> List[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(node.itertext()) for node in root.findall(f"{{{MAIN}}}si")]


def _sheet_paths(archive: zipfile.ZipFile) -> Dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall(f"{{{REL_PKG}}}Relationship")
    }
    result = {}
    for sheet in workbook.find(f"{{{MAIN}}}sheets"):
        target = targets[sheet.attrib[f"{{{REL_DOC}}}id"]]
        normalized = target.lstrip("/")
        result[sheet.attrib["name"]] = normalized if normalized.startswith("xl/") else "xl/" + normalized
    return result


def read_sheet(path: Path, sheet_name: str) -> List[Dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        shared = _shared_strings(archive)
        sheet_path = _sheet_paths(archive)[sheet_name]
        root = ET.fromstring(archive.read(sheet_path))
        rows: List[List[str]] = []
        for row in root.findall(f".//{{{MAIN}}}sheetData/{{{MAIN}}}row"):
            values: List[str] = []
            for cell in row.findall(f"{{{MAIN}}}c"):
                index = _column_index(cell.attrib["r"])
                while len(values) <= index:
                    values.append("")
                kind = cell.attrib.get("t")
                if kind == "inlineStr":
                    node = cell.find(f"{{{MAIN}}}is")
                    value = "" if node is None else "".join(node.itertext())
                else:
                    node = cell.find(f"{{{MAIN}}}v")
                    value = "" if node is None else (node.text or "")
                    if kind == "s" and value:
                        value = shared[int(value)]
                values[index] = value
            rows.append(values)
    if not rows:
        return []
    width = len(rows[0])
    header = rows[0]
    return [
        dict(zip(header, row + [""] * (width - len(row))))
        for row in rows[1:]
        if any(row)
    ]


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("Wilson interval requires a positive denominator")
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    half_width = z * math.sqrt(
        proportion * (1 - proportion) / total + z * z / (4 * total * total)
    ) / denominator
    return max(0.0, centre - half_width), min(1.0, centre + half_width)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def reconcile(workbook: Path) -> dict:
    benchmark = read_sheet(workbook, "Fig2_Benchmark")
    endpoints = read_sheet(workbook, "Fig2_Endpoints")
    e2e = read_sheet(workbook, "Fig3_E2E")
    invalidities = read_sheet(workbook, "Fig4_Invalidities")
    atlas = read_sheet(workbook, "Fig5_Atlas")

    require(len(benchmark) == 15, "Fig2 benchmark denominator must equal 15")
    classes = Counter(row["frozen_human_reference_class"] for row in benchmark)
    require(
        classes == Counter({
            "VALID_DESIGN": 4,
            "HARD_INVALID_DESIGN": 6,
            "STRUCTURALLY_UNRESOLVED": 5,
        }),
        f"unexpected benchmark class counts: {dict(classes)}",
    )
    expected_states = {
        "VALID_DESIGN": "PROCEED",
        "HARD_INVALID_DESIGN": "BLOCK",
        "STRUCTURALLY_UNRESOLVED": "NON_EVALUABLE",
    }
    concordant = sum(
        row["scdesignguard_state"] == expected_states[row["frozen_human_reference_class"]]
        for row in benchmark
    )
    valid_clearance = sum(
        row["frozen_human_reference_class"] == "VALID_DESIGN"
        and row["scdesignguard_state"] == "PROCEED"
        for row in benchmark
    )
    hard_invalid_detection = sum(
        row["frozen_human_reference_class"] == "HARD_INVALID_DESIGN"
        and row["scdesignguard_state"] == "BLOCK"
        for row in benchmark
    )
    unresolved_containment = sum(
        row["frozen_human_reference_class"] == "STRUCTURALLY_UNRESOLVED"
        and row["scdesignguard_state"] == "NON_EVALUABLE"
        for row in benchmark
    )
    unsafe_continuation = sum(
        row["frozen_human_reference_class"] == "HARD_INVALID_DESIGN"
        and row["scdesignguard_state"] == "PROCEED"
        for row in benchmark
    )
    observed = {
        "Valid clearance": (valid_clearance, 4),
        "Hard-invalid detection": (hard_invalid_detection, 6),
        "Unresolved containment": (unresolved_containment, 5),
        "Exact state concordance": (concordant, 15),
        "Unsafe continuation": (unsafe_continuation, 6),
    }
    endpoint_map = {row["endpoint"]: row for row in endpoints}
    require(set(endpoint_map) == set(observed), "unexpected Fig2 endpoint registry")
    for name, (numerator, denominator) in observed.items():
        row = endpoint_map[name]
        require(int(float(row["numerator"])) == numerator, f"{name} numerator mismatch")
        require(int(float(row["denominator"])) == denominator, f"{name} denominator mismatch")
        low, high = wilson(numerator, denominator)
        require(abs(float(row["wilson_95_low"]) - low) < 1e-12, f"{name} lower CI mismatch")
        require(abs(float(row["wilson_95_high"]) - high) < 1e-12, f"{name} upper CI mismatch")

    require(len(e2e) == 4, "E2E denominator must equal 4")
    full_passes = sum(row["final_authorization"] == "PASS" for row in e2e)
    early_stops = sum(row["terminal_result"].startswith("EARLY_STOP") for row in e2e)
    require((full_passes, early_stops) == (2, 2), "E2E result split must be 2 PASS and 2 early stop")
    require(all(row["de_executed"] == "NO" for row in e2e), "DE execution leaked into E2E")
    require(all(row["effect_estimated"] == "NO" for row in e2e), "effect estimation leaked into E2E")

    require(len(invalidities) == 9, "known-invalid denominator must equal 9")
    require(all(row["safe_nonproceed"] == "YES" for row in invalidities), "known-invalid unsafe continuation")
    require(all(row["exact_primary_reason_match"] == "YES" for row in invalidities), "known-invalid reason mismatch")

    atlas_map = {row["metric"]: int(float(row["value"])) for row in atlas}
    expected_atlas = {
        "state_resolved_genes": 225,
        "atlas_genes": 511,
        "overlap_genes": 136,
        "significant_associations": 418,
        "overlap_associations": 310,
        "direction_concordant_overlap_associations": 310,
    }
    require(atlas_map == expected_atlas, f"same-cohort atlas reconciliation failed: {atlas_map}")

    return {
        "status": "PASS",
        "benchmark": {
            "denominator": 15,
            "class_counts": dict(classes),
            "endpoints": {
                name: {
                    "numerator": numerator,
                    "denominator": denominator,
                    "estimate": numerator / denominator,
                    "wilson_95": list(wilson(numerator, denominator)),
                }
                for name, (numerator, denominator) in observed.items()
            },
            "claim_boundary": "state concordance with frozen source-bound human consensus; not independently labelled external accuracy",
        },
        "e2e": {"denominator": 4, "full_passes": full_passes, "early_stops": early_stops},
        "known_invalid": {"denominator": 9, "safe_nonproceed": 9, "exact_reason_match": 9},
        "same_cohort_atlas": expected_atlas,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = reconcile(args.workbook)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
