#!/usr/bin/env python3
"""Static author checks scoped to the Sandbox manifest; no cloud operations."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
manifest = ROOT / "workshops/sandbox/manifest.json"
errors = []
links = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def check_markdown(path, instructional=False):
    text = path.read_text(encoding="utf-8")
    if text.count("```") % 2:
        errors.append(f"Unbalanced code fences: {path.relative_to(ROOT)}")
    for target in links.findall(text):
        clean = target.strip().split("#", 1)[0].strip("<>")
        clean = re.split(r"\s+(?=[\"'])", clean, maxsplit=1)[0]
        if not clean or re.match(r"^(https?://|mailto:)", clean):
            continue
        if not (path.parent / clean).resolve().exists():
            errors.append(f"Broken link: {path.relative_to(ROOT)} -> {clean}")
    if instructional:
        for section in ("## Introduction", "### Objectives", "### Prerequisites", "## Task 1:",
                        "## Troubleshooting", "## Completion checkpoint and recap", "## Acknowledgements"):
            if section not in text:
                errors.append(f"Missing {section}: {path.relative_to(ROOT)}")
        for phrase in ("Estimated", "Expected result", "Observe"):
            if phrase not in text:
                errors.append(f"Missing {phrase}: {path.relative_to(ROOT)}")
        if len(re.findall(r"^\s*\d+\.\s+", text, re.M)) < 3:
            errors.append(f"Insufficient numbered learner steps: {path.relative_to(ROOT)}")
        for block in re.findall(r"```bash\n(.*?)```", text, re.S):
            if "<copy>" not in block or "</copy>" not in block:
                errors.append(f"Bash block lacks LiveLabs copy markup: {path.relative_to(ROOT)}")


def main():
    data = json.loads(manifest.read_text(encoding="utf-8"))
    local = []
    for tutorial in data["tutorials"]:
        filename = tutorial["filename"]
        if filename.startswith("https://"):
            continue
        path = (manifest.parent / filename).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            errors.append(f"Invalid manifest tutorial: {filename}")
            continue
        local.append(path)
        check_markdown(path, instructional=True)
    for path in ROOT.rglob("*.md"):
        if path not in local and not any(part in {".runs", ".generated", ".offline-demo"} for part in path.parts):
            check_markdown(path)
    starter = ROOT / "files/starter"
    contract = json.loads((starter / "contract.json").read_text(encoding="utf-8"))
    for stage in contract["stages"]:
        if not (starter / f"prompts/{stage}.md").is_file():
            errors.append(f"Missing prompt: {stage}")
    for required in ("lab.py", "requirements-runner.txt", "config.example.json", "deployment.example.json",
                     "specs/app-brief.md", "specs/sdk-reference.md", "prompts/system.md", "prompts/repair.md"):
        if not (starter / required).is_file():
            errors.append(f"Missing starter asset: {required}")
    launcher = manifest.parent / "index.html"
    if not launcher.is_file() or "redwood-hol/js/main.min.js" not in launcher.read_text(encoding="utf-8"):
        errors.append("Missing or unexpected Redwood launcher")
    if len(local) != 7 or len(set(local)) != len(local):
        errors.append("Expected introduction plus six distinct local labs")
    print(json.dumps({"passed": not errors, "variant": "sandbox", "local_tutorials": len(local),
                      "errors": errors, "limitations": "Static content/asset checks only; no endpoint or cloud execution."}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
