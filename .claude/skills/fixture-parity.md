---
name: fixture-parity
description: Every new engine adapter MUST ship with a truth-tracking synthetic fixture in cross_domain.py AND a parametrized conformance test. Triggers when adding a file under factor_factory/engines/.
---

# Fixture parity

Every adapter that lands in `factor_factory/engines/` must have a matching synthetic fixture and a conformance test that proves the adapter recovers the ground truth.

## The fixture

Add to `factor_factory/tests/_fixtures/cross_domain.py`:

```python
def <family>_<scenario>_panel() -> Panel:
    """
    Synthetic Panel with known ground truth embedded in the provenance.

    Ground truth: ATT = 4.0 (units: outcome-level), n_units_treated = 5,
    treatment_date = 2024-06-01, controls = random walk, treated = random
    walk + 4 * 1[t ≥ treatment_date]. Recoverable by any DiD estimator
    within 1 SE at n=100 units.
    """
    rng = np.random.default_rng(SEED)
    # ... build records ...
    panel = Panel.from_records(records, ...)
    # Stash the truth in provenance.annotations so tests can assert against it:
    panel.provenance.annotations["ground_truth_att"] = 4.0
    return panel
```

## The test

```python
# factor_factory/tests/test_engines/test_<family>_<adapter>.py
import pytest
from factor_factory.tests._fixtures.cross_domain import <family>_<scenario>_panel

pytestmark = pytest.mark.importorskip("<upstream_package_or_skip>")


def test_<adapter>_recovers_ground_truth():
    panel = <family>_<scenario>_panel()
    result = estimate(panel, method="<adapter-key>")
    truth = panel.provenance.annotations["ground_truth_att"]
    assert abs(result.estimate - truth) < max(2 * result.std_error, 0.1 * truth), (
        f"Recovered {result.estimate} ± {result.std_error} vs ground truth {truth}"
    )
```

## Parametrize the cross-domain conformance test

In `factor_factory/tests/test_cross_domain.py`, register the new fixture so it runs through the universal Panel-contract conformance loop. Every fixture must:

- pass `Panel.validate()`
- round-trip through parquet via `panel.to_parquet()` + `Panel.from_parquet()`
- produce a sane `Panel.summary()` dict
- expose `provenance.annotations["ground_truth_<metric>"]` for the metric the family produces

## Why this matters

Without a truth-tracking fixture, an engine adapter is just claiming to implement a method — not proving it. SDID + Mediation validated against ground truth to within 1 SE before merge; every subsequent family must meet or exceed that bar.

## Tolerance guidance

- For unbiased estimators: `abs(recovered - truth) < 2 * se`
- For estimators with known finite-sample bias: document the bias in the adapter docstring and use `abs(recovered - expected_biased) < 2 * se`
- For methods that return a distribution (bootstrap CIs): assert the 95% CI contains the truth
