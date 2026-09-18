# A/B Testing Portfolio Project Instructions

This is an advanced, professional A/B testing portfolio project.

- Keep the project clean, structured, and reproducible.
- Never modify original files inside `data/raw/`.
- Put cleaned or transformed data in `data/processed/`.
- Put reusable Python functions in `src/`.
- Put SQL queries in `sql/`.
- Put Jupyter notebooks in `notebooks/`.
- Put generated figures, tables, and reports in `outputs/`.
- Do not create unnecessary files.
- Use clear, readable Python code and descriptive variable names.
- Document important analytical decisions.
- Do not fabricate results or make assumptions about the dataset without checking.
- Do not change validated analytical methodology or results without documenting and approving the change.

## Before Treatment-Effect Testing

- Check for sample ratio mismatch.
- Check for duplicate users.
- Check for users appearing in multiple variants.
- Check missingness by treatment group.
- Check baseline balance where appropriate.
