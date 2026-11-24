"""Ursa assignment: Explore work patterns with Saya.
Dataset version 2026-11-16 (240 worker-weeks, 24 workers, 4 teams, 10 weeks, 2026-09-07..2026-11-09).

Usage:  python3 analysis.py saya-synthetic-work-signals.csv outdir
Missing-data rule: blank ai_tool_hours / browser_observed_hours are NEVER set to 0.
AI-exposure uses only rows where BOTH are observed: sum(ai_tool_hours) / sum(browser_observed_hours).
"""
import sys, os
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
df = pd.read_csv(src)
PILOT = "2026-10-12"
df["post"] = df.week_of >= PILOT
df["group"] = np.where(df.team == "Engineering", "Engineering", "Other 3 teams")

# ---- Step 1: grain / coverage / missing ----
print("rows", len(df), "workers", df.employee_id.nunique(), "weeks", df.week_of.nunique(),
      "dup worker-weeks", df.duplicated(["employee_id", "week_of"]).sum())
print("missing:\n", df.isna().sum()[lambda s: s > 0])
paired = df.dropna(subset=["ai_tool_hours", "browser_observed_hours"]).copy()
print("paired rows", len(paired), "excluded", len(df) - len(paired))

# ---- Q1: mean meeting hours by team (all 240 rows, no missing) ----
q1 = df.groupby("team").meeting_hours.agg(n="count", mean_meeting_hours="mean").round(2).sort_values("mean_meeting_hours", ascending=False)
q1.to_csv(f"{out}/q1_team_meeting_hours.csv"); print(q1)

# ---- Q2: Engineering before (2026-09-07..10-05) vs pilot (2026-10-12..11-09), with other teams as comparison ----
cols = ["meeting_hours", "focus_blocks", "completed_tasks", "reopened_tasks", "after_hours_meetings", "emails_after_hours"]
q2 = df.groupby(["group", "post"])[cols].mean().round(2)
q2.index = q2.index.set_names(["group", "pilot_period"])
q2.to_csv(f"{out}/q2_engineering_pre_post.csv"); print(q2)
did = {}
for c in cols:
    e = q2.loc[("Engineering", True), c] - q2.loc[("Engineering", False), c]
    o = q2.loc[("Other 3 teams", True), c] - q2.loc[("Other 3 teams", False), c]
    did[c] = round(e - o, 2)
print("difference-in-differences (Eng change minus others' change):", did)

# ---- Q3: AI exposure vs completed tasks (paired rows only) ----
paired["ai_share"] = paired.ai_tool_hours / paired.browser_observed_hours
paired["ai_band"] = pd.cut(paired.ai_share, [-0.001, 0.0001, 0.15, 0.30, 2], labels=["0%", ">0-15%", "15-30%", ">30%"])
q3 = paired.groupby("ai_band", observed=True).agg(
    n=("completed_tasks", "size"), ai_hours=("ai_tool_hours", "sum"), browser_hours=("browser_observed_hours", "sum"),
    mean_completed_tasks=("completed_tasks", "mean")).round(2)
q3["ai_exposure_pct"] = (100 * q3.ai_hours / q3.browser_hours).round(1)
q3.to_csv(f"{out}/q3_ai_bands.csv"); print(q3)
overall = paired.ai_tool_hours.sum() / paired.browser_observed_hours.sum()
r = paired[["ai_share", "completed_tasks"]].corr().iloc[0, 1]
w = paired.copy()
w["s"] = w.ai_share - w.groupby("employee_id").ai_share.transform("mean")
w["t"] = w.completed_tasks - w.groupby("employee_id").completed_tasks.transform("mean")
print(f"overall AI exposure {overall:.4f}; pooled r={r:.3f}; within-worker r={w[['s','t']].corr().iloc[0,1]:.3f}")

# ---- Charts ----
C = {"Engineering": "#1f5fbf", "Other 3 teams": "#8a8f98"}
wk = df.groupby(["group", "week_of"]).meeting_hours.mean().unstack(0)
fig, ax = plt.subplots(figsize=(8, 4.2))
for g in wk: ax.plot(wk.index, wk[g], marker="o", color=C[g], label=g)
ax.axvline(PILOT, ls="--", color="k", lw=1); ax.text(PILOT, ax.get_ylim()[1], " pilot starts 2026-10-12", va="top", fontsize=8)
ax.set_title("Chart 1. Mean weekly meeting hours per worker\nWindow 2026-09-07 to 2026-11-09; n=60 Eng rows, 180 other rows")
ax.set_ylabel("Mean meeting hours per worker-week"); ax.tick_params(axis="x", rotation=45); ax.legend(); fig.tight_layout()
fig.savefig(f"{out}/chart1_meeting_hours_by_week.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4.2))
ax.bar(q3.index.astype(str), q3.mean_completed_tasks, color="#1f5fbf")
for i, (m, n) in enumerate(zip(q3.mean_completed_tasks, q3.n)): ax.text(i, m + .1, f"{m:.1f}\n(n={n})", ha="center", fontsize=8)
ax.set_ylim(0, 11); ax.set_xlabel("AI share of observed browser hours (per worker-week)")
ax.set_ylabel("Mean completed tasks (synthetic)")
ax.set_title(f"Chart 2. Completed tasks by AI exposure band\nPaired rows only, 2026-09-07 to 2026-11-09, n={len(paired)} of 240 (7 excluded)")
fig.tight_layout(); fig.savefig(f"{out}/chart2_tasks_by_ai_band.png", dpi=150); plt.close(fig)
