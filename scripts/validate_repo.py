"""Validate original assets, the Claude Web package, catalogs, and documentation links."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

from build_web_plugin import check as check_web_plugin

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/code-animation-prompts"
LIBRARY = SKILL / "assets/library"
WEB_LIBRARY = ROOT / "plugins/code-animation-prompts/skills/code-animation-prompts/assets/library"


def main():
    manifest = json.loads((ROOT / "docs/source-manifest.json").read_text(encoding="utf-8"))
    files = {p.relative_to(LIBRARY).as_posix(): p for p in LIBRARY.rglob("*") if p.is_file()}
    assert set(files) == set(manifest["files"]), "Original library file set differs"
    for name, digest in manifest["files"].items():
        assert hashlib.sha256(files[name].read_bytes()).hexdigest() == digest, f"Original file changed: {name}"
    data = json.loads((SKILL / "references/catalog.json").read_text(encoding="utf-8"))
    assert data["total"] == len(data["entries"]) == 341
    assert len({e["id"] for e in data["entries"]}) == 341
    assert sum(bool(e["image"]) for e in data["entries"]) == data["with_still"] == 193
    for entry in data["entries"]:
        for key in ["file", "image"]:
            if entry[key]:
                assert (SKILL / entry[key]).is_file(), entry[key]
    web = check_web_plugin()
    checked = 0
    for doc in ROOT.rglob("*.md"):
        if any(part in {".git", ".build", ".agents", ".claude"} for part in doc.relative_to(ROOT).parts):
            continue
        if LIBRARY in doc.parents or WEB_LIBRARY in doc.parents:
            continue  # Original documents are retained verbatim in both distributions.
        for target in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding="utf-8")):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            path = unquote(target.split("#")[0])
            assert (doc.parent / path).exists(), f"Broken link: {doc.relative_to(ROOT)} -> {target}"
            checked += 1
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    prompt = re.search(r'```text\n(请将 https://github.com/XiaoyeCodes/code-animation-prompts.*?)(?:\n```)', readme, re.S).group(1)
    assert prompt in (ROOT / "prompts/one-click-import.md").read_text(encoding="utf-8")
    print(f"PASS: {len(files)} original files unchanged; 341 styles; 193 stills; {checked} local links; import prompt consistent.")
    print(f"PASS: Claude Web plugin {web['version']}; {web['files']} files; {web['bytes'] / 1024 / 1024:.2f} MiB; generated package matches source.")


if __name__ == "__main__":
    main()
