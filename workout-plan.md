# Workout Plan — 3 Days/Week (Mon / Wed / Fri-Sat)

**Profile:** 20 y/o male · 95 kg · 175 cm · "skinny fat" with belly fat
**Constraints:** no direct abs work, no legs
**Goal:** lose fat, build visible upper-body muscle

> Cardio is not optional here. It's the fat-loss driver; the lifting is what keeps muscle while you lose the weight.

---

## Day 1 — Monday: Push (Chest / Shoulders / Triceps)

| # | Exercise | Sets × Reps | Notes |
|---|---|---|---|
| 1 | Barbell or DB flat bench press | 4 × 6–10 | Main lift. Add weight when you hit 10 on all sets. |
| 2 | Incline DB press | 3 × 8–12 | Upper chest — this is what makes the torso look wide. |
| 3 | Seated DB shoulder press | 3 × 8–12 | |
| 4 | DB lateral raises | 3 × 12–15 | Light, strict, no swinging. Side delts = shoulder width. |
| 5 | Triceps rope pushdown *(or bench dips)* | 3 × 10–15 | |
| 6 | Cardio — incline treadmill walk or bike | 20–30 min | Incline 8–12%, brisk pace. |
| 7 | Treadmill cooldown walk | 5 min | |

## Day 2 — Wednesday: Pull (Back / Biceps)

| # | Exercise | Sets × Reps | Notes |
|---|---|---|---|
| 1 | Lat pulldown *(or assisted pull-ups)* | 4 × 8–12 | Pull to upper chest, squeeze 1s. |
| 2 | Seated cable row *(or one-arm DB row)* | 4 × 8–12 | Chest up, don't round the lower back. |
| 3 | Face pulls *(or reverse flyes)* | 3 × 15 | Posture + rear delts. Counteracts desk posture. |
| 4 | DB curls | 3 × 10–12 | |
| 5 | Hammer curls | 3 × 10–12 | |
| 6 | Cardio — incline walk, bike, or rower | 20–30 min | |

## Day 3 — Friday or Saturday: Upper Body + Arms

| # | Exercise | Sets × Reps | Notes |
|---|---|---|---|
| 1 | Incline DB press | 3 × 8–12 | |
| 2 | Chest-supported or DB row | 3 × 8–12 | |
| 3 | Arnold press or DB shoulder press | 3 × 10 | |
| 4 | Lateral raises | 3 × 15 | |
| 5 | Superset: BB curl + overhead triceps extension | 3 × 10–12 each | Back-to-back, no rest between the two. |
| 6 | Cardio — steady state | 25–35 min | Longer, easier pace. |

**Warm-up every session:** 5 min easy cardio, then 1–2 light sets of the first exercise at ~50% working weight.

---

## Progression Rules

- Stop each set **1–2 reps shy of failure** (RIR 1–2). Grinding to failure every set is what stalls progress.
- Each week, add either **1 rep per set** or **+2.5 kg on the bar**.
- When you hit the **top of the rep range on all sets**, increase the weight and drop back to the bottom of the range.
- Rest: **2–3 min** on the big compounds, **60–90 s** on isolation work.
- Log every set in the tracker. If a lift hasn't moved in 3 weeks, change the exercise or the rep range, not the whole program.

## The Belly (the part that actually matters)

Lifting doesn't spot-reduce fat. The belly is a **calorie and activity** problem:

| Lever | Target |
|---|---|
| Calories | ~1,800–2,100 kcal/day → ~0.5 kg loss per week |
| Protein | 150–180 g/day (this is what protects muscle in a deficit) |
| Steps | 8,000–10,000 daily, on top of the cardio above |
| Sleep | 7–8 h — poor sleep wrecks appetite control |
| Alcohol | Cut it; it's the biggest hidden calorie source for most people |

Weigh yourself **weekly** (same day, same time, after waking) — daily numbers are noise.

## Two Honest Notes

1. **Legs:** skipping them is fine for the next few months, but they're your largest muscle group — training them raises daily calorie burn and fixes the "skinny fat" look from the ground up. Even 2 sets of goblet squats + RDLs per week pays off. Your call.
2. **Abs:** you're right that crunches don't burn belly fat. But note that visible abs are made in the kitchen at a lower body-fat percentage — not by ab exercises.

## No-Gym Version

Swap the machines for: push-ups or DB floor press, DB rows, DB lateral raises, DB curls, overhead DB extension. Everything else works with a pair of adjustable dumbbells.

## Tracking

```bash
python3 tracker/track.py log bench 60 8 4      # exercise, weight_kg, reps, sets
python3 tracker/track.py progress              # all exercises: best e1RM, trend
python3 tracker/track.py history bench         # every set of bench, by date
python3 tracker/track.py summary               # volume per session
python3 tracker/track.py undo                  # delete the last entry
```

Estimated 1RM uses the Epley formula: $1\text{RM} = w \times (1 + r/30)$.
