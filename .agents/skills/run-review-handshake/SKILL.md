---
name: run-review-handshake
description: Set up, run, resume, pause, or stop the reviewer side of a Git-backed asynchronous worker-reviewer loop for design documents or code changes. Use when a human must approve a scope ceiling before agents begin, and an independent reviewer must poll a shared status file, review an immutable target commit within that scope, escalate scope drift, and approve or return work without editing the target.
---

# Run Review Handshake

Use one Git-tracked status file as the durable handoff between a worker and an independent reviewer. The reviewer never edits the target artifact or implementation repository.

Read `references/handshake-schema.md` before operating a loop. Use `assets/handshake-template.md` for a new handshake and `assets/heartbeat-prompt.md` when creating a recurring poll.

## Choose the operation

- **Set up**: draft a scope contract with the human, obtain explicit approval, create a status file, validate it, commit it, and only then provide worker instructions or start monitoring.
- **Review now**: perform one eligible review pass.
- **Monitor**: schedule quiet eligibility checks and perform at most one review per run. A `poll_minutes` value alone does not select this operation; monitoring must be explicitly requested.
- **Resume**: inspect the existing status and restore monitoring without resetting history.
- **Pause or stop**: update or delete the host automation when authorized. Do not alter target work.

## Set up a handshake

Collect or discover:

- handshake repository and status-file path
- target repository and target artifact or code branch
- base branch for code review
- review kind: `design` or `code`
- worker and reviewer identifiers
- polling interval
- intended users and outcome
- scale and rollout ceiling
- in-scope deliverables and explicitly deferred work
- quality and risk bar for this delivery stage
- acceptance evidence and maximum review rounds

Create the status file from the template with `status: not-ready`, `scope_status: awaiting-human-approval`, and `review_round: 1`. Validate it with `scripts/validate_handshake.py`. Commit and push only the status file.

## Require human scope approval

Do not give the worker a start prompt, create polling, or allow target work while scope approval is pending.

1. Draft `Scope Contract — Version 1` with the human. State the outcome and users, scale and rollout ceiling, in-scope deliverables, explicitly deferred work, quality and risk bar, acceptance evidence, and review-round limit.
2. Convert broad source documents into only the requirements applicable to this review unit. The approved scope is a ceiling, not a prompt to complete every adjacent production concern.
3. Ask the human for explicit approval of the complete scope contract. Never infer approval from silence, earlier project enthusiasm, an existing specification, or an agent's recommendation.
4. After approval, record `scope_status: approved`, `scope_approved_by`, and `scope_approved_at`, and append the human decision to the scope contract. Only then provide `assets/implementer-handoff.md` and create monitoring.
5. Treat any protocol-v1 handshake as requiring migration to protocol v2 and a fresh human scope decision before resuming automated work. Preserve its history.

## Gate every review

Start real review work only when all gates pass:

1. `protocol_version` is `2`, `scope_status` is exactly `approved`, and the recorded human approval is present.
2. The frontmatter status is exactly `awaiting-review`.
3. The current agent was explicitly assigned the reviewer role. The `reviewer` value is a role label, not authentication; stop if the assignment is ambiguous.
4. The status file is tracked and has no staged, unstaged, or untracked change at that exact path. Unrelated handshake-repository files do not block the review.
5. Fetching `handshake_remote` succeeds, and local `HEAD` exactly equals `refs/remotes/<handshake_remote>/<handshake_branch>`. Ahead, behind, or divergent states are ineligible.
6. `review_commit` is a full 40-character SHA and exists on the configured target remote.
7. The pair `(review_commit, scope_version)` differs from `(last_reviewed_commit, last_reviewed_scope_version)`.
8. Required target, base-branch, and review-kind fields are valid for the requested review.
9. `review_round` does not exceed `max_review_rounds`. If it does, pause for a human decision instead of silently extending the loop.

Routine ineligibility is not an error. End silently and do not create visible progress messages.

## Review the immutable target

1. Announce that real review work is starting only after all gates pass.
2. Read the human-approved scope contract first, then applicable repository instructions, the worker handoff, in-scope normative requirements, prior rounds, and the complete target files at `review_commit`.
3. For code, compare the merge-base diff between the configured base branch and `review_commit`. Do not switch branches or modify the target checkout.
4. Build a coverage matrix before deep analysis, bounded by the approved scope:
   - each in-scope normative requirement;
   - each parallel path, role, request scope, stage, and call site;
   - each trust boundary, permission grant, or policy relaxation;
   - retry, concurrency, partial-failure, and negative behavior.
5. Verify every defined path at least once before going deep on the most complex path.
6. Treat only the specification prose incorporated by the scope contract as executable review criteria. Do not promote deferred enterprise, scale, compliance, or hardening work into blockers for a smaller approved delivery stage.
7. Re-audit every grant or relaxation introduced since the previous round as new code. Check direct-read exposure, namespace or temporary-object shadowing where applicable, and the approved privilege matrix.
8. When one defect appears, search the entire defect class across sibling paths. Continue the full review after finding blockers so the worker receives a consolidated round.
9. Validate each potential finding against complete files at the immutable SHA. Cite exact repository-relative `file:line` locations from that commit.
10. Run safe, non-mutating verification when useful. Distinguish observed results from inference.

## Enforce the scope ceiling

Both roles protect the same human-approved boundary.

- Raise `[P1]` or `[P2]` findings only for failures against the approved outcome, in-scope requirements, quality bar, or acceptance evidence.
- Do not request an out-of-scope enhancement as a finding, even when it would be appropriate for a later production stage. Record it only as deferred context when useful.
- If the reviewer believes the scope itself must change before the current unit can be accepted, do not unilaterally expand it. Append `## Scope Escalation — <timestamp>` with the conflict, impact, options, and current immutable SHA. Set `scope_status: change-requested`, record `scope_resume_status: awaiting-review`, and set `status: paused` as the final edit. Notify the human and the worker.
- If the worker implemented material work outside the contract, use the same escalation rather than reviewing the expansion as implicitly accepted. Explain what drifted and whether it should be removed, deferred, or proposed as a new scope version.
- Only record a scope decision after explicit human instruction. A rejected change preserves the current scope version and resumes the human-selected state. An approved change appends a new scope-contract version, increments `scope_version`, refreshes the approval fields, and returns the target to `not-ready` for reconciliation.

## Write the review round

Use the current `review_round` as `N`. Append, never replace:

```markdown
## Independent Review — Round N

### Findings

- [P1] Short title — `path/to/file:line`
  Concrete failure mode, impact, and required correction.

### Final verdict

Revision requested because ...
```

Use `[P1]` for correctness, security, data-loss, or contract failures that block acceptance. Use `[P2]` for material but lower-risk defects. Do not invent findings to prolong the loop.

If actionable findings exist:

1. Append the review and explicit revision verdict.
2. Set `last_reviewed_commit` to the reviewed SHA.
3. Set `last_reviewed_scope_version` to the reviewed `scope_version`.
4. Increment `review_round` by exactly one.
5. Set `status: awaiting-revision` only as the final content edit. If this was the last allowed review round, set `status: paused` instead and request a human decision on extending, narrowing, accepting, or replanning the unit.

If no actionable findings remain:

1. State plainly that no blocking findings remain and approve the review unit.
2. Set `last_reviewed_commit` to the reviewed SHA.
3. Set `last_reviewed_scope_version` to the reviewed `scope_version`.
4. Increment `review_round` by exactly one.
5. Set `status: approved` only as the final content edit.

Before committing, validate the file, run `git diff --check`, and confirm only the intended status file changed. Commit and push only that file.

## Preserve reviewer independence

- Never edit, stage, commit, switch branches in, or push the target repository.
- Never review a dirty or mutable handoff.
- Never review the same `(review_commit, scope_version)` pair twice.
- Never accept a claim without checking the cited artifact or code.
- Never expand the human-approved scope, delivery stage, scale ceiling, or review budget by implication.
- Never treat an out-of-scope recommendation as a blocker without pausing for a human decision.
- Preserve the complete append-only history.
- Report a pushed review or terminal approval; otherwise keep routine polling silent.
