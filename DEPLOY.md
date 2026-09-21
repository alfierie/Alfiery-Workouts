# Setup, start to finish

Follow these in order. Steps 1–5 put the app on your phone (~10 minutes, GitHub
account required). Steps 6–13 also put your log on every device (~10 minutes,
Supabase account required, optional).

**You need:** a free GitHub account, a free Supabase account, and your phone.

Everything here is done once. After that, updating the app is a single `git push`.

---

## Part 1 — Put the app online

GitHub Pages gives you a real `https://` URL, which is the only way the app can
install to your home screen and run offline.

### 1. Create the repository

1. Go to <https://github.com/new>
2. Repository name: `Workouts`
3. Visibility: **Public** ← required for free GitHub Pages on a repository
4. Do **not** tick "Add a README" — you already have one
5. Create repository

> **Why public is fine here:** your training log lives in your phone's browser
> storage, not in this repository. `tracker/log.csv` is listed in `.gitignore`
> specifically so it never gets committed. Nothing personal is ever pushed.

### 2. Push this folder

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

### 3. Turn on Pages

1. In the repo: **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **main**, folder: **/ (root)**
4. Save

### 4. Check it loads

Wait about a minute, then open this in any browser:

```
https://<your-username>.github.io/Workouts/
```

`index.html` at the root redirects straight to the app, so you should land on the
workout screen. The direct link is `.../Workouts/app/` if you ever want it. The
first deploy can take a couple of minutes; a 404 just means wait and refresh.

### 5. Install it on your phone

**iPhone (iOS):** open the URL in **Safari** (must be Safari, not Chrome) → tap the
**Share** button → **Add to Home Screen** → Add.

**Android:** open the URL in Chrome → **⋮** menu → **Install app** (or "Add to home
screen").

You now get a real app icon, no browser chrome, and it works with no signal.

**The app is now on your phone.** Your log is still local to each device, so if you
only ever use one phone you're finished — continue to *Day to day* below.

Otherwise carry on with Part 2 to share one log across all your devices.

---

## Part 2 — Put your log on every device

Part 1 put the *app* everywhere. It did not put your *data* anywhere — entries live
in the browser that created them, so your phone and laptop are currently two
separate logs. This part fixes that, and it's free.

The app stays offline-first either way: logging never waits on the network, so a
gym with no signal works exactly like being at home. It reconciles with the
database whenever it next has a connection.

### 6. Create a Supabase project

Sign up at <https://supabase.com>, create a project (any name, nearest region) and
wait for it to finish provisioning. Free tier is plenty — your log will be a few
hundred rows a year.

### 7. Create the table

Project → **SQL Editor** → New query → paste the whole of
[`supabase/schema.sql`](supabase/schema.sql) → **Run**.

That creates the table, an index, and row-level security policies. Every policy is
scoped to `auth.uid() = user_id`, so a signed-in user can only ever read or write
their own rows. The `anon` role is granted nothing at all — without this, the
publishable key in a public web page would expose your whole log.

### 8. Allow your URL to receive the sign-in link

**This is the step that silently breaks if you skip it.** Authentication →
**URL Configuration**:

- **Site URL**: `https://<your-username>.github.io/Workouts/app/`
- **Redirect URLs**: add both
  - `https://<your-username>.github.io/Workouts/app/`
  - `http://localhost:8765/` (so you can test on your Mac)

Supabase only redirects to URLs on this list. If it's missing, the magic link dumps
you on the project's default Site URL and nothing happens.

### 9. Copy your project URL and key

Project → **Settings → API Keys** (older dashboards: **Settings → API**). Copy two
things:

- **Project URL** — looks like `https://abcdefgh.supabase.co`
- **Publishable key** — `sb_publishable_…` (older projects: the `anon` key, `eyJ…`)

### 10. Connect the app

Open the installed app → **Data** tab → **Sync across devices**. Paste both values,
tap **Save & connect**, then tap **Test connection**.

> **Checkpoint:** you must see "Connection OK". If you don't, stop here and fix it
> via *Troubleshooting* below — sync cannot work until this passes.

### 11. Sign in

Enter your email, tap **Email me a sign-in link**, and open that link **on the
device you're setting up**. The link signs in whichever device opens it.

### 12. Set up your other devices

On every additional device: open the app URL, add it to the home screen, then
repeat steps 10 and 11. Each device ends up sharing the one log.

The header carries a small dot: green when synced, amber when changes are waiting,
red on an error. Tap through to **Data** for the detail.

### 13. Prove it syncs

Do this once. Sync failures are deliberately quiet, and you don't want to find out
weeks later that only one device has been receiving anything.

1. On your phone, log a set you'll recognise — say bench, `20 kg × 1 × 1`.
2. Open the app on your laptop.
3. Confirm the set is there. If it isn't, tap **Data → Sync now**.
4. Now **delete** that test set on either device, then tap **Sync now** on the other
   and confirm it disappears there too.

Step 4 is the one that matters. Creating rows is the easy half; deletion has to
travel as well, and that's the half that breaks silently when it breaks.

### Troubleshooting

| Symptom | Cause |
|---|---|
| "Test connection" fails, `relation does not exist` | The table isn't exposed to the API. Check Settings → Data API → Exposed tables, and re-run the SQL. |
| `permission denied for table entries` | The `grant` statements didn't run. Re-run `supabase/schema.sql`. |
| Sign-in email never arrives | Supabase's built-in sender is rate-limited (a few per hour) and won't deliver to some domains. Wait, or configure your own SMTP under Authentication → Emails. |
| Magic link does nothing | The redirect URL isn't on the allowlist — see step 8. |
| Two devices disagree | Last-write-wins per entry by timestamp, so they settle on the newest edit. Clock skew between devices decides close calls. |
| Project stopped responding after a week away | Free projects pause after 7 days of inactivity. Open the dashboard and restore it; no data is lost. |

### What sync does *not* do

- It is **not a backup**. Keep exporting CSV now and then; a cloud table you can
  accidentally wipe is not a backup either.
- Deletions propagate, and there is no undo across devices. The Undo button in the
  toast covers the immediate mistake only.
- `tracker/track.py` still reads a local CSV. Sync doesn't change that — export and
  drop the file into `tracker/` as before.


## Day to day

- **Log** on the Today tab. Weight boxes pre-fill with your last entry — usually you
  just tap **+** for 2.5 kg and hit **Log**.
- **Undo** appears in the toast right after logging, in case you fat-finger it.
- Rest timer starts itself on your first log of the session.
- The header dot is your sync health at a glance: green synced, amber pending, red
  error. Tap through to **Data** for the detail.
- **Data → Download CSV** every week or two. Sync is *not* a backup — if you wipe
  the table by accident, or clear the browser's site data, that export is what
  saves you.

## Updating the app

```bash
# edit app/index.html, then
git add -A && git commit -m "tweak the app" && git push
```

Pages redeploys automatically. Because the service worker fetches the page
network-first, the new version lands on the next launch — but if you ever change
the **icons**, the scripts, or the shell file list, bump `CACHE = "workouts-v3"` in
`app/sw.js` to something new, or phones will keep serving the old ones.

## Using your log in the terminal

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
