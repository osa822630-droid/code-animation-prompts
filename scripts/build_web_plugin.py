"""Build or check the lightweight Claude Web plugin from the canonical skill.

Only the generated skill subtree and plugin LICENSE.md are managed here. The
marketplace/plugin manifests, plugin README, and command are authored directly.
No third-party packages or network access are required. Python 3.10+.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "code-animation-prompts"
SOURCE = ROOT / "skills" / NAME
PLUGIN = ROOT / "plugins" / NAME
TARGET = PLUGIN / "skills" / NAME
MARKETPLACE = ROOT / ".claude-plugin/marketplace.json"
EXCLUDED_SUFFIXES = {".mp4", ".pyc", ".pyo"}
EXCLUDED_DIRS = {"__pycache__", ".git"}
EXCLUDED_FILENAMES = {".DS_Store", "Thumbs.db"}
AUTHORED = {
    ".claude-plugin/plugin.json",
    "README.md",
    "commands/animate.md",
    "assets/icon.png",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files_under(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    if directory.is_symlink():
        raise ValueError(f"Symlinked package directory is not allowed: {directory}")
    result = set()
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symlinked package file is not allowed: {path}")
        if path.is_file():
            result.add(path.relative_to(directory).as_posix())
    return result


def source_files() -> set[str]:
    return {
        name for name in files_under(SOURCE)
        if Path(name).suffix.lower() not in EXCLUDED_SUFFIXES
        and Path(name).name not in EXCLUDED_FILENAMES
        and not EXCLUDED_DIRS.intersection(Path(name).parts)
    }


def managed_files() -> dict[str, Path]:
    """Map package-relative paths to their canonical source files."""
    managed = {f"skills/{NAME}/{name}": SOURCE / name for name in source_files()}
    managed["LICENSE.md"] = ROOT / "LICENSE.md"
    return managed


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_manifests() -> dict:
    marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    require(marketplace.get("name") == NAME, "Unexpected marketplace name")
    require(bool(marketplace.get("owner", {}).get("name")), "Marketplace owner is required")
    entries = marketplace.get("plugins", [])
    require(len(entries) == 1, "Marketplace must list exactly one plugin")
    entry = entries[0]
    require(entry.get("name") == NAME, "Marketplace plugin name differs")
    require(entry.get("source") == f"./plugins/{NAME}",
            "Claude Web source must be the relative ./plugins/... path")
    require(entry.get("strict", True) is True, "Plugin uses its own manifest; strict must be true")

    manifest = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    require(manifest.get("name") == NAME, "Plugin manifest name differs")
    require(bool(re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", ""))),
            "Plugin version must use major.minor.patch")
    require(bool(manifest.get("description")), "Plugin description is required")
    require(bool(manifest.get("author", {}).get("name")), "Plugin author is required")
    require("license" not in manifest, "Mixed-source collection must not declare a single SPDX license")

    skill_text = (SOURCE / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", skill_text, re.S)
    require(frontmatter is not None, "Canonical SKILL.md needs YAML frontmatter")
    name_match = re.search(r"^name:\s*[\"']?([\w-]+)[\"']?\s*$", frontmatter.group(1), re.M)
    require(name_match is not None and name_match.group(1) == NAME, "Skill name differs")
    description = re.search(r"^description:\s*(.+)$", frontmatter.group(1), re.M)
    require(description is not None and len(description.group(1)) <= 1024,
            "Skill description is required and must be at most 1024 characters")
    require("<" not in description.group(1) and ">" not in description.group(1),
            "Avoid angle brackets in skill descriptions for web sync compatibility")
    require("references/claude-web.md" in skill_text, "Skill must link the web execution guide")
    require("references/video-examples.md" in skill_text, "Skill must link the original video examples")
    require((SOURCE / "references/video-examples.md").is_file(), "Original video example links are missing")

    command = PLUGIN / "commands/animate.md"
    require(command.is_file(), "The short animate command is missing")
    require(command.read_text(encoding="utf-8").startswith("---\ndescription:"),
            "animate command needs frontmatter and a description")
    return manifest


def differences() -> tuple[set[str], set[str], set[str]]:
    managed = managed_files()
    expected = set(managed) | AUTHORED
    actual = files_under(PLUGIN)
    missing = expected - actual
    extra = actual - expected
    changed = {
        name for name in set(managed) & actual
        if digest(PLUGIN / name) != digest(managed[name])
    }
    return missing, extra, changed


def check() -> dict:
    manifest = validate_manifests()
    missing, extra, changed = differences()
    require(not missing, f"Web package is missing {len(missing)} files: {sorted(missing)[:5]}")
    require(not extra, f"Unexpected files in generated web package: {sorted(extra)[:5]}")
    require(not changed, f"Web package differs from source in {len(changed)} files: {sorted(changed)[:5]}")
    all_files = files_under(PLUGIN)
    require(not any(Path(name).suffix.lower() == ".mp4" for name in all_files),
            "Large example videos must stay out of the web package")
    catalog = json.loads((TARGET / "references/catalog.json").read_text(encoding="utf-8"))
    require(catalog["total"] == len(catalog["entries"]) == 341, "Web catalog must retain all 341 styles")
    require(sum(bool(entry["image"]) for entry in catalog["entries"]) == 193,
            "Web catalog must retain all 193 stills")
    size = sum((PLUGIN / name).stat().st_size for name in all_files)
    return {"version": manifest["version"], "files": len(all_files), "bytes": size}


def prune_empty_dirs(directory: Path) -> None:
    for path in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and not path.is_symlink() and not any(path.iterdir()):
            path.rmdir()


def build(prune: bool = False) -> dict:
    validate_manifests()
    require(TARGET.resolve() == (ROOT / "plugins" / NAME / "skills" / NAME).resolve(),
            "Generated target escaped the repository")
    missing, extra, changed = differences()
    stale_skill_files = {name for name in extra if name.startswith(f"skills/{NAME}/")}
    other_extra = extra - stale_skill_files
    require(not other_extra, f"Unmanaged plugin files need manual review: {sorted(other_extra)}")
    require(not stale_skill_files or prune,
            "Stale generated skill files exist; review them and rerun with --prune")
    for name, source in managed_files().items():
        destination = PLUGIN / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists() or digest(destination) != digest(source):
            shutil.copy2(source, destination)
    for name in sorted(stale_skill_files):
        (PLUGIN / name).unlink()
    prune_empty_dirs(TARGET)
    return check()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check only; do not write files")
    parser.add_argument("--prune", action="store_true", help="Remove stale files only inside the generated skill subtree")
    args = parser.parse_args()
    if args.check and args.prune:
        parser.error("--check and --prune cannot be combined")
    try:
        result = check() if args.check else build(prune=args.prune)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    action = "checked" if args.check else "built"
    print(f"PASS: {action} Claude Web plugin {result['version']}; "
          f"{result['files']} files, {result['bytes'] / 1024 / 1024:.2f} MiB; "
          "341 styles and 193 stills retained; no MP4 duplicates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
