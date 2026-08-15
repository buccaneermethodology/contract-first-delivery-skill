#!/usr/bin/env python3
"""Dependency-free CI check compatible with the required Codex Skill shape."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_skill_shape.py <skill-dir>", file=sys.stderr)
        return 2
    skill_dir = Path(argv[1])
    skill_file = skill_dir / "SKILL.md"
    agent_file = skill_dir / "agents" / "openai.yaml"
    reference_file = skill_dir / "references" / "REFERENCE.md"
    missing = [path for path in (skill_file, agent_file, reference_file) if not path.is_file()]
    if missing:
        for path in missing:
            print(f"SKILL-SHAPE-MISSING: {path}")
        return 1
    text = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        print("SKILL-SHAPE-FRONTMATTER: SKILL.md lacks YAML frontmatter")
        return 1
    frontmatter = match.group(1)
    if not re.search(r"^name:\s+contract-first-delivery\s*$", frontmatter, re.MULTILINE):
        print("SKILL-SHAPE-NAME: unexpected or missing skill name")
        return 1
    if not re.search(r"^description:\s+\S", frontmatter, re.MULTILINE):
        print("SKILL-SHAPE-DESCRIPTION: description is missing")
        return 1
    agent_text = agent_file.read_text(encoding="utf-8")
    required_agent_keys = ("display_name:", "short_description:", "default_prompt:")
    if any(key not in agent_text for key in required_agent_keys):
        print("SKILL-SHAPE-AGENT: agents/openai.yaml is incomplete")
        return 1
    if "$contract-first-delivery" not in agent_text:
        print("SKILL-SHAPE-PROMPT: default_prompt must mention $contract-first-delivery")
        return 1
    print("SKILL-SHAPE-VALID: required skill surfaces are present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
