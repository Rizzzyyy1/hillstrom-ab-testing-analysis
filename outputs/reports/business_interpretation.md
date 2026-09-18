# Hillstrom Email Experiment — Business Interpretation

## Executive Summary

This experiment analyzed 64,000 observations across three arms: No E-Mail (control), Mens E-Mail, and Womens E-Mail (treatments). Group sizes showed no evidence of sample ratio mismatch under the assumed equal allocation, and measured customer characteristics were closely balanced.

Stage 05 is the primary treatment-effect analysis. Both email treatments produced positive estimated effects versus No E-Mail across spend, conversion, and visits. Stage 08 robustness checks broadly supported those findings.

## Primary Business KPIs

| Treatment | Sample size | Mean spend | Visit rate | Conversion rate | Incremental spend | Incremental conversion | Incremental visit | Spend lift | Spend 95% CI | Holm p-value |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| No E-Mail | 21,306 | $0.6528 | 10.6167% | 0.5726% | — | — | — | — | — | — |
| Mens E-Mail | 21,307 | $1.4226 | 18.2757% | 1.2531% | +$0.7698 | +0.681 pp | +7.659 pp | +117.9% | $0.4916 to $1.0588 | 2.33e-7 |
| Womens E-Mail | 21,387 | $1.0772 | 15.1400% | 0.8837% | +$0.4244 | +0.311 pp | +4.523 pp | +65.0% | $0.1707 to $0.6857 | 0.00113 |

The executive KPI CSV retains exact values from project outputs.

## Business Scale Interpretation

| Treatment | Incremental spend per 1,000 | Incremental conversions per 1,000 | Incremental visits per 1,000 |
|---|---:|---:|---:|
| Mens E-Mail | +$769.83 | +6.81 | +76.59 |
| Womens E-Mail | +$424.41 | +3.11 | +45.23 |

These are experiment-scaled estimates, not forecasts of future profit.

## Primary Outcome — Spend

Spend per assigned customer is the project's primary outcome because it connects to economic value, incorporates purchase frequency and amount, and retains all assigned customers in the denominator. Mens E-Mail was estimated at +$0.7698 and Womens E-Mail at +$0.4244 per assigned customer versus control. Both bootstrap intervals excluded zero, and Holm-adjusted reference tests support the same qualitative inference. The results provide evidence consistent with higher spend; they do not guarantee future revenue.

## Secondary Outcomes and Funnel

Mens E-Mail was estimated at +0.681 percentage points for conversion (95% CI: +0.500 to +0.861 pp) and +7.659 pp for visits (95% CI: +6.995 to +8.323 pp). Womens E-Mail was estimated at +0.311 pp for conversion (95% CI: +0.150 to +0.472 pp) and +4.523 pp for visits (95% CI: +3.889 to +5.157 pp).

A percentage-point change is an absolute rate difference; it differs from relative lift. The funnel is assigned customer → visit → conversion → spend. Positive-spend rates were 0.57% for control, 1.25% for Mens E-Mail, and 0.88% for Womens E-Mail. Mean spend among positive spenders was $114.00, $113.53, and $121.89 respectively. Descriptively, spend differences appear more related to purchase frequency than to dramatic changes in purchaser amounts. Conditional purchaser amounts are explanatory only because purchase is post-treatment.

## Experiment Reliability and Sensitivity

The SRM diagnostic was chi-square = 0.2025, p = 0.9037. The largest baseline absolute SMD was 0.0164; no observed SMD exceeded 0.10. These diagnostics support observed allocation and balance but do not prove perfect randomization.

The control conversion baseline was 0.5726%, and the 80% power conversion MDE was +0.223 pp. The control visit baseline was 10.6167%, with an 80% power visit MDE of +0.850 pp. Detecting a +0.10 pp conversion change at 80% power would require about 96,971 customers per group under the documented planning assumptions.

## Robustness

Adjusted Stage 08 spend effects were close to Stage 05: Mens E-Mail +$0.764 (95% CI: $0.479 to $1.049) and Womens E-Mail +$0.426 (95% CI: $0.170 to $0.681). Spend permutation p-values were 0.0001 and 0.0014.

After excluding the 20 largest spend observations globally, estimates attenuated to +$0.638 for Mens E-Mail and +$0.379 for Womens E-Mail, but remained positive. The 99.5th percentile among positive spenders was the observed maximum, $499, so that winsorization made no change. Results are not entirely dependent on a handful of extreme transactions.

## Treatment Comparison Discipline

Mens E-Mail has the larger observed point estimates. However, the pre-specified primary comparisons were each email treatment versus No E-Mail. Mens versus Womens was not a primary confirmatory comparison, so point estimates alone do not formally prove one email treatment superior to the other.

## Segmentation and Heterogeneity

Stage 07 examined 114 subgroup comparisons. Thirteen raw interaction p-values were below 0.05, and six remained notable after Benjamini-Hochberg FDR correction. The notable patterns largely involved visit response by customer-newness, mens, womens, and zip_code, plus a Womens E-Mail by newbie conversion interaction.

These findings are exploratory. Some subgroup arms were small and conversion events were sparse in some history segments. They are future-experiment hypotheses, not targeting rules.

## Decision Framework

Both email treatments produced positive experimental effects relative to No E-Mail across the main measured outcomes. A full profit or ROI decision cannot be calculated because campaign cost, contribution margin, fulfillment costs, customer lifetime value, and future reachable audience are absent.

Incremental profit per assigned customer equals:

(incremental spend × contribution margin) − incremental campaign cost per assigned customer

For break-even reasoning, Mens E-Mail incremental contribution before campaign cost is approximately 0.7698 × M, and Womens E-Mail is 0.4244 × M, where M is actual contribution margin. Net contribution equals incremental spend × M − C, where C is actual campaign cost per customer. No values for M or C are assumed.

## Limitations

- No customer identifier exists, so duplicate experimental units cannot be independently verified.
- No timestamp is available, so time trends cannot be assessed.
- The original allocation ratio, outcome window, pre-registration, and original primary metric are unavailable.
- Spend is highly zero-inflated and right-skewed.
- Subgroup findings are exploratory and may not generalize.
- Campaign cost, margin, CLV, and reachable audience are absent.

## Key Business Takeaways

- Both email treatments had positive estimated effects versus No E-Mail.
- Mens E-Mail had larger observed point estimates, but was not formally confirmed superior to Womens E-Mail.
- Incremental spend appears primarily associated with increased purchase frequency.
- Bootstrap, adjustment, permutation, and extreme-value checks broadly support the primary results.
- Segment patterns are hypotheses for future validation, not targeting rules.
- Profitability requires actual campaign-cost and margin inputs.
