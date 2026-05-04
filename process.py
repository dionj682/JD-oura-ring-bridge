import json
import datetime
import subprocess

TODAY = datetime.date.today().strftime("%Y-%m-%d")
YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

def fetch(endpoint, start, end):
    import os
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

print("Fetching all Oura endpoints...")

daily_sleep     = fetch("daily_sleep", TODAY, TODAY)
sleep_sessions  = fetch("sleep", YESTERDAY, TODAY)
readiness       = fetch("daily_readiness", TODAY, TODAY)
activity        = fetch("daily_activity", YESTERDAY, TODAY)
stress          = fetch("daily_stress", TODAY, TODAY)
resilience      = fetch("daily_resilience", TODAY, TODAY)
spo2            = fetch("daily_spo2", TODAY, TODAY)

# --- Parse daily sleep ---
ds = daily_sleep.get('data', [{}])[0]

# --- Parse sleep session (longest) ---
sessions = sleep.get('data', [])
# Prefer session filed under today, fallback to most recent
today_sessions = [x for x in sessions if x.get('day') == TODAY]
if today_sessions:
    s = max(today_sessions, key=lambda x: x.get('total_sleep_duration', 0))
elif sessions:
    # Sort by bedtime_end to get most recently completed sleep
    s = max(sessions, key=lambda x: x.get('bedtime_end', ''))
else:
    s = {}

# --- Parse readiness ---
r = readiness.get('data', [{}])[0]
r_contributors = r.get('contributors', {})

# --- Parse activity (most recent) ---
a = activity.get('data', [{}])[-1] if activity.get('data') else {}

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
        "score": ds.get('score'),
        "contributors": ds.get('contributors', {}),
        "hrv": s.get('average_hrv'),
        "restingHeartRate": s.get('lowest_heart_rate'),
        "deepSleepSeconds": s.get('deep_sleep_duration'),
        "remSleepSeconds": s.get('rem_sleep_duration'),
        "lightSleepSeconds": s.get('light_sleep_duration'),
        "totalSleepSeconds": s.get('total_sleep_duration'),
        "totalBedTimeSeconds": s.get('time_in_bed'),
        "efficiency": s.get('efficiency'),
        "latencySeconds": s.get('latency'),
        "restlessPeriods": s.get('restless_periods'),
        "restfulnessScore": ds.get('contributors', {}).get('restfulness'),
        "awakeSeconds": s.get('awake_time'),
        "sleepStart": s.get('bedtime_start'),
        "sleepEnd": s.get('bedtime_end')
    },
    "readiness": {
        "score": r.get('score'),
        "temperatureDeviation": r.get('temperature_deviation'),
        "temperatureTrendDeviation": r.get('temperature_trend_deviation'),
        "contributors": {
            "activityBalance": r_contributors.get('activity_balance'),
            "bodyTemperature": r_contributors.get('body_temperature'),
            "hrvBalance": r_contributors.get('hrv_balance'),
            "previousDayActivity": r_contributors.get('previous_day_activity'),
            "previousNight": r_contributors.get('previous_night'),
            "recoveryIndex": r_contributors.get('recovery_index'),
            "restingHeartRate": r_contributors.get('resting_heart_rate'),
            "sleepBalance": r_contributors.get('sleep_balance'),
            "sleepRegularity": r_contributors.get('sleep_regularity')
        }
    },
    "activity": {
        "date": a.get('day'),
        "score": a.get('score'),
        "steps": a.get('steps'),
        "activeCalories": a.get('active_calories'),
        "totalCalories": a.get('total_calories'),
        "targetCalories": a.get('target_calories'),
        "meetDailyTargets": a.get('meet_daily_targets'),
        "moveEveryHour": a.get('move_every_hour'),
        "recoveryTime": a.get('recovery_time'),
        "stayActive": a.get('stay_active'),
        "trainingFrequency": a.get('training_frequency'),
        "trainingVolume": a.get('training_volume'),
        "equivalentWalkingDistance": a.get('equivalent_walking_distance'),
        "highActivitySeconds": a.get('high_activity_time'),
        "mediumActivitySeconds": a.get('medium_activity_time'),
        "lowActivitySeconds": a.get('low_activity_time'),
        "sedentarySeconds": a.get('sedentary_time'),
        "restSeconds": a.get('rest_time')
    },
    "stress": {
        "stressHigh": st.get('stress_high'),
        "recoveryHigh": st.get('recovery_high'),
        "daySum": st.get('day_summary')
    },
    "resilience": {
        "score": res.get('level'),
        "sleepRecovery": res.get('contributors', {}).get('sleep_recovery'),
        "daytimeRecovery": res.get('contributors', {}).get('daytime_recovery'),
        "stress": res.get('contributors', {}).get('stress')
    },
    "spo2": {
        "average": sp.get('spo2_percentage', {}).get('average') if sp else None
    },
    "raw": {
        "daily_sleep": daily_sleep,
        "sleep_sessions": sleep_sessions,
        "readiness": readiness,
        "activity": activity,
        "stress": stress,
        "resilience": resilience,
        "spo2": spo2
    }
}

with open('oura_data.json', 'w') as f:
    json.dump(output, f, indent=2)

print("SLEEP SESSIONS RAW:", json.dumps(sleep_sessions, indent=2))
print("OUTPUT:", json.dumps({k: v for k, v in output.items() if k != 'raw'}, indent=2))
print("Done.")
