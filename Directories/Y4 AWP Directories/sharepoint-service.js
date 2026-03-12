const msal = require('@azure/msal-node');
const { Client } = require('@microsoft/microsoft-graph-client');
const XLSX = require('xlsx');
require('dotenv').config();

class SharePointService {
    constructor() {
        this.msalConfig = {
            auth: {
                clientId: process.env.AZURE_CLIENT_ID,
                clientSecret: process.env.AZURE_CLIENT_SECRET,
                authority: `https://login.microsoftonline.com/${process.env.AZURE_TENANT_ID}`,
            },
        };
        this.cca = new msal.ConfidentialClientApplication(this.msalConfig);
        this.graphClient = null;
    }

    async authenticate() {
        const tokenRequest = {
            scopes: ['https://graph.microsoft.com/.default'],
        };

        try {
            const response = await this.cca.acquireTokenByClientCredential(tokenRequest);
            this.graphClient = Client.init({
                authProvider: (done) => {
                    done(null, response.accessToken);
                },
            });
            console.log('[SharePoint] Authenticated successfully');
            return true;
        } catch (error) {
            console.error('[SharePoint] Authentication failed:', error.message);
            return false;
        }
    }

    async fetchExcelData() {
        if (!this.graphClient) {
            const authenticated = await this.authenticate();
            if (!authenticated) {
                throw new Error('SharePoint authentication failed. Check your Azure AD credentials in .env');
            }
        }

        try {
            // Try fetching via sharing link
            const shareUrl = process.env.SHAREPOINT_SHARE_URL;
            if (shareUrl) {
                return await this.fetchViaShareLink(shareUrl);
            }

            // Fallback: fetch via drive path
            return await this.fetchViaDrivePath();
        } catch (error) {
            console.error('[SharePoint] Error fetching data:', error.message);
            throw error;
        }
    }

    async fetchViaShareLink(shareUrl) {
        // Encode the sharing URL for Graph API
        const encodedUrl = Buffer.from(shareUrl).toString('base64')
            .replace(/=/g, '').replace(/\//g, '_').replace(/\+/g, '-');
        const shareToken = `u!${encodedUrl}`;

        const driveItem = await this.graphClient
            .api(`/shares/${shareToken}/driveItem`)
            .get();

        const content = await this.graphClient
            .api(`/shares/${shareToken}/driveItem/content`)
            .responseType('arraybuffer')
            .get();

        const workbook = XLSX.read(content, { type: 'buffer' });
        return this.parseWorkbook(workbook);
    }

    async fetchViaDrivePath() {
        const siteParts = process.env.SHAREPOINT_SITE.split('.');
        const userPath = process.env.SHAREPOINT_FILE_PATH;

        const content = await this.graphClient
            .api(`/sites/${process.env.SHAREPOINT_SITE}:/`)
            .get();

        const driveContent = await this.graphClient
            .api(`/sites/${content.id}/drive/root:${userPath}:/content`)
            .responseType('arraybuffer')
            .get();

        const workbook = XLSX.read(driveContent, { type: 'buffer' });
        return this.parseWorkbook(workbook);
    }

    parseWorkbook(workbook) {
        const results = {};
        for (const sheetName of workbook.SheetNames) {
            const sheet = workbook.Sheets[sheetName];
            const data = XLSX.utils.sheet_to_json(sheet, { defval: '' });
            results[sheetName] = data;
        }
        return results;
    }
}

module.exports = SharePointService;
