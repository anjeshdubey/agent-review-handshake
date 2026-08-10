---
name: review-loop
description: Run the worker side of a Git-backed, asynchronous worker-reviewer loop for design documents or code changes. Use when preparing a review handoff, responding to findings, resuming a paused loop, or coordinating with an independent reviewer through a shared status file.
---

# Review Loop Worker

Use Git and one status file as the durable message bus between a worker and an independent reviewer. The worker owns the target artifact and implementation-revision entries. The reviewer owns review entries and `review_round`.

Read `references/handshake-schema.md` before creating or changing a handshake. Use `assets/handshake-template.md` when a new status file is needed and `scripts/validate_handshake.py` before every status-file commit.

## Gather the minimum inputs

Confirm these values before starting:

- handshake repository and status-file path
- target repository and artifact, branch, or pull request
- review kind: `design` or `code`
- worker and reviewer identifiers
- base branch for code review

Ask only for inputs that cannot be discovered safely. Do not infer a target that could redirect the review.

## Prepare the first handoff

1. Read all applicable repository instructions and normative specifications.
2. Sync the target repository without overwriting unrelated work.
3. Create or revise the target artifact on its own branch when the repository workflow requires one.
4. Build a pre-review evidence map:
   - every normative requirement and where it is implemented;
   - every parallel path, role, scope, stage, and call site the requirement covers;
   - relevant negative, retry, concurrency, and failure behavior;
   - every permission grant, policy relaxation, or trust-boundary change.
5. Verify breadth before spending disproportionate effort on one complex path. Exercise every defined path at least once.
6. Treat specification prose as a literal checklist. Record evidence for each requirement instead of relying on intent or a passing happy-path test.
7. Run proportionate tests and static checks. For code, inspect the complete changed files and their callers, not only the diff.
8. Commit and push the target work. Resolve `review_commit` to the exact 40-character commit SHA available on the target remote.
9. Append an `## Implementer Handoff — Initial` section to the status file with scope, rationale, evidence, known limitations, and the exact verification commands and results.
10. Update the handshake metadata, commit the status file, and push it. Set `status: awaiting-review` only as the final content edit.

The handoff is not ready until the target commit and status-file commit are both available remotely.

## Respond to a review

Act only when the current agent was explicitly assigned the worker role, `status: awaiting-revision`, and the status file passes the protocol's tracked-file and synchronization gates. The `implementer` value is a role label, not authentication; stop if the role assignment is ambiguous.

1. Read the complete latest review round and all earlier unresolved findings.
2. Validate each finding against the exact reviewed commit and the normative source. Do not implement a finding blindly if its premise is false; document concrete evidence when challenging it.
3. Fix every valid finding in the target repository.
4. Re-audit the entire defect class across sibling paths, roles, scopes, stages, and call sites. A local fix is incomplete when the same invariant can fail elsewhere.
5. Treat any grant or relaxation introduced by the fix as new security-sensitive code. Check direct-read exposure, namespace or temporary-object shadowing where applicable, and the approved privilege matrix.
6. Re-run the literal requirement checklist and relevant negative, retry, concurrency, and failure tests.
7. Commit and push the revised target work. Capture the new immutable SHA.
8. Append `## Implementer Revision — After Review Round N`, where `N` is the review round just addressed. Include a finding-by-finding response plus the broader audit and verification evidence.
9. Replace `review_commit` with the new SHA. Preserve `last_reviewed_commit`.
10. Commit and push only the intended status file. Set `status: awaiting-review` only as the final content edit.

Never increment `review_round`; the reviewer appends that numbered review and increments it exactly once.

## Preserve role boundaries

- Modify the target only as the worker. Never write the reviewer's review section.
- Preserve every previous handoff, review, and revision section as an append-only audit trail.
- Keep one handshake file per independently reviewable unit.
- Never put secrets, tokens, or private credentials in the status file.
- Never use a branch name, short SHA, or mutable ref as `review_commit`.
- Never mark the artifact approved. Only the reviewer may set `status: approved`.
- If work must stop, set `status: paused` with a concrete reason and required resumption condition.

## Keep waiting quiet

When the reviewer has not handed work back, do not emit routine visible updates. Prefer the host's native scheduling or loop capability over a shell polling process. Notify only when work is ready, an error prevents progress, or the loop reaches a terminal state.
