# Getting the app onto your phone

**Recommendation: GitHub Pages.** It gives you a real `https://` URL, which is the
only way the app can install to your home screen and work offline. A free GitHub
account is enough.

Everything below is done once. After that, updating the app is a single `git push`.

---

## Step 1 — Create the repository

1. Go to <https://github.com/new>
2. Repository name: `Workouts`
3. Visibility: **Public** ← required for free GitHub Pages on a repository
4. Do **not** tick "Add a README" — you already have one
5. Create repository

> **Why public is fine here:** your training log lives in your phone's browser
> storage, not in this repository. `tracker/log.csv` is listed in `.gitignore`
> specifically so it never gets committed. Nothing personal is ever pushed.

## Step 2 — Push this folder

GitHub shows you these commands after creating the repo. It's already initialised
locally, so you only need the last three:

```bash
cd ~/Documents/Projects/Workouts
git remote add origin https://github.com/<your-username>/Workouts.git
git branch -M main
git push -u origin main
```

The first push opens a browser window to authenticate. No password typing, no
`gh` CLI needed.

## Step 3 — Turn on Pages

1. In the repo: **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **main**, folder: **/ (root)**
4. Save

Wait ~60 seconds. Your app is then live at:

```
https://<your-username>.github.io/Workouts/
```

`index.html` at the root redirects straight to the app. You can also link directly
to `https://<your-username>.github.io/Workouts/app/`.

## Step 4 — Install it on your phone

**iPhone (iOS):** open the URL in **Safari** (must be Safari, not Chrome) → tap the
**Share** button → **Add to Home Screen** → Add.

**Android:** open the URL in Chrome → **⋮** menu → **Install app** (or "Add to home
screen").

You now get a real app icon, no browser chrome, and it works with no signal.

---

## Day to day

- **Log** on the Today tab. Weight boxes pre-fill with your last entry — usually you
  just tap **+** for 2.5 kg and hit **Log**.
- **Undo** appears in the toast right after logging, in case you fat-finger it.
- **Data → Download CSV** every week or two. That is your backup and the only way to
  recover if you ever clear Safari's website data.
- Rest timer starts itself on your first log of the session.

## Optional: your log on every device

Hosting puts the *app* on every device. It does not put your *data* there — entries
live in the browser that created them, so your phone and laptop would otherwise be
two separate logs. This part fixes that, and it's free.

The app stays offline-first: logging never waits on the network, so a basement gym
with no signal works exactly like being at home. It reconciles with the database
whenever it next has a connection.

### 1. Create a Supabase project

Sign up at <https://supabase.com>, create a project (any name, nearest region) and
wait for it to finish provisioning. Free tier is plenty — your log will be a few
hundred rows a year.

### 2. Create the table

Project → **SQL Editor** → New query → paste the whole of
[`supabase/schema.sql`](supabase/schema.sql) → **Run**.

That creates the table, an index, and row-level security policies. Every policy is
scoped to `auth.uid() = user_id`, so a signed-in user can only ever read or write
their own rows. The `anon` role is granted nothing at all — without this, the
publishable key in a public web page would expose your whole log.

### 3. Allow your URL to receive the sign-in link

**This is the step that silently breaks if you skip it.** Authentication →
**URL Configuration**:

- **Site URL**: `https://<your-username>.github.io/Workouts/app/`
- **Redirect URLs**: add both
  - `https://<your-username>.github.io/Workouts/app/`
  - `http://localhost:8765/` (so you can test on your Mac)

Supabase only redirects to URLs on this list. If it's missing, the magic link dumps
you on the project's default Site URL and nothing happens.

### 4. Connect the app

Project → **Settings → API Keys**. Copy:

- **Project URL** — looks like `https://abcdefgh.supabase.co`
- **Publishable key** — `sb_publishable_…` (older projects: the `anon` key, `eyJ…`)

In the app: **Data → Sync across devices**, paste both, tap **Save & connect**.
Then tap **Test connection** — you want "Connection OK".

### 5. Sign in

Enter your email, tap **Email me a sign-in link**, and open the link **on the device
you're setting up**. Repeat step 4–5 on every device and they all share one log.

The header shows a small dot: green when synced, amber when changes are waiting,
red on an error. Tap through to **Data** for the detail.

### Troubleshooting

| Symptom | Cause |
|---|---|
| "Test connection" fails, `relation does not exist` | The table isn't exposed to the API. Check Settings → Data API → Exposed tables, and re-run the SQL. |
| `permission denied for table entries` | The `grant` statements didn't run. Re-run `supabase/schema.sql`. |
| Sign-in email never arrives | Supabase's built-in sender is rate-limited (a few per hour) and won't deliver to some domains. Wait, or configure your own SMTP under Authentication → Emails. |
| Magic link does nothing | The redirect URL isn't on the allowlist — see step 3. |
| Two devices disagree | Last-write-wins per entry by timestamp, so they settle on the newest edit. Clock skew between devices decides close calls. |
| Project stopped responding after a week away | Free projects pause after 7 days of inactivity. Open the dashboard and restore it; no data is lost. |

### What sync does *not* do

- It is **not a backup**. Keep exporting CSV now and then; a cloud table you can
  accidentally wipe is not a backup either.
- Deletions propagate, and there is no undo across devices. The Undo button in the
  toast covers the immediate mistake only.
- `tracker/track.py` still reads a local CSV. Sync doesn't change that — export and
  drop the file into `tracker/` as before.


## Updating the app

```bash
# edit app/index.html, then
git add -A && git commit -m "tweak the app" && git push
```

Pages redeploys automatically. Because the service worker fetches the page
network-first, the new version lands on the next launch — but if you ever change
the **icons** or the shell file list, bump `CACHE = "workouts-v1"` in
`app/sw.js` to something new, or phones will keep serving the old ones.

## Reconnecting the phone data to your terminal

Export the CSV on your phone, AirDrop or email it to yourself, drop it into
`tracker/`, and the terminal commands work on the same data:

```bash
cp ~/Downloads/workouts-2026-09-21.csv tracker/log.csv
python3 tracker/track.py progress
```

Import is intentionally merge-only: the app skips any row that exactly matches one
you already have, so re-importing the same file twice is harmless.

---

## Alternative: no GitHub account at all

Fine for testing, but you lose offline mode and the proper home-screen install,
because there is no `https://`.

```bash
cd ~/Documents/Projects/Workouts
python3 -m http.server 8765 --directory app
ipconfig getifaddr en0        # e.g. 192.168.1.42
```

With your phone on the **same Wi-Fi**, open `http://192.168.1.42:8765/`. Add to
home screen still works on both platforms, but the service worker is skipped
(plain HTTP is not a secure context), so it will not run offline and the page can
fail to load if your Mac is asleep or the IP changes.

For a permanent no-account option you'd need a tunnel like Tailscale or
Cloudflare Tunnel — GitHub Pages is less to maintain.
