# Quiet reviewer monitor prompt

Replace bracketed values before creating a recurring automation.

```text
Watch [absolute handshake status-file path] every [poll_minutes] minutes.

Routine-silence rule: when no eligible handoff is ready, emit no visible commentary or status sentence. Use the host's quiet/no-notification outcome. Notify only when real review work starts, a blocking error prevents review, a review is committed and pushed, approval is reached, or the loop is explicitly stopped.

Use $run-review-handshake. Process at most one review pass per run. Act only when the frontmatter status is exactly awaiting-review, the status file is clean, the handshake repository matches [handshake_remote]/[handshake_branch], review_commit is an exact 40-character SHA available on the target remote, and it differs from last_reviewed_commit.

Review only the immutable review_commit. Never edit, stage, commit, switch branches in, or push the target repository. Append the current numbered review, increment review_round exactly once, make the status change the final content edit, commit only the status file, and push the handshake branch.
```
