/*
Purpose: Demonstrate scalable segment-level experiment KPI reporting.
Input: hillstrom
Output grain: one row per requested customer segment level and treatment group.
Important: Descriptive business reporting only; no p-values or subgroup inference.
*/

-- Reusable KPI pattern for channel × treatment.
SELECT channel, segment AS treatment_group, COUNT(*) AS sample_size,
       ROUND(100.0 * AVG(visit::numeric), 2) AS visit_rate_pct,
       ROUND(100.0 * AVG(conversion::numeric), 2) AS conversion_rate_pct,
       ROUND(AVG(spend), 4) AS mean_spend, ROUND(SUM(spend), 2) AS total_spend,
       ROUND(100.0 * AVG((spend > 0)::int), 2) AS positive_spend_rate_pct
FROM hillstrom GROUP BY channel, segment
ORDER BY channel, CASE segment WHEN 'No E-Mail' THEN 1 WHEN 'Mens E-Mail' THEN 2 ELSE 3 END;

-- New versus existing customer reporting.
SELECT newbie, segment AS treatment_group, COUNT(*) AS sample_size,
       ROUND(100.0 * AVG(visit::numeric), 2) AS visit_rate_pct,
       ROUND(100.0 * AVG(conversion::numeric), 2) AS conversion_rate_pct,
       ROUND(AVG(spend), 4) AS mean_spend, ROUND(SUM(spend), 2) AS total_spend,
       ROUND(100.0 * AVG((spend > 0)::int), 2) AS positive_spend_rate_pct
FROM hillstrom GROUP BY newbie, segment
ORDER BY newbie, CASE segment WHEN 'No E-Mail' THEN 1 WHEN 'Mens E-Mail' THEN 2 ELSE 3 END;

-- Historical-value segment reporting; conversion counts are included because conversion is rare.
SELECT history_segment, segment AS treatment_group, COUNT(*) AS sample_size,
       COUNT(*) FILTER (WHERE conversion = 1) AS conversion_count,
       ROUND(100.0 * AVG(visit::numeric), 2) AS visit_rate_pct,
       ROUND(100.0 * AVG(conversion::numeric), 2) AS conversion_rate_pct,
       ROUND(AVG(spend), 4) AS mean_spend, ROUND(SUM(spend), 2) AS total_spend
FROM hillstrom GROUP BY history_segment, segment
ORDER BY history_segment, CASE segment WHEN 'No E-Mail' THEN 1 WHEN 'Mens E-Mail' THEN 2 ELSE 3 END;

-- zip_code is treated as an observed categorical geography label, not assumed postal ZIP.
SELECT zip_code, segment AS treatment_group, COUNT(*) AS sample_size,
       ROUND(100.0 * AVG(visit::numeric), 2) AS visit_rate_pct,
       ROUND(100.0 * AVG(conversion::numeric), 2) AS conversion_rate_pct,
       ROUND(AVG(spend), 4) AS mean_spend, ROUND(SUM(spend), 2) AS total_spend,
       ROUND(100.0 * AVG((spend > 0)::int), 2) AS positive_spend_rate_pct
FROM hillstrom GROUP BY zip_code, segment
ORDER BY zip_code, CASE segment WHEN 'No E-Mail' THEN 1 WHEN 'Mens E-Mail' THEN 2 ELSE 3 END;

-- Control-relative metrics within each channel using conditional aggregation and CTEs.
WITH channel_kpis AS (
    SELECT channel,
           COUNT(*) FILTER (WHERE segment = 'No E-Mail') AS control_n,
           AVG(conversion::numeric) FILTER (WHERE segment = 'No E-Mail') AS control_conversion_rate,
           AVG(spend) FILTER (WHERE segment = 'No E-Mail') AS control_mean_spend,
           AVG(conversion::numeric) FILTER (WHERE segment = 'Mens E-Mail') AS mens_conversion_rate,
           AVG(spend) FILTER (WHERE segment = 'Mens E-Mail') AS mens_mean_spend,
           AVG(conversion::numeric) FILTER (WHERE segment = 'Womens E-Mail') AS womens_conversion_rate,
           AVG(spend) FILTER (WHERE segment = 'Womens E-Mail') AS womens_mean_spend
    FROM hillstrom
    GROUP BY channel
)
SELECT channel, control_n,
       ROUND(100.0 * (mens_conversion_rate - control_conversion_rate), 4) AS mens_conversion_difference_pp,
       ROUND(100.0 * (womens_conversion_rate - control_conversion_rate), 4) AS womens_conversion_difference_pp,
       ROUND(mens_mean_spend - control_mean_spend, 4) AS mens_mean_spend_difference,
       ROUND(womens_mean_spend - control_mean_spend, 4) AS womens_mean_spend_difference
FROM channel_kpis
ORDER BY channel;
