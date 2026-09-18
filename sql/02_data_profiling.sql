/* Purpose: pre-analysis profiling. Input: hillstrom. Descriptive only. */
SELECT COUNT(*) AS total_rows, MIN(recency) AS min_recency, MAX(recency) AS max_recency,
       MIN(history) AS min_history, MAX(history) AS max_history, AVG(history) AS avg_history,
       AVG(spend) AS avg_spend, COUNT(*) FILTER (WHERE visit=1) AS visits,
       COUNT(*) FILTER (WHERE conversion=1) AS conversions
FROM hillstrom;
SELECT segment, COUNT(*) AS observation_count FROM hillstrom GROUP BY segment ORDER BY observation_count DESC;
SELECT 'channel' AS variable, channel AS category, COUNT(*) AS observation_count FROM hillstrom GROUP BY channel
UNION ALL SELECT 'zip_code',zip_code,COUNT(*) FROM hillstrom GROUP BY zip_code
UNION ALL SELECT 'history_segment',history_segment,COUNT(*) FROM hillstrom GROUP BY history_segment
ORDER BY variable, observation_count DESC;
SELECT MIN(spend) AS min_spend, MAX(spend) AS max_spend,
       PERCENTILE_CONT(.5) WITHIN GROUP (ORDER BY spend) AS median_spend,
       COUNT(*) FILTER (WHERE spend=0) AS zero_spend_count
FROM hillstrom;
