# K6 Performance Analysis

Latency figures below are computed from the raw per-request data points in `results/ramp_up_results.json` and `results/spike_results.json`, bucketed into 5-second windows.

## Ramp-up test

During the first minute (0 → 10 VUs) the API was effectively idle and p95 latency hovered around 5–7 ms. Tail latency only began to climb in earnest around the **15–20 VU range (~t=80s)**, where p95 stepped up from ~6 ms to ~9–10 ms. From **30 VUs onward p95 settled into the 12–14 ms band**, and at the sustained 50-VU plateau (t=180–210s) p95 reached its peak of **20.15 ms** — still ~40× under the 800 ms budget. Failure rate stayed at **0.00 %** for every bucket of the run, including the plateau, so no capacity ceiling was reached; the test simply showed orderly linear scaling, not saturation.

## Spike test

The 5-VU baseline ran at ~7 ms p95. When the 20× burst hit at t=10s, p95 jumped within a single 5-second bucket to **10.96 ms**, settling between 11–14 ms for the 30-second 100-VU hold (peak 14.38 ms at the end of the burst). Crucially, the burst produced **zero 5xx responses and zero failed requests**, so the Flask server did not queue or stall — it absorbed the load synchronously. Recovery was effectively immediate: within the first 5-second bucket after VUs dropped back to 5, p95 returned to **9.43 ms**, and held in the 9–10 ms range for the remainder of the run. No tail of lingering slow requests was observed.
