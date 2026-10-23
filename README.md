# WeeklyMoat MCP Server

Value-investing signals for Claude and other AI agents. 966 stocks across 6 markets, screened every week using Graham & Buffett criteria, delivered as tools your agent can call.

Ask your agent things like:
- "What are the best value stocks this week?"
- "Which stocks are close to a buy zone right now?"
- "Show me this week's signals with a margin of safety above 20%."

## Get a free key

[weeklymoat.com/api-signup.html](https://weeklymoat.com/api-signup.html). 500 credits a month, no credit card.

## Set up

### Claude Desktop

Add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weeklymoat": {
      "command": "npx",
      "args": ["-y", "weeklymoat-mcp"],
      "env": { "WEEKLYMOAT_API_KEY": "wm_live_YOUR_KEY_HERE" }
    }
  }
}
```

### Claude Code

```bash
claude mcp add weeklymoat -e WEEKLYMOAT_API_KEY=wm_live_YOUR_KEY_HERE -- npx -y weeklymoat-mcp
```

### Cursor, Windsurf and other MCP clients

Use the same `command`, `args` and `env` as the Claude Desktop example.

## Tools

| Tool | What it returns | Credits |
|---|---|---|
| `get_weekly_signals` | This week's buy signals, ranked by composite score | 5 |
| `get_watchlist` | Stocks approaching the buy zone | 3 |
| `get_screener` | Full universe with Graham, Buffett and Deep Value scores (Starter plan+) | 10 |
| `get_status` | API health and last screener run | Free |
| `get_usage` | Remaining credits this month | — |

Each signal includes ticker, exchange, sector, Graham/Buffett/composite scores, P/E, P/B, ROE, margin of safety, dividend yield, signal and confidence.

## Not using MCP?

The REST API is documented at [weeklymoat.com/api](https://weeklymoat.com/api), with an OpenAPI spec at [weeklymoat.com/openapi.json](https://weeklymoat.com/openapi.json).

## Disclaimer

WeeklyMoat data is quantitative screening output, not personalised financial advice.

## License

MIT
