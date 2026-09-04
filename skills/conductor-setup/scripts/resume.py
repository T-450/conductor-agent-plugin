#!/usr/bin/env python3
"""
Determines the next unblocked setup step in the Conductor workflow.
Cross-platform compatible across Windows, macOS, and Linux.
"""

import json
import os
import sys

def _file_has_content(path):
    """True iff path is a readable file with non-whitespace text.

    Fail-closed: missing, unreadable, or blank files count as incomplete.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return bool(f.read().strip())
    except OSError:
        return False


def _artifact_complete(path):
    """True iff a setup artifact counts as done.

    Files need non-whitespace content (a stub file is not a finished step);
    directories need to contain at least one file.
    """
    if os.path.isdir(path):
        try:
            return any(
                os.path.isfile(os.path.join(path, entry))
                for entry in os.listdir(path)
            )
        except OSError:
            return False
    return _file_has_content(path)


def determine_resumption():
    """Checks existing setup artifacts and returns the next unblocked step."""
    conductor_dir = "conductor"
    files = [
        "product.md",
        "product-guidelines.md",
        "tech-stack.md",
        "code_styleguides",
        "workflow.md",
    ]

    checklist = {}
    for filename in files:
        path = os.path.join(conductor_dir, filename)
        checklist[filename] = _artifact_complete(path)

    setup_complete = _file_has_content(os.path.join(conductor_dir, "index.md"))

    next_step = None

    chain = [
        ("product.md", "Product Definition"),
        ("product-guidelines.md", "Product Guidelines"),
        ("tech-stack.md", "Technology Stack"),
        ("code_styleguides", "Code Style Guides"),
        ("workflow.md", "Workflow Configuration"),
    ]

    for filename, step_name in chain:
        if not checklist.get(filename, False):
            next_step = {
                "step": step_name,
                "file": filename,
            }
            break

    return {
        "setup_complete": setup_complete,
        "checklist": checklist,
        "next_step": next_step,
    }

if __name__ == "__main__":
    try:
        result = determine_resumption()
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as err:
        error_payload = {
            "setup_complete": False,
            "error": str(err),
            "next_step": {"step": "Project Discovery", "file": "product.md"}
        }
        print(json.dumps(error_payload, indent=2))
        sys.exit(0)
