#!/usr/bin/env python3
"""Parse the selected lab Bash snippets without executing learner commands."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    git_bash = Path("C:/Program Files/Git/bin/bash.exe")
    bash = str(git_bash) if sys.platform == "win32" and git_bash.is_file() else shutil.which("bash")
    if not bash:
        print("Bash is required for syntax checking; no learner commands were run.")
        return 2
    manifest = ROOT / "workshops/sandbox/manifest.json"
    errors, count = [], 0
    for tutorial in json.loads(manifest.read_text(encoding="utf-8"))["tutorials"]:
        if tutorial["filename"].startswith("https://"):
            continue
        path = (manifest.parent / tutorial["filename"]).resolve()
        text = path.read_text(encoding="utf-8")
        for index, block in enumerate(re.findall(r"```bash\n(.*?)```", text, re.S), 1):
            snippet = block.replace("<copy>", "").replace("</copy>", "")
            result = subprocess.run([bash, "-n"], input=snippet, capture_output=True, text=True)
            count += 1
            if result.returncode:
                errors.append({"file": path.relative_to(ROOT).as_posix(), "block": index,
                               "error": result.stderr.strip()})
    print(json.dumps({"passed": not errors, "bash_blocks": count, "errors": errors,
                      "limitations": "Syntax only; no cloud, build, or learner commands executed."}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
