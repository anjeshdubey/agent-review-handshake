---
name: review-loop
description: Run the worker side of a Git-backed, asynchronous worker-reviewer loop for design documents or code changes. Use when a human-approved scope ceiling governs target work, and the worker must prepare immutable handoffs, respond to in-scope findings, or escalate scope drift through a shared status file.
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
- a protocol-v2 scope contract with explicit human approval
- maximum review rounds

Ask only for inputs that cannot be discovered safely. Do not infer a target that could redirect the review.

## Require scope approval before target work

Do not create or revise the target while `scope_status` is `awaiting-human-approval` or `change-requested`, or when the protocol is still version 1.

1. Read the complete latest scope contract and its human approval record.
2. Require `protocol_version: 2`, `scope_status: approved`, non-empty `scope_approved_by` and `scope_approved_at`, and a current `review_round` within `max_review_rounds`.
3. Treat the contract as a ceiling. Implement the approved outcome and acceptance evidence, not adjacent enterprise, scale, compliance, or hardening work that is explicitly deferred.
4. Never infer a broader mandate from a master specification, roadmap, reviewer suggestion, or technically attractive architecture.

## Prepare the first handoff

1. Read all applicable repository instructions and normative specifications.
2. Sync the target repository without overwriting unrelated work.
3. Create or revise the target artifact on its own branch when the repository workflow requires one.
4. Build a pre-review evidence map bounded by the approved scope:
   - every in-scope normative requirement and where it is implemented;
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
2. Validate each finding against the exact reviewed commit, the human-approved scope contract, and the applicable normative source. Do not implement a finding blindly if its premise is false or outside scope; document concrete evidence when challenging it.
3. Fix every valid finding in the target repository.
4. Re-audit the entire defect class across sibling paths, roles, scopes, stages, and call sites. A local fix is incomplete when the same invariant can fail elsewhere.
5. Treat any grant or relaxation introduced by the fix as new security-sensitive code. Check direct-read exposure, namespace or temporary-object shadowing where applicable, and the approved privilege matrix.
6. Re-run the literal requirement checklist and relevant negative, retry, concurrency, and failure tests.
7. Commit and push the revised target work. Capture the new immutable SHA.
8. Append `## Implementer Revision — After Review Round N`, where `N` is the review round just addressed. Include a finding-by-finding response plus the broader audit and verification evidence.
9. Replace `review_commit` with the new SHA. Preserve `last_reviewed_commit` and `last_reviewed_scope_version`.
10. Commit and push only the intended status file. Set `status: awaiting-review` only as the final content edit.

Never increment `review_round`; the reviewer appends that numbered review and increments it exactly once.

## Escalate scope drift to the human

Neither role may expand the scope contract on behalf of the human.

- If the reviewer requests work outside the approved scope, do not implement it. Append `## Scope Escalation — <timestamp>` identifying the suggestion, the conflicting scope clause, impact, options, and the state that should resume after a decision. Set `scope_status: change-requested`, set `scope_resume_status`, and set `status: paused` as the final edit. Notify the human and state in the handshake that the other role was informed through the shared file.
- If the worker discovers or wants an out-of-scope change, use the same escalation before making that change.
- If out-of-scope work was already added, disclose it immediately and pause. Do not use sunk cost as implied approval.
- Only act on a scope decision after explicit human instruction. If rejected, preserve the current scope version and follow the human-selected resume state. If approved, append a new scope-contract version, increment `scope_version`, refresh the approval fields, and return to `not-ready` before reconciling the target.
- When `review_round` would exceed `max_review_rounds`, pause for a human choice to extend the budget, narrow the unit, accept a documented risk, or replan. Do not continue automatically.

## Preserve role boundaries

- Modify the target only as the worker. Never write the reviewer's review section.
- Preserve every previous handoff, review, and revision section as an append-only audit trail.
- Keep one handshake file per independently reviewable unit.
- Never put secrets, tokens, or private credentials in the status file.
- Never use a branch name, short SHA, or mutable ref as `review_commit`. Review identity is the immutable SHA plus the approved scope version.
- Never mark the artifact approved. Only the reviewer may set `status: approved`.
- Never implement an out-of-scope reviewer suggestion without human approval.
- Never add unrelated scaffolding merely because it would be needed at a later delivery stage.
- If work must stop, set `status: paused` with a concrete reason and required resumption condition.

## Keep waiting quiet

When the reviewer has not handed work back, do not emit routine visible updates. Prefer the host's native scheduling or loop capability over a shell polling process. Notify only when work is ready, an error prevents progress, or the loop reaches a terminal state.
