---
protocol_version: 2
status: not-ready
review_round: 1
max_review_rounds: 3
scope_version: 1
scope_status: awaiting-human-approval
scope_approved_by: null
scope_approved_at: null
scope_resume_status: null
review_kind: design
target_kind: file
implementer: worker
reviewer: reviewer
target_repo: /absolute/path/to/target-repo
target_remote: origin
target_file: path/to/artifact.md
branch: null
base_branch: null
pr_number: null
review_commit: null
last_reviewed_commit: null
last_reviewed_scope_version: null
poll_minutes: 7
handshake_remote: origin
handshake_branch: main
---

# Review Handshake

## Scope Contract — Version 1

### Intended outcome and users

Describe the user-visible outcome and who will use it.

### Scale and rollout ceiling

State the approved scale, audience, environment, and delivery stage.

### In scope

- List only the deliverables required for this review unit.

### Explicitly out of scope or deferred

- List later-stage scale, compliance, hardening, architecture, and product work that must not become current blockers.

### Quality and risk bar

- Delivery stage:
- Must-not-fail behaviors:
- Risks explicitly accepted for this stage:

### Acceptance evidence

- List the demonstrations, tests, or artifacts required for acceptance.

### Review budget

- Maximum independent review rounds: 3
- If exhausted: pause for a human decision; do not extend automatically.

### Human approval

- Decision: pending
- Approved by: pending
- Approved at: pending

Do not start worker implementation or reviewer polling until the human explicitly approves this complete contract and the frontmatter records that decision.

## Normative sources

- `path/to/specification.md` — applicable only within the approved scope above.

## Implementer Handoff — Initial

Append the first worker handoff only after scope approval. Include scope mapping, rationale, evidence, known limitations, and verification results. Set `status: awaiting-review` only after the target commit and this handoff are available remotely.
