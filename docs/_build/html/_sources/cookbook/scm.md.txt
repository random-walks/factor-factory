# Synthetic Control Method

```python
from factor_factory.engines.scm import estimate

result = estimate(
    panel,
    methods=("augmented",),  # or "pysyncon" for classic SCM
    outcome="gdp",
)[0]
print(result.summary_table())
print(result.donor_weights)
```

## Classic vs Augmented

- **`pysyncon`** (classic, Abadie et al. 2010) — simplex donor weights, good pre-period fit required.
- **`augmented`** (Ben-Michael et al. 2021, homegrown) — adds ridge outcome-model correction for poor pre-period fit. Controlled by `ridge_lambda=` kwarg (default 1.0).

## Comparison to SDID

SCM assumes a single treated unit with a specific rollout. For multiple treated units sharing a single date, use `engines.sdid`. For staggered rollout, use `engines.did.callaway_santanna`.

## References

- Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic control methods for comparative case studies. *JASA*, 105(490), 493–505.
- Ben-Michael, E., Feller, A., & Rothstein, J. (2021). The augmented synthetic control method. *JASA*, 116(536), 1789–1803.
