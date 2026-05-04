const https = require('https');
const GITHUB_URL = 'https://raw.githubusercontent.com/dionj682/JD-oura-ring-bridge/main/oura_data.json';

require('http').createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json');

  https.get(GITHUB_URL, (githubRes) => {
    let data = '';
    githubRes.on('data', chunk => data += chunk);
    githubRes.on('end', () => {
      try {
        const raw = JSON.parse(data);

        const filtered = {
          date: raw.date,
          sleep: {
            score: raw.sleep?.score ?? null
          },
          readiness: {
            score: raw.readiness?.score ?? null
          },
          activity: {
            date: raw.activity?.date ?? null,
            score: raw.activity?.score ?? null,
            steps: raw.activity?.steps ?? null,
            activeCalories: raw.activity?.activeCalories ?? null
          },
          rhr: raw.rhr ?? null,
          spo2: raw.spo2 ?? null,
          stress: {
            score: raw.stress?.score ?? null
          },
          resilience: {
            level: raw.resilience?.level ?? null,
            sleepRecovery: raw.resilience?.sleepRecovery ?? null,
            daytimeRecovery: raw.resilience?.daytimeRecovery ?? null,
            stress: raw.resilience?.stress ?? null
          }
        };

        res.writeHead(200);
        res.end(JSON.stringify(filtered, null, 2));
      } catch (e) {
        res.writeHead(500);
        res.end(JSON.stringify({ error: 'Failed to parse data: ' + e.message }));
      }
    });
  }).on('error', (e) => {
    res.writeHead(500);
    res.end(JSON.stringify({ error: e.message }));
  });
}).listen(process.env.PORT || 3000);

console.log('Oura bridge running');
