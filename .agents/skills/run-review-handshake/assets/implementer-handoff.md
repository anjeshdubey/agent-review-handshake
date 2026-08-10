# Worker handoff prompt

Replace bracketed values before sending this prompt to the worker.

```text
Use $review-loop for the worker side of this review handshake.

Handshake repository: [absolute path]
Status file: [repository-relative path]
Target repository: [absolute path]
Review unit: [target file, branch, or pull request]

Read the status file and its protocol before acting. Own only target changes, implementer handoffs, and implementation-revision sections. Before handoff, map every normative requirement and parallel path, verify breadth before depth, treat spec prose as a literal checklist, and re-audit any permission grant or relaxation as new security-sensitive code.

Commit and push the target, record the exact remote 40-character SHA as review_commit, append your evidence and verification results, and set status to awaiting-review only as the final content edit. Never increment review_round and never write a reviewer section.
```
