Name: Aryan Chawla
Dataset version: 2026-11-16 (saya-synthetic-work-signals.csv; fictional data, 240 worker-weeks)

**Question:** How can we optimize employee workload efficiency? (Sub-questions: which team spends the most time in meetings, what changed in Engineering during the meeting-policy pilot, and is AI use associated with completed tasks?) "Efficiency" is only measured by proxies here (meeting hours, focus blocks, completed tasks). It is not productivity or wellbeing.

**Filters and dates:** All teams, weeks 2026-09-07 to 2026-11-09 (10 weeks). Engineering "before" = 5 weeks 2026-09-07..2026-10-05 (meeting_policy=usual); "pilot" = 5 weeks 2026-10-12..2026-11-09.

**Rows included / excluded and why:**
- Q1 and Q2: all 240 rows (no missing values in the fields used, no duplicate employee_id + week_of).
- Q3: 233 of 240 rows. Excluded 7 rows where ai_tool_hours (4 rows) or browser_observed_hours (3 rows) is blank. Blanks were NOT treated as zero. Nothing was imputed.

**Finding 1 (value, units, denominator):** Engineering has the highest mean meeting hours: 19.5 hours per worker-week (60 worker-weeks) vs 17.0 for Product, Operations and Customer Success (60 each). But this gap is entirely from the pre-pilot period: Engineering averaged 22.0 hours before the pilot (30 worker-weeks) vs 17.0 for every other team.

**Finding 2:** Engineering meeting hours fell from 22.0 to 17.0 (-5.0 hours per worker-week) after the pilot began; focus blocks (calendar gaps of 60+ minutes) rose from 8.27 to 10.73 per week (+2.46). The other three teams did not change (17.0 to 17.0 hours; 10.73 to 10.73 blocks), so the Engineering change is not a company-wide trend. Completed tasks did not rise: 8.7 to 8.3 (-0.4) in Engineering vs 8.43 to 8.57 (+0.14) elsewhere, a difference-in-differences of -0.54 tasks, which is small and not tested for significance. After-hours meetings (2.0 to 2.0) and reopened tasks (1.0 to 1.0) were unchanged. Engineering pilot weeks simply look like the other teams' weeks.

**Finding 3:** Overall observed AI exposure = 13.1% (total AI hours / total browser hours, using 233 paired rows). Rows with 15-30% AI exposure completed the most tasks (9.15, n=72) vs 7.50 at 0% (n=24), 8.22 at >0-15% (n=119) and 8.61 at >30% (n=18). The correlation is weak: r = 0.13 (pooled), 0.14 after removing each worker's own average. It is not monotonic (it dips above 30%), and the 0% group has only 24 rows. This is an association, not an effect of AI.

**Chart links:** chart1_meeting_hours_by_week.png (mean meeting hours by week, Engineering vs other teams, 2026-09-07 to 2026-11-09). chart2_tasks_by_ai_band.png (mean completed tasks by AI exposure band, paired rows, same window).

**Reproduction steps / repository:**
1. Download saya-synthetic-work-signals.csv (version 2026-11-16).
2. Run `python3 analysis.py saya-synthetic-work-signals.csv out` (needs pandas, matplotlib).
3. It prints all numbers in this report and writes the three summary CSVs and two charts.
Repository: [paste your link in your Ursa Engineering log].

**Recommendation:** Extend the meeting cap to one more team and measure it properly (see experiment). In this data the pilot cut meeting time by about 5 hours a week and added about 2.5 focus blocks without a visible drop in completed tasks. That is encouraging for cost, but it does not show tasks improved.

**Experiment and guardrail:**
- Intervention: cap weekly meeting hours at about 17 for Product (or Operations) for 6 weeks.
- Comparison: randomly assign half the workers (or teams, if possible) to the cap, with the other half keeping the usual schedule over the same weeks.
- Outcome metric: mean focus blocks per worker-week (primary) and completed tasks per observed day (secondary).
- Guardrail: reopened_tasks and emails_after_hours must not rise; stop or review if either increases for the capped group.

**Limitations and alternative explanations:**
- The pilot was not randomized, so Engineering may have changed for other reasons (a project phase ending, new tooling, seasonal workload). The other teams only partly control for that.
- Only one team, 5 pilot weeks, 6 workers: a very small sample.
- Task counts are not standardized for difficulty, and completed_tasks follows a repeating pattern across workers in this synthetic data, so small differences should not be over-read.
- AI use and task counts can both depend on role, task type or worker habits (confounders). Browser hours are not total working time, and 7 rows are missing.
- observation_days ranges 3-5; I did not adjust for it (mean tasks by observation days: 8.4, 8.5, 8.6, so the effect looks small).
- Meetings, focus blocks and task counts are proxies. None of this shows productivity, wellbeing, burnout or causation.
