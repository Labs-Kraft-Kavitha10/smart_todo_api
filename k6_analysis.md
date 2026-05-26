# K6 Performance Analysis

Latency figures below are computed from the raw per-request data points in `results/ramp_up_results.json` and `results/spike_results.json`, bucketed into 5-second windows. Run date: 2026-05-26.

## Ramp-up test

During the first minute (0 → 10 VUs) the API was effectively idle and p95 latency hovered around 5–7 ms. Tail latency began climbing around the **15–20 VU range (~t=80s)**, where p95 stepped up from ~6 ms to ~8–9 ms. From **30 VUs onward p95 settled into the 9–12 ms band**, and at the sustained 50-VU plateau (t=180–215s) p95 reached its peak of **16.76 ms** — still ~48× under the 800 ms budget. Overall run p95 was **12.29 ms** across 6,086 requests. Failure rate stayed at **0.00 %** for every bucket of the run, including the plateau, so no capacity ceiling was reached; the test simply showed orderly linear scaling, not saturation.

## Spike test

The 5-VU baseline ran at ~5–9 ms p95. When the 20× burst hit at t=10s, p95 jumped within a single 5-second bucket to **11.55 ms**, settling between 10–16 ms for the 30-second 100-VU hold (peak 16.36 ms at t=25s, mid-burst). Crucially, the burst produced **zero 5xx responses and zero failed requests** across 3,986 total requests, so the Flask server did not queue or stall — it absorbed the load synchronously. Recovery was effectively immediate: within the first 5-second bucket after VUs dropped back to 5, p95 returned to **8.81 ms**, and held in the 9–11 ms range for the remainder of the run. No tail of lingering slow requests was observed.
