---
name: run-review-handshake
description: Set up, run, resume, pause, or stop the reviewer side of a Git-backed asynchronous worker-reviewer loop for design documents or code changes. Use when an independent reviewer must poll a shared status file, review an immutable target commit, append evidence-backed findings, and approve or return work without editing the target.
---

# Run Review Handshake

Use one Git-tracked status file as the durable handoff between a worker and an independent reviewer. The reviewer never edits the target artifact or implementation repository.

Read `references/handshake-schema.md` before operating a loop. Use `assets/handshake-template.md` for a new handshake and `assets/heartbeat-prompt.md` when creating a recurring poll.

## Choose the operation

- **Set up**: create a status file, validate it, commit it, and provide the worker handoff instructions.
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

Create the status file from the template with `status: not-ready` and `review_round: 1`. Validate it with `scripts/validate_handshake.py`. Commit and push only the status file. Give the worker the instructions in `assets/implementer-handoff.md` with the concrete paths substituted.

## Gate every review

Start real review work only when all gates pass:

1. The frontmatter status is exactly `awaiting-review`.
2. The current agent was explicitly assigned the reviewer role. The `reviewer` value is a role label, not authentication; stop if the assignment is ambiguous.
3. The status file is tracked and has no staged, unstaged, or untracked change at that exact path. Unrelated handshake-repository files do not block the review.
4. Fetching `handshake_remote` succeeds, and local `HEAD` exactly equals `refs/remotes/<handshake_remote>/<handshake_branch>`. Ahead, behind, or divergent states are ineligible.
5. `review_commit` is a full 40-character SHA and exists on the configured target remote.
6. `review_commit` differs from `last_reviewed_commit`.
7. Required target, base-branch, and review-kind fields are valid for the requested review.

Routine ineligibility is not an error. End silently and do not create visible progress messages.

## Review the immutable target

1. Announce that real review work is starting only after all gates pass.
2. Read all applicable repository instructions, the worker handoff, normative specifications, prior rounds, and the complete target files at `review_commit`.
3. For code, compare the merge-base diff between the configured base branch and `review_commit`. Do not switch branches or modify the target checkout.
4. Build a coverage matrix before deep analysis:
   - each normative requirement;
   - each parallel path, role, request scope, stage, and call site;
   - each trust boundary, permission grant, or policy relaxation;
   - retry, concurrency, partial-failure, and negative behavior.
5. Verify every defined path at least once before going deep on the most complex path.
6. Treat specification prose as executable review criteria. Require concrete implementation or test evidence for every normative statement.
7. Re-audit every grant or relaxation introduced since the previous round as new code. Check direct-read exposure, namespace or temporary-object shadowing where applicable, and the approved privilege matrix.
8. When one defect appears, search the entire defect class across sibling paths. Continue the full review after finding blockers so the worker receives a consolidated round.
9. Validate each potential finding against complete files at the immutable SHA. Cite exact repository-relative `file:line` locations from that commit.
10. Run safe, non-mutating verification when useful. Distinguish observed results from inference.

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
3. Increment `review_round` by exactly one.
4. Set `status: awaiting-revision` only as the final content edit.

If no actionable findings remain:

1. State plainly that no blocking findings remain and approve the review unit.
2. Set `last_reviewed_commit` to the reviewed SHA.
3. Increment `review_round` by exactly one.
4. Set `status: approved` only as the final content edit.

Before committing, validate the file, run `git diff --check`, and confirm only the intended status file changed. Commit and push only that file.

## Preserve reviewer independence

- Never edit, stage, commit, switch branches in, or push the target repository.
- Never review a dirty or mutable handoff.
- Never review the same SHA twice.
- Never accept a claim without checking the cited artifact or code.
- Preserve the complete append-only history.
- Report a pushed review or terminal approval; otherwise keep routine polling silent.
