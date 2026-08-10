# Quiet reviewer monitor prompt

Replace bracketed values before creating a recurring automation.

```text
Watch [absolute handshake status-file path] every [poll_minutes] minutes.

Routine-silence rule: when no eligible handoff is ready, emit no visible commentary or status sentence. Use the host's quiet/no-notification outcome. Notify only when real review work starts, a blocking error prevents review, a review is committed and pushed, approval is reached, or the loop is explicitly stopped.

Use $run-review-handshake. Process at most one review pass per run. Act only when the frontmatter status is exactly awaiting-review, the status file is clean, the handshake repository matches [handshake_remote]/[handshake_branch], review_commit is an exact 40-character SHA available on the target remote, and the pair (review_commit, scope_version) differs from (last_reviewed_commit, last_reviewed_scope_version).

Require protocol_version 2, scope_status approved, explicit human approval fields, and review_round no greater than max_review_rounds. Read the approved scope contract before normative sources. Review only the immutable review_commit and only against the approved outcome, scale ceiling, in-scope requirements, quality bar, and acceptance evidence.

Never expand scope through a finding. If the reviewer believes an out-of-scope change is required, or detects material worker scope drift, append a scope escalation, set scope_status to change-requested, record scope_resume_status, pause the loop, and notify the human. Do not resolve scope on either agent's authority.

Never edit, stage, commit, switch branches in, or push the target repository. Append the current numbered review, record both last_reviewed_commit and last_reviewed_scope_version, increment review_round exactly once, make the status change the final content edit, commit only the status file, and push the handshake branch. If the review budget is exhausted with findings remaining, pause for a human decision instead of extending the loop.
```
