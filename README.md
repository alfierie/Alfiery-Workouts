# Alfiery Workouts

A 3-day upper-body plan, plus two ways to log it that share the same data format.

| Path | What it is |
|---|---|
| `workout-plan.md` | The Monday / Wednesday / Friday–Saturday program |
| `app/` | Phone web app — tap-to-log, works offline, installs to your home screen |
| `app/sync.js` | Optional cross-device sync. Local storage stays the source of truth. |
| `app/vendor/supabase.js` | Vendored Supabase client (MIT, v2.116.0) so sync works offline |
| `supabase/schema.sql` | Table + row-level security policies, run once in the Supabase SQL editor |
| `tracker/track.py` | Terminal tracker — `log`, `progress`, `history`, `summary`, `undo` |
| `tracker/log.csv` | Terminal data file (plain CSV, git-ignored) |
| `DEPLOY.md` | How to get the app onto your phone (GitHub Pages, ~5 min) |
| `tools/make_icons.py` | Regenerates the app icons (the deadlifting "A" mark), no dependencies |

## On your phone

Open the app's URL, then **Share → Add to Home Screen** (iOS Safari) or
**⋮ → Install app** (Android Chrome). Full instructions in `DEPLOY.md`.

- **Today** — your session with last week's numbers pre-filled. Tap **+** for
  2.5 kg and **Log**. An **Undo** appears in case you fat-finger it.
- **Progress** — estimated 1RM per lift with a trend arrow (↑ ↓ →).
- **History** — every session, with delete.
- **Data** — sync setup, export / import CSV, and a warning before you delete anything.

Rest timer starts itself on your first log of the session.

## One log, several devices

By default the log is local to the browser that created it. To share it — and back
it up — connect a free Supabase project: follow **`DEPLOY.md`**, then paste two
values into **Data → Sync across devices**.

It stays offline-first either way. Logging never waits on the network, and changes
reconcile when there is one. Deletions are tombstoned rather than removed, so
deleting on your phone also removes it on your laptop.

## In the terminal

```bash
# log a set: <exercise> <weight_kg> <reps> <sets>
python3 tracker/track.py log bench 60 8 4

python3 tracker/track.py progress              # best e1RM + trend per lift
python3 tracker/track.py history bench         # every bench entry by date
python3 tracker/track.py summary               # volume per session
python3 tracker/track.py undo                  # delete the last entry
```

Add `-d some.csv` to work on a different file, and run `--help` for everything.

## Keeping the two in sync

Both sides write the same CSV columns:

```
date,exercise,weight_kg,reps,sets,notes
```

Export from the app, drop the file in as `tracker/log.csv`, and the terminal
commands pick up right where your phone left off:

```bash
cp ~/Downloads/workouts-2026-09-21.csv tracker/log.csv
python3 tracker/track.py progress
```

The app's import is merge-only — it skips rows that exactly match ones you already
have, so importing the same file twice does nothing.

## Estimating strength

Both the app and the CLI score a set with the Epley formula:

$$1\text{RM} = w \times \left(1 + \frac{r}{30}\right)$$

So a heavy triple and a light set of 12 are comparable, which is how you tell
whether a lift is actually progressing rather than just fluctuating.

## Local development

```bash
python3 -m http.server 8765 --directory app   # then open http://localhost:8765/
python3 tools/make_icons.py                   # regenerate icons after editing the mark
```

No build step, no dependencies, no test suite — the app is one self-contained
`index.html`.
