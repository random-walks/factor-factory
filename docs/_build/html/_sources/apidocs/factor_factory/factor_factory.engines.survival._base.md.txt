---
orphan: true
---

# {py:mod}`factor_factory.engines.survival._base`

```{py:module} factor_factory.engines.survival._base
```

```{autodoc2-docstring} factor_factory.engines.survival._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SurvivalResult <factor_factory.engines.survival._base.SurvivalResult>`
  - ```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult
    :summary:
    ```
* - {py:obj}`SurvivalEngine <factor_factory.engines.survival._base.SurvivalEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalEngine
    :summary:
    ```
````

### API

`````{py:class} SurvivalResult
:canonical: factor_factory.engines.survival._base.SurvivalResult

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult
```

````{py:attribute} method
:canonical: factor_factory.engines.survival._base.SurvivalResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.method
```

````

````{py:attribute} median_survival
:canonical: factor_factory.engines.survival._base.SurvivalResult.median_survival
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.median_survival
```

````

````{py:attribute} n_subjects
:canonical: factor_factory.engines.survival._base.SurvivalResult.n_subjects
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.n_subjects
```

````

````{py:attribute} n_events
:canonical: factor_factory.engines.survival._base.SurvivalResult.n_events
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.n_events
```

````

````{py:attribute} coefficients
:canonical: factor_factory.engines.survival._base.SurvivalResult.coefficients
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.coefficients
```

````

````{py:attribute} hazard_ratios
:canonical: factor_factory.engines.survival._base.SurvivalResult.hazard_ratios
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.hazard_ratios
```

````

````{py:attribute} p_values
:canonical: factor_factory.engines.survival._base.SurvivalResult.p_values
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.p_values
```

````

````{py:attribute} confidence_intervals
:canonical: factor_factory.engines.survival._base.SurvivalResult.confidence_intervals
:type: dict[str, tuple[float, float]] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.confidence_intervals
```

````

````{py:attribute} survival_curve
:canonical: factor_factory.engines.survival._base.SurvivalResult.survival_curve
:type: pandas.DataFrame | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.survival_curve
```

````

````{py:attribute} proportional_hazards_test
:canonical: factor_factory.engines.survival._base.SurvivalResult.proportional_hazards_test
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.proportional_hazards_test
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.survival._base.SurvivalResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.survival._base.SurvivalResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.survival._base.SurvivalResult.to_dict

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.survival._base.SurvivalResult.summary_table

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalResult.summary_table
```

````

`````

`````{py:class} SurvivalEngine
:canonical: factor_factory.engines.survival._base.SurvivalEngine

Bases: {py:obj}`typing.Protocol`

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.survival._base.SurvivalEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, duration_col: str = 'duration', event_col: str = 'event', covariates: tuple[str, ...] = (), cluster: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.survival._base.SurvivalResult
:canonical: factor_factory.engines.survival._base.SurvivalEngine.fit

```{autodoc2-docstring} factor_factory.engines.survival._base.SurvivalEngine.fit
```

````

`````
