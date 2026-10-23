#!/usr/bin/env node
// WeeklyMoat MCP server: exposes the WeeklyMoat value-investing API as MCP tools.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const BASE_URL = (process.env.WEEKLYMOAT_BASE_URL || "https://weeklymoat.com/api/v1").replace(/\/$/, "");
const API_KEY = process.env.WEEKLYMOAT_API_KEY || "";
const SIGNUP_URL = "https://weeklymoat.com/api-signup.html";

async function callApi(path, { auth = true, allowDemo = false } = {}) {
  if (auth && !API_KEY && !allowDemo) {
    return errorResult(
      `No API key set. Get a free key (500 credits/month, no card) at ${SIGNUP_URL}, ` +
        `then set WEEKLYMOAT_API_KEY in your MCP client config.`
    );
  }
  const url = BASE_URL + path;
  const headers = { Accept: "application/json", "User-Agent": "weeklymoat-mcp/1.0.1" };
  if (auth && API_KEY) headers.Authorization = `Bearer ${API_KEY}`;

  let res;
  try {
    res = await fetch(url, { headers, signal: AbortSignal.timeout(30000) });
  } catch (err) {
    return errorResult(`Could not reach the WeeklyMoat API: ${err.message}`);
  }
  const text = await res.text();
  if (!res.ok) {
    const hints = {
      401: `The API key was rejected. Check WEEKLYMOAT_API_KEY or get a new key at ${SIGNUP_URL}.`,
      402: "Out of credits for this month. Upgrade at https://weeklymoat.com/api#pricing.",
      403: "This endpoint isn't included in your plan (/screener needs Starter or higher). See https://weeklymoat.com/api#pricing.",
      429: "Rate limited. Wait a moment and try again.",
      503: "Screener data temporarily unavailable — the weekly refresh may be in progress. Try again shortly.",
    };
    return errorResult(`WeeklyMoat API error ${res.status}. ${hints[res.status] || ""}\n${text.slice(0, 1000)}`);
  }
  return { content: [{ type: "text", text }] };
}

function errorResult(message) {
  return { isError: true, content: [{ type: "text", text: message }] };
}

const DISCLAIMER =
  "Data is quantitative screening output, not personalised financial advice.";

const server = new McpServer({ name: "weeklymoat", version: "1.0.1" });

server.registerTool(
  "get_weekly_signals",
  {
    title: "This week's value-investing buy signals",
    description:
      "Get this week's top value stocks meeting Graham + Buffett criteria, ranked by composite score (total_score). " +
      "Returns up to 20 signals. Each signal includes: ticker, exchange, total_score, pe, pb, roe, margin_of_safety, " +
      "sector (may be null), and moat_signals (array of passing criteria tags like 'PE<15', 'ROE>15%', 'FCF>0'). " +
      "Also returns watch_count (total stocks on watchlist) and _meta with credit usage. " +
      `Use for questions like 'what are the best value stocks this week?'. Costs 5 credits. ` +
      `Without a key, returns the top 3 signals as a free demo (20 calls/day, no key needed). ${DISCLAIMER}`,
    inputSchema: {},
    annotations: { readOnlyHint: true, openWorldHint: true },
  },
  async () => API_KEY ? callApi("/signals/weekly") : callApi("/signals/weekly", { auth: false })
);

server.registerTool(
  "get_watchlist",
  {
    title: "Value stocks approaching the buy zone",
    description:
      "Get stocks with strong fundamentals that are approaching, but not yet at, a full margin of safety. " +
      "Returns up to 50 stocks. Each entry includes: ticker, total_score, pe, sector (may be null). " +
      `Useful for building a monitoring list. Costs 3 credits. ${DISCLAIMER}`,
    inputSchema: {},
    annotations: { readOnlyHint: true, openWorldHint: true },
  },
  async () => callApi("/signals/watchlist")
);

server.registerTool(
  "get_screener",
  {
    title: "Full value screener (all 966 stocks)",
    description:
      "Get the full screener output: every stock in the universe with Graham, Buffett and Deep Value scores, " +
      "key metrics and rankings. buy_list contains all buy-qualified stocks with full scoring breakdown. " +
      "watch_list contains top 100 watchlist stocks. Requires a Starter plan or higher. Costs 10 credits. " +
      `Prefer get_weekly_signals for 'top picks' questions. ${DISCLAIMER}`,
    inputSchema: {},
    annotations: { readOnlyHint: true, openWorldHint: true },
  },
  async () => callApi("/screener")
);

server.registerTool(
  "get_status",
  {
    title: "API status",
    description:
      "Check WeeklyMoat API health, when the screener last ran (data_updated field), and which endpoints are available. Free, no key needed.",
    inputSchema: {},
    annotations: { readOnlyHint: true, openWorldHint: true },
  },
  async () => callApi("/status", { auth: false })
);

server.registerTool(
  "get_usage",
  {
    title: "Credit balance",
    description:
      "Check credit balance and recent call history for your WeeklyMoat API key. " +
      "Returns: plan, credits_remaining, credits_total, credits_used, member_since, last_used, calls_by_endpoint, recent_calls.",
    inputSchema: {},
    annotations: { readOnlyHint: true, openWorldHint: true },
  },
  async () => callApi("/usage")
);

const transport = new StdioServerTransport();
await server.connect(transport);
