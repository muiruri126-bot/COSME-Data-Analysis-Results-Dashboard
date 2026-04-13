// COSME Visitor Log Backend - Google Apps Script
// Deploy as Web app, access: Anyone, execute as: Me

function getOrCreateSheet() {
  var name = 'COSME Visitor Log';
  var sheetName = 'Visitors';
  var files = DriveApp.getFilesByName(name);
  var ss;
  if (files.hasNext()) {
    ss = SpreadsheetApp.open(files.next());
  } else {
    ss = SpreadsheetApp.create(name);
    var sheet = ss.getActiveSheet();
    sheet.setName(sheetName);
    sheet.appendRow(['Timestamp', 'City', 'Region', 'Country', 'Country Code']);
    sheet.getRange(1, 1, 1, 5).setFontWeight('bold');
  }
  return ss.getSheetByName(sheetName) || ss.getActiveSheet();
}

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
    return ContentService.createTextOutput(JSON.stringify({status: 'ok'}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({status: 'error', message: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

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
    visitors.reverse();
    return ContentService.createTextOutput(JSON.stringify(visitors))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
