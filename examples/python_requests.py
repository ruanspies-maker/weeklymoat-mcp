"""
WeeklyMoat API — Python requests example
pip install requests
"""
import requests

API_KEY = "wm_live_YOUR_KEY_HERE"
BASE_URL = "https://weeklymoat.com/api/v1"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Check API status (no key needed)
status = requests.get(f"{BASE_URL}/status").json()
print(f"API status: {status['status']}, last run: {status['data_updated']}")

# Get this week's buy signals
r = requests.get(f"{BASE_URL}/signals/weekly", headers=headers)
r.raise_for_status()
data = r.json()

print(f"\nThis week's buy signals ({data['total_screened']} stocks screened):")
for s in data["buy_signals"]:
    mos = f"{s['margin_of_safety']:.0%}" if s.get("margin_of_safety") else "n/a"
    print(f"  {s['ticker']:12s}  score={s['total_score']}  P/E={s.get('pe', 'n/a'):.1f}  MoS={mos}")
    print(f"             signals: {', '.join(s.get('moat_signals', []))}")

print(f"\nCredits remaining: {data['_meta']['credits_remaining']}")

# Get watchlist
r = requests.get(f"{BASE_URL}/signals/watchlist", headers=headers)
wl = r.json()
print(f"\nWatchlist ({len(wl['watch_list'])} stocks approaching buy zone):")
for s in wl["watch_list"][:5]:
    print(f"  {s['ticker']:12s}  score={s['total_score']}  P/E={s.get('pe', 'n/a'):.1f}")

# Check usage
usage = requests.get(f"{BASE_URL}/usage", headers=headers).json()
print(f"\nPlan: {usage['plan']}  Credits used: {usage['credits_used']}/{usage['credits_total']}")
