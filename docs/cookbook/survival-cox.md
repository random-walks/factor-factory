# Survival — Cox proportional hazards

```python
from factor_factory.engines.survival import estimate

result = estimate(
    panel,
    method="cox_ph",
    duration_col="days_to_event",
    event_col="event_observed",
    covariates=("age", "bmi", "treatment"),
)
print(result.hazard_ratios)
print(result.schoenfeld_p_values)
```

## Proportional-hazards assumption

Check `result.schoenfeld_p_values` — low p-values indicate PH violations. Options:

1. **Stratify** the violator: `stratify_by="sex"` (Batch 6 adds the full strata kwarg).
2. **Time-varying coefficients**: fit `CoxTimeVaryingFitter` manually via lifelines.
3. **Use parametric AFT** instead (Weibull, log-normal) — not yet wrapped; file an issue.

## Stratified Cox PH *(Batch 6)*

```python
result = estimate(panel, method="cox_ph", stratify_by="sex", covariates=(...))
```

Strata have their own baseline hazards; the coefficients are shared across strata.

## References

- Cox, D. R. (1972). Regression models and life-tables. *Journal of the Royal Statistical Society, Series B*, 34(2), 187–220.
- Reference implementation: [`lifelines`](https://lifelines.readthedocs.io/)
