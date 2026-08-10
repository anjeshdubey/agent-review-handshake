#!/usr/bin/env python3
"""Run deterministic checks for the public Agent Review Handshake package."""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "review-loop": ROOT / ".agents/skills/review-loop",
    "run-review-handshake": ROOT / ".agents/skills/run-review-handshake",
}
REQUIRED_PATHS = {
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / ".github/workflows/validate.yml",
    ROOT / "examples/design-review-status.md",
    ROOT / "examples/code-review-status.md",
    ROOT / "scripts/validate_release.py",
}
PRIVATE_NEEDLES = {
    "/" + "Users/" + "anjesh" + "dubey",
    "adubey" + "-ai-vault",
    "Axiom" + "8",
    "Phase_" + "5A1",
}


def skill_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path} is missing YAML frontmatter")
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line in {path}: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def main() -> int:
    errors: list[str] = []

    for path in sorted(REQUIRED_PATHS):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    for name, directory in SKILLS.items():
        required = {
            directory / "SKILL.md",
            directory / "agents/openai.yaml",
            directory / "assets/handshake-template.md",
            directory / "references/handshake-schema.md",
            directory / "scripts/validate_handshake.py",
        }
        for path in sorted(required):
            if not path.is_file():
                errors.append(f"missing skill file: {path.relative_to(ROOT)}")
        if (directory / "SKILL.md").is_file():
            try:
                metadata = skill_frontmatter(directory / "SKILL.md")
            except ValueError as exc:
                errors.append(str(exc))
            else:
                if set(metadata) != {"name", "description"}:
                    errors.append(f"{name}/SKILL.md frontmatter must contain only name and description")
                if metadata.get("name") != name:
                    errors.append(f"{name}/SKILL.md name must match its directory")
        openai_yaml = directory / "agents/openai.yaml"
        if openai_yaml.is_file() and f"${name}" not in openai_yaml.read_text(encoding="utf-8"):
            errors.append(f"{name}/agents/openai.yaml default prompt must mention ${name}")

    shared_paths = (
        "assets/handshake-template.md",
        "references/handshake-schema.md",
        "scripts/validate_handshake.py",
    )
    for relative in shared_paths:
        worker = SKILLS["review-loop"] / relative
        reviewer = SKILLS["run-review-handshake"] / relative
        if worker.is_file() and reviewer.is_file() and worker.read_bytes() != reviewer.read_bytes():
            errors.append(f"shared protocol file differs between skills: {relative}")

    text_extensions = {".md", ".py", ".yaml", ".yml"}
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in text_extensions and ".git" not in path.parts:
            text = path.read_text(encoding="utf-8")
            for needle in PRIVATE_NEEDLES:
                if needle in text:
                    errors.append(f"private project reference {needle!r} in {path.relative_to(ROOT)}")

    validator = SKILLS["run-review-handshake"] / "scripts/validate_handshake.py"
    validator_namespace: dict[str, object] = {}
    if validator.is_file():
        exec(
            compile(validator.read_text(encoding="utf-8"), str(validator), "exec"),
            validator_namespace,
        )
    for example in (ROOT / "examples/design-review-status.md", ROOT / "examples/code-review-status.md"):
        if validator.is_file() and example.is_file():
            example_errors = validator_namespace["validate"](example)
            if example_errors:
                errors.append(f"example failed validation: {example.name}: {'; '.join(example_errors)}")

    design_example = ROOT / "examples/design-review-status.md"
    if validator.is_file() and design_example.is_file():
        design_text = design_example.read_text(encoding="utf-8")
        invalid_text = design_text.replace(
            "review_commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "review_commit: null",
            1,
        )
        with tempfile.TemporaryDirectory(prefix="agent-review-handshake-") as temp_dir:
            invalid_path = Path(temp_dir) / "invalid-status.md"
            invalid_path.write_text(invalid_text, encoding="utf-8")
            if not validator_namespace["validate"](invalid_path):
                errors.append("handshake validator accepted an awaiting-review file without a commit")

        unapproved_text = design_text.replace(
            "scope_status: approved",
            "scope_status: awaiting-human-approval",
            1,
        )
        with tempfile.TemporaryDirectory(prefix="agent-review-handshake-") as temp_dir:
            invalid_path = Path(temp_dir) / "unapproved-status.md"
            invalid_path.write_text(unapproved_text, encoding="utf-8")
            if not validator_namespace["validate"](invalid_path):
                errors.append("handshake validator accepted active work without human scope approval")

        exhausted_text = design_text.replace("review_round: 1", "review_round: 4", 1)
        with tempfile.TemporaryDirectory(prefix="agent-review-handshake-") as temp_dir:
            invalid_path = Path(temp_dir) / "exhausted-status.md"
            invalid_path.write_text(exhausted_text, encoding="utf-8")
            if not validator_namespace["validate"](invalid_path):
                errors.append("handshake validator accepted an active review beyond its round ceiling")

        stale_scope_text = design_text.replace("scope_version: 1", "scope_version: 2", 1)
        with tempfile.TemporaryDirectory(prefix="agent-review-handshake-") as temp_dir:
            invalid_path = Path(temp_dir) / "stale-scope-status.md"
            invalid_path.write_text(stale_scope_text, encoding="utf-8")
            if not validator_namespace["validate"](invalid_path):
                errors.append("handshake validator accepted metadata without the matching scope contract version")

        scope_change_text = (
            design_text.replace("status: awaiting-review", "status: paused", 1)
            .replace("scope_status: approved", "scope_status: change-requested", 1)
            .replace("scope_resume_status: null", "scope_resume_status: awaiting-review", 1)
        )
        with tempfile.TemporaryDirectory(prefix="agent-review-handshake-") as temp_dir:
            valid_path = Path(temp_dir) / "scope-change-status.md"
            valid_path.write_text(scope_change_text, encoding="utf-8")
            scope_change_errors = validator_namespace["validate"](valid_path)
            if scope_change_errors:
                errors.append(
                    "handshake validator rejected a valid paused scope escalation: "
                    + "; ".join(scope_change_errors)
                )

        scope_start = design_text.index("## Scope Contract — Version 1")
        scope_end = design_text.index("\n## Purpose", scope_start)
        scope_v2 = design_text[scope_start:scope_end].replace(
            "## Scope Contract — Version 1",
            "## Scope Contract — Version 2",
            1,
        )
        rescoped_text = (
            design_text.replace("scope_version: 1", "scope_version: 2", 1)
            .replace(
                "last_reviewed_commit: null",
                "last_reviewed_commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                1,
            )
            .replace("last_reviewed_scope_version: null", "last_reviewed_scope_version: 1", 1)
            .replace("\n## Purpose", f"\n{scope_v2}\n\n## Purpose", 1)
        )
        with tempfile.TemporaryDirectory(prefix="agent-review-handshake-") as temp_dir:
            valid_path = Path(temp_dir) / "rescoped-same-commit.md"
            valid_path.write_text(rescoped_text, encoding="utf-8")
            rescoped_errors = validator_namespace["validate"](valid_path)
            if rescoped_errors:
                errors.append(
                    "handshake validator rejected the same commit under a new approved scope: "
                    + "; ".join(rescoped_errors)
                )

    python_files = [ROOT / "scripts/validate_release.py", validator]
    for path in python_files:
        if path.is_file():
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except SyntaxError as exc:
                errors.append(f"Python compilation failed for {path.relative_to(ROOT)}: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Release validation passed for both skills and both examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
