"""
WeeklyMoat — Anthropic Claude SDK example (tool use)
pip install anthropic requests
"""
import os, json, requests
import anthropic

API_KEY = os.environ.get("WEEKLYMOAT_API_KEY", "wm_live_YOUR_KEY_HERE")
BASE_URL = "https://weeklymoat.com/api/v1"
WM_HEADERS = {"Authorization": f"Bearer {API_KEY}"}
client = anthropic.Anthropic()

tools = [
    {
        "name": "get_weekly_signals",
        "description": "Get this week's value-investing buy signals using Graham & Buffett criteria, ranked by composite score.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_watchlist",
        "description": "Get stocks approaching the buy zone — strong fundamentals, not yet at full margin of safety.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "check_api_status",
        "description": "Check WeeklyMoat API health and when the screener last ran.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


def call_tool(name: str) -> str:
    if name == "get_weekly_signals":
        return json.dumps(requests.get(f"{BASE_URL}/signals/weekly", headers=WM_HEADERS).json())
    if name == "get_watchlist":
        return json.dumps(requests.get(f"{BASE_URL}/signals/watchlist", headers=WM_HEADERS).json())
    if name == "check_api_status":
        return json.dumps(requests.get(f"{BASE_URL}/status").json())
    return json.dumps({"error": f"Unknown tool: {name}"})


messages = [{"role": "user", "content": "What are the best value stocks this week? Pick your top 3 and explain why."}]

while True:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

    if response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = call_tool(block.name)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
    else:
        for block in response.content:
            if hasattr(block, "text"):
                print(block.text)
        break
