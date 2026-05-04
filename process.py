import json
import datetime
import subprocess
import os

TODAY = datetime.date.today().strftime("%Y-%m-%d")
YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

def fetch(endpoint, start, end):
    token = os.environ.get("OURA_TOKEN")
    url = f"https://api.ouraring.com/v2/usercollection/{endpoint}?start_date={start}&end_date={end}"
    result = subprocess.run(
        ["curl", "-s", url, "-H", f"Authorization: Bearer {token}"],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except:
        return {}

print("Fetching Oura endpoints...")

daily_sleep  = fetch("daily_sleep", TODAY, TODAY)
readiness    = fetch("daily_readiness", TODAY, TODAY)
activity     = fetch("daily_activity", TODAY, TODAY)
stress       = fetch("daily_stress", TODAY, TODAY)
resilience   = fetch("daily_resilience", TODAY, TODAY)
spo2         = fetch("daily_spo2", TODAY, TODAY)

# --- Parse daily sleep ---
ds = daily_sleep.get('data', [{}])[0]

# --- Parse readiness ---
r = readiness.get('data', [{}])[0]
r_contributors = r.get('contributors', {})

# --- Parse activity (today only) ---
activity_data = activity.get('data', [])
a = next((x for x in activity_data if x.get('day') == TODAY), {})
# Fallback to yesterday if today not yet available
if not a:
    activity_today = fetch("daily_activity", YESTERDAY, YESTERDAY)
    a = activity_today.get('data', [{}])[0]

# --- Parse stress ---
st = stress.get('data', [{}])[0]

# --- Parse resilience ---
res = resilience.get('data', [{}])[0]

# --- Parse SpO2 ---
sp = spo2.get('data', [{}])[0]

# --- Build output ---
output = {
    "date": TODAY,
    "sleep": {
        "score": ds.get('score')
    },
    "readiness": {
        "score": r.get('score')
    },
    "activity": {
        "date": a.get('day'),
        "score": a.get('score'),
        "steps": a.get('steps'),
        "activeCalories": a.get('active_calories')
    },
    "rhr": r_contributors.get('resting_heart_rate'),
    "spo2": sp.get('spo2_percentage', {}).get('average') if sp else None,
    "stress": {
        "score": st.get('stress_high')
    },
    "resilience": {
        "level": res.get('level'),
        "sleepRecovery": res.get('contributors', {}).get('sleep_recovery'),
        "daytimeRecovery": res.get('contributors', {}).get('daytime_recovery'),
        "stress": res.get('contributors', {}).get('stress')
    }
}

with open('oura_data.json', 'w') as f:
    json.dump(output, f, indent=2)

print("OUTPUT:", json.dumps(output, indent=2))
print("Done.")
