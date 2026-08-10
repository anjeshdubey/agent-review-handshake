# Worker handoff prompt

Replace bracketed values before sending this prompt to the worker.

```text
Use $review-loop for the worker side of this review handshake.

Handshake repository: [absolute path]
Status file: [repository-relative path]
Target repository: [absolute path]
Review unit: [target file, branch, or pull request]

Read the status file and its protocol before acting. Own only target changes, implementer handoffs, and implementation-revision sections. Before handoff, map every normative requirement and parallel path, verify breadth before depth, treat spec prose as a literal checklist, and re-audit any permission grant or relaxation as new security-sensitive code.

Do not touch the target until protocol_version is 2, scope_status is approved, explicit human approval is recorded, and review_round is within max_review_rounds. Treat the approved scope contract as a ceiling. Apply the checklist only to requirements incorporated by that scope; do not add deferred enterprise, scale, compliance, or hardening work.

If you want an out-of-scope change, the reviewer requests one, or you discover material scope drift, do not implement it. Append a scope escalation, set scope_status to change-requested, record scope_resume_status, set status to paused as the final edit, and bring the human into the loop. Only the human may approve a new scope version.

Commit and push the in-scope target, record the exact remote 40-character SHA as review_commit, append your evidence and verification results, and set status to awaiting-review only as the final content edit. Never increment review_round and never write a reviewer section.
```
