"""
WeeklyMoat — CrewAI tool example
pip install crewai requests
"""
import os, requests
from crewai.tools import BaseTool
from crewai import Agent, Task, Crew
from pydantic import BaseModel

API_KEY = os.environ.get("WEEKLYMOAT_API_KEY", "wm_live_YOUR_KEY_HERE")
BASE_URL = "https://weeklymoat.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


class WeeklySignalsTool(BaseTool):
    name: str = "get_weekly_signals"
    description: str = (
        "Get this week's top value-investing buy signals (Graham & Buffett criteria). "
        "Returns ticker, total_score, P/E, P/B, ROE, margin_of_safety, moat_signals."
    )

    def _run(self) -> str:
        data = requests.get(f"{BASE_URL}/signals/weekly", headers=HEADERS).json()
        lines = [f"WeeklyMoat buy signals ({data['total_screened']} stocks screened, {data['watch_count']} on watchlist):"]
        for s in data.get("buy_signals", []):
            mos = f"{s['margin_of_safety']:.0%}" if s.get("margin_of_safety") else "n/a"
            lines.append(f"  {s['ticker']} | score={s['total_score']} | P/E={s.get('pe','?'):.1f} | MoS={mos} | {', '.join(s.get('moat_signals',[]))}")
        return "\n".join(lines)


class WatchlistTool(BaseTool):
    name: str = "get_watchlist"
    description: str = "Get stocks approaching the buy zone — strong fundamentals, not yet at full margin of safety."

    def _run(self) -> str:
        data = requests.get(f"{BASE_URL}/signals/watchlist", headers=HEADERS).json()
        lines = ["Watchlist (approaching buy zone):"]
        for s in data.get("watch_list", [])[:20]:
            lines.append(f"  {s['ticker']} | score={s['total_score']} | P/E={s.get('pe','?'):.1f}")
        return "\n".join(lines)


analyst = Agent(
    role="Value Investing Analyst",
    goal="Identify the best value stocks using Graham & Buffett criteria",
    backstory="You are a disciplined value investor trained on Graham's Security Analysis and Buffett's letters.",
    tools=[WeeklySignalsTool(), WatchlistTool()],
    verbose=True,
)

task = Task(
    description="Get this week's buy signals and watchlist. Identify the 3 most compelling opportunities with your reasoning.",
    expected_output="A ranked list of 3 stocks with investment thesis for each.",
    agent=analyst,
)

crew = Crew(agents=[analyst], tasks=[task], verbose=True)
result = crew.kickoff()
print(result)
