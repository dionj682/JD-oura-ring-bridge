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
      res.writeHead(200);
      res.end(data);
    });
  }).on('error', (e) => {
    res.writeHead(500);
    res.end(JSON.stringify({ error: e.message }));
  });
}).listen(process.env.PORT || 3000);

console.log('Oura bridge running');
