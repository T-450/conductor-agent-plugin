"""
Evaluation Runner for Eval-Driven Development (EDD).
Executes capability and regression test cases across k trials and computes pass@k metrics.
"""

import time
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from .metrics import compute_aggregate_metrics, calculate_pass_at_k, calculate_pass_pow_k
from .graders import CodeGrader, RuleGrader, ModelGrader, HumanGrader, BaseGrader

@dataclass
class EvalTrialResult:
    trial_index: int
    passed: bool
    score: float
    reasoning: str
    latency_ms: float
    grader_type: str
    output_sample: Optional[str] = None

@dataclass
class EvalCaseResult:
    case_id: str
    name: str
    category: str
    trials_count: int
    success_count: int
    pass_at_1: float
    pass_at_3: float
    pass_pow_3: float
    avg_latency_ms: float
    trials: List[Dict[str, Any]]

class EvalRunner:
    """Executes evaluation cases with k trials and calculates statistical metrics."""
    
    def __init__(self, graders: Optional[Dict[str, BaseGrader]] = None):
        self.graders = graders or {
            "code": CodeGrader("CodeGrader"),
            "rule": RuleGrader("RuleGrader"),
            "model": ModelGrader("ModelGrader"),
            "human": HumanGrader("HumanGrader"),
        }
        
    def run_case(self, case_spec: Dict[str, Any], trials_count: int = 3, executor_fn: Optional[callable] = None) -> EvalCaseResult:
        case_id = case_spec.get("id", "unknown_case")
        name = case_spec.get("name", case_id)
        category = case_spec.get("category", "capability")
        grader_type = case_spec.get("grader_type", "rule").lower()
        expected = case_spec.get("expected", {})
        
        grader = self.graders.get(grader_type, self.graders["rule"])
        trials = []
        
        for i in range(trials_count):
            start_time = time.time()
            if executor_fn:
                try:
                    actual_output = executor_fn(case_spec, i)
                except Exception as err:
                    actual_output = f"ERROR: {str(err)}"
            else:
                actual_output = case_spec.get("mock_output", "")
                
            latency_ms = round((time.time() - start_time) * 1000, 2)
            eval_res = grader.evaluate(actual_output, expected)
            
            trial = EvalTrialResult(
                trial_index=i + 1,
                passed=eval_res["passed"],
                score=eval_res.get("score", 1.0 if eval_res["passed"] else 0.0),
                reasoning=eval_res.get("reasoning", ""),
                latency_ms=latency_ms,
                grader_type=grader.name,
                output_sample=str(actual_output)[:200] if actual_output else None
            )
            trials.append(asdict(trial))
            
        successes = sum(1 for t in trials if t["passed"])
        pass_at_1 = calculate_pass_at_k(trials_count, successes, 1)
        pass_at_3 = calculate_pass_at_k(trials_count, successes, min(3, trials_count))
        pass_pow_3 = calculate_pass_pow_k(trials_count, successes, min(3, trials_count))
        avg_latency = sum(t["latency_ms"] for t in trials) / len(trials) if trials else 0.0
        
        return EvalCaseResult(
            case_id=case_id,
            name=name,
            category=category,
            trials_count=trials_count,
            success_count=successes,
            pass_at_1=round(pass_at_1, 4),
            pass_at_3=round(pass_at_3, 4),
            pass_pow_3=round(pass_pow_3, 4),
            avg_latency_ms=round(avg_latency, 2),
            trials=trials
        )
        
    def run_suite(self, case_specs: List[Dict[str, Any]], trials_per_case: int = 3, executor_fn: Optional[callable] = None) -> Dict[str, Any]:
        results = []
        trial_dict = {}
        
        for spec in case_specs:
            case_res = self.run_case(spec, trials_count=trials_per_case, executor_fn=executor_fn)
            results.append(asdict(case_res))
            trial_dict[case_res.case_id] = case_res.trials
            
        aggregate = compute_aggregate_metrics(trial_dict, k_values=[1, 3, 5])
        
        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_cases": len(case_specs),
            "trials_per_case": trials_per_case,
            "metrics": aggregate,
            "cases": results
        }
