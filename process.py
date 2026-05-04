import json
import datetime

with open('daily_sleep_raw.json') as f:
    daily_sleep = json.load(f)
with open('sleep_raw.json') as f:
    sleep = json.load(f)
with open('readiness_raw.json') as f:
    readiness = json.load(f)
with open('activity_raw.json') as f:
    activity = json.load(f)

ds = daily_sleep['data'][0] if daily_sleep.get('data') else {}

sleep_sessions = sleep.get('data', [])
s = max(sleep_sessions, key=lambda x: x.get('total_sleep_duration', 0)) if sleep_sessions else {}

r = readiness['data'][0] if readiness.get('data') else {}
a = activity['data'][-1] if activity.get('data') else {}

contributors = r.get('contributors', {})

output = {
    "date": str(datetime.date.today()),
    "sleep": {
        "score": ds.get('score'),
        "hrv": s.get('average_hrv'),
        "restingHeartRate": s.get('lowest_heart_rate'),
        "deepSleepSeconds": s.get('deep_sleep_duration'),
        "remSleepSeconds": s.get('rem_sleep_duration'),
        "restfulnessScore": ds.get('contributors', {}).get('restfulness'),
        "totalSleepSeconds": s.get('total_sleep_duration'),
        "efficiency": s.get('efficiency'),
        "latencySeconds": s.get('sleep_latency')
    },
    "readiness": {
        "score": r.get('score'),
        "hrvBalance": contributors.get('hrv_balance'),
        "bodyTemperature": contributors.get('body_temperature'),
        "restingHeartRate": contributors.get('resting_heart_rate'),
        "activityBalance": contributors.get('activity_balance'),
        "recoveryIndex": contributors.get('recovery_index')
    },
    "activity": {
        "date": a.get('day'),
        "steps": a.get('steps'),
        "activeCalories": a.get('active_calories'),
        "score": a.get('score')
    }
}

with open('oura_data.json', 'w') as f:
    json.dump(output, f, indent=2)

print("OUTPUT:", json.dumps(output, indent=2))
