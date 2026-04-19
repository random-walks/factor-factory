# Four-way mediation decomposition

VanderWeele (2014) decomposes a treatment's total effect into four components:

- **CDE** — Controlled Direct Effect (no mediation, no interaction)
- **INT_ref** — Reference Interaction (interaction at the control mediator level)
- **INT_med** — Mediated Interaction (interaction only activated via the mediator)
- **PIE** — Pure Indirect Effect (mediated, non-interactive)

The four sum to the Total Effect. This is a strict superset of the Imai-Keele-Tingley 2-component NDE/NIE decomposition available in `statsmodels.stats.mediation`.

```python
from factor_factory.engines.mediation import estimate

result = estimate(
    panel,
    treatment="treatment",
    mediator="mediator",
    outcome="outcome",
    covariates=("age", "bmi"),
    bootstrap=1000,
)
print(f"CDE     = {result.cde:.3f} ± {result.std_errors['cde']:.3f}")
print(f"INT_ref = {result.int_ref:.3f} ± {result.std_errors['int_ref']:.3f}")
print(f"INT_med = {result.int_med:.3f} ± {result.std_errors['int_med']:.3f}")
print(f"PIE     = {result.pie:.3f} ± {result.std_errors['pie']:.3f}")
print(f"Total   = {result.cde + result.int_ref + result.int_med + result.pie:.3f}")
```

## When to use four-way vs two-way

- **Four-way** — whenever you suspect treatment × mediator interaction. The four-way decomposition surfaces it via `INT_ref` and `INT_med`.
- **Two-way (NDE/NIE)** — when interaction is ruled out a priori or not of interest. `statsmodels.stats.mediation` is fine.

## Families

Currently supported (v0.1):

- Linear outcome + linear mediator

Batch 5 adds:

- Logistic outcome + linear mediator (closed-form via VanderWeele 2014 §3)
- Logistic outcome + logistic mediator (Monte-Carlo integration over mediator)
- Linear outcome + logistic mediator

## Sensitivity analysis *(Batch 5)*

Unobserved-confounding sensitivity (the rho-test from R `CMAverse`):

```python
sensitivity = result.sensitivity(rho=np.linspace(-0.5, 0.5, 21))
```

Returns a DataFrame showing how each component shifts as a function of the assumed unmeasured-confounding correlation `rho`.

## Validation

The `mediation_panel` fixture in `_fixtures/cross_domain.py` has a known ground truth:

| Component | True | Estimated | SE |
|---|---|---|---|
| CDE | 2.00 | 2.004 | 0.087 |
| PIE | 1.50 | 1.514 | 0.070 |
| INT_med | 0.45 | 0.397 | 0.085 |
| INT_ref | 0.15 | 0.137 | 0.030 |

All four recovered within 1 SE.

## References

- VanderWeele, T. J. (2014). A unification of mediation and interaction: A four-way decomposition. *Epidemiology*, 25(5), 749–761. https://doi.org/10.1097/EDE.0000000000000121
- Reference R implementation: [`CMAverse`](https://bs1125.github.io/CMAverse/)
