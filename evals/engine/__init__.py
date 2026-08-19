"""
Eval-Driven Development (EDD) Engine Package.
"""

from .metrics import calculate_pass_at_k, calculate_pass_pow_k, wilson_score_interval, compute_aggregate_metrics
from .graders import BaseGrader, CodeGrader, RuleGrader, ModelGrader, HumanGrader
from .runner import EvalRunner, EvalCaseResult, EvalTrialResult

__all__ = [
    "calculate_pass_at_k",
    "calculate_pass_pow_k",
    "wilson_score_interval",
    "compute_aggregate_metrics",
    "BaseGrader",
    "CodeGrader",
    "RuleGrader",
    "ModelGrader",
    "HumanGrader",
    "EvalRunner",
    "EvalCaseResult",
    "EvalTrialResult",
]
