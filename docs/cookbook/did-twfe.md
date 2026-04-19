# DiD — Two-way fixed effects

Two-way fixed-effects (TWFE) DiD is the classic starting point. Under a single treatment event with homogeneous effects and parallel pre-trends, TWFE recovers the ATT unbiasedly.

```python
from datetime import date
from factor_factory.tidy import Panel, TreatmentEvent
from factor_factory.engines.did import estimate

panel = Panel.from_records(
    records,
    dimension="community_district",
    freq="ME",
    treatment_events=(TreatmentEvent(
        name="rat_pilot",
        treated_units=("MN-01", "MN-02"),
        treatment_date=date(2024, 6, 1),
        dimension="community_district",
    ),),
    outcome_col="complaint_count",
)

result = estimate(panel, method="twfe", cluster="unit_id")
print(result.summary_table())
```

## When to use TWFE

- Single treatment event (one cohort, one timing)
- Homogeneous treatment effects assumed
- Parallel pre-trends verifiable

## When NOT to use TWFE

- **Staggered rollout** → use `method="cs"` (Callaway-Sant'Anna) or `method="sa"` (Sun-Abraham, Batch 6). TWFE under staggered adoption has the Goodman-Bacon bias; forbidden comparisons contaminate the ATT.
- **Heterogeneous treatment effects across cohorts** → same as above.
- **Many treated units with heterogeneous trends** → `method="sdid"` (Synthetic DiD).

See the [Callaway-Sant'Anna cookbook](did-callaway-santanna.md) for the staggered-rollout pattern.

## Clustered standard errors

Pass `cluster=<column-name>` to cluster at the unit level (default) or any other panel column (e.g. `cluster="state"` for state-level clustering in a county-level panel).

## References

- Goodman-Bacon, A. (2021). Difference-in-differences with variation in treatment timing. *Journal of Econometrics*, 225(2), 254–277.
