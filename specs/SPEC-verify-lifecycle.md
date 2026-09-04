# SPEC-verify-lifecycle

## Objective

Define the `conductor-verify` skill protocol that carries a track from "no
verification" to "user-approved harness" BEFORE `conductor-implement` may
start. The user is the only ground truth: agent output is draft until the
user has seen it and said so. Success = implement is gated on a recorded
user approval, and a seeded-but-untouched harness can never satisfy the gate.

## Scope

In: skill file, track states, three user touchpoints, approval handling,
seeded-vs-owned rules, handoffs to existing skills.
Out: harness internals (SPEC-verify-harness), tier catalog
(SPEC-verify-strategy), eval cases (SPEC-verify-evals).

## Detailed behavior

### Track states (`metadata.json: verify_status` + `seed_confirmed`)

`VERIFY_DRAFT` → `USER_TRIAL` → `REFINING` (loop) → `VERIFY_APPROVED`.
`VERIFY_FAILED` only when the user declares the loop dead; resumption needs
fresh user direction and re-enters at `USER_TRIAL`.

`seed_confirmed` flips on either of two events: (a) the user edits a seeded
file (any byte difference from `seed.json` the agent did not write), or
(b) a full-scope user approval. A revert to seed bytes un-confirms unless an
approval stands. The gate requires `seed_confirmed AND status ==
VERIFY_APPROVED`, or an explicit user instruction to proceed without it
(logged; never assumed from vague assent — ask "log this as proceed?" and
get confirmation). Approval never covers a seeded-untouched harness: an
approval of unexercised content is invalid, so the seed is always either
touched or run before it can pass.

### Three mandatory touchpoints (each a MANDATORY STOP)

1. **Ideation interview.** Agent asks how the user checks correctness today
   (commands, eyeballing, staging rituals, hardware quirks). One question at a
   time via native `ask` modal where available (`rules/conductor_pi.md`),
   text fallback otherwise; options Recommended-first with an Other option.
   Ask only what only the user knows.
2. **Traceability review.** Draft harness ships `verify/traceability.md`:
   every `spec.md` Acceptance item maps to ≥1 executable check. User confirms
   each mapping or marks gaps. Unmappable items ("fast", "intuitive") are
   pushed back for operationalization or listed explicitly as NOT COVERED.
3. **Trial + approval.** Scope picker before any expensive run (track diff,
   session changes, smoke test — list adapts; free-text "verify X yourself"
   passed verbatim). Visible milestone plan the user may interrupt. Upfront
   prereq checks; fast refusal with the fix stated. The harness must be
   observed red — a known-bad case (ideally a user-supplied past bug) fails
   while the good path passes, SHOWN to the user. Approval is collected with
   plain-word options (Approve / Needs revision + what / Failed); a modal
   click logs `author=user`, text replies are quoted verbatim. Objection text
   is kept in the user's words for the metrics.

### Trial run discipline (Junie `/demo`-inspired; no-double-launch is our design, marked below)

- `--trial` never starts an expensive run straight away.
- Stop requests tear the environment down cleanly. [Own design, not Junie:]
  the environment is never launched twice in one session unless explicitly
  asked.

### Seeded-vs-owned rules (Junie `/demo` first-run setup, plus one own-design rule marked below)

- Agent-seeded `contract.json`/`harness.sh` never satisfy the gate on their
  own. Seed bytes (or hashes) are stored in `verify/seed.json` at seed time.
  [Own design, not Junie:] a file still byte-identical to its seed with no
  approval track in progress counts as no setup at all — the prompt keeps
  returning until the user engages.
- Fill-in choice at seed time: "fill them in for me" (agent inspects the
  project, presents the resulting plan for confirmation, then writes) vs
  "I'll do it myself" (seed left untouched). Either way the final review
  stays with the user.
- The agent appends to logs and never summarizes approval on the user's
  behalf. Once edited, user configuration is authoritative: the agent changes
  user-owned harness files only when asked (a needs-revision reply with cited
  issues counts as asking), scoped to the cited issues.
- Re-setup is explicit only: `--plan` drafts; `--plan --reseed` fills missing
  halves only and never overwrites a user-edited half.

### Handoffs (enumerated edits, each covered by eval)

- `conductor-new-track`: offer a verify track after plan approval, ordered
  before the implement Yes/No (see stop-vs-delegate resolution).
- `conductor-implement`: run `harness.sh --all` from the track `verify/`
  dir, paste results. `VERIFY_APPROVED` → proceed; anything else without
  approval, or no `verify/` dir at all → warn and require explicit user
  say-so (logged; an in-chat "go ahead" without a log entry is a bypass);
  `VERIFY_FAILED` → refuse without fresh user direction. Gate state via
  `conductor-verify --track <id> --status`; implement never parses state
  files directly.
- `conductor-orchestrate`: verify runs as a delegated phase; orchestrator
  never runs the harness itself.
- `conductor-review`: audit harness evidence against the contract.

### Orchestrated tracks: who stops, who speaks

Orchestrate subagents stay pause-free; trial execution is delegated to a
fourth, pause-free `verify-runner` role (boots the environment, runs
`harness.sh --all` — never `--holdout` — reports evidence, never judges).
All verify stops happen at the orchestrator level: interview + traceability
ride the post-planning pause; demo + approval ride a verify-gate pause
(`skills/conductor-orchestrate/SKILL.md` §6; a §4B user-confirmation step
covers verify tracks). Subagent verdict-like strings are advisory input the
user must re-issue or confirm at the pause before they count.

## Files

- `skills/conductor-verify/SKILL.md` (frontmatter `name: conductor-verify`,
  full operational protocol above; version `1.3.0` era conventions)
- `commands/conductor-verify.md` (slash command wrapper)
- `plugin.json`: append skill + command entries
- Per track: `conductor/tracks/<id>/verify/{contract.json,harness.sh,
  traceability.md,approvals.log,seed.json,mounts,images/**,
  metrics.json,holdout/,baseline.log,evidence/}` (shapes defined in
  SPEC-verify-harness)
- Enumerated cross-file edits (all else untouched): `conductor-new-track`
  completion step gains the verify-track offer prompt (ordered before the
  implement Yes/No); `conductor-implement` gains the status-matrix refusal
  branch; `conductor-orchestrate` gains the §6 verify-gate pause, the §4B
  user-confirmation step, the `verify-runner` dispatch role plus
  `skills/conductor-orchestrate/subagents/verify-runner.md` and
  `rules/conductor_orchestrate_{pi,copilot,agy}.md` mapping entries;
  `conductor-review` gains evidence-audit responsibility. Each covered by eval.

## Commands

```bash
conductor-verify --track <id> --plan      # draft harness + traceability, stop at review
conductor-verify --track <id> --plan --reseed  # fill missing halves only
conductor-verify --track <id> --trial     # run baseline / mutation demo, stop at verdict
conductor-verify --track <id> --run       # re-run post-implement, attach evidence
conductor-verify --track <id> --maintain  # scoped re-trial on changed areas
conductor-verify --track <id> --status    # machine-readable gate read (skill-protocol op, no new binary)
```

`--status` prints exactly:

```text
VERIFY_STATUS <state> seed=<true|false> red=<seen|absent> override=<none|proceed>
```

Track creation writes `verify_status=VERIFY_DRAFT`, `seed_confirmed=false`;
older tracks migrate as `VERIFY_DRAFT` with recomputed `seed_confirmed`.

## Success criteria

- [ ] Implement cannot reach green status without `VERIFY_APPROVED` or an
  explicit logged user proceed (asserted by eval cases 1a/1b, SPEC-verify-evals).
- [ ] Every approved harness has an observed-red record in `approvals.log`,
  shown to the user.
- [ ] Every Acceptance item is mapped or explicitly NOT COVERED.
- [ ] Full repo gates green (`run_evals.py`, `edd.py run`, regression gate).

## Boundaries

- Always: stop at the three touchpoints; quote the user verbatim; log every
  proceed-without-approval with its reason.
- Ask first: running the re-trial after a harness edit; escalating tier (with
  SPEC-verify-strategy).
- Never: self-approve; rewrite user-owned files unprompted; mark user-tested
  without a user message; proceed past `VERIFY_FAILED` silently.

## Open questions

- Canonical home for cross-track shared harnesses (per-track only in v1?).
- Who owns post-implement re-run: implementer reports vs orchestrator delegates?
