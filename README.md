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
- clear ownership boundaries;
- resumability across sessions;
- quiet polling when no work is ready.

```text
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

Both skills use three practices that helped catch more issues in the first pass:

1. **Breadth before depth.** Map every parallel path, role, request scope, stage, and call site before focusing on the most complex path.
2. **Re-audit grants and relaxations.** Treat permissions or loosened restrictions introduced by a fix as new security-sensitive code.
3. **Use normative prose as a checklist.** Require implementation or test evidence for every stated invariant, including retry, concurrency, and failure behavior.

They also require defect-class audits, immutable SHAs, exact citations, complete review rounds, and a final status edit only after verification.

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
```

The reviewer creates a status file and gives the worker a concrete prompt. The worker then uses `$review-loop` to publish the target SHA and set `status: awaiting-review`.

For code, provide the review branch and base branch. Keep each status file scoped to one independently reviewable unit or PR-sized change.

## Protocol states

| State | Owner of the next action |
| --- | --- |
| `not-ready` | Worker |
| `awaiting-review` | Reviewer |
| `awaiting-revision` | Worker |
| `approved` | Terminal |
| `paused` | Nobody until resumed |

`review_round` always names the next reviewer pass. It starts at `1`; only the reviewer increments it, exactly once after appending that round. See either skill's `references/handshake-schema.md` for the complete protocol.

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
- Reviews use a full 40-character commit SHA available on the target remote.
- Each role commits only the intended status file in the handshake repository.
- Previous handoffs and review rounds are never overwritten.
- Routine polls produce no visible message when no work is eligible.
- Secrets and credentials never belong in the status file.

## Project status

This is an early public release. Protocol version `1` is the current compatibility boundary. Test the skills in your own repository workflow before relying on unattended operation.

This community project is independent and is not affiliated with, endorsed by, or maintained by Anthropic or OpenAI.

## License

MIT. See [LICENSE](LICENSE).
