"""
Eval case validator for Eval-Driven Development (EDD).
Statically flags vacuous (grades nothing, always passes) or unwinnable
(mock fails its own criteria) eval cases at load time.

Severity contract:
  error   - the case cannot meaningfully pass or can never pass; fix the case.
  warning - the case passes but weakly; human judgment required.
Flagged cases are still loaded (warn-and-keep): skipping them would trip the
regression gate's missing-case rule and produce false regressions.
"""

import re
from typing import Dict, Any, List

KNOWN_GRADERS = ("rule", "code", "model", "human")

# Criteria keys that actually influence each grader's verdict. A case whose
# expected block contains none of these for its grader passes vacuously.
EFFECTIVE_CRITERIA = {
    "rule": ("must_contain", "must_not_contain", "regex_patterns",
             "json_schema", "checkbox_states"),
    "code": ("must_contain", "must_not_contain", "regex_patterns"),
    "model": ("rubric", "min_score"),
    "human": ("risk_level", "manual_checklist"),
}


def _is_catch_all(pattern: str) -> bool:
    """True when the pattern matches empty output (probatively worthless)."""
    try:
        return re.fullmatch(pattern, "") is not None
    except re.error:
        return False


def validate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """Validates one eval case spec. Returns {case_id, errors, warnings}."""
    from .graders import CodeGrader, RuleGrader, ModelGrader, HumanGrader

    errors: List[str] = []
    warnings: List[str] = []
    case_id = case.get("id", "<missing id>")

    grader_type = str(case.get("grader_type", "rule")).lower()
    if grader_type not in KNOWN_GRADERS:
        errors.append(
            f"unknown grader_type '{case.get('grader_type')}' "
            f"(known: {', '.join(KNOWN_GRADERS)})"
        )
        return {"case_id": case_id, "errors": errors, "warnings": warnings}

    expected = case.get("expected")
    if not isinstance(expected, dict) or not expected:
        errors.append("empty or missing 'expected' criteria: case grades nothing")
        return {"case_id": case_id, "errors": errors, "warnings": warnings}

    effective = [k for k in EFFECTIVE_CRITERIA[grader_type] if expected.get(k)]
    if not effective:
        errors.append(
            f"no effective criteria for grader '{grader_type}': "
            f"expected keys {sorted(expected.keys())} are all ignored by it"
        )

    for pat in expected.get("regex_patterns", []):
        try:
            re.compile(pat)
        except re.error as err:
            errors.append(f"invalid regex pattern '{pat}': {err}")
        else:
            if _is_catch_all(pat):
                warnings.append(
                    f"catch-all regex '{pat}' matches empty output; "
                    f"it cannot discriminate pass from fail"
                )

    if grader_type == "human":
        warnings.append("human grader auto-passes; case requires manual adjudication")

    if "mock_output" not in case or case.get("mock_output") is None:
        if case.get("requires_executor") is True:
            # Executor-supplied output arrives at run time; nothing to self-check.
            pass
        else:
            warnings.append("no mock_output: default runs grade an empty string")
    else:
        grader = {
            "rule": RuleGrader("RuleGrader"),
            "code": CodeGrader("CodeGrader"),
            "model": ModelGrader("ModelGrader"),
            "human": HumanGrader("HumanGrader"),
        }[grader_type]
        res = grader.evaluate(case["mock_output"], expected)
        if not res.get("passed", False):
            errors.append(
                "mock_output fails its own criteria "
                f"(case can never pass unmodified): {res.get('reasoning', '')}"
            )

    return {"case_id": case_id, "errors": errors, "warnings": warnings}


def validate_suite(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validates a list of case specs. Returns counts plus per-case flags."""
    flagged = [validate_case(c) for c in cases]
    flagged = [f for f in flagged if f["errors"] or f["warnings"]]
    return {
        "total_cases": len(cases),
        "flagged_cases": len(flagged),
        "error_count": sum(len(f["errors"]) for f in flagged),
        "warning_count": sum(len(f["warnings"]) for f in flagged),
        "cases": flagged,
    }
