# Handshake protocol v1

The status file is an append-only Markdown document with YAML frontmatter. Git provides synchronization and audit history; the frontmatter provides the state machine.

## Required fields

| Field | Meaning |
| --- | --- |
| `protocol_version` | Integer `1`. Reject unknown versions. |
| `status` | One of the protocol states below. |
| `review_round` | Positive integer naming the next reviewer pass. Initial value is `1`. |
| `review_kind` | `design` or `code`. |
| `target_kind` | `file`, `branch`, or `pull-request`. |
| `implementer` | Stable scalar identifier for the worker. |
| `reviewer` | Stable scalar identifier for the independent reviewer. |
| `target_repo` | Absolute local path to the target Git repository. |
| `target_remote` | Remote containing immutable review commits, normally `origin`. |
| `target_file` | Repository-relative artifact path for file reviews; otherwise `null`. |
| `branch` | Review branch for code work; otherwise `null`. |
| `base_branch` | Merge-base comparison branch for code work; otherwise `null`. |
| `pr_number` | Integer pull-request number when applicable; otherwise `null`. |
| `review_commit` | Exact 40-character target commit SHA ready for review; otherwise `null`. |
| `last_reviewed_commit` | Exact SHA most recently reviewed; initially `null`. |
| `poll_minutes` | Positive polling interval. |
| `handshake_remote` | Remote for the status-file repository. |
| `handshake_branch` | Branch used to exchange status-file commits. |

## States

```text
not-ready -> awaiting-review -> awaiting-revision -> awaiting-review
                               \-> approved
any nonterminal state <-> paused
```

- `not-ready`: the worker has not published a complete immutable handoff.
- `awaiting-review`: the reviewer may act after all synchronization gates pass.
- `awaiting-revision`: the worker owns the next action.
- `approved`: terminal success for this review unit.
- `paused`: no role acts until the documented resumption condition is met.

## Ownership rules

- The worker owns the target artifact, worker handoff sections, and implementation-revision sections.
- The reviewer owns reviewer-review sections, `last_reviewed_commit`, approval, and `review_round` increments.
- The worker never increments `review_round`.
- For round `N`, the reviewer appends round `N` and then increments the field to `N + 1` exactly once.
- After a revision, the worker appends `Implementer Revision — After Review Round N`, where `N` is the prior reviewer round.
- Each role changes `status` only as its final content edit, then commits and pushes only the intended status file.
- `implementer` and `reviewer` are durable role labels, not authentication. The current agent must be explicitly assigned its role before acting.

## Immutability and synchronization

- `review_commit` must be a full 40-character SHA reachable from `target_remote`.
- The status file must be tracked. Path-specific staged, unstaged, or untracked changes make it ineligible; unrelated working-tree changes do not.
- Synchronization means fetching `handshake_remote` succeeds and local `HEAD` exactly equals `refs/remotes/<handshake_remote>/<handshake_branch>`. Ahead, behind, and divergent states are ineligible.
- A reviewer must not review when the status file is dirty, the handshake repository is out of sync, or `review_commit == last_reviewed_commit`.
- A worker must not advertise `awaiting-review` until the target SHA and handshake commit are remotely available.
- Branch names, tags, pull-request heads, and short SHAs are discovery aids, never immutable review identities.

## Field relationships

- A `design` review uses `target_kind: file`; `branch`, `base_branch`, and `pr_number` are `null`.
- A `file` target requires `target_file` and requires `pr_number: null`.
- A `branch` target requires `branch` and `base_branch`; `target_file` and `pr_number` are `null`.
- A `pull-request` target requires `branch`, `base_branch`, and a positive `pr_number`; `target_file` is `null`.

## Append-only body

Preserve all prior handoffs, reviews, revisions, and verdicts. Corrections belong in a new section; do not rewrite history.
