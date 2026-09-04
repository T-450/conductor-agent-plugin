# SPEC-verify-harness

## Objective

Define the executable artifacts a verify track produces so that "verified"
means "a program exited 0", not "an agent feels good". Success = any party
(user, implementer, reviewer, CI) can re-run one command and get a
machine-checkable verdict plus reviewable evidence.

## Scope

In: `verify/` layout, `contract.json` schema (incl. T0–T4 backends),
`harness.sh` contract, baseline capture, evidence folder, re-run and maintain
protocols, fixtures/seeds/mounts conventions.
Out: gate protocol (lifecycle), tier selection (strategy), harness evals
(evals module).

## Detailed behavior

### Layout (per track)

```text
conductor/tracks/<id>/verify/
  contract.json      # machine-checkable: commands, pass criteria, backend, tier per item
  harness.sh         # single entrypoint -> exit 0 pass / 1 fail / 2 refused; JSON summary
  mounts             # optional host:guest binds (Junie shape)
  images/<name>/     # per-track environment templates (Dockerfiles)
  metrics.json       # written by harness.sh --report (rounds, issues, classes)
  traceability.md    # acceptance-item <-> check matrix (lifecycle touchpoint 2)
  approvals.log      # append-only user approvals + proceed-with-reason lines
                       # (author-marked) plus agent RED-DEMO lines
  seed.json          # stored seed bytes/hashes per file (byte-identity checks)
  holdout/           # reserved set; implementer never receives contents (see custody)
  baseline.log       # harness output on the preferred-clean tree (red, or green + hold-out set)
  evidence/          # per-run logs, screenshots, reports

All `command` paths in contract.json resolve with `verify/` as the working
directory (e.g. `./harness.sh --check acc-1`); a stranger runs from
`conductor/tracks/<id>/verify/`. Shared starting templates may be copied
from the project-level seeding library `conductor/verify-images/<name>/`,
but the per-track copy is canonical — the library never overrides track files.
```

### contract.json (v1 schema)

```json
{
  "track": "<id>",
  "checks": [
    {"id": "acc-1", "acceptance": "quote of spec item", "tier": "T2",
     "command": "./harness.sh --check acc-1",
     "pass": "exit 0 and summary.failed == 0", "backend": "docker",
     "estimated_minutes": 4, "seam": true, "quarantine": false,
     "profile": {"scores": {"state": 1, "deps": 1, "hw": 0, "blast": 1},
                 "total": 3, "reason": "shared PG state, user ratified"}}
  ],
  "backend": "docker",
  "backends": {
    "docker": {"template": "images/default/Dockerfile"},
    "remote-lab": {"template": "images/hw-lab/Dockerfile",
                   "access": "user-supplied ssh/device-farm handle",
                   "budget_cap_usd_per_run": 5.00,
                   "rate_usd_per_min": 0.05}
  },
  "unfaithful": ["documented known divergences, user-confirmed"],
  "artifacts": ["paths the run itself may dirty (build outputs, in-repo logs)"],
  "readiness": "how the harness signals the app is up (port 200 / log line / visual)"
}
```

Backend vocabulary is single and closed: `local | docker | <named-template>`.
Selector precedence: per-check `backend` beats the top-level default; both
name entries in `backends`. `--all` groups checks per backend (local first,
then each named backend); a mixed-backend run reports per-group verdicts.
T4-required is a predicate, not a label: a check with `tier == T4` is
T4-required. Quarantine is a per-check flag (`quarantine: true`); the old
backend-level id list is removed.
Templates are concrete; no `TBD` providers — a template that cannot name
its backend fails validation. Path resolution rule: `template:` strings
resolve against the track `verify/` dir (`template: images/hw-lab` →
`<track>/verify/images/hw-lab/`); the project seeding library is addressed
only by `seed_from: conductor/verify-images/<name>` at seed time and never
by `template:` — per-track copies are canonical. `estimated_minutes` per
check feeds the pre-run cost projection; `seam: true` flags checks belonging
to the T1/T2 overlap suite (eval cases 6a/6b).
T4 entries MUST carry `access`, numeric `budget_cap_usd_per_run` plus
`rate_usd_per_min`, and `quarantine`. Spend accounting is pre-run projection
plus report-time reconciliation: `--check-contract` refuses when the
projected cost (estimated minutes × rate) exceeds the cap, and `--report`
logs actual duration × rate against it. Known limitation, stated plainly:
local wall-clock is a proxy, not provider billing — the cap gates runaway
runs, it does not settle invoices. For contracts containing any T4 check,
`--check-contract` additionally refuses unless ≥1 NON-quarantined T4 check
exists in the same contract (per-contract minimum — a green verdict with
zero T4 signal is invalid);
quarantine covers supplemental checks only; quarantined failures go to
explicit user review.

### Environment templates (borrowed from Junie `/demo` config shape)

- Two halves, both committed: `verify/images/<name>/Dockerfile` layering app
  runtimes over a base that already provides the display/tooling stack (never
  reinstall the base), plus the launch binding in `contract.json`
  (`backend:` + build/launch/readiness, mirroring Junie's `vm:` +
  Build/Launch sections). Single-template shortcut: `verify/images/Dockerfile`
  referenced as `backend: default`.
- `verify/mounts` (optional, one `<host>:<guest>[:ro|:rw]` per line,
  `$HOME` expansion, `#` comments): extra bind mounts for credentials,
  fixtures, prebuilt artifacts. Missing host paths warn and are skipped,
  never refuse the run. The project root is always mounted read-write at
  `/workspace` automatically. Because the baseline requires an untouched
  tree, every run records `git status --porcelain` before and after: a dirty
  tree at baseline is recorded in `baseline.log`; drift introduced DURING a
  run fails the run's cleanliness check. Drift = after-state minus
  before-state (a post-implement tree starts dirty legitimately — only paths
  the run itself changed count), excluding `evidence/` and paths listed in
  the contract's `artifacts:` array (declared run outputs: build artifacts,
  in-repo logs the app touches). Undeclared drift corrupts evidence
  attribution (which change produced this output?), so it fails. Rationale
  for the asymmetry: a dirty tree at baseline is the user's intentional
  mid-work state and refusing it would block legitimate verification.
- Host-side builds happen only when the contract explicitly asks; by default
  everything builds inside the environment.

### harness.sh contract ("build the lever", pstack)

- One entrypoint, subcommands per check plus `--all`; `--dry-run` for
  destructive steps; rich `--help`; descriptive errors telling the operator
  what to do instead; JSON summary (`{passed, failed, skipped, duration_s}`).
  `--all` excludes `holdout/` by default; the holdout leg runs only via
  `harness.sh --holdout`, executed by the holder (user in solo tracks, an
  orchestrator-designated non-implement party otherwise) — never by
  `verify-runner`, never by implement delegates.
- `--check-contract` preflight: validates the contract schema at runtime
  (≥1 check configured; named backends exist; T4 fields present; no TBD
  providers; contracts with T4 checks keep ≥1 non-quarantined T4 check) and
  refuses with the missing field named. Runs before any expensive step. Zero
  checks is refused outright — the empty harness can never grade `pass`.
  A fully faithful harness (empty `unfaithful` list) MUST validate: the list
  records divergences, and inventing unfaithfulness to satisfy a checker is
  forbidden.
- `--report` writes `verify/metrics.json` (rounds-to-approval, issues per
  round counted from `USER:` NEEDS_REVISION message bodies (verdict line
  plus following lines) in `approvals.log`, observed-red flag, class
  `approved | overridden`). "Issues" = distinct user-worded objections
  (quoted strings), not agent paraphrases. The observed-red flag is set
  when a `RED-DEMO` line (failing run shown to the user) is on file, never
  asserted independently.
- Exit 0 iff all non-quarantined checks pass (with the T4 non-quarantined
  minimum above); exit 2 means refused (contract invalid or over budget).
  Deterministic seeds; fixture setup/teardown inside the harness (host mounts
  declared like Junie `mounts`, missing paths warn, never hard-fail setup).
- Base images layer app runtimes over a display/tooling base where UI driving
  is needed; project root mounted read-write at a documented path.

### Evidence folder (borrowed from Junie `/demo` artifacts)

Each run writes a per-run directory under `verify/evidence/` holding the
JSON summary log, any screenshots/recordings, and a self-contained report
with two sections: what was tested (steps + what was observed) and the
verdict plus issues spotted. Payload-to-report mapping (harness layer
only): execution payload `{passed, failed, skipped}` maps to report
`pass` (all passed), `fail` (any non-quarantined failed), `partial`
(only quarantined failed or any skipped). Report-to-track mapping lives in
SPEC-verify-lifecycle (gate protocol), not here: two layers with a
specified mapping, not one vocabulary. Evidence is kept
across runs — nothing auto-cleans; deletion is manual and explicit.

### Hold-out custody

`verify/holdout/` holds the reserved set the implementer never sees.
Enforcement is by information flow, not filesystem: in orchestrated tracks
the orchestrator never passes holdout contents to implement delegates and
never assigns the `--holdout` leg to `verify-runner` (which runs `--all`
only and therefore never executes holdout checks); in solo tracks the user
holds it (runs `harness.sh --holdout` themselves or pastes it at review).
Stated limit: in solo mode holder and implementer are the same human behind
one agent — custody there is informed-consent labeling (`holdout/` is
clearly marked do-not-train), not a mechanism. The claim "implementer never
sees" is therefore a protocol rule with a named enforcer per mode, not a
filesystem property.

### Baseline and re-run

- Baseline is captured on the preferred-clean tree BEFORE implement: failing
  acceptance checks recorded red, or green baseline plus a reserved hold-out
  set the implementer never sees. `baseline.log` records the HEAD commit
  hash at capture; the ordering criterion (baseline predates the first
  implement commit) is enforced by the review audit comparing hashes via
  merge-base, not by `--check-contract`.
- Post-implement, the implementer (or orchestrator delegate) re-runs the same
  `harness.sh --all`; output lands in `evidence/` and is attached at review.
- Maintain: scoped re-trial over changed areas on track events or explicit
  user invocation (`--maintain`); user-gated per lifecycle protocol. No
  daemon or scheduler in v1 (zero-runtime-dependency design holds).

## Success criteria

- [ ] `harness.sh --all` exit code agrees with its JSON summary on 5/5 runs.
- [ ] Baseline log HEAD hash is an ancestor of the first implement commit
  (checked by the review audit, not the preflight).
- [ ] `--check-contract` refuses a T4 entry missing access/budget/rate/
  quarantine or an unnamed backend — and accepts a fully faithful harness
  (empty `unfaithful` list).
- [ ] Over-cap run is refused (exit 2) rather than billed.
- [ ] A stranger can run the harness from the contract alone (reviewer test).

## Boundaries

- Always: JSON summary; teardown (VMs/containers stopped); evidence archived.
- Ask first: adding host mounts with credentials; exceeding budget caps
  (the meter, not vibes, decides).
- Never: destructive steps without `--dry-run`; secrets in logs or evidence.

## Open questions

- Screenshot/video evidence requirements for CLI-only tracks (logs suffice?).
- Hold-out set custody: who holds it so implementers can't train to it?
