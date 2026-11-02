# Melso plugins

Official [Melso](https://melso.ai) plugins for Claude Code and Codex. Melso is
a tax service (gestoría) with a personal AI agent for autónomos and companies
in Spain.

The `melso` plugin connects your assistant to Melso's fiscal MCP server at
`https://mcp.melso.ai/mcp` and adds a skill that explains how to work with it.
You sign in with your Melso account through OAuth and choose one company per
connection. You can then review your tax calendar, the returns Melso prepares,
your expenses, income, contacts and documents, and open and follow Gestiones
with Melso's professionals. Tax returns and Gestiones are always approved in
the Melso web app. You can revoke the connection at any time in Melso's
Settings.

The plugin runs no local code: it contains only the manifests, the MCP server
address, a skill and an icon.

## Claude Code

```sh
claude plugin marketplace add melso-ai/plugins
claude plugin install melso@melso
```

Then run `/mcp`, choose `plugin:melso:melso` and sign in to Melso.

## Codex

```sh
codex plugin marketplace add melso-ai/plugins
codex plugin add melso@melso
```

Enable Melso in the Plugins directory and complete its OAuth connection.

## Try it

- "Connect Melso and confirm which company I am working in."
- "What are my next tax deadlines in Melso?"
- "Which Gestiones do I have open in Melso?"

## Links

- Server and connection guide: https://melso.ai/mcp
- Privacy policy: https://melso.ai/privacy
- Terms: https://melso.ai/terms
- Support: hello@melso.ai

This repository is published from Melso's main repository. Report problems
through Melso support or a GitHub issue here.
