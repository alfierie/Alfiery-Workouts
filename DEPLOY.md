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
