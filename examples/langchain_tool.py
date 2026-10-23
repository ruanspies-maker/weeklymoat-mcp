"""
WeeklyMoat — LangChain tool example
pip install langchain langchain-openai requests
"""
import os, requests
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

API_KEY = os.environ.get("WEEKLYMOAT_API_KEY", "wm_live_YOUR_KEY_HERE")
BASE_URL = "https://weeklymoat.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


@tool
def get_weekly_signals() -> dict:
    """Get this week's top value-investing buy signals from WeeklyMoat. 
    Returns stocks meeting Graham & Buffett criteria, ranked by composite score."""
    r = requests.get(f"{BASE_URL}/signals/weekly", headers=HEADERS)
    r.raise_for_status()
    return r.json()


@tool
def get_watchlist() -> dict:
    """Get stocks approaching the buy zone from WeeklyMoat.
    These have strong fundamentals but haven't yet reached a full margin of safety."""
    r = requests.get(f"{BASE_URL}/signals/watchlist", headers=HEADERS)
    r.raise_for_status()
    return r.json()


@tool
def check_api_status() -> dict:
    """Check WeeklyMoat API health and when data was last updated."""
    return requests.get(f"{BASE_URL}/status").json()


tools = [get_weekly_signals, get_watchlist, check_api_status]

llm = ChatOpenAI(model="gpt-4o", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a value investing assistant. Use WeeklyMoat tools to answer questions about stocks."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = executor.invoke({"input": "What are the best value stocks this week? Give me the top 5 with their scores."})
print(result["output"])
