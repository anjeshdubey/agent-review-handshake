---
protocol_version: 1
status: awaiting-revision
review_round: 2
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
poll_minutes: 7
handshake_remote: origin
handshake_branch: main
---

# Idempotent Job Execution Review

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
