# Melso plugin

Plugin for Claude Code and Codex that connects to Melso's fiscal MCP server at
`https://mcp.melso.ai/mcp`. OAuth selects one autónomo or company. It packages
the connection and a fiscal workflow skill; it does not run a local backend.

## Install

In Claude Code 2.1.275 or later:

```
/plugin install melso --marketplace melso-ai/plugins
```

For older versions and for Codex, see the repository README.

## Use

After installing it, complete the OAuth connection
and select the intended company. Start a new conversation if the current one
still shows an old tool catalog. Then ask: “Connect Melso and confirm which
company I am working in.”

Connection checks are read-only. The assistant writes only when you ask for
specific work, and tax returns and Gestiones are approved in the Melso web app.

- `plugin.json`, `mcp.json`: portable Agent Plugins manifest used by Codex.
- `.claude-plugin/plugin.json`, `.mcp.json`: Claude Code manifest.
- `skills/melso/SKILL.md`: how the assistant works with Melso's tools.
