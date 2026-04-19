---
orphan: true
---

# {py:mod}`factor_factory.engines.mediation._base`

```{py:module} factor_factory.engines.mediation._base
```

```{autodoc2-docstring} factor_factory.engines.mediation._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MediationResult <factor_factory.engines.mediation._base.MediationResult>`
  - ```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult
    :summary:
    ```
* - {py:obj}`MediationEngine <factor_factory.engines.mediation._base.MediationEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationEngine
    :summary:
    ```
````

### API

`````{py:class} MediationResult
:canonical: factor_factory.engines.mediation._base.MediationResult

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult
```

````{py:attribute} method
:canonical: factor_factory.engines.mediation._base.MediationResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.method
```

````

````{py:attribute} n_subjects
:canonical: factor_factory.engines.mediation._base.MediationResult.n_subjects
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.n_subjects
```

````

````{py:attribute} treatment
:canonical: factor_factory.engines.mediation._base.MediationResult.treatment
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.treatment
```

````

````{py:attribute} mediator
:canonical: factor_factory.engines.mediation._base.MediationResult.mediator
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.mediator
```

````

````{py:attribute} outcome
:canonical: factor_factory.engines.mediation._base.MediationResult.outcome
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.outcome
```

````

````{py:attribute} total_effect
:canonical: factor_factory.engines.mediation._base.MediationResult.total_effect
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.total_effect
```

````

````{py:attribute} cde
:canonical: factor_factory.engines.mediation._base.MediationResult.cde
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.cde
```

````

````{py:attribute} int_ref
:canonical: factor_factory.engines.mediation._base.MediationResult.int_ref
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.int_ref
```

````

````{py:attribute} int_med
:canonical: factor_factory.engines.mediation._base.MediationResult.int_med
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.int_med
```

````

````{py:attribute} pie
:canonical: factor_factory.engines.mediation._base.MediationResult.pie
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.pie
```

````

````{py:attribute} decomposition_residual
:canonical: factor_factory.engines.mediation._base.MediationResult.decomposition_residual
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.decomposition_residual
```

````

````{py:attribute} total_effect_se
:canonical: factor_factory.engines.mediation._base.MediationResult.total_effect_se
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.total_effect_se
```

````

````{py:attribute} cde_se
:canonical: factor_factory.engines.mediation._base.MediationResult.cde_se
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.cde_se
```

````

````{py:attribute} int_ref_se
:canonical: factor_factory.engines.mediation._base.MediationResult.int_ref_se
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.int_ref_se
```

````

````{py:attribute} int_med_se
:canonical: factor_factory.engines.mediation._base.MediationResult.int_med_se
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.int_med_se
```

````

````{py:attribute} pie_se
:canonical: factor_factory.engines.mediation._base.MediationResult.pie_se
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.pie_se
```

````

````{py:attribute} confidence_intervals
:canonical: factor_factory.engines.mediation._base.MediationResult.confidence_intervals
:type: dict[str, tuple[float, float]] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.confidence_intervals
```

````

````{py:attribute} proportion_eliminated
:canonical: factor_factory.engines.mediation._base.MediationResult.proportion_eliminated
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.proportion_eliminated
```

````

````{py:attribute} proportion_mediated
:canonical: factor_factory.engines.mediation._base.MediationResult.proportion_mediated
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.proportion_mediated
```

````

````{py:attribute} outcome_family
:canonical: factor_factory.engines.mediation._base.MediationResult.outcome_family
:type: str
:value: >
   'linear'

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.outcome_family
```

````

````{py:attribute} mediator_family
:canonical: factor_factory.engines.mediation._base.MediationResult.mediator_family
:type: str
:value: >
   'linear'

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.mediator_family
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.mediation._base.MediationResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.mediation._base.MediationResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.mediation._base.MediationResult.to_dict

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.mediation._base.MediationResult.summary_table

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.summary_table
```

````

````{py:method} sensitivity(rho_range: tuple[float, float] = (-0.5, 0.5), n_points: int = 21) -> pandas.DataFrame
:canonical: factor_factory.engines.mediation._base.MediationResult.sensitivity

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationResult.sensitivity
```

````

`````

`````{py:class} MediationEngine
:canonical: factor_factory.engines.mediation._base.MediationEngine

Bases: {py:obj}`typing.Protocol`

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.mediation._base.MediationEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str, mediator: str, covariates: tuple[str, ...] = (), n_bootstrap: int = 0, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.mediation._base.MediationResult
:canonical: factor_factory.engines.mediation._base.MediationEngine.fit

```{autodoc2-docstring} factor_factory.engines.mediation._base.MediationEngine.fit
```

````

`````
