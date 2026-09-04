#!/usr/bin/env python3
"""
Automated evaluation and benchmark suite for Conductor Pi/OMP plugin.
Tests manifests, skill frontmatter, script execution, and SDD workflow invariants.
"""

import json
import os
import importlib.util
from pathlib import Path

def test_manifests(base_dir: Path):
    print("[1/7] Testing manifests and installer scripts...")
    manifest_files = [
        base_dir / "plugin.json",
        base_dir / ".claude-plugin" / "plugin.json",
        base_dir / ".claude-plugin" / "marketplace.json",
        base_dir / "gemini-extension.json",
        base_dir / "package.json",
        base_dir / "VERSION",
    ]
    for mf in manifest_files:
        if not mf.exists():
            raise FileNotFoundError(f"Missing manifest or version file: {mf}")
        if mf.suffix == ".json":
            with open(mf, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert "name" in data, f"Missing 'name' in {mf}"

    # Verify installer scripts exist and are valid
    assert (base_dir / "install.sh").exists(), "Missing install.sh"
    assert (base_dir / "install.ps1").exists(), "Missing install.ps1"
    assert (base_dir / "bin" / "conductor").exists(), "Missing bin/conductor"
    print("  -> All manifests, VERSION, and installer scripts verified.")

def plugin_names(base_dir: Path, key: str, prefix: str):
    """Derive expected names from plugin.json (source of truth)."""
    manifest = json.loads((base_dir / "plugin.json").read_text(encoding="utf-8"))
    entries = manifest.get(key, [])
    assert entries, f"plugin.json '{key}' is empty or missing"
    names = []
    for entry in entries:
        assert entry.startswith(prefix), f"Unexpected plugin.json '{key}' entry: {entry}"
        names.append(entry[len(prefix):])
    return names


def test_skills_frontmatter(base_dir: Path):
    print("[2/6] Testing skill frontmatters and markdown integrity...")
    skills = plugin_names(base_dir, "skills", "./skills/")
    for s in skills:
        skill_path = base_dir / "skills" / s / "SKILL.md"
        if not skill_path.exists():
            raise FileNotFoundError(f"Missing SKILL.md for {s}")
        content = skill_path.read_text(encoding="utf-8")
        assert content.startswith("---"), f"SKILL.md in {s} does not start with frontmatter"
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"SKILL.md in {s} has unclosed frontmatter"
        frontmatter = parts[1]
        assert f"name: {s}" in frontmatter, f"Name mismatch in {s} frontmatter"
        assert "description:" in frontmatter, f"Missing description in {s} frontmatter"
        assert len(content) > 1000, f"Skill content in {s} is suspiciously short ({len(content)} chars)"
    registered = set(skills)
    for d in sorted((base_dir / "skills").iterdir()):
        if (d / "SKILL.md").is_file():
            assert d.name in registered, f"Skill '{d.name}' exists but is not registered in plugin.json"
    print(f"  -> All {len(skills)} skills verified with correct frontmatter and structure.")

def test_rules(base_dir: Path):
    print("[3/7] Testing rule definitions...")
    rules = [
        base_dir / "rules" / "conductor_pi.md",
        base_dir / "conductor_antigravity.md",
        base_dir / "rules" / "conductor_antigravity.md",
        base_dir / "rules" / "conductor_orchestrate_pi.md",
        base_dir / "rules" / "conductor_orchestrate_copilot.md",
        base_dir / "rules" / "conductor_orchestrate_agy.md",
    ]
    for r in rules:
        if not r.exists():
            raise FileNotFoundError(f"Missing rule file: {r}")
        content = r.read_text(encoding="utf-8")
        assert "trigger:" in content, f"Missing trigger in {r}"
        assert "description:" in content, f"Missing description in {r}"
    print("  -> All UX adapter rules verified.")

def test_agents_and_commands(base_dir: Path):
    print("[4/7] Testing subagents and slash commands...")
    agents = ["orchestra-planning.md", "orchestra-implement.md", "orchestra-code-review.md"]
    for a in agents:
        agent_path = base_dir / "agents" / a
        assert agent_path.exists(), f"Missing agent: {a}"
        content = agent_path.read_text(encoding="utf-8")
        assert "subagent: true" in content, f"Missing subagent: true in {a}"

    commands = plugin_names(base_dir, "commands", "./commands/")
    for c in commands:
        cmd_path = base_dir / "commands" / c
        assert cmd_path.exists(), f"Missing command: {c}"
        content = cmd_path.read_text(encoding="utf-8")
        assert "name:" in content, f"Missing name: in {c}"
    registered_cmds = set(commands)
    for f in sorted((base_dir / "commands").glob("*.md")):
        assert f.name in registered_cmds, f"Command '{f.name}' exists but is not registered in plugin.json"
    print(f"  -> All {len(agents)} subagents and {len(commands)} slash commands verified.")

def test_resume_script(base_dir: Path):
    print("[5/7] Testing resume.py script logic...")
    script_path = base_dir / "skills" / "conductor-setup" / "scripts"
    spec = importlib.util.spec_from_file_location("conductor_resume", script_path / "resume.py")
    resume = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resume)
    res = resume.determine_resumption()
    assert isinstance(res, dict), "resume.py did not return a dictionary"
    assert "setup_complete" in res
    assert "checklist" in res
    assert "next_step" in res
    print("  -> resume.py executed successfully and returned valid status schema.")

def test_assets(base_dir: Path):
    print("[6/7] Testing assets and styleguides...")
    setup_assets = base_dir / "skills" / "conductor-setup" / "assets"
    assert (setup_assets / "workflow.md").exists(), "Missing workflow.md"
    assert (setup_assets / "catalog.md").exists(), "Missing catalog.md"
    
    styleguides_dir = setup_assets / "code_styleguides"
    assert styleguides_dir.exists(), "Missing code_styleguides directory"
    required_guides = ["python.md", "typescript.md", "javascript.md", "go.md", "general.md", "cpp.md", "csharp.md", "dart.md", "html-css.md", "ruby.md"]
    for g in required_guides:
        assert (styleguides_dir / g).exists(), f"Missing styleguide {g}"
    print(f"  -> All {len(required_guides)} code styleguides and assets verified.")

def test_doctor_cli(base_dir: Path):
    print("[7/7] Testing conductor doctor CLI diagnostic...")
    import subprocess
    res = subprocess.run(["node", str(base_dir / "bin" / "conductor"), "doctor"], capture_output=True, text=True)
    assert res.returncode == 0, f"conductor doctor exited with non-zero code {res.returncode}: {res.stderr}"
    assert "CONDUCTOR HEALTH DIAGNOSTIC" in res.stdout, "Missing header in doctor output"
    print("  -> conductor doctor executed cleanly and verified environment.")

def run_benchmark():
    print("==================================================")
    print("   CONDUCTOR PI / OH-MY-PI PLUGIN EVALUATION   ")
    print("==================================================")
    base_dir = Path(__file__).resolve().parent.parent
    test_manifests(base_dir)
    test_skills_frontmatter(base_dir)
    test_rules(base_dir)
    test_agents_and_commands(base_dir)
    test_resume_script(base_dir)
    test_assets(base_dir)
    test_doctor_cli(base_dir)
    print("==================================================")
    print("   ALL EVALS PASSED (7/7) - 100% SCORE GRADE A+   ")
    print("==================================================")

if __name__ == "__main__":
    run_benchmark()

