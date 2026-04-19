# Spec: Engine Protocol pattern

Every stats method family in factor-factory follows the same
contract: a Protocol-typed engine + a frozen result dataclass + a
registry-backed `estimate()` dispatcher.

This spec pins the pattern. Every engine adapter MUST conform.

## The pattern (one example: DiD)

### 1. Frozen result dataclass

```python
# factor_factory/engines/did/_base.py
from dataclasses import dataclass

@dataclass(frozen=True)
class DidResult:
    """Result of a single DiD estimation."""

    # ─── Required for all engines ──────────────────────────────────
    method: str                          # e.g. "callaway_santanna"
    att: float                           # the headline aggregate ATT
    se: float                            # standard error of att
    ci_95: tuple[float, float]           # 95% CI (lower, upper)
    p_value: float                       # null: ATT == 0
    n: int                               # observation count

    # ─── Optional, set when available ──────────────────────────────
    # Event-study coefficients keyed by relative period (negative=pre, positive=post)
    cohort_atts: dict[int, float] | None = None
    cohort_ses: dict[int, float] | None = None

    # Method-specific diagnostic info (e.g., pre-trend test, donor weights)
    diagnostics: dict | None = None

    # The raw output object from the underlying package, for users who
    # want full access. Do NOT rely on its shape across engines.
    meta: dict | None = None
```

### 2. Engine Protocol

```python
# factor_factory/engines/did/_base.py
from typing import Protocol
from ..tidy import Panel

class DidEngine(Protocol):
    """Protocol every DiD engine adapter must satisfy."""

    name: str  # short identifier; "twfe", "cs", "sa", "bjs"

    def fit(self,
            panel: Panel,
            *,
            outcome: str,
            treatment: str = "treatment",
            cluster: str | None = None,
            **engine_specific_kwargs) -> DidResult:
        """Fit the DiD model on `panel`. Returns a DidResult."""
        ...
```

### 3. Engine adapter (one per implementation)

```python
# factor_factory/engines/did/twfe.py
from linearmodels.panel import PanelOLS
from ._base import DidEngine, DidResult

class TwfeEngine:
    name = "twfe"

    def fit(self, panel, *, outcome, treatment="treatment", cluster=None, **_):
        df = panel.df
        y = df[outcome]
        x = df[[treatment]]
        cov_kw = {"cov_type": "clustered", "cluster_entity": True} if cluster else {"cov_type": "robust"}
        result = PanelOLS(y, x, entity_effects=True, time_effects=True).fit(**cov_kw)
        att = float(result.params[treatment])
        se = float(result.std_errors[treatment])
        return DidResult(
            method=self.name,
            att=att,
            se=se,
            ci_95=(float(result.conf_int().loc[treatment, "lower"]),
                   float(result.conf_int().loc[treatment, "upper"])),
            p_value=float(result.pvalues[treatment]),
            n=int(result.nobs),
            meta={"r_squared": float(result.rsquared)},
        )
```

### 4. Registry + dispatcher

```python
# factor_factory/engines/_registry.py
from typing import Generic, TypeVar

E = TypeVar("E")

class EngineRegistry(Generic[E]):
    """Lazy-loading engine registry. Engines that depend on missing
    optional packages raise ImportError only when called."""

    def __init__(self, engines: dict[str, E]):
        self._engines = engines

    def __getitem__(self, name: str) -> E:
        if name not in self._engines:
            raise KeyError(
                f"Unknown engine '{name}'. Available: {sorted(self._engines)}"
            )
        return self._engines[name]

    def register(self, name: str, engine: E) -> None:
        """Register a new engine at runtime (e.g., from a downstream package)."""
        self._engines[name] = engine

    def available(self) -> list[str]:
        return sorted(self._engines)
```

```python
# factor_factory/engines/did/__init__.py
from .._registry import EngineRegistry
from ._base import DidEngine, DidResult
from .twfe import TwfeEngine

# Engines that need optional deps register lazily
_engines = {"twfe": TwfeEngine()}

try:
    from .callaway_santanna import CallawaySantannaEngine
    _engines["cs"] = CallawaySantannaEngine()
except ImportError:
    pass  # `factor-factory[did]` extra not installed

# ... same for "sa", "bjs"

registry = EngineRegistry[DidEngine](_engines)

def estimate(panel,
             *,
             methods: tuple[str, ...] = ("twfe",),
             outcome: str,
             treatment: str = "treatment",
             cluster: str | None = None,
             **engine_specific_kwargs) -> "DidResults":
    """Estimate the DiD effect under one or more methods.

    Returns a DidResults wrapper with `.summary_table()` for
    side-by-side comparison."""
    results = [
        registry[m].fit(panel, outcome=outcome, treatment=treatment,
                        cluster=cluster, **engine_specific_kwargs)
        for m in methods
    ]
    return DidResults(results)


class DidResults:
    """Wrapper around a list of DidResult objects with comparison helpers."""

    def __init__(self, results: list[DidResult]):
        self.results = results

    def __iter__(self):
        return iter(self.results)

    def summary_table(self) -> "pd.DataFrame":
        """Side-by-side table: method × (att, se, p, ci_lo, ci_hi, n)."""
        ...
```

## The pattern repeats for every method family

`factor_factory/engines/<family>/`:
- `_base.py` — Protocol + Result dataclass
- `__init__.py` — registry + `estimate()` (or family-specific dispatcher)
- `<engine_name>.py` per implementation
- `tests/test_<family>_conformance.py` per family (see § Conformance)

Result dataclasses per family:

| Family | Result class | Required fields |
|---|---|---|
| `did/` | `DidResult` | method, att, se, ci_95, p_value, n |
| `rdd/` | `RddResult` | method, treatment_effect, se, ci_95, p_value, bandwidth, n_left, n_right |
| `scm/` | `ScmResult` | method, att, donor_weights, pre_treatment_mspe, n_donors |
| `changepoint/` | `ChangepointResult` | method, breakpoints, n_segments, penalty |
| `stl/` | `STLResult` | method, trend, seasonal, residual, period, seasonal_amplitude |
| `panel_reg/` | `PanelRegressionResult` | method, coefficients, std_errors, p_values, r_squared, n_observations |
| `inequality/` | `InequalityResult` | method, total, between_group, within_group, n_units |
| `oaxaca_blinder/` | `OaxacaBlinderResult` | total_gap, explained, unexplained, ... |
| `spatial/` | `MoranResult`, `LISAResult`, `SpatialLagResult` | (per docstring) |
| `reporting_bias/` | `LatentReportingResult` | reporting_probabilities, converged, n_iterations |
| `hawkes/` | `HawkesResult` | mu, alpha, beta, branching_ratio |

## Conformance tests

Every engine adapter MUST pass:

```python
# factor_factory/tests/test_engines/test_did_conformance.py
import pytest
from factor_factory.engines.did import registry as did_registry
from factor_factory.engines.did._base import DidResult
from factor_factory.tests._fixtures.synthetic_panels import (
    small_treatment_effect_panel,
    null_effect_panel,
)

@pytest.fixture(params=did_registry.available())
def engine(request):
    return did_registry[request.param]

def test_returns_did_result(engine):
    panel = small_treatment_effect_panel()
    result = engine.fit(panel, outcome=panel.outcome_col)
    assert isinstance(result, DidResult)
    assert result.method == engine.name
    assert isinstance(result.att, float)
    assert isinstance(result.ci_95, tuple) and len(result.ci_95) == 2
    assert 0 <= result.p_value <= 1
    assert result.n > 0

def test_recovers_known_treatment_effect(engine):
    panel = small_treatment_effect_panel()  # ATT = 5.0
    result = engine.fit(panel, outcome=panel.outcome_col)
    assert abs(result.att - 5.0) < 2.0, (
        f"{engine.name}: ATT {result.att} differs from true 5.0 by >2"
    )

def test_null_effect_not_significant_at_05(engine):
    panel = null_effect_panel()
    result = engine.fit(panel, outcome=panel.outcome_col)
    assert result.p_value > 0.05, (
        f"{engine.name} found significant effect on null panel"
    )

def test_ci_brackets_estimate(engine):
    panel = small_treatment_effect_panel()
    result = engine.fit(panel, outcome=panel.outcome_col)
    lo, hi = result.ci_95
    assert lo <= result.att <= hi
```

The `null_effect_panel` and `small_treatment_effect_panel` fixtures
provide ground truth. Every new engine adapter is tested against the
same fixtures, ensuring contract conformance + sanity of the
underlying math.

## Adding a new engine

To add a new DiD engine adapter:

1. Add a module under `factor_factory/engines/did/<engine_name>.py`
   implementing the `DidEngine` Protocol
2. If it needs an optional dep, add to `pyproject.toml`'s `[did]`
   extra
3. Register it in `factor_factory/engines/did/__init__.py` (lazy
   import in a try/except)
4. The conformance tests automatically pick it up (parametrized
   over `did_registry.available()`)
5. Add a one-paragraph docstring + canonical citation to the engine
   class
6. Update `docs/getting-started.md` if the new engine introduces
   user-facing concepts

## Naming conventions

- Engine class names: `<MethodName>Engine` (e.g., `TwfeEngine`,
  `CallawaySantannaEngine`)
- Engine `name` attribute: short snake_case (e.g., `"twfe"`,
  `"cs"`, `"sa"`, `"bjs"`)
- Result dataclasses: `<MethodFamily>Result` (e.g., `DidResult`)
- Result wrappers (when multiple results returned): `<Family>Results`

## Open questions

- **Result dataclass evolution**: when an engine produces extra
  diagnostic fields not in the Result spec, where do they live?
  Default: `meta` dict. Revisit if patterns emerge.
- **Cross-engine result combining**: `DidResults` has
  `summary_table()`. Should it also have `meta_analysis()` (e.g.,
  inverse-variance weighted ATT across engines)? Defer; Phase 2
  decision.
- **Engine versioning**: when an underlying package (e.g., rdrobust)
  ships a breaking API change, the adapter version may need to bump.
  Defer formal policy until first occurrence.
