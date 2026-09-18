/* Purpose: allocation and baseline inputs for Python experiment-health inference. */
WITH allocation AS (SELECT segment,COUNT(*) AS sample_size FROM hillstrom GROUP BY segment)
SELECT segment AS treatment_group,sample_size,
       ROUND(100.0*sample_size/SUM(sample_size) OVER (),2) AS allocation_pct,
       ROUND(SUM(sample_size) OVER ()/3.0,2) AS assumed_equal_expected_count
FROM allocation ORDER BY CASE segment WHEN 'No E-Mail' THEN 1 WHEN 'Mens E-Mail' THEN 2 ELSE 3 END;
SELECT segment AS treatment_group,AVG(recency) AS mean_recency,AVG(history) AS mean_history,
       AVG(mens::numeric) AS mens_rate,AVG(womens::numeric) AS womens_rate,AVG(newbie::numeric) AS newbie_rate
FROM hillstrom GROUP BY segment;
