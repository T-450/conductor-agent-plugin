#!/usr/bin/env python3
"""
Eval-Driven Development (EDD) CLI for AI-assisted workflows.
Commands:
  run         Run evaluation test cases with pass@k calculation
  baseline    Create or update golden baseline snapshots
  regression  Compare candidate runs against baseline to detect regressions
  benchmark   Benchmark agent performance across model configurations
  define      Scaffold a new eval case definition
  report      Generate a markdown evaluation summary report
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add evals directory to sys.path
base_eval_dir = Path(__file__).resolve().parent
if str(base_eval_dir) not in sys.path:
    sys.path.insert(0, str(base_eval_dir))

from engine.runner import EvalRunner
from engine.regression import RegressionTracker
from engine.benchmark import ModelBenchmarkHarness

def load_cases(cases_dir: Path, filter_id: str = None) -> list:
    cases = []
    if not cases_dir.exists():
        return cases
    for p in sorted(cases_dir.glob("*.json")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if filter_id and data.get("id") != filter_id and p.stem != filter_id:
                    continue
                cases.append(data)
        except Exception as err:
            print(f"Warning: Failed to load {p.name}: {err}", file=sys.stderr)
    return cases

def cmd_run(args):
    cases_dir = base_eval_dir / "cases"
    cases = load_cases(cases_dir, filter_id=args.case)
    if not cases:
        print(f"No eval cases found matching: {args.case or '*'}")
        sys.exit(1)
        
    print(f"Running {len(cases)} eval case(s) with {args.trials} trials per case...")
    runner = EvalRunner()
    results = runner.run_suite(cases, trials_per_case=args.trials)
    
    if args.json:
        print(json.dumps(results, indent=2))
        return
        
    metrics = results.get("metrics", {})
    print("\n" + "=" * 55)
    print("           EVALUATION RUN RESULTS (EDD)           ")
    print("=" * 55)
    print(f"Total Cases:     {results['total_cases']}")
    print(f"Trials per Case: {results['trials_per_case']}")
    print(f"Total Trials:    {metrics.get('total_trials', 0)}")
    print(f"Overall Acc:     {metrics.get('overall_accuracy', 0)*100:.1f}%")
    print(f"pass@1:          {metrics.get('pass@1', 0)*100:.1f}%")
    print(f"pass@3:          {metrics.get('pass@3', 0)*100:.1f}%")
    print(f"pass^3 (Stable): {metrics.get('pass^3', 0)*100:.1f}%")
    ci = metrics.get('confidence_interval_95', {})
    print(f"95% Conf. Int:   [{ci.get('lower',0)*100:.1f}%, {ci.get('upper',0)*100:.1f}%]")
    print("-" * 55)
    
    for c in results.get("cases", []):
        status = "PASS" if c["success_count"] > 0 else "FAIL"
        p1 = f"{c['pass_at_1']*100:.0f}%"
        print(f" [{status}] {c['name']} (pass@1: {p1}, {c['success_count']}/{c['trials_count']} trials, {c['avg_latency_ms']}ms)")
    print("=" * 55)

def cmd_baseline(args):
    cases_dir = base_eval_dir / "cases"
    cases = load_cases(cases_dir)
    runner = EvalRunner()
    results = runner.run_suite(cases, trials_per_case=args.trials)
    
    out_path = Path(args.save) if args.save else base_eval_dir / "baselines" / "baseline_latest.json"
    RegressionTracker.save_baseline(results, out_path)
    print(f"Golden baseline saved to: {out_path} ({len(cases)} cases recorded)")

def cmd_regression(args):
    baseline_path = Path(args.baseline) if args.baseline else base_eval_dir / "baselines" / "baseline_latest.json"
    if not baseline_path.exists():
        print(f"Error: Baseline file not found: {baseline_path}. Run 'baseline' command first.", file=sys.stderr)
        sys.exit(1)
        
    baseline_data = RegressionTracker.load_baseline(baseline_path)
    cases_dir = base_eval_dir / "cases"
    cases = load_cases(cases_dir)
    
    runner = EvalRunner()
    candidate_data = runner.run_suite(cases, trials_per_case=args.trials)
    comparison = RegressionTracker.compare(baseline_data, candidate_data)
    
    print("\n" + "=" * 55)
    print("          REGRESSION TEST SUITE REPORT          ")
    print("=" * 55)
    print(f"Verdict:           {comparison['verdict']}")
    print(f"Regressions Count: {comparison['regressions_count']}")
    print(f"Baseline Acc:      {comparison['summary']['baseline_accuracy']*100:.1f}%")
    print(f"Candidate Acc:     {comparison['summary']['candidate_accuracy']*100:.1f}%")
    print(f"Accuracy Delta:    {comparison['summary']['accuracy_delta']*100:+.1f}%")
    print(f"pass@3 Delta:      {comparison['summary']['pass@3_delta']*100:+.1f}%")
    
    if comparison["has_regressions"]:
        print("\n[!] REGRESSIONS DETECTED:")
        for r in comparison["regressions"]:
            print(f"  - FAIL: {r['name']} ({r['case_id']}): {r['reason']}")
        sys.exit(1)
    else:
        print("\n[✓] No regressions detected. Safe to release!")
    print("=" * 55)

def cmd_benchmark(args):
    cases_dir = base_eval_dir / "cases"
    cases = load_cases(cases_dir)
    
    # Define benchmark model profiles
    model_profiles = [
        {
            "id": "conductor_pi_v1.2",
            "name": "Conductor Pi/OMP Engine v1.2 (Current)",
            "family": "Multi-Harness Native",
            "cost_per_1k": 0.00
        },
        {
            "id": "gemini_cli_baseline",
            "name": "Gemini CLI Extension v1.0 (Baseline)",
            "family": "Antigravity",
            "cost_per_1k": 0.00
        },
        {
            "id": "claude_code_adapter",
            "name": "Claude Code Conductor Adapter",
            "family": "Claude Code Plugin",
            "cost_per_1k": 0.00
        }
    ]
    
    harness = ModelBenchmarkHarness()
    results = harness.run_benchmark(model_profiles, cases, trials_per_case=args.trials)
    
    print("\n" + "=" * 65)
    print("       CROSS-MODEL & HARNESS AGENT BENCHMARK REPORT       ")
    print("=" * 65)
    table_md = ModelBenchmarkHarness.generate_markdown_comparison_table(results)
    print(table_md)
    print("=" * 65)

def cmd_define(args):
    case_name = args.name
    case_id = case_name.lower().replace(" ", "_").replace("-", "_")
    cases_dir = base_eval_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    target_file = cases_dir / f"{case_id}.json"
    
    template = {
        "id": case_id,
        "name": case_name,
        "category": args.category,
        "grader_type": args.grader,
        "description": f"Evaluation case for {case_name}",
        "expected": {
            "must_contain": ["expected_key_token"],
            "regex_patterns": [r".*"]
        },
        "mock_output": "Sample output matching criteria"
    }
    
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2)
    print(f"Scaffolded new eval case at: {target_file}")

def main():
    parser = argparse.ArgumentParser(description="Eval-Driven Development (EDD) CLI Harness")
    subparsers = parser.add_subparsers(dest="command", help="EDD commands")
    
    # Run
    p_run = subparsers.add_parser("run", help="Run evaluation cases")
    p_run.add_argument("case", nargs="?", default=None, help="Case ID to run (omit for all)")
    p_run.add_argument("--trials", "-t", type=int, default=3, help="Number of trials per case (default: 3)")
    p_run.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # Baseline
    p_base = subparsers.add_parser("baseline", help="Create or update golden baseline snapshot")
    p_base.add_argument("--save", "-s", type=str, default=None, help="Path to save baseline")
    p_base.add_argument("--trials", "-t", type=int, default=3, help="Number of trials per case")
    
    # Regression
    p_reg = subparsers.add_parser("regression", help="Run regression suite against baseline")
    p_reg.add_argument("--baseline", "-b", type=str, default=None, help="Path to baseline file")
    p_reg.add_argument("--trials", "-t", type=int, default=3, help="Number of trials per case")
    
    # Benchmark
    p_bench = subparsers.add_parser("benchmark", help="Benchmark performance across model configurations")
    p_bench.add_argument("--trials", "-t", type=int, default=3, help="Number of trials per case")
    
    # Define
    p_def = subparsers.add_parser("define", help="Scaffold a new eval case definition")
    p_def.add_argument("name", type=str, help="Human-readable name of the eval case")
    p_def.add_argument("--category", choices=["capability", "regression", "adversarial"], default="capability")
    p_def.add_argument("--grader", choices=["rule", "code", "model", "human"], default="rule")
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    cmd_map = {
        "run": cmd_run,
        "baseline": cmd_baseline,
        "regression": cmd_regression,
        "benchmark": cmd_benchmark,
        "define": cmd_define
    }
    
    cmd_map[args.command](args)

if __name__ == "__main__":
    main()
