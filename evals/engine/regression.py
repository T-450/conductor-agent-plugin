"""
Regression Test Suite and Baseline Manager for Eval-Driven Development (EDD).
Tracks baseline performance snapshots and flags breaking regressions.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class RegressionTracker:
    """Manages baseline comparison and detects regressions in prompt or agent changes."""
    
    @staticmethod
    def save_baseline(eval_run_result: Dict[str, Any], baseline_path: Path):
        """Saves an evaluation run as the golden baseline."""
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(eval_run_result, f, indent=2)
            
    @staticmethod
    def load_baseline(baseline_path: Path) -> Dict[str, Any]:
        """Loads a saved golden baseline."""
        if not baseline_path.exists():
            raise FileNotFoundError(f"Baseline not found: {baseline_path}")
        with open(baseline_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    @staticmethod
    def compare(baseline: Dict[str, Any], candidate: Dict[str, Any],
                degradation_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Compares candidate eval results against a baseline.
        Returns detailed delta analysis, including regressions, improvements, and metrics changes.

        Besides full pass->fail flips, a case counts as a regression when its
        pass@1 drops severely: relative drop >= degradation_threshold AND
        absolute drop >= degradation_threshold (default 0.5/0.5, so a single
        flaky trial out of 3 is a warning, not a gate failure). Smaller drops
        are recorded in the non-blocking ``warnings`` list.
        """
        baseline_cases = {c["case_id"]: c for c in baseline.get("cases", [])}
        candidate_cases = {c["case_id"]: c for c in candidate.get("cases", [])}

        regressions = []
        improvements = []
        warnings = []
        unchanged_pass = []
        unchanged_fail = []
        latency_changes = []
        
        all_case_ids = sorted(list(set(baseline_cases.keys()).union(candidate_cases.keys())))
        
        for cid in all_case_ids:
            b_case = baseline_cases.get(cid)
            c_case = candidate_cases.get(cid)
            
            if not b_case:
                # New test case
                if c_case.get("pass_at_1", 0.0) > 0.0:
                    improvements.append({"case_id": cid, "note": "New passing case added"})
                continue
                
            if not c_case:
                regressions.append({"case_id": cid, "reason": "Test case missing from candidate run"})
                continue
                
            b_p1 = b_case.get("pass_at_1", 0.0)
            c_p1 = c_case.get("pass_at_1", 0.0)
            
            # Regression check: full pass->fail flip, or severe partial degradation.
            if b_p1 > 0.0 and c_p1 == 0.0:
                regressions.append({
                    "case_id": cid,
                    "name": c_case.get("name", cid),
                    "baseline_pass@1": round(b_p1, 4),
                    "candidate_pass@1": round(c_p1, 4),
                    "reason": "Case previously passed, now failing"
                })
            elif b_p1 > 0.0 and c_p1 < b_p1:
                abs_drop = b_p1 - c_p1
                rel_drop = abs_drop / b_p1
                entry = {
                    "case_id": cid,
                    "name": c_case.get("name", cid),
                    "baseline_pass@1": b_p1,
                    "candidate_pass@1": round(c_p1, 4),
                    "reason": (f"Partial degradation: pass@1 {b_p1:.2f} -> {c_p1:.2f} "
                               f"(relative drop {rel_drop*100:.0f}%)")
                }
                if rel_drop >= degradation_threshold and abs_drop >= degradation_threshold:
                    regressions.append(entry)
                else:
                    warnings.append(entry)
            elif b_p1 == 0.0 and c_p1 > 0.0:
                improvements.append({
                    "case_id": cid,
                    "name": c_case.get("name", cid),
                    "baseline_pass@1": b_p1,
                    "candidate_pass@1": c_p1
                })
            elif b_p1 > 0.0:
                unchanged_pass.append(cid)
            else:
                unchanged_fail.append(cid)
                
            # Latency delta
            b_lat = b_case.get("avg_latency_ms", 0.0)
            c_lat = c_case.get("avg_latency_ms", 0.0)
            if b_lat > 0:
                lat_diff_pct = ((c_lat - b_lat) / b_lat) * 100.0
                latency_changes.append({"case_id": cid, "delta_pct": round(lat_diff_pct, 1)})
                
        b_metrics = baseline.get("metrics", {})
        c_metrics = candidate.get("metrics", {})
        
        accuracy_delta = c_metrics.get("overall_accuracy", 0.0) - b_metrics.get("overall_accuracy", 0.0)
        pass_at_3_delta = c_metrics.get("pass@3", 0.0) - b_metrics.get("pass@3", 0.0)
        
        has_regressions = len(regressions) > 0
        
        return {
            "verdict": "FAIL - REGRESSIONS DETECTED" if has_regressions else "PASS - NO REGRESSIONS",
            "has_regressions": has_regressions,
            "regressions_count": len(regressions),
            "improvements_count": len(improvements),
            "warnings_count": len(warnings),
            "regressions": regressions,
            "improvements": improvements,
            "warnings": warnings,
            "summary": {
                "baseline_accuracy": b_metrics.get("overall_accuracy", 0.0),
                "candidate_accuracy": c_metrics.get("overall_accuracy", 0.0),
                "accuracy_delta": round(accuracy_delta, 4),
                "baseline_pass@3": b_metrics.get("pass@3", 0.0),
                "candidate_pass@3": c_metrics.get("pass@3", 0.0),
                "pass@3_delta": round(pass_at_3_delta, 4)
            }
        }
