#!/bin/sh
# Pilot harness: verify-runner parity (T0 file-shape checks).
# Usage: ./harness.sh --check <id> | --all | --check-contract | --report | --holdout | --dry-run | --help
# cwd: conductor/tracks/verify_runner_parity_20260904/verify/
set -u
ROOT="${HARNESS_ROOT:-../../../..}"
COPILOT="$ROOT/.github/agents/orchestra-verify-runner.agent.md"
AGY="$ROOT/.agents/agents/orchestra-verify-runner.md"

domain_hash() {
  cat contract.json harness.sh traceability.md 2>/dev/null | sha256sum | cut -d' ' -f1
}

check_acc1() {
  [ -f "$COPILOT" ] || { echo "missing $COPILOT"; return 1; }
  grep -q "^name: orchestra-verify-runner" "$COPILOT" || { echo "bad name frontmatter"; return 1; }
  grep -q "subagents/verify-runner.md" "$COPILOT" || { echo "no shared role-prompt reference"; return 1; }
  echo "acc-1 ok"
}

check_acc2() {
  [ -f "$AGY" ] || { echo "missing $AGY"; return 1; }
  grep -q "^name: orchestra-verify-runner" "$AGY" || { echo "bad name frontmatter"; return 1; }
  grep -q "subagent: true" "$AGY" || { echo "missing subagent:true"; return 1; }
  grep -qi "evidence.only\|evidence-only" "$AGY" || { echo "role not evidence-only"; return 1; }
  echo "acc-2 ok"
}

check_acc3() {
  cd "$ROOT" || return 1
  python3 evals/run_evals.py >/dev/null 2>&1 || { echo "run_evals failed"; return 1; }
  python3 evals/edd.py validate >/dev/null 2>&1 || { echo "edd validate failed"; return 1; }
  echo "acc-3 ok"
}

check_contract() {
  python3 -c "import json;d=json.load(open('contract.json'));assert d['checks'], 'zero checks';assert d.get('backend'), 'no backend'" || return 1
  echo "contract ok"
}

do_report() {
  RED=$(grep -h "RED-DEMO" approvals.log 2>/dev/null | tail -1)
  FLAG="absent"
  if [ -n "$RED" ]; then
    RHASH=$(echo "$RED" | sed 's/.*hash=\([^ ]*\).*/\1/')
    [ "$RHASH" = "$(domain_hash)" ] && FLAG="bound" || FLAG="orphaned"
  fi
  python3 -c "import json;json.dump({'rounds_to_approval': 0, 'issues_per_round': [], 'observed_red': '$FLAG', 'class': 'approved'}, open('metrics.json','w'), indent=2)"
  echo "observed-red: $FLAG"
}

summary() { # $1 passed $2 failed $3 skipped
  python3 -c "import json;print(json.dumps({'passed': $1, 'failed': $2, 'skipped': $3}))"
}

run_one() {
  case "$1" in
    acc-1) check_acc1;; acc-2) check_acc2;; acc-3) check_acc3;;
    *) echo "unknown check $1"; return 2;;
  esac
}

case "${1:---help}" in
  --check) run_one "$2"; rc=$?; [ $rc -eq 0 ] && summary 1 0 0 || summary 0 1 0; exit $rc;;
  --all)
    p=0; f=0
    for c in acc-1 acc-2 acc-3; do
      if run_one "$c"; then p=$((p+1)); else f=$((f+1)); fi
    done
    summary $p $f 0; [ $f -eq 0 ];;
  --check-contract) check_contract;;
  --report) do_report;;
  --holdout) echo "NO-HOLDOUT: T0 pilot, no reserved set";;
  --dry-run) echo "would run: acc-1 acc-2 acc-3 (local, ~5 min acc-3)";;
  *) echo "usage: $0 --check <id> | --all | --check-contract | --report | --holdout | --dry-run | --help"; exit 2;;
esac
