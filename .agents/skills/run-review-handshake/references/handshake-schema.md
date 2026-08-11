# Handshake protocol v2

The status file is an append-only Markdown document with YAML frontmatter. Git provides synchronization and audit history; the frontmatter provides the state machine.

## Required fields

| Field | Meaning |
| --- | --- |
| `protocol_version` | Integer `2`. Protocol-v1 loops require migration and human scope approval before resuming. |
| `status` | One of the protocol states below. |
| `review_round` | Positive integer naming the next reviewer pass. Initial value is `1`. |
| `max_review_rounds` | Positive integer approved by the human. Automation pauses rather than exceeding it. |
| `scope_version` | Positive integer naming the current append-only scope contract. Initial value is `1`. |
| `scope_status` | `awaiting-human-approval`, `approved`, or `change-requested`. |
| `scope_approved_by` | Human identifier for the explicit approval, or `null` while awaiting it. |
| `scope_approved_at` | ISO-8601 timestamp for explicit approval, or `null` while awaiting it. |
| `scope_resume_status` | Prior action state to consider after a scope escalation, otherwise `null`. |
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
| `last_reviewed_scope_version` | Scope version used for the most recent review; initially `null`. |
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

No active worker-reviewer transition is permitted unless `scope_status: approved`. New loops remain `not-ready` while awaiting the first human scope decision.

## Human scope contract

Each scope version is an append-only body section titled `## Scope Contract — Version N`. It must define:

- intended outcome and users;
- scale and rollout ceiling;
- in-scope deliverables;
- explicitly deferred or out-of-scope work;
- quality and risk bar for the delivery stage;
- acceptance evidence;
- review budget;
- explicit human approval.

The scope contract is a ceiling. Broad specifications and roadmaps are normative only where the approved contract incorporates them. Neither agent may convert later-stage enterprise, scale, compliance, or hardening concerns into current blockers by implication.

The first worker prompt and recurring reviewer monitor may be created only after explicit human approval is recorded. Silence, prior approval of a different artifact, or agent agreement is not approval.

## Ownership rules

- The worker owns the target artifact, worker handoff sections, and implementation-revision sections.
- The reviewer owns reviewer-review sections, `last_reviewed_commit`, approval, and `review_round` increments.
- The human owns scope approval, rejection, expansion, narrowing, and review-budget changes. Agents may draft or record a decision but may not make it.
- The worker never increments `review_round`.
- For round `N`, the reviewer appends round `N` and then increments the field to `N + 1` exactly once.
- After a revision, the worker appends `Implementer Revision — After Review Round N`, where `N` is the prior reviewer round.
- Each role changes `status` only as its final content edit, then commits and pushes only the intended status file.
- `implementer` and `reviewer` are durable role labels, not authentication. The current agent must be explicitly assigned its role before acting.

## Scope drift and escalation

If either role proposes or detects material work outside the approved contract:

1. Do not implement, require, or implicitly approve the expansion.
2. Append `## Scope Escalation — <timestamp>` with the proposer, conflicting contract clause, impact, options, current target SHA, and proposed resume state.
3. Set `scope_status: change-requested`, set `scope_resume_status` to `not-ready`, `awaiting-review`, or `awaiting-revision`, and set `status: paused` as the final content edit.
4. Notify the human. The shared committed file informs the other role.

After explicit human instruction:

- rejection preserves `scope_version`, restores `scope_status: approved`, clears `scope_resume_status`, and resumes the human-selected state;
- approval appends `Scope Contract — Version N+1`, increments `scope_version`, refreshes the approval fields, clears `scope_resume_status`, and returns to `not-ready` so the worker can reconcile the target.

When `review_round` would exceed `max_review_rounds`, pause and ask the human to extend the budget, narrow the unit, accept a documented risk, or replan.

## Immutability and synchronization

- `review_commit` must be a full 40-character SHA reachable from `target_remote`.
- The status file must be tracked. Path-specific staged, unstaged, or untracked changes make it ineligible; unrelated working-tree changes do not.
- Synchronization means fetching `handshake_remote` succeeds and local `HEAD` exactly equals `refs/remotes/<handshake_remote>/<handshake_branch>`. Ahead, behind, and divergent states are ineligible.
- A reviewer must not review when the status file is dirty, the handshake repository is out of sync, or both `review_commit == last_reviewed_commit` and `scope_version == last_reviewed_scope_version`.
- A worker must not advertise `awaiting-review` until the target SHA and handshake commit are remotely available.
- A worker must not change the target before scope approval or while a scope change is pending.
- A reviewer must not start when scope approval is absent, a scope change is pending, or the review budget is exhausted.
- Review identity is the pair `(review_commit, scope_version)`. This permits the same artifact commit to be reconsidered after an explicit human-approved scope change without a fake target commit.
- Branch names, tags, pull-request heads, and short SHAs are discovery aids, never immutable review identities.

## Field relationships

- A `design` review uses `target_kind: file`; `branch`, `base_branch`, and `pr_number` are `null`.
- A `file` target requires `target_file` and requires `pr_number: null`.
- A `branch` target requires `branch` and `base_branch`; `target_file` and `pr_number` are `null`.
- A `pull-request` target requires `branch`, `base_branch`, and a positive `pr_number`; `target_file` is `null`.

## Append-only body

Preserve all prior handoffs, reviews, revisions, and verdicts. Corrections belong in a new section; do not rewrite history.

Preserve all prior scope contracts and decisions. A changed scope is a new numbered version, never an edit to the approved version.
