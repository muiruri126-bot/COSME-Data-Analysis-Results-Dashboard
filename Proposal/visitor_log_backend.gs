/**
 * COSME Platform — Visitor Log Backend (Google Apps Script)
 * 
 * SETUP INSTRUCTIONS:
 * 1. Go to https://script.google.com and create a new project
 * 2. Replace the default code with this entire file
 * 3. Click "Deploy" → "New deployment"
 * 4. Select type: "Web app"
 * 5. Set "Execute as": Me (your account)
 * 6. Set "Who has access": Anyone
 * 7. Click "Deploy" and copy the Web App URL
 * 8. Paste the URL into COSME_Phase2_Design_Platform.html where it says:
 *      var VISITOR_LOG_URL = '';
 *    → var VISITOR_LOG_URL = 'https://script.google.com/macros/s/YOUR_ID/exec';
 * 
 * The script automatically creates a "Visitor Log" spreadsheet in your
 * Google Drive on first use. All visitor data is stored there.
 */

var SHEET_NAME = 'Visitors';
var SPREADSHEET_NAME = 'COSME Visitor Log';

function getOrCreateSheet() {
  var files = DriveApp.getFilesByName(SPREADSHEET_NAME);
  var ss;
  if (files.hasNext()) {
    ss = SpreadsheetApp.open(files.next());
  } else {
    ss = SpreadsheetApp.create(SPREADSHEET_NAME);
    var sheet = ss.getActiveSheet();
    sheet.setName(SHEET_NAME);
    sheet.appendRow(['Timestamp', 'City', 'Region', 'Country', 'Country Code']);
    sheet.getRange(1, 1, 1, 5).setFontWeight('bold');
  }
  return ss.getSheetByName(SHEET_NAME) || ss.getActiveSheet();
}

// Handle POST — log a new visitor
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = getOrCreateSheet();
    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.city || '',
      data.region || '',
      data.country || '',
      data.country_code || ''
    ]);
    return ContentService.createTextOutput(JSON.stringify({ status: 'ok' }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Handle GET — return all visitors as JSON
function doGet(e) {
  try {
    var sheet = getOrCreateSheet();
    var data = sheet.getDataRange().getValues();
    var headers = data[0];
    var visitors = [];
    for (var i = 1; i < data.length; i++) {
      var row = {};
      for (var j = 0; j < headers.length; j++) {
        row[headers[j].toLowerCase().replace(/\s+/g, '_')] = data[i][j];
      }
      visitors.push(row);
    }
    // Return newest first
    visitors.reverse();
    return ContentService.createTextOutput(JSON.stringify(visitors))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
