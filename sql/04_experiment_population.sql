/* Purpose: intention-to-treat analytical population. Input: hillstrom. */
WITH experiment_population AS (
 SELECT recency,history_segment,history,mens,womens,zip_code,newbie,channel,segment AS treatment_group,
        CASE segment WHEN 'No E-Mail' THEN 'control' WHEN 'Mens E-Mail' THEN 'mens_email' ELSE 'womens_email' END AS treatment_label,
        visit AS visitor_flag, conversion AS purchaser_flag, spend
 FROM hillstrom
)
SELECT recency,history_segment,history,mens,womens,zip_code,newbie,channel,treatment_group,treatment_label,visitor_flag,purchaser_flag,spend
FROM experiment_population;
