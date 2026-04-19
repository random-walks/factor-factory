# Regression Discontinuity

```python
from factor_factory.engines.rdd import estimate

# Sharp RDD: treatment = 1(score >= cutoff)
result = estimate(
    panel,
    methods=("rd_robust",),
    outcome="earnings",
    running_variable="test_score",
    cutoff=60.0,
    design="sharp",
    polynomial_order=1,
    kernel="triangular",
    bwselect="mserd",
)[0]
print(result.summary_table())
```

## Fuzzy RDD

When treatment receipt is non-deterministic (e.g. scholarship offer → take-up isn't 100%):

```python
result = estimate(
    panel,
    methods=("rd_robust",),
    outcome="earnings",
    running_variable="test_score",
    cutoff=60.0,
    design="fuzzy",
    treatment="received_scholarship",  # binary take-up indicator
)[0]
print(f"First-stage F: {result.first_stage_f}")
```

## Bandwidth selection

`bwselect` options (passed through to `rdrobust`):

- `"mserd"` — default; MSE-optimal symmetric bandwidth
- `"msetwo"` — separate bandwidths on each side of the cutoff
- `"msesum"` — sum-of-squared-bias-plus-variance optimal
- `"cerrd"` — coverage-error-rate optimal

## References

- Calonico, S., Cattaneo, M. D., & Titiunik, R. (2014). Robust nonparametric confidence intervals for regression-discontinuity designs. *Econometrica*, 82(6), 2295–2326. https://doi.org/10.3982/ECTA11757
- Reference implementation: [`rdrobust`](https://rdpackages.github.io/rdrobust/)
