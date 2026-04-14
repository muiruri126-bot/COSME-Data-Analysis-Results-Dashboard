const https = require('https');
const fs = require('fs');
const path = require('path');

// Read the Netlify auth token
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

const envVars = [
  { key: 'NODE_ENV', values: [{ value: 'production', context: 'all' }] },
  { key: 'JWT_SECRET', values: [{ value: 'f10d2ec6506e0d22374228570f0b66a40e49944a659ccc564e5157f3daa3f485d8e25c77bb8986aa1bdb49805fb56319', context: 'all' }] },
  { key: 'CORS_ORIGIN', values: [{ value: 'https://cosme-procurement.netlify.app', context: 'all' }] },
  { key: 'VITE_API_URL', values: [{ value: '/api/v1', context: 'all' }] },
];

function setEnvVars(vars) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(vars);
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
          const result = JSON.parse(data);
          result.forEach(v => console.log(`✓ Set ${v.key}`));
          resolve();
        } else {
          console.error(`✗ Failed: ${res.statusCode} ${data.substring(0, 300)}`);
          resolve();
        }
      });
    });
    req.on('error', (e) => { console.error(`✗ Error:`, e.message); resolve(); });
    req.write(payload);
    req.end();
  });
}

async function main() {
  await setEnvVars(envVars);
  console.log('\nDone! DATABASE_URL still needs to be set after creating cloud DB.');
}

main();
