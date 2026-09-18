# SQL Analytics Layer

Purpose: descriptive PostgreSQL validation and KPI preparation for the Hillstrom experiment.

Workflow: Raw CSV → PostgreSQL → validation and aggregation → analytical views → Python statistical analysis → dashboard/report.

Execution order: 01 schema, 02 profiling, 03 quality, 04 experiment population, 05 experiment health, 06 funnel, 07 metrics, 08 segments, 09 views.

SQL provides descriptive metrics and clean inputs. Python performs hypothesis tests, confidence intervals, bootstrap, power, multiplicity correction, and advanced treatment-effect analysis.

Assumptions: processed CSV is loaded into hillstrom. No reliable customer ID, timestamp, documented allocation ratio, or outcome window is present.
