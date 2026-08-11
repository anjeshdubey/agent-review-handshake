# Agent Review Handshake

Cross-provider, Git-backed worker-reviewer loops for AI agents.

There are two compatible skills:

- `review-loop`: the worker prepares an immutable handoff, responds to findings, and owns target changes.
- `run-review-handshake`: the independent reviewer gates, reviews, records findings, and approves without modifying the target.

The roles are provider-neutral. I first used Claude as the worker and Codex as the reviewer, but either role can run on another capable agent. Models from different providers can bring different blind spots. The protocol, not the vendor, keeps the collaboration safe.

## Why Git is the message bus

Chat sessions do not share context reliably across providers. A Git-tracked Markdown status file gives both roles:

- an explicit state machine;
- an immutable commit to review;
- append-only review history;
- a human-approved scope ceiling;
- clear ownership boundaries;
- resumability across sessions;
- quiet polling when no work is ready.

```text
human approves scope
        |
        v
worker publishes SHA
        |
        v
 awaiting-review ---> reviewer appends one complete round
        ^                         |
        |                         v
worker revises <--------- awaiting-revision
        |
        +-----------------------> approved
```

## Review behavior designed to reduce rounds

Both skills start with a human scope decision. Before either agent begins, the status file records the intended users, rollout ceiling, in-scope work, deferred work, quality bar, acceptance evidence, and maximum review rounds. The agents cannot treat a later production concern as an alpha blocker unless the human changes that contract.

Within that boundary, both skills use three practices that help catch more issues in the first pass:

1. **Breadth before depth.** Map every parallel path, role, request scope, stage, and call site before focusing on the most complex path.
2. **Re-audit grants and relaxations.** Treat permissions or loosened restrictions introduced by a fix as new security-sensitive code.
3. **Use normative prose as a checklist.** Require implementation or test evidence for every stated invariant, including retry, concurrency, and failure behavior.

They also require defect-class audits, immutable SHAs, exact citations, complete review rounds, and a final status edit only after verification. If either agent proposes or detects work outside scope, the loop pauses and asks the human. The worker and reviewer cannot approve the expansion for each other.

## Repository layout

```text
.agents/skills/review-loop/           # worker skill
.agents/skills/run-review-handshake/  # reviewer and orchestration skill
examples/                             # valid design and code handshakes
scripts/validate_release.py           # dependency-free package checks
```

## Install

Clone the repository once:

```bash
git clone https://github.com/anjeshdubey/agent-review-handshake.git
```

Then copy or symlink each role into the skill directory used by that agent. One common Claude-worker/Codex-reviewer setup is:

```bash
mkdir -p ~/.claude/skills ~/.codex/skills
ln -s /absolute/path/agent-review-handshake/.agents/skills/review-loop ~/.claude/skills/review-loop
ln -s /absolute/path/agent-review-handshake/.agents/skills/run-review-handshake ~/.codex/skills/run-review-handshake
```

For project-scoped installation, copy the desired skill directories into the project's `.agents/skills/` directory when supported by the host. Install both skills in both hosts if you want to swap roles.

## Start a loop

Ask the reviewer/orchestrator:

```text
Use $run-review-handshake to set up a design review.
Handshake repository: /path/to/coordination-repo
Target repository: /path/to/product-repo
Target file: docs/feature-spec.md
Worker: claude
Reviewer: codex
Poll every 7 minutes and keep routine polls silent.
Scope: friends-and-family alpha for 10 users.
In scope: one end-to-end happy path and its must-not-fail correctness cases.
Deferred: enterprise scale, regulated compliance, and unrelated platform scaffolding.
Maximum review rounds: 3.
```

The reviewer drafts the scope contract and stops for your explicit approval. It does not start the worker or polling yet. After approval, the worker uses `$review-loop` to publish the target SHA and set `status: awaiting-review`.

For code, provide the review branch and base branch. Keep each status file scoped to one independently reviewable unit or PR-sized change.

## Protocol states

| State | Owner of the next action |
| --- | --- |
| `not-ready` | Human while scope is pending, then worker |
| `awaiting-review` | Reviewer |
| `awaiting-revision` | Worker |
| `approved` | Terminal |
| `paused` | Nobody until resumed |

`review_round` always names the next reviewer pass. It starts at `1`; only the reviewer increments it, exactly once after appending that round. See either skill's `references/handshake-schema.md` for the complete protocol.

Scope has its own gate:

| Scope state | Meaning |
| --- | --- |
| `awaiting-human-approval` | No worker implementation or reviewer polling may start |
| `approved` | Both roles must stay inside the signed scope contract |
| `change-requested` | The loop is paused until the human approves or rejects the change |

When a scope change is approved, the file appends a new numbered scope version and returns the target to `not-ready`. When it is rejected, the existing version remains authoritative.

## Validate

Run the dependency-free release checks:

```bash
python3 scripts/validate_release.py
```

Validate an individual status file:

```bash
python3 .agents/skills/run-review-handshake/scripts/validate_handshake.py path/to/status.md
```

## Safety boundaries

- The reviewer never edits the target repository.
- Neither agent starts until a human approves the scope contract.
- Neither agent may expand scope or the review budget without another human decision.
- Reviews use a full 40-character commit SHA available on the target remote.
- Each role commits only the intended status file in the handshake repository.
- Previous handoffs and review rounds are never overwritten.
- Routine polls produce no visible message when no work is eligible.
- Secrets and credentials never belong in the status file.

## Project status

This is an early public release. Protocol version `2` adds the required human scope gate. Existing version-1 handshakes must be migrated and explicitly approved before automated work resumes. Test the skills in your own repository workflow before relying on unattended operation.

This community project is independent and is not affiliated with, endorsed by, or maintained by Anthropic or OpenAI.

## License

MIT. See [LICENSE](LICENSE).
