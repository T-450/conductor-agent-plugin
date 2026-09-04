# SPEC-verify-strategy

## Objective

Choose the cheapest verification tier that can actually observe each
acceptance item, with the user ratifying the choice. Success = no track pays
for T3 ceremony on lint-gated work, and no firmware ships on T1 hand-waving;
every tier choice is recorded with a reason.

## Scope

In: tier catalog T0–T4, per-item complexity profiler, selection interview,
escalation triggers, unfaithful-list convention.
Out: gate mechanics (lifecycle), harness file formats (harness module).

## Tier catalog (`skills/conductor-verify/assets/strategies.md`)

| Tier | Shape | Proves | Costs | Needs from user |
|---|---|---|---|---|
| T0 | Lint, typecheck, schema/trace checks | Shape conformance | Seconds, $0 | Ratify repo-standard gate list (agent drafts via convention discovery) |
| T1 | In-process hermetic (SQLite, HTTP stubs, fake clock, seeded RNG) | Logic minus real-I/O semantics | Seconds, $0, deterministic | Known-unfaithful adjudication |
| T2 | Local real services (Compose DB/queue, Playwright vs local server, seeded tenants) | Full-stack local behavior | Minutes per run, capable machine | Seeds, auth strategy, stub-vs-real line |
| T3 | Emulated/virtualized HW (QEMU, Renode-class MCU, device simulators) | Driver logic vs a model | GB images, minutes boot, approximate timing | Fidelity contract: modeled vs idealized per behavior |
| T4 | Remote real substrate (device farms, cloud GPUs, staging, HIL rigs) | Real behavior | Real money, minutes–hours, flaky | Access, budget caps, quarantine policy |

Every track gets T0 free. Default posture: cheapest tier that observes the
item; escalate on evidence. Multiple templates may coexist per track
(`verify/images/<role>/`, e.g. backend/frontend/cli — mirroring Junie's
multi-VM layout); all discovered templates are listed to the agent on every
run so it picks per the contract, with `default` as the single-template
shortcut. Per-track copies are canonical; the project-level library
`conductor/verify-images/<name>/` is a seeding source only and never
overrides track files.

## Complexity profiler (per acceptance item, stored in contract.json)

Score each axis 0–2 with these anchors (pure function specified as
`skills/conductor-verify/assets/profile.py`; see SPEC-verify-evals case 5):

- statefulness: 0 = pure function of inputs; 1 = local persisted state
  (files, sqlite); 2 = shared/external mutable state (DB, queue, actors).
- external deps (non-hardware services/APIs only, to avoid double-counting
  hardware; EXCLUDING the primary data store, which statefulness already
  scores): 0 = none; 1 = one; 2 = two or more. Example: a shared Postgres
  behind one API scores statefulness 2, deps 1 (the API), not deps 2.
- hardware coupling: 0 = none; 1 = timing/peripheral-sensitive but
  emulatable; 2 = observable only on physical substrate.
- blast radius of a miss: 0 = dev-only; 1 = user-visible degradation;
  2 = data loss, safety, or money.

Tier decision (precedence order, first match wins):

1. Hardware coupling = 2 → T4 (physical-only short-circuits the sum).
2. Else sum: 0 → T0; 1–2 → T1; 3–5 → T2; 6+ → T3.

The profiler proposes; the user ratifies or overrides in the selection
interview (modal ask, Recommended-first). Overrides are recorded with reason.
Mixed-tier tracks are the expected outcome, not an edge. Thresholds are
provisional v1 (`profiler_version` in the catalog), calibrated against 3
pilot tracks before hardening.

## Selection interview and escalation

- Agent presents 2–3 tier options with fidelity/cost tradeoffs; user picks.
  Recorded as `tier: <T> because <reason>` per item.
- Escalation triggers (scoped re-trial, contract carries over, revision-round
  count NOT reset): T1-green but behavior known backend-specific → T2;
  emulator idealizes load-bearing timing → T3 spot-checks; release gate →
  T4 smoke ONLY with a cap pre-authorized at selection, otherwise warn and
  stop. Escalation never resets the lifecycle revision count (no infinite
  loop via re-tiering).
- Every tier with runtime execution (T1–T4) carries a non-empty `unfaithful`
  list (known divergences), user-confirmed; T0 is exempt (no runtime).
  Catalog carries order-of-magnitude $/run bands per backend, refreshed each
  release; no T4 spend without a stated envelope the user ratified.

## Success criteria

- [ ] Catalog covers T0–T4 with criteria, $/run envelopes, and templates.
- [ ] Profiler output matches the 4 gold-standard fixtures (CRUD → T1,
  PG-locking → T2, MCU-timing → T3, release-gate → T4), co-authored by user
  and agent at the pilot track's selection interview (see SPEC-verify-evals).
- [ ] Every shipped contract records `tier` + `reason` + `profile` scores per
  item; unfaithful lists non-empty for T1–T4.

## Boundaries

- Always: cheapest-viable default; user ratification recorded.
- Ask first: any escalation; any T4 spend (pre-authorized cap or fresh approval).
- Never: T3+ ceremony for T0-grade items; silent tier downgrades; escalation
  as revision-count reset.

## Open questions

- None open: calibration runs on 3 pilot tracks against provisional
  thresholds; cost envelopes refreshed per release. Both are scheduled work,
  not undecided design.
