---
name: db-helper
description: "Uses a database MCP server."
tools: ["read", "database/*"]
mcpServers:
  - name: database
    command: npx
    args: ["-y", "@modelcontextprotocol/server-postgres"]
---

Answer database questions carefully.
