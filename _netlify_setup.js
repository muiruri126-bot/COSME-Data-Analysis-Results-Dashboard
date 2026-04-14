const https = require('https');
const fs = require('fs');
const path = require('path');

// Read the Netlify auth token from config
const configPath = path.join(process.env.APPDATA || '', 'netlify', 'Config', 'config.json');
let token;
try {
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  token = config.users ? Object.values(config.users)[0]?.auth?.token : null;
} catch(e) {
  // Try alternative config location
  const altPath = path.join(process.env.HOME || process.env.USERPROFILE || '', '.netlify', 'config.json');
  try {
    const config = JSON.parse(fs.readFileSync(altPath, 'utf8'));
    token = config.users ? Object.values(config.users)[0]?.auth?.token : null;
  } catch(e2) {
    console.error('Could not find Netlify token');
    process.exit(1);
  }
}

if (!token) {
  console.error('No Netlify token found in config');
  process.exit(1);
}

const siteId = '8f573234-d01b-4b2b-817f-f80e5412f123';

const payload = JSON.stringify({
  repo: {
    provider: 'github',
    repo: 'muiruri126-bot/COSME-Data-Analysis-Results-Dashboard',
    branch: 'main',
    cmd: 'cd frontend && npm install && npm run build && cd ../backend && npm install && npx prisma generate',
    dir: 'frontend/dist',
    functions_dir: 'netlify/functions'
  }
});

const options = {
  hostname: 'api.netlify.com',
  path: `/api/v1/sites/${siteId}`,
  method: 'PATCH',
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
      const site = JSON.parse(data);
      console.log('SUCCESS! Site updated with GitHub repo');
      console.log('Site URL:', site.ssl_url || site.url);
      console.log('Admin URL:', site.admin_url);
      console.log('Repo:', site.build_settings?.repo_url);
      console.log('Branch:', site.build_settings?.branch);
    } else {
      console.error('Error:', res.statusCode, data);
    }
  });
});

req.on('error', (e) => console.error('Request error:', e.message));
req.write(payload);
req.end();
