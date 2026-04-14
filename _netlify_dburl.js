const https = require('https');
const fs = require('fs');
const path = require('path');

const configPath = path.join(process.env.APPDATA || '', 'netlify', 'Config', 'config.json');
let token;
try {
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  token = config.users ? Object.values(config.users)[0]?.auth?.token : null;
} catch(e) {
  console.error('Could not find Netlify token');
  process.exit(1);
}

const siteId = '8f573234-d01b-4b2b-817f-f80e5412f123';
const dbUrl = 'postgresql://neondb_owner:npg_IgVK9buQki8f@ep-calm-glade-alqgx226.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require';

const envVars = [
  { key: 'DATABASE_URL', values: [{ value: dbUrl, context: 'all' }] },
];

const payload = JSON.stringify(envVars);
const options = {
  hostname: 'api.netlify.com',
  path: `/api/v1/accounts/muiruri126/env?site_id=${siteId}`,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'Content-Length': Buffer.byteLength(payload)
  }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      console.log('✓ DATABASE_URL set on Netlify');
    } else {
      console.error('✗ Failed:', res.statusCode, data.substring(0, 300));
    }
  });
});
req.on('error', (e) => console.error('Error:', e.message));
req.write(payload);
req.end();
