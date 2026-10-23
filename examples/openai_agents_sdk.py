"""
WeeklyMoat — OpenAI Agents SDK example
pip install openai requests
"""
import os, json, requests
from openai import OpenAI

API_KEY = os.environ.get("WEEKLYMOAT_API_KEY", "wm_live_YOUR_KEY_HERE")
BASE_URL = "https://weeklymoat.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
client = OpenAI()

# Define tools for function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weekly_signals",
            "description": "Get this week's value-investing buy signals (Graham & Buffett criteria), ranked by score.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_watchlist",
            "description": "Get stocks approaching the buy zone — strong fundamentals, not yet at full margin of safety.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def call_tool(name: str) -> str:
    if name == "get_weekly_signals":
        return json.dumps(requests.get(f"{BASE_URL}/signals/weekly", headers=HEADERS).json())
    if name == "get_watchlist":
        return json.dumps(requests.get(f"{BASE_URL}/signals/watchlist", headers=HEADERS).json())
    return json.dumps({"error": f"Unknown tool: {name}"})


messages = [
    {"role": "system", "content": "You are a value investing assistant. Use WeeklyMoat to answer stock questions."},
    {"role": "user", "content": "What are the top 5 value stocks this week and why are they interesting?"},
]

while True:
    response = client.chat.completions.create(model="gpt-4o", tools=tools, messages=messages)
    msg = response.choices[0].message
    messages.append(msg)

    if msg.tool_calls:
        for tc in msg.tool_calls:
            result = call_tool(tc.function.name)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    else:
        print(msg.content)
        break
