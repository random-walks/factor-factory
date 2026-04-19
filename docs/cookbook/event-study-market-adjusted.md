# Event study — market-adjusted returns

The market-adjusted baseline uses the cross-sectional control mean as the benchmark return. No market model fitting — hence no extra dependencies.

```python
from factor_factory.engines.event_study import estimate

result = estimate(
    panel,
    method="market_adjusted",
    event_window=(-3, 5),  # days relative to event
    estimation_window=(-252, -30),
)
print(result.car)
print(result.t_stat, result.p_value)
```

## When to use

- Quick screening of event effects
- No market-model fit available or needed
- The control mean is a reasonable proxy for expected returns

## When NOT to use

- When proper factor-model residuals are required (earnings-announcement effects, policy event studies in finance). Use `method="fama_french"` *(Batch 6)* instead.
- Long event windows where mean-reversion matters.

## References

- MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature*, 35(1), 13–39.
