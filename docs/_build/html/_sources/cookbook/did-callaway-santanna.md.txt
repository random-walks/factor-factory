# DiD — Callaway-Sant'Anna

Callaway & Sant'Anna (2021) decompose the ATT into cohort- and time-specific pieces (the ATT(g,t) matrix), side-stepping the TWFE forbidden-comparisons bias under staggered rollout.

```python
from factor_factory.engines.did import estimate

result = estimate(
    panel,
    method="cs",
    control_group="never_treated",  # or "not_yet_treated"
    anticipation=0,
    bootstrap=1000,
)
print(result.summary_table())
```

## When to use CS

- **Staggered treatment timing** — the headline use-case
- Multiple cohorts treated at different dates
- Heterogeneity across cohorts plausible

## Control groups

- `"never_treated"` — units never receiving the treatment. Preferred when such units exist.
- `"not_yet_treated"` — units treated in the future serve as controls for earlier cohorts. Use when never-treated units don't exist.

## Event-time aggregation

```python
result = estimate(panel, method="cs", event_time_agg="simple")
# or: "calendar", "dynamic", "group", "overall"
```

## Caveats (per current adapter)

- The CS adapter silently drops `cluster=` because the upstream `differences` package handles clustering via columns on the dataframe itself. Include your cluster column in the panel and `differences` picks it up.
- `period_kind ∉ {"timestamp", "integer"}` is rejected — float / ordinal periods aren't supported by the upstream.

## References

- Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200–230. https://doi.org/10.1016/j.jeconom.2020.12.001
- Reference implementation: [`differences`](https://github.com/bernardodionisi/differences)
