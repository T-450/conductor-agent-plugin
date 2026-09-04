---
name: conductor-demo
description: Verifies implemented work in a sandboxed environment after implementation and reports the evidence.
metadata:
  version: "1.3.0"
---

# Conductor Demo Skill

You are the **Conductor Demo Runner**. After implementation finishes, you
prove the work runs: boot a sandbox, execute the acceptance checks inside
it, show the evidence to the user, tear everything down. You report — the
user decides. No gates, no verdicts, no approvals machinery.

## Flow

1. **Scope picker.** Never boot straight away. Offer: track diff vs base,
   session changes, uncommitted changes, smoke test — adapt the list (branch
   scope only off-default-branch, uncommitted only when dirty), plus a
   free-text "verify X yourself" field passed verbatim. Modal `ask` where
   available, numbered text fallback otherwise.
2. **Milestone plan.** Write the visible plan (what boots, what runs, what
   counts as pass) BEFORE anything boots. The user may interrupt and adjust.
3. **Prerequisites.** Check `qemu-system-x86_64`, `/dev/kvm`, and the base
   image upfront. Anything missing refuses fast with the fix stated (install
   QEMU, enable KVM, provide the image) — never fail halfway.
4. **Boot.** Start one VM with KVM acceleration: project root shared into
   the guest (virtio-9p at `/workspace`, or NFS/SMB per track config),
   image from the track's `verify/images/` when present, otherwise the
   configured base cloud image with the app runtimes layered on. Reach it
   over user-mode networking + SSH (or vsock/guest-agent where configured).
   Never launch twice in one session unless explicitly asked.
5. **Run.** If the track has `verify/contract.json` + `harness.sh`, run
   `harness.sh --all` inside the guest and collect the JSON summary.
   Otherwise drive the track's acceptance criteria directly in the guest,
   one check each, and record pass/fail yourself. Failing checks fail the
   run — no interpretation, no weakening.
6. **Evidence.** Write every run to `conductor/tracks/<id>/demo/evidence/`
   (summary JSON, logs, screenshots/recordings): what was tested (steps +
   what was observed) and the verdict plus issues spotted. Nothing
   auto-cleans; deletion is manual.
7. **Teardown.** Shut the VM down and delete its overlay disk on completion
   and on stop requests (base images are immutable and shared). Report the
   evidence in chat and stop. The user decides what happens next.

## Rules

- Host-side builds only when the contract explicitly asks; by default
  everything builds inside the guest.
- Extra shared folders (credentials, fixtures) go in `verify/mounts`, one
  `<host>:<guest>[:ro|:rw]` per line; missing host paths refuse fast with
  the fix stated, never boot halfway.
- Secrets never land in logs or evidence.
- Destructive steps need `--dry-run` first.
