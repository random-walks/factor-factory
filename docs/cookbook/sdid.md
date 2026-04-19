# Synthetic Difference-in-Differences (SDID)

Arkhangelsky et al. (2021) combine **unit weights** (synthetic-control style) with **time weights** and a weighted DiD estimator. The SDID estimator is consistent under weaker parallel-trends assumptions than TWFE because the time weights down-weight pre-periods that don't match the post-period trend.

```python
from factor_factory.engines.sdid import estimate

result = estimate(panel)  # binary block treatment, SDID defaults

print(f"ATT = {result.att:.3f} ± {result.std_error:.3f}")
print(result.unit_weights.head(10))   # synthetic-control weights
print(result.time_weights.head(10))   # time-averaging weights
```

## When to use SDID

- Parallel-trends fragility in vanilla DiD (heterogeneous unit trends)
- Binary block treatment (all treated units share a common adoption date)
- ≥ 2 treated units (inference quality improves quickly with treated count)

## When NOT to use SDID

- Staggered adoption (SDID assumes a common treatment date; use CS / SA / BJS instead)
- Single treated unit — placebo inference degenerates to a rough sigma estimate; the jackknife is undefined. Batch 5 lands proper placebo-test inference for this case.
- Panels where the pre-period is shorter than the post-period (time weights can't regularize well)

## Inference

```python
result = estimate(panel, inference="jackknife")  # default for n_treated >= 2
result = estimate(panel, inference="placebo")    # Batch 5 — placebo-based p-values
```

The current jackknife holds `omega` and `lam` fixed across leave-one-out iterations (matches the R `synthdid` default). Re-solving the QPs per iteration is correct but ~N_tr × slower.

## Prop-99 validation *(Batch 5)*

The AER paper's canonical California-Prop-99 example is reproduced in `tests/test_sdid_prop99.py`.

## References

- Arkhangelsky, D., Athey, S., Hirshberg, D. A., Imbens, G. W., & Wager, S. (2021). Synthetic Difference-in-Differences. *American Economic Review*, 111(12), 4088–4118. https://doi.org/10.1257/aer.20190159
- Reference R implementation: [`synthdid`](https://synth-inference.github.io/synthdid/)
