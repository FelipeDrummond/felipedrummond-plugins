# felipedrummond-plugins

A Claude Code plugin marketplace — my personal collection of plugins and skills.

## Plugins

| Plugin | Description |
|--------|-------------|
| [`linear-agent-tickets`](./linear-agent-tickets) | Author agent-ready Linear tickets with Q/A clarification and a parallel multi-agent council critique. |

## Use this marketplace

```bash
# Add the marketplace (from a local clone)
claude plugin marketplace add /path/to/felipedrummond-plugins

# Install a plugin
claude plugin install linear-agent-tickets
```

## Layout

```
.claude-plugin/marketplace.json   # marketplace manifest
linear-agent-tickets/             # one folder per plugin
  .claude-plugin/plugin.json
  .mcp.json
  agents/
  skills/
```
