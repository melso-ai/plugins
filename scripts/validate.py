#!/usr/bin/env python3
"""Validate the marketplaces and plugins in this repository without network access."""

import json
from pathlib import Path
import re
import struct
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "https://mcp.melso.ai/mcp"
# Directory links only the Claude manifest declares, with the OpenAI
# interface field each must match (None: Claude only).
CLAUDE_LINKS = {
    "repository": None,
    "documentationUrl": "websiteURL",
    "supportUrl": "supportURL",
    "privacyPolicyUrl": "privacyPolicyURL",
    "termsOfServiceUrl": "termsOfServiceURL",
}
errors = []


def fail(message):
    errors.append(message)


def tracked():
    output = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout
    return [ROOT / name for name in output.decode().split("\0") if name]


def load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as error:
        fail(f"{path.relative_to(ROOT)}: {error}")
        return None


def inside(base, relative, label):
    path = (base / relative).resolve()
    if not relative.startswith("./") or not path.is_relative_to(base.resolve()):
        fail(f"{label}: {relative} must be a ./ path inside {base.relative_to(ROOT)}")
        return None
    if not path.exists():
        fail(f"{label}: {relative} does not exist")
        return None
    return path


def check_plugin(plugin):
    label = str(plugin.relative_to(ROOT))
    manifest = load(plugin / "plugin.json")
    claude = load(plugin / ".claude-plugin" / "plugin.json")
    mcp = load(plugin / "mcp.json")
    claude_mcp = load(plugin / ".mcp.json")
    if None in (manifest, claude, mcp, claude_mcp):
        return
    if manifest.get("name") != plugin.name:
        fail(f"{label}/plugin.json: name {manifest.get('name')!r} must match the folder")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version"))):
        fail(f"{label}/plugin.json: version must be semantic (x.y.z)")
    expected = {key: value for key, value in manifest.items() if key not in {"$schema", "extensions"}}
    if {key: value for key, value in claude.items() if key not in CLAUDE_LINKS} != expected:
        fail(f"{label}: .claude-plugin/plugin.json differs from plugin.json (name, version, description, author, links)")
    extension = manifest.get("extensions", {}).get("com.openai", {})
    interface = extension.get("interface", {})
    for key, openai_key in CLAUDE_LINKS.items():
        if openai_key and claude.get(key) != interface.get(openai_key):
            fail(f"{label}: Claude {key} differs from the OpenAI {openai_key}")
    for key in ("mcpServers", "onboardingSkill"):
        if key in extension:
            inside(plugin, extension[key], f"{label}/plugin.json {key}")
    for key in ("composerIcon", "composerIconDark", "logo", "logoDark"):
        if key in interface:
            icon = inside(plugin, interface[key], f"{label}/plugin.json {key}")
            if icon:
                check_icon(icon)
    if mcp.get("mcpServers") != {plugin.name: {"type": "streamable-http", "url": ENDPOINT}}:
        fail(f"{label}/mcp.json must only hold the Melso connection at {ENDPOINT}, without credentials or headers")
    if claude_mcp.get("mcpServers") != {plugin.name: {"type": "http", "url": ENDPOINT}}:
        fail(f"{label}/.mcp.json must only hold the Melso connection at {ENDPOINT}, without credentials or headers")
    skills = sorted((plugin / "skills").glob("*/SKILL.md"))
    if not skills:
        fail(f"{label}: no skills/*/SKILL.md")
    for skill in skills:
        check_skill(skill)


def check_icon(path):
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        fail(f"{path.relative_to(ROOT)}: not a PNG")
        return
    if struct.unpack(">II", data[16:24]) != (512, 512):
        fail(f"{path.relative_to(ROOT)}: icon must be 512x512")


def check_skill(path):
    label = str(path.relative_to(ROOT))
    match = re.match(r"---\n(.*?)\n---\n", path.read_text(), re.S)
    if not match:
        fail(f"{label}: missing YAML frontmatter")
        return
    fields = dict(re.findall(r"^(\w+):\s*(.+)$", match.group(1), re.M))
    if fields.get("name") != path.parent.name:
        fail(f"{label}: frontmatter name must be {path.parent.name!r}")
    if not fields.get("description", "").strip('" '):
        fail(f"{label}: frontmatter description is empty")


def check_marketplaces():
    claude = load(ROOT / ".claude-plugin" / "marketplace.json")
    for entry in (claude or {}).get("plugins", []):
        plugin = inside(ROOT, entry.get("source", ""), f".claude-plugin/marketplace.json {entry.get('name')}")
        if plugin:
            manifest = load(plugin / ".claude-plugin" / "plugin.json") or {}
            if manifest.get("name") != entry.get("name"):
                fail(f".claude-plugin/marketplace.json: {entry.get('name')!r} does not match its plugin name")
            if entry.get("description") not in (None, manifest.get("description")):
                fail(f".claude-plugin/marketplace.json: {entry.get('name')!r} description differs from plugin.json")
    codex = load(ROOT / ".agents" / "plugins" / "marketplace.json")
    for entry in (codex or {}).get("plugins", []):
        source = entry.get("source", {})
        if source.get("source") != "local":
            fail(f".agents/plugins/marketplace.json: {entry.get('name')!r} must use a local source")
            continue
        plugin = inside(ROOT, source.get("path", ""), f".agents/plugins/marketplace.json {entry.get('name')}")
        if plugin and (load(plugin / "plugin.json") or {}).get("name") != entry.get("name"):
            fail(f".agents/plugins/marketplace.json: {entry.get('name')!r} does not match its plugin name")
    if claude and codex and claude.get("name") != codex.get("name"):
        fail("The Claude and Codex marketplaces must share a name")


def check_text(files):
    for path in files:
        if path.suffix not in {".md", ".json"}:
            continue
        label = str(path.relative_to(ROOT))
        text = path.read_text()
        for url in re.findall(r"https://mcp\.melso\.ai[^\s`\"')>]*", text):
            if url.rstrip(".,") != ENDPOINT:
                fail(f"{label}: MCP URL {url} differs from {ENDPOINT}")
        if path.suffix == ".md":
            for target in re.findall(r"\]\(([^)\s]+)\)", text):
                if re.match(r"[a-z]+:|#", target):
                    continue
                if not (path.parent / target.split("#")[0]).exists():
                    fail(f"{label}: link {target} does not exist")


def main():
    files = tracked()
    for path in files:
        if path.suffix == ".json":
            load(path)
    check_marketplaces()
    for manifest in sorted(ROOT.glob("plugins/*/plugin.json")):
        check_plugin(manifest.parent)
    check_text(files)
    if errors:
        print("\n".join(f"error: {message}" for message in errors), file=sys.stderr)
        sys.exit(1)
    print("Validated marketplaces and plugins")


if __name__ == "__main__":
    main()
