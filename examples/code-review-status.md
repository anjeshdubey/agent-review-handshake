---
protocol_version: 2
status: awaiting-revision
review_round: 2
max_review_rounds: 3
scope_version: 1
scope_status: approved
scope_approved_by: human-product-owner
scope_approved_at: 2026-08-10T16:00:00Z
scope_resume_status: null
review_kind: code
target_kind: branch
implementer: claude
reviewer: codex
target_repo: /work/example-service
target_remote: origin
target_file: null
branch: feature/idempotent-jobs
base_branch: main
pr_number: null
review_commit: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
last_reviewed_commit: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
last_reviewed_scope_version: 1
poll_minutes: 7
handshake_remote: origin
handshake_branch: main
---

# Idempotent Job Execution Review

## Scope Contract — Version 1

### Intended outcome and users

Make ingest, transform, and publish safe to retry for the internal job-processing team.

### Scale and rollout ceiling

One production worker pool at current traffic. Multi-region active-active execution is deferred.

### In scope

- Idempotent execution for ingest, transform, and publish.
- Duplicate delivery, concurrent workers, and crash-before-acknowledgment behavior.

### Explicitly out of scope or deferred

- Multi-region coordination.
- General workflow orchestration.
- A new organization-wide deduplication service.

### Quality and risk bar

- Delivery stage: controlled production rollout.
- Must-not-fail behaviors: duplicate external publish and lost completed work.
- Risks explicitly accepted for this stage: manual recovery from prolonged provider outage.

### Acceptance evidence

- Unit coverage for all three stages.
- Multi-connection integration proof for concurrent publish claims.

### Review budget

- Maximum independent review rounds: 3.

### Human approval

- Decision: approved.
- Approved by: human-product-owner.
- Approved at: 2026-08-10T16:00:00Z.

## Purpose

Review one PR-sized change that makes all job stages retryable without double application.

## Normative sources

- `docs/job-processing-contract.md`

## Implementer Handoff — Initial

Added stage-level idempotency keys and conflict handling for ingest, transform, and publish.

### Verification

- Unit tests cover the three stages and duplicate delivery.
- Integration tests cover concurrent workers and a crash before acknowledgment.

### Rationale and limitations

Stage-level keys reuse the existing job identifier and avoid a second deduplication service. External publish atomicity is the only known unresolved boundary in this handoff.

## Independent Review — Round 1

### Findings

- [P1] Publish side effect is not guarded atomically — `src/jobs/publish.py:84`
  Two workers can both send the external notification before either records the idempotency key. Move the claim into the same atomic boundary or introduce an outbox with a unique claim.

### Final verdict

Revision requested because the publish stage can still apply its external side effect twice.
