# Data

## Hillstrom Email Experiment Dataset

**Source:** Kevin Hillstrom's *MineThatData E-Mail Analytics and Data Mining Challenge* (2008).

Original source URL: <https://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv>

The dataset contains 64,000 observations and 12 columns across three experiment arms:

- No E-Mail
- Mens E-Mail
- Womens E-Mail

The dataset was released publicly for analysis, but no formal license text accompanies the original CSV. Downstream documentation, including [UpliftBench's Hillstrom dataset record](https://github.com/binshuangli/uplift-bench/blob/main/docs/DATASETS.md), describes the same redistribution limitation.

Accordingly, this repository intentionally does not redistribute either the raw dataset or its value-preserving processed copy. This repository does not grant any dataset redistribution rights.

## Local setup

Download the dataset from the original source and save it locally as:

```text
data/raw/Hillstrom.csv
```

Before running the notebooks, execute the existing Stage 02 workflow to create or validate:

```text
data/processed/Hillstrom_clean.csv
```

Stage 02 found no justified row- or value-level transformations. The processed file is therefore value-equivalent to the raw source.

## Expected local checksums

Use SHA-256 to confirm the expected local files:

```text
Hillstrom.csv:       0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece
Hillstrom_clean.csv: 00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0
```
