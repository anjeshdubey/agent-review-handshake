#!/usr/bin/env python3
"""Validate an Agent Review Handshake protocol v1 status file."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "protocol_version",
    "status",
    "review_round",
    "review_kind",
    "target_kind",
    "implementer",
    "reviewer",
    "target_repo",
    "target_remote",
    "target_file",
    "branch",
    "base_branch",
    "pr_number",
    "review_commit",
    "last_reviewed_commit",
    "poll_minutes",
    "handshake_remote",
    "handshake_branch",
}
STATUSES = {"not-ready", "awaiting-review", "awaiting-revision", "approved", "paused"}
REVIEW_KINDS = {"design", "code"}
TARGET_KINDS = {"file", "branch", "pull-request"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def parse_scalar(raw: str) -> object:
    value = raw.strip()
    if value in {"null", "~"}:
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("file must begin with YAML frontmatter")

    try:
        closing = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("frontmatter is missing its closing delimiter") from exc

    metadata: dict[str, object] = {}
    for line_number, line in enumerate(lines[1:closing], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"frontmatter line {line_number} is not a key-value pair")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key or key in metadata:
            raise ValueError(f"frontmatter line {line_number} has an empty or duplicate key")
        metadata[key] = parse_scalar(raw_value)

    return metadata, "\n".join(lines[closing + 1 :])


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data, body = parse_frontmatter(path)
    except (OSError, ValueError) as exc:
        return [str(exc)]

    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))

    if data.get("protocol_version") != 1:
        errors.append("protocol_version must be integer 1")

    status = data.get("status")
    if status not in STATUSES:
        errors.append("status must be one of: " + ", ".join(sorted(STATUSES)))

    review_round = data.get("review_round")
    if not isinstance(review_round, int) or isinstance(review_round, bool) or review_round < 1:
        errors.append("review_round must be a positive integer")

    review_kind = data.get("review_kind")
    if review_kind not in REVIEW_KINDS:
        errors.append("review_kind must be design or code")
    if data.get("target_kind") not in TARGET_KINDS:
        errors.append("target_kind must be file, branch, or pull-request")

    for field in (
        "implementer",
        "reviewer",
        "target_remote",
        "handshake_remote",
        "handshake_branch",
    ):
        if not nonempty_string(data.get(field)):
            errors.append(f"{field} must be a non-empty scalar string")

    if data.get("implementer") == data.get("reviewer"):
        errors.append("implementer and reviewer must identify independent roles")

    target_repo = data.get("target_repo")
    if not nonempty_string(target_repo) or not Path(str(target_repo)).is_absolute():
        errors.append("target_repo must be an absolute path")

    poll_minutes = data.get("poll_minutes")
    if not isinstance(poll_minutes, int) or isinstance(poll_minutes, bool) or poll_minutes < 1:
        errors.append("poll_minutes must be a positive integer")

    review_commit = data.get("review_commit")
    last_reviewed = data.get("last_reviewed_commit")
    if review_commit is not None and (not isinstance(review_commit, str) or not SHA_RE.fullmatch(review_commit)):
        errors.append("review_commit must be null or an exact lowercase 40-character SHA")
    if last_reviewed is not None and (not isinstance(last_reviewed, str) or not SHA_RE.fullmatch(last_reviewed)):
        errors.append("last_reviewed_commit must be null or an exact lowercase 40-character SHA")

    if status in {"awaiting-review", "awaiting-revision", "approved"} and not (
        isinstance(review_commit, str) and SHA_RE.fullmatch(review_commit)
    ):
        errors.append(f"review_commit is required when status is {status}")
    if status == "awaiting-review" and review_commit == last_reviewed:
        errors.append("awaiting-review requires a review_commit different from last_reviewed_commit")
    if status in {"awaiting-revision", "approved"} and review_commit != last_reviewed:
        errors.append(f"{status} requires last_reviewed_commit to equal review_commit")

    target_kind = data.get("target_kind")
    target_file = data.get("target_file")
    branch = data.get("branch")
    base_branch = data.get("base_branch")
    pr_number = data.get("pr_number")

    for field, value in (("target_file", target_file), ("branch", branch), ("base_branch", base_branch)):
        if value is not None and not nonempty_string(value):
            errors.append(f"{field} must be null or a non-empty string")

    if review_kind == "design":
        if target_kind != "file":
            errors.append("design reviews require target_kind file")
        for field in ("branch", "base_branch", "pr_number"):
            if data.get(field) is not None:
                errors.append(f"{field} must be null for design reviews")

    if target_kind == "file":
        if not nonempty_string(target_file):
            errors.append("target_file is required for target_kind file")
        if pr_number is not None:
            errors.append("pr_number must be null for target_kind file")
    if target_kind in {"branch", "pull-request"}:
        if not nonempty_string(data.get("branch")):
            errors.append(f"branch is required for target_kind {target_kind}")
        if not nonempty_string(data.get("base_branch")):
            errors.append(f"base_branch is required for target_kind {target_kind}")
        if target_file is not None:
            errors.append(f"target_file must be null for target_kind {target_kind}")
    if target_kind == "branch" and pr_number is not None:
        errors.append("pr_number must be null for target_kind branch")
    if target_kind == "pull-request":
        if not isinstance(pr_number, int) or isinstance(pr_number, bool) or pr_number < 1:
            errors.append("pr_number must be a positive integer for target_kind pull-request")

    if not body.strip():
        errors.append("status-file body must not be empty")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("status_file", type=Path)
    args = parser.parse_args()

    errors = validate(args.status_file)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Valid handshake: {args.status_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
