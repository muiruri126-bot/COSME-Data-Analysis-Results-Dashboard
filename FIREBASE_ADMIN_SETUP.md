# NbS Outputs tab — administrator setup

The **Project Outputs → NbS Interventions** tab is read-only for everyone by
default. An administrator who signs in can edit the *Achieved* and *Notes*
figures and can see where each source document lives.

Two things have to be configured in the Firebase console before the admin side
works. Until then the tab still works perfectly as a read-only dashboard.

## Why the source locations are not in this repo

This dashboard is a static page served from public GitHub Pages. **Anything
written into the HTML is readable by anyone** — "view source" is enough, and a
JavaScript check cannot prevent it. Hiding the SharePoint and OneDrive paths
behind an admin toggle in the page would have looked like protection without
being protection.

So the paths are not in the published file at all. They live in the Firebase
Realtime Database under `nbsOutputs/sourceLocations`, where the database rules —
which are enforced on Firebase's servers, not in the browser — release them only
to a signed-in user. The page shows "Location restricted" to everyone else.

## 1. Enable email/password sign-in

Firebase console → **Authentication** → *Sign-in method* → enable
**Email/Password**, then **Users** → *Add user* and create the administrator
account. Create one account per administrator; there is no shared password.

## 2. Set the database rules

Firebase console → **Realtime Database** → *Rules*. Replace the rules with:

```json
{
  "rules": {
    "analytics": { ".read": true, ".write": true },
    "presence":  { ".read": true, ".write": true },
    "visits":    { ".read": true, ".write": true },

    "nbsOutputs": {
      "sourceLocations": {
        ".read": "auth != null",
        ".write": "auth != null"
      },
      "overrides": {
        ".read": true,
        ".write": "auth != null"
      }
    }
  }
}
```

**Do not add `.read` or `.write` at the top level.** Realtime Database rules
cascade downwards and cannot be revoked further down: a `".read": true` at the
root would make `sourceLocations` world-readable again, silently.

The three existing nodes stay public because the visitor-presence and analytics
code already writes to them without signing in.

## 3. Load the source locations

Import the source paths to `nbsOutputs/sourceLocations` (Realtime Database →
*Import JSON*, with `nbsOutputs/sourceLocations` selected). The keys `s0`–`s4`
match the order of the rows in the Sources table.

The file is deliberately **not** committed to this repo. Ask Ben for
`fbloc.json`, or retype the five locations from the `Sources` sheet of
`COSME_Outputs_Data.xlsx`.

## How editing behaves

- Admins edit the *Achieved* and *Notes* cells directly in the table.
- Saves go to `nbsOutputs/overrides/<row number>` with the editor's email and a
  timestamp, and are visible to **every** viewer immediately.
- An edited row is marked with a blue dot next to its row number.
- `% of target` recalculates from the edited figure.
- The published workbook figures stay in the page as the fallback, so clearing
  an override in Firebase restores the original number.

## Refreshing from a new workbook

The table is generated from the `NBS_ROWS` array in
`Women_Survey_Professional_Dashboard.html`, transcribed cell-for-cell from
`COSME_Outputs_Data.xlsx`. A new workbook means regenerating that array, not
rewriting the tab.
