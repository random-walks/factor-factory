# Testing

## Test layout

```
factor_factory/tests/
├── _fixtures/
│   └── cross_domain.py     # 15 synthetic Panels covering every shipping domain
├── test_engines/
│   ├── test_did_conformance.py
│   ├── test_callaway_santanna.py
│   ├── test_survival.py
│   ├── test_event_study.py
│   ├── test_sdid.py
│   ├── test_mediation.py
│   └── ...                 # one file per adapter
├── test_cross_domain.py    # universal Panel-contract + fixture parametrization
├── test_panel_contract.py
├── test_treatment_events.py
├── test_geography.py
├── test_diagnostics.py
├── test_jellycell_integration.py
└── properties/             # hypothesis property-based (Batch 14+)
```

## Running

```bash
make test                 # full suite
make test-engines
make test-cross-domain
uv run pytest factor_factory/tests/test_engines/test_sdid.py::test_sdid_recovers_known_att -v
```

Current runtime: ~3 s locally, ~30 s in CI. Keep this budget — stay under 2 min total wall-clock in CI including lint + mypy.

## Optional-dependency gating

Adapters behind optional extras use `pytest.importorskip` at the top of the test module:

```python
import pytest
linearmodels = pytest.importorskip("linearmodels")
```

CI installs the specific extras its job needs. The default test job installs `[did,survival,event-study,dev]`; family-specific jobs install their own extras.

## Truth-tracking fixtures

Every conformance test asserts recovery of a known ground truth:

```python
def test_twfe_recovers_known_att():
    panel = staggered_did_panel()                         # fixture
    result = estimate(panel, method="twfe")
    truth = panel.provenance.annotations["ground_truth_att"]
    assert abs(result.estimate - truth) < 2 * result.std_error
```

Ground truths live in `panel.provenance.annotations` — read them from there, don't hardcode in the test. The fixture is the single source of truth.

## Property-based tests (Batch 14+)

```bash
make test-property
```

Strategies live in `factor_factory/tests/properties/strategies.py`. Panel shapes, TreatmentEvent configs, and record-stream distributions all have strategies.

## Snapshot tests for tearsheets (Batch 14+)

Uses `pytest-regressions`. Rendering a demo showcase's 5 tearsheets produces JSON + HTML outputs; we snapshot those. Any drift fails the test.

```bash
uv run pytest factor_factory/tests/test_jellycell_integration.py --regen-snapshots
```

`--regen-snapshots` intentionally updates baselines when the template change is wanted.

## Benchmarks (Batch 14+)

`pytest-benchmark` over `Panel.from_records` on a 100k-record fixture + engine fits on a 10k-record fixture. CI flags > 2× regressions.

```bash
uv run pytest factor_factory/tests/benchmarks/ --benchmark-only
```
