/*
Purpose: Reproduce core data-quality checks for the processed experiment data.
Input: hillstrom
Output grain: validation summaries and row-pattern diagnostics.
Important: Descriptive validation only. Identical rows do not prove duplicate
customers because this dataset has no unique customer identifier.

Expected PostgreSQL-compatible schema:
  recency integer, history_segment text, history numeric,
  mens integer, womens integer, zip_code text, newbie integer,
  channel text, segment text, visit integer, conversion integer, spend numeric
*/

-- Dataset dimensions. The 12-column schema is documented above.
SELECT COUNT(*) AS total_rows
FROM hillstrom;

-- Null counts for every expected column.
SELECT
    COUNT(*) FILTER (WHERE recency IS NULL) AS recency_nulls,
    COUNT(*) FILTER (WHERE history_segment IS NULL) AS history_segment_nulls,
    COUNT(*) FILTER (WHERE history IS NULL) AS history_nulls,
    COUNT(*) FILTER (WHERE mens IS NULL) AS mens_nulls,
    COUNT(*) FILTER (WHERE womens IS NULL) AS womens_nulls,
    COUNT(*) FILTER (WHERE zip_code IS NULL) AS zip_code_nulls,
    COUNT(*) FILTER (WHERE newbie IS NULL) AS newbie_nulls,
    COUNT(*) FILTER (WHERE channel IS NULL) AS channel_nulls,
    COUNT(*) FILTER (WHERE segment IS NULL) AS segment_nulls,
    COUNT(*) FILTER (WHERE visit IS NULL) AS visit_nulls,
    COUNT(*) FILTER (WHERE conversion IS NULL) AS conversion_nulls,
    COUNT(*) FILTER (WHERE spend IS NULL) AS spend_nulls
FROM hillstrom;

-- Expected labels: No E-Mail, Mens E-Mail, Womens E-Mail.
SELECT segment, COUNT(*) AS observation_count
FROM hillstrom
GROUP BY segment
ORDER BY observation_count DESC, segment;

-- Binary-code checks: expected values are 0 and 1.
SELECT
    COUNT(*) FILTER (WHERE visit NOT IN (0, 1) OR visit IS NULL) AS invalid_visit_values,
    COUNT(*) FILTER (WHERE conversion NOT IN (0, 1) OR conversion IS NULL) AS invalid_conversion_values,
    COUNT(*) FILTER (WHERE mens NOT IN (0, 1) OR mens IS NULL) AS invalid_mens_values,
    COUNT(*) FILTER (WHERE womens NOT IN (0, 1) OR womens IS NULL) AS invalid_womens_values,
    COUNT(*) FILTER (WHERE newbie NOT IN (0, 1) OR newbie IS NULL) AS invalid_newbie_values,
    COUNT(*) FILTER (WHERE history < 0) AS negative_history_values,
    COUNT(*) FILTER (WHERE spend < 0) AS negative_spend_values,
    COUNT(*) FILTER (WHERE recency < 1 OR recency > 12) AS invalid_recency_values
FROM hillstrom;

-- Exact duplicate-row patterns. Do not delete these rows: without an ID,
-- repeated observed values can represent distinct customers.
WITH row_patterns AS (
    SELECT
        recency, history_segment, history, mens, womens, zip_code,
        newbie, channel, segment, visit, conversion, spend,
        COUNT(*) AS duplicate_group_size
    FROM hillstrom
    GROUP BY
        recency, history_segment, history, mens, womens, zip_code,
        newbie, channel, segment, visit, conversion, spend
),
repeated_patterns AS (
    SELECT duplicate_group_size
    FROM row_patterns
    WHERE duplicate_group_size > 1
)
SELECT
    COUNT(*) AS repeated_row_patterns,
    COALESCE(SUM(duplicate_group_size), 0) AS observations_in_repeated_patterns,
    COALESCE(MAX(duplicate_group_size), 0) AS maximum_duplicate_group_size
FROM repeated_patterns;

-- Outcome logical-consistency checks.
SELECT
    COUNT(*) FILTER (WHERE conversion = 1 AND visit = 0) AS conversion_without_visit,
    COUNT(*) FILTER (WHERE spend > 0 AND conversion = 0) AS spend_without_conversion,
    COUNT(*) FILTER (WHERE spend > 0 AND visit = 0) AS spend_without_visit,
    COUNT(*) FILTER (WHERE conversion = 1 AND spend = 0) AS conversion_without_spend,
    COUNT(*) FILTER (WHERE spend < 0) AS negative_spend,
    COUNT(*) FILTER (WHERE visit NOT IN (0, 1)) AS invalid_visit,
    COUNT(*) FILTER (WHERE conversion NOT IN (0, 1)) AS invalid_conversion
FROM hillstrom;

-- Compact validation summary for reporting.
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE segment IS NULL) AS missing_treatment_labels,
    COUNT(*) FILTER (WHERE visit IS NULL OR conversion IS NULL OR spend IS NULL) AS rows_with_missing_outcomes,
    COUNT(*) FILTER (WHERE conversion = 1 AND visit = 0) AS invalid_funnel_rows
FROM hillstrom;
