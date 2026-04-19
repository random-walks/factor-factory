# Spec: Diagnostics contract

`factor_factory.diagnostics.*` ships the diagnostic primitives that
every showcase ends up writing. The four required-for-v0.1 ones are
specified below; the others are sketches.

## Required for v0.1 (Phase 1 acceptance gate)

### 1. Standardized mean differences

```python
def standardized_mean_differences(
    panel: Panel,
    *,
    treated_col: str = "treated_unit",
    covariates: tuple[str, ...],
    pre_treatment_only: bool = True,
) -> pd.DataFrame:
    """Compute SMDs between treated + control units on each covariate.

    Useful as a balance check before running DiD.

    Parameters
    ----------
    panel : Panel
        Must have `treated_col` (binary, time-invariant or computed
        as time-invariant via per-unit mean).
    covariates : tuple of str
        Column names to compute SMDs for. Each must exist on the
        panel as a numeric column.
    pre_treatment_only : bool, default True
        If True and the panel has a `treatment` column, restrict to
        pre-treatment periods only. If False, use all periods.

    Returns
    -------
    pd.DataFrame
        Columns: covariate, treated_mean, control_mean, diff,
        pooled_sd, smd, imbalance_flag (one of "", "*" for
        |SMD|>0.1, "***" for |SMD|>0.5).
    """
```

### 2. Parallel-trends visual

```python
def parallel_trends_plot(
    panel: Panel,
    *,
    treated_col: str = "treated_unit",
    outcome_col: str | None = None,
    treatment_date: date | None = None,
    ax: matplotlib.axes.Axes | None = None,
) -> matplotlib.figure.Figure:
    """Plot mean outcome over time for treated vs. control.

    Parameters
    ----------
    panel : Panel
        Must have `treated_col` and an outcome column.
    outcome_col : str, optional
        Defaults to `panel.outcome_col`.
    treatment_date : date, optional
        If given, draws a vertical line at this date. If None and
        the panel has treatment_events, uses the first event's date.
    ax : matplotlib.axes.Axes, optional
        Plot to this axis. If None, creates a new figure.

    Returns
    -------
    matplotlib.figure.Figure
        The figure containing the plot.
    """
```

### 3. MultiIndex assertions

```python
def multi_index_assertions(panel: Panel) -> None:
    """Raise AssertionError if the panel violates structural invariants.

    Used as a defensive check at the start of any analysis cell.
    Idempotent — safe to call multiple times.

    Checks:
    - Index is MultiIndex with names ('unit_id', 'period')
    - unit_id is str dtype
    - period is pd.Timestamp dtype
    - Index is sorted
    - Panel is balanced (every unit has every period)
    - Outcome column exists
    """
```

### 4. Residual diagnostics

```python
def residual_diagnostics(
    residuals: pd.Series,
    *,
    fitted_values: pd.Series | None = None,
    sample_size_for_shapiro: int = 5000,
) -> dict:
    """Run the canonical normality + heteroskedasticity test set on
    fitted residuals.

    Parameters
    ----------
    residuals : pd.Series
        Residuals from a fitted regression model.
    fitted_values : pd.Series, optional
        If provided, also runs Breusch-Pagan heteroskedasticity test.
        If None, only normality tests are run.
    sample_size_for_shapiro : int, default 5000
        Shapiro-Wilk's sample-size limit. If residuals.size > this,
        a random sample is used (with a fixed seed for reproducibility).

    Returns
    -------
    dict with keys:
        n : int
        mean : float
        std : float
        jarque_bera_stat : float
        jarque_bera_p : float
        shapiro_wilk_stat : float
        shapiro_wilk_p : float
        breusch_pagan_stat : float | None
        breusch_pagan_p : float | None
        normality_passes : bool  (jarque_bera_p > 0.05)
        homoskedasticity_passes : bool | None
    """
```

## Required for v0.2+ (engine fan-out)

These ship as engines arrive. Each follows the spec sketch below.

### Outliers + leverage

```python
def cooks_distance(
    panel: Panel,
    *,
    fitted_residuals: pd.Series,
    leverage: pd.Series,
) -> pd.Series:
    """Per-observation Cook's distance. Returns Series indexed like the panel."""

def dfbetas(
    panel: Panel,
    *,
    fitted_model,  # statsmodels or linearmodels result
    coefficient: str,
) -> pd.Series:
    """Per-observation DFBETAS for a specific coefficient."""

def influence_summary(
    panel: Panel,
    *,
    fitted_residuals: pd.Series,
    leverage: pd.Series,
    cooks_threshold: float = "4/n",  # or numeric
) -> pd.DataFrame:
    """Combined influence-flagging table."""
```

### Distributions

```python
def distribution_diagnostics(
    series: pd.Series,
) -> dict:
    """Skewness, kurtosis, Jarque-Bera; useful for outcome-distribution audits."""
```

### Missingness

```python
def missingness_heatmap(
    panel: Panel,
    *,
    by: Literal["unit", "period", "both"] = "both",
) -> matplotlib.figure.Figure:
    """Visualize where the panel has nulls."""

def missingness_summary(
    panel: Panel,
) -> pd.DataFrame:
    """Per-column + per-unit + per-period null counts."""
```

### Balance (richer than SMD)

```python
def balance_check(
    panel: Panel,
    *,
    treated_col: str,
    covariates: tuple[str, ...],
    methods: tuple[Literal["smd", "ks", "wasserstein"], ...] = ("smd",),
) -> pd.DataFrame:
    """Multi-metric balance comparison."""
```

## Conventions

- All diagnostic functions are **side-effect-free** (no logging,
  no plotting unless that's the function's job). They return data
  or matplotlib figures.
- Plotting functions accept an optional `ax` parameter for use in
  subplots.
- All functions raise `ValueError` with a clear message when inputs
  violate expectations (e.g., missing column, wrong dtype).
- Diagnostic results are `dict`s (small, JSON-serializable) or
  `pd.DataFrame`s (tabular). Frozen dataclasses are reserved for
  engine results.

## Test coverage

`tests/test_diagnostics/` mirrors the source layout. Each diagnostic
function is tested against:

1. A synthetic panel with known properties (balanced, normal
   residuals, etc.) — should pass / show clean
2. A synthetic panel with violations (imbalanced, heavy-tailed
   residuals) — should flag
3. An edge case (single unit, single period, all-null column) —
   should raise a clear error
