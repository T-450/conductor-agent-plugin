"""
Statistical metrics calculation for Eval-Driven Development (EDD).
Implements unbiased pass@k (Chen et al. / HumanEval), pass^k, and confidence intervals.
"""

import math
from typing import Dict, Any, Tuple

def calculate_pass_at_k(n: int, c: int, k: int) -> float:
    """
    Computes the unbiased estimator for pass@k.
    pass@k = 1 - prod_{i=0}^{k-1} (n - c - i) / (n - i)
    
    Args:
        n: Total number of trials per problem.
        c: Number of successful trials.
        k: Threshold (e.g. k=1, k=3, k=5).
        
    Returns:
        float between 0.0 and 1.0
    """
    if n < k:
        # If fewer samples than k, fallback to empirical success rate
        return float(c) / float(n) if n > 0 else 0.0
    if n - c < k:
        return 1.0
    
    # 1 - (comb(n-c, k) / comb(n, k))
    prod = 1.0
    for i in range(k):
        prod *= float(n - c - i) / float(n - i)
    return max(0.0, min(1.0, 1.0 - prod))

def calculate_pass_pow_k(n: int, c: int, k: int) -> float:
    """
    Computes pass^k (consecutive stability metric).
    pass^k = (c / n) ^ k
    """
    if n == 0:
        return 0.0
    p = float(c) / float(n)
    return p ** k

def wilson_score_interval(successes: int, trials: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Computes the Wilson score interval for binomial proportions.
    Returns (lower_bound, upper_bound).
    """
    if trials == 0:
        return (0.0, 0.0)
    
    z = 1.96  # 95% confidence
    if confidence == 0.99:
        z = 2.576
    elif confidence == 0.90:
        z = 1.645
        
    p = float(successes) / float(trials)
    denominator = 1.0 + (z ** 2) / trials
    centre_adjusted_probability = p + (z ** 2) / (2.0 * trials)
    adjusted_standard_deviation = math.sqrt((p * (1.0 - p) + (z ** 2) / (4.0 * trials)) / trials)
    
    lower = (centre_adjusted_probability - z * adjusted_standard_deviation) / denominator
    upper = (centre_adjusted_probability + z * adjusted_standard_deviation) / denominator
    
    return (max(0.0, lower), min(1.0, upper))

def compute_aggregate_metrics(trial_results: Dict[str, list], k_values: list = None) -> Dict[str, Any]:
    """
    Computes comprehensive pass@k, pass^k, and confidence intervals for a test suite.
    """
    if k_values is None:
        k_values = [1, 3, 5]
        
    total_cases = len(trial_results)
    if total_cases == 0:
        return {}
        
    pass_at_k_scores = {f"pass@{k}": [] for k in k_values}
    pass_pow_k_scores = {f"pass^{k}": [] for k in k_values}
    total_successes = 0
    total_trials = 0
    
    for case_id, trials in trial_results.items():
        n = len(trials)
        c = sum(1 for t in trials if t.get("passed", False))
        total_trials += n
        total_successes += c

        for k in k_values:
            # Always score every k: calculate_pass_at_k falls back to the
            # empirical rate (c/n) when n < k, so small-trial suites report
            # their true rate instead of a misleading 0.0 from an empty average.
            p_k = calculate_pass_at_k(n, c, k)
            pass_at_k_scores[f"pass@{k}"].append(p_k)
            p_pow_k = calculate_pass_pow_k(n, c, k)
            pass_pow_k_scores[f"pass^{k}"].append(p_pow_k)
                
    summary = {}
    for k in k_values:
        key = f"pass@{k}"
        scores = pass_at_k_scores[key]
        summary[key] = (sum(scores) / len(scores)) if scores else 0.0
        
        pow_key = f"pass^{k}"
        pow_scores = pass_pow_k_scores[pow_key]
        summary[pow_key] = (sum(pow_scores) / len(pow_scores)) if pow_scores else 0.0
        
    ci_lower, ci_upper = wilson_score_interval(total_successes, total_trials)
    summary["overall_accuracy"] = (total_successes / total_trials) if total_trials > 0 else 0.0
    summary["total_trials"] = total_trials
    summary["total_successes"] = total_successes
    summary["confidence_interval_95"] = {"lower": round(ci_lower, 4), "upper": round(ci_upper, 4)}
    
    return summary
