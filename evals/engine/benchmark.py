"""
Cross-Model Benchmarking Harness for Eval-Driven Development (EDD).
Compares agent performance, reliability (pass@k), latency, and token efficiency across model versions.
"""

import time
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from .runner import EvalRunner

class ModelBenchmarkHarness:
    """Benchmarks agent performance across multiple model versions or configurations."""
    
    def __init__(self, runner: Optional[EvalRunner] = None):
        self.runner = runner or EvalRunner()
        
    def run_benchmark(self, model_configs: List[Dict[str, Any]], eval_cases: List[Dict[str, Any]], trials_per_case: int = 3) -> Dict[str, Any]:
        """
        Runs the test suite across multiple model configurations.
        """
        benchmark_results = {}
        
        for model in model_configs:
            model_id = model.get("id", "default_model")
            model_name = model.get("name", model_id)
            print(f"[*] Benchmarking model: {model_name} ({len(eval_cases)} cases, {trials_per_case} trials/case)...")
            
            # Simulated or actual model executor
            executor = model.get("executor_fn", None)
            start_t = time.time()
            suite_res = self.runner.run_suite(eval_cases, trials_per_case=trials_per_case, executor_fn=executor)
            total_duration = round(time.time() - start_t, 2)
            
            metrics = suite_res.get("metrics", {})
            benchmark_results[model_id] = {
                "name": model_name,
                "model_family": model.get("family", "Unknown"),
                "duration_seconds": total_duration,
                "overall_accuracy": metrics.get("overall_accuracy", 0.0),
                "pass_at_1": metrics.get("pass@1", 0.0),
                "pass_at_3": metrics.get("pass@3", 0.0),
                "pass_pow_3": metrics.get("pass^3", 0.0),
                "confidence_interval_95": metrics.get("confidence_interval_95", {}),
                "avg_latency_ms": sum(c.get("avg_latency_ms", 0.0) for c in suite_res.get("cases", [])) / len(eval_cases) if eval_cases else 0.0,
                "estimated_cost_per_1k_runs": model.get("cost_per_1k", 0.0),
                "detailed_cases": suite_res.get("cases", [])
            }
            
        # Rank models by pass@3 then latency
        ranked_models = sorted(
            benchmark_results.keys(),
            key=lambda mid: (benchmark_results[mid]["pass_at_3"], -benchmark_results[mid]["avg_latency_ms"]),
            reverse=True
        )
        
        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_models": len(model_configs),
            "total_cases_per_model": len(eval_cases),
            "rankings": ranked_models,
            "models": benchmark_results
        }
        
    @staticmethod
    def generate_markdown_comparison_table(benchmark_output: Dict[str, Any]) -> str:
        """Renders an ASCII/Markdown benchmark comparison table."""
        models = benchmark_output.get("models", {})
        rankings = benchmark_output.get("rankings", [])
        
        lines = [
            "| Rank | Model / Agent Version | pass@1 | pass@3 | pass^3 (Stability) | Avg Latency | 95% Conf. Interval |",
            "|---|---|---|---|---|---|---|"
        ]
        
        for rank, mid in enumerate(rankings, 1):
            m = models[mid]
            p1 = f"{m['pass_at_1']*100:.1f}%"
            p3 = f"{m['pass_at_3']*100:.1f}%"
            p_pow = f"{m['pass_pow_3']*100:.1f}%"
            lat = f"{m['avg_latency_ms']:.1f}ms"
            ci = f"[{m['confidence_interval_95'].get('lower', 0)*100:.1f}%, {m['confidence_interval_95'].get('upper', 0)*100:.1f}%]"
            lines.append(f"| #{rank} | **{m['name']}** | {p1} | {p3} | {p_pow} | {lat} | {ci} |")
            
        return "\n".join(lines)
