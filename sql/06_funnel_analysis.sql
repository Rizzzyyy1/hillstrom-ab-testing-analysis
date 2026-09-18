/*
Purpose: Build treatment-level funnel and spend-decomposition metrics.
Input: hillstrom
Output grain: one row per treatment group.
Important: Descriptive only; conditional purchaser spend is not a causal treatment effect.
*/

-- Funnel metrics. Rates explicitly identify all-assigned versus conditional denominators.
SELECT
    segment AS treatment_group,
    COUNT(*) AS assigned_customers,
    COUNT(*) FILTER (WHERE visit = 1) AS visitors,
    ROUND(100.0 * AVG(visit::numeric), 2) AS visit_rate_among_assigned_pct,
    COUNT(*) FILTER (WHERE conversion = 1) AS conversions,
    ROUND(100.0 * AVG(conversion::numeric), 2) AS conversion_rate_among_assigned_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE conversion = 1)
          / NULLIF(COUNT(*) FILTER (WHERE visit = 1), 0), 2) AS conversion_rate_among_visitors_pct,
    COUNT(*) FILTER (WHERE spend > 0) AS positive_spenders,
    ROUND(100.0 * AVG((spend > 0)::int), 2) AS positive_spender_rate_among_assigned_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE spend > 0)
          / NULLIF(COUNT(*) FILTER (WHERE visit = 1), 0), 2) AS positive_spender_rate_among_visitors_pct
FROM hillstrom
GROUP BY segment
ORDER BY CASE segment WHEN 'No E-Mail' THEN 1 WHEN 'Mens E-Mail' THEN 2 ELSE 3 END;

-- Funnel drop-offs: assigned to visit and visit to conversion are distinct denominators.
WITH funnel AS (
    SELECT segment, COUNT(*)::numeric AS assigned,
           COUNT(*) FILTER (WHERE visit = 1)::numeric AS visitors,
           COUNT(*) FILTER (WHERE conversion = 1)::numeric AS conversions
    FROM hillstrom GROUP BY segment
)
SELECT segment AS treatment_group,
       ROUND(100.0 * (assigned - visitors) / assigned, 2) AS assigned_to_nonvisit_dropoff_pct,
       ROUND(100.0 * (visitors - conversions) / NULLIF(visitors, 0), 2) AS visit_to_nonconversion_dropoff_pct
FROM funnel
ORDER BY CASE segment WHEN 'No E-Mail' THEN 1 WHEN 'Mens E-Mail' THEN 2 ELSE 3 END;

-- Spend decomposition: mean spend is descriptively related to purchase frequency × amount.
SELECT
    segment AS treatment_group,
    ROUND(AVG((spend > 0)::int)::numeric, 6) AS positive_spend_probability,
    ROUND(AVG(spend) FILTER (WHERE spend > 0), 2) AS mean_spend_given_positive,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY spend) FILTER (WHERE spend > 0), 2) AS median_spend_given_positive,
    ROUND(AVG(spend), 4) AS mean_spend_per_assigned_customer
FROM hillstrom
GROUP BY segment
ORDER BY CASE segment WHEN 'No E-Mail' THEN 1 WHEN 'Mens E-Mail' THEN 2 ELSE 3 END;
