# NbS Outputs tab — administrator notes

The **Project Outputs → NbS Interventions** tab is read-only by default. Signing
in unlocks editing of the *Achieved* and *Notes* figures.

## Signing in

Use the **same username and password as the Analytics tab**. The two share one
session flag (`sessionStorage.analytics_auth`), so:

- signing in on either tab unlocks both;
- signing out of either signs out of both;
- the session ends when the browser tab is closed.

## What editing does

- Click an *Achieved* or *Notes* cell and type. Enter saves, Escape cancels.
- Saves go to Firebase at `nbsOutputs/overrides/<row number>`, with the username
  and a timestamp.
- Edits are visible to **every viewer**, not just you.
- An edited row gets a blue dot next to its row number, and `% of target`
  recalculates from the new figure.
- The workbook figures remain in the page as the fallback, so deleting an
  override in Firebase restores the original number.

If saves silently fail, the Realtime Database rules are blocking the write. Add:

```json
"nbsOutputs": {
  "overrides": { ".read": true, ".write": true }
}
```

alongside the existing `analytics`, `presence` and `visits` rules. Do not put
`.read`/`.write` at the top level — Realtime Database rules cascade downwards and
cannot be revoked further down.

## What this sign-in is and is not

**It unlocks the editing interface. It is not a security boundary.**

This dashboard is a static page served from public GitHub Pages. The username and
the password hash are in the page source, the check runs in the visitor's own
browser, and the session flag is a value anyone can set from the developer
console. Anyone determined to edit the figures can, regardless of this gate.

Two consequences worth knowing:

1. **Nothing confidential may be placed behind it.** This is why the SharePoint
   and OneDrive source locations are not in this file at all. The Sources panel
   shows the document names and what each was used for; the locations stay in the
   `Sources` sheet of `COSME_Outputs_Data.xlsx`. Putting them in the page behind
   the sign-in would have looked like protection without being protection.

2. **Published figures can be altered by anyone who finds the database.** The
   override path has to be world-writable for the gate to work as built. For a
   donor-reporting dashboard that may not be acceptable, in which case the fix is
   Firebase Authentication — real accounts, with a `".write": "auth != null"`
   rule that Firebase enforces on its own servers rather than in the browser.

Also note the Analytics credentials currently in the page are the defaults
(`admin`, with the SHA-256 of `password`). That hash is in every rainbow table.
Changing it is a one-line edit to `ANALYTICS_CREDENTIALS.passwordHash` in
`Women_Survey_Professional_Dashboard.html` — worth doing now that the same
credentials also unlock editing of the results figures.

## Refreshing from a new workbook

The table is generated from the `NBS_ROWS` array in
`Women_Survey_Professional_Dashboard.html`, transcribed cell-for-cell from
`COSME_Outputs_Data.xlsx`. A new workbook means regenerating that array, not
rewriting the tab.
