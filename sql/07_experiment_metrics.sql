/*
Purpose: Produce treatment-level descriptive experiment KPIs and control-relative metrics.
Input: hillstrom
Output grain: one row per treatment group; then one row per treatment versus control.
Important: Descriptive analysis only. Statistical inference is performed in Python.
*/

WITH experiment_totals AS (
    SELECT COUNT(*)::numeric AS total_assigned
    FROM hillstrom
)
SELECT
    h.segment AS treatment_group,
    COUNT(*) AS sample_size,
    ROUND(100.0 * COUNT(*) / t.total_assigned, 2) AS population_share_pct,
    COUNT(*) FILTER (WHERE h.visit = 1) AS visit_count,
    ROUND(100.0 * AVG(h.visit::numeric), 2) AS visit_rate_pct,
    COUNT(*) FILTER (WHERE h.conversion = 1) AS conversion_count,
    ROUND(100.0 * AVG(h.conversion::numeric), 2) AS conversion_rate_pct,
    ROUND(SUM(h.spend), 2) AS total_spend,
    ROUND(AVG(h.spend), 4) AS mean_spend_per_assigned_customer,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY h.spend), 2) AS median_spend,
    COUNT(*) FILTER (WHERE h.spend > 0) AS positive_spend_count,
    ROUND(100.0 * AVG((h.spend > 0)::int), 2) AS positive_spend_rate_pct,
    ROUND(AVG(h.spend) FILTER (WHERE h.spend > 0), 2) AS mean_spend_among_positive_spenders
FROM hillstrom h
CROSS JOIN experiment_totals t
GROUP BY h.segment, t.total_assigned
ORDER BY CASE h.segment WHEN 'No E-Mail' THEN 1 WHEN 'Mens E-Mail' THEN 2 ELSE 3 END;

-- Treatment versus No E-Mail KPI differences. Rate differences are percentage points.
WITH group_kpis AS (
    SELECT
        segment,
        AVG(visit::numeric) AS visit_rate,
        AVG(conversion::numeric) AS conversion_rate,
        AVG(spend) AS mean_spend
    FROM hillstrom
    GROUP BY segment
),
control AS (
    SELECT * FROM group_kpis WHERE segment = 'No E-Mail'
)
SELECT
    k.segment AS treatment_group,
    ROUND(100.0 * (k.visit_rate - c.visit_rate), 4) AS visit_rate_difference_pp,
    ROUND(100.0 * (k.conversion_rate - c.conversion_rate), 4) AS conversion_rate_difference_pp,
    ROUND(k.mean_spend - c.mean_spend, 4) AS mean_spend_difference,
    ROUND(100.0 * (k.visit_rate - c.visit_rate) / NULLIF(c.visit_rate, 0), 2) AS visit_relative_lift_pct,
    ROUND(100.0 * (k.conversion_rate - c.conversion_rate) / NULLIF(c.conversion_rate, 0), 2) AS conversion_relative_lift_pct,
    ROUND(100.0 * (k.mean_spend - c.mean_spend) / NULLIF(c.mean_spend, 0), 2) AS spend_relative_lift_pct
FROM group_kpis k
CROSS JOIN control c
WHERE k.segment <> 'No E-Mail'
ORDER BY treatment_group;

-- Effect-scaled descriptive estimates per 1,000 assigned customers, not forecasts.
WITH group_kpis AS (
    SELECT segment, AVG(visit::numeric) AS visit_rate,
           AVG(conversion::numeric) AS conversion_rate, AVG(spend) AS mean_spend
    FROM hillstrom
    GROUP BY segment
),
control AS (SELECT * FROM group_kpis WHERE segment = 'No E-Mail')
SELECT
    k.segment AS treatment_group,
    ROUND(1000 * (k.visit_rate - c.visit_rate), 2) AS additional_visits_per_1000_assigned,
    ROUND(1000 * (k.conversion_rate - c.conversion_rate), 2) AS additional_conversions_per_1000_assigned,
    ROUND(1000 * (k.mean_spend - c.mean_spend), 2) AS additional_expected_spend_per_1000_assigned
FROM group_kpis k CROSS JOIN control c
WHERE k.segment <> 'No E-Mail'
ORDER BY treatment_group;
