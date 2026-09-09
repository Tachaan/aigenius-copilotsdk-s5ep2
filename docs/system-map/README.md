# System map

An interactive map of the retail analytics app, generated with
[Archify](https://github.com/tt-a1i/archify) from a typed JSON source and
rendered as a single self-contained HTML file.

Both tracks are behavioural mirrors, so one map covers them: where the stacks
differ, the node carries both names (`ASP.NET Core · FastAPI`).

<iframe src="map.html"
        title="Agent HQ Demo — retail analytics runtime architecture"
        loading="lazy"
        style="width: 100%; height: 780px; border: 1px solid var(--md-default-fg-color--lightest); border-radius: 4px;">
</iframe>

Tight on space? [Open the map full screen ↗](map.html){target=_blank rel=noopener}

## Guided views

The map ships with three curated views. Each link opens it focused on one
story:

| View | Shows |
|:-----|:------|
| [Chat request path](map.html#view=chat-request-path) | One prompt from the browser to the model and back as streamed tokens |
| [How the model reads data](map.html#view=model-data-access) | The read-only MCP tool path into SQLite |
| [REST and persistence](map.html#view=rest-and-persistence) | The application's own read/write path |

## Two paths to one database

The detail worth pausing on is that `retail.db` is reached two different ways,
with deliberately different privileges:

- **The application** reads and writes through `RetailAnalyticsService` —
  EF Core in .NET, SQLModel in Python.
- **The model** never touches SQLite directly. It calls five read-only tools on
  the `retail-analytics` MCP server, which opens SQLite with `mode=ro`. A write
  is rejected by the driver, so even a prompt-injected instruction to modify
  data cannot succeed.

The tool surface is the security boundary: the model gets
`get_customer_summary`, not `run_query`, so there is no arbitrary-SQL escape
hatch to reason about.

## Using the viewer

| Action | Control |
|:-------|:--------|
| Open the diagram guide | `?` |
| Find and focus a node | `/` |
| Trace a route between two nodes | `R` or **PATH** |
| Compare component roles | `L` or **LENS** |
| Overview radar | `M` or **MAP** |
| Play the guided story | `P` |

Light and dark themes, pan/zoom, and PNG/SVG export are in the top-right menu.

## Regenerating the map

The typed source is
[`agent-hq-demo.architecture.json`](agent-hq-demo.architecture.json) — edit it
rather than the HTML, which is generated output. With the Archify CLI
available:

```bash
node bin/archify.mjs validate architecture \
  docs/system-map/agent-hq-demo.architecture.json --quality showcase --json

node bin/archify.mjs deliver architecture \
  docs/system-map/agent-hq-demo.architecture.json \
  docs/system-map/map.html --quality showcase --json
```

`deliver` only replaces `map.html` when every check passes, so a broken edit
leaves the last good map in place.

## Related

- [Architecture reference](../breakouts/architecture.md) — the written
  walkthrough, request sequence, and data model
- [.NET Lab 06 — MCP](../labs/06-mcp/) · [Python Lab 06 — MCP](../labs-python/06-mcp/)
- [Hooks and governance](../breakouts/hooks-and-governance.md) — the other half
  of the least-privilege story
