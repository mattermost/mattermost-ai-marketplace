# grafana

Investigate production issues, query logs and metrics, and explore dashboards on the Mattermost Grafana instance.

## Skills

### `grafana:grafana`

Activates a Grafana investigation assistant scoped to the Mattermost production environment. Provides access to Loki logs, Prometheus metrics, dashboards, on-call schedules, and alert groups.

**Invoke**: `/grafana:grafana`

**Requires**: Grafana MCP server configured and connected.

## Prerequisites

The Grafana MCP server must be configured in your Claude Code settings. See the [Grafana MCP documentation](https://grafana.com/docs/grafana-cloud/developer-resources/ai-observability/mcp/) for setup instructions.
