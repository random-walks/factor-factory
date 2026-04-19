# Survival — Kaplan-Meier

```python
from factor_factory.engines.survival import estimate

result = estimate(
    panel,
    method="kaplan_meier",
    duration_col="days_to_event",
    event_col="event_observed",
    stratify_by=None,  # pass a column name for stratified KM
)
print(result.summary_function.head())
```

`SurvivalResult.survival_function` is a DataFrame indexed by time with columns per stratum. CI bands come from Greenwood's formula.

## When to use KM

- Non-parametric survival curve estimation
- Log-rank test for group-difference significance
- Preliminary EDA before fitting a Cox model

## Log-rank test

```python
result.logrank_p_value  # None for unstratified runs
```

## References

- Kaplan, E. L., & Meier, P. (1958). Nonparametric estimation from incomplete observations. *Journal of the American Statistical Association*, 53(282), 457–481.
- Reference implementation: [`lifelines`](https://lifelines.readthedocs.io/)
