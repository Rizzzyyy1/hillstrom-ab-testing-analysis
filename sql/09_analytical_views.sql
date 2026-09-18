/* Reusable descriptive views for downstream Python and dashboards; no inference. */
CREATE OR REPLACE VIEW vw_experiment_population AS
SELECT *,CASE WHEN segment='No E-Mail' THEN 'control' ELSE 'treatment' END AS assignment_type FROM hillstrom;
CREATE OR REPLACE VIEW vw_experiment_metrics AS
SELECT segment AS treatment_group,COUNT(*) AS sample_size,AVG(visit::numeric) AS visit_rate,
       AVG(conversion::numeric) AS conversion_rate,AVG(spend) AS mean_spend,SUM(spend) AS total_spend
FROM hillstrom GROUP BY segment;
CREATE OR REPLACE VIEW vw_funnel_metrics AS
SELECT segment AS treatment_group,COUNT(*) AS assigned_customers,
       COUNT(*) FILTER (WHERE visit=1) AS visitors,COUNT(*) FILTER (WHERE conversion=1) AS conversions,
       COUNT(*) FILTER (WHERE spend>0) AS positive_spenders
FROM hillstrom GROUP BY segment;
