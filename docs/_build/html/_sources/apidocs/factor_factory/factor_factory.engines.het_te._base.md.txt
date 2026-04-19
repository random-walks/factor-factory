---
orphan: true
---

# {py:mod}`factor_factory.engines.het_te._base`

```{py:module} factor_factory.engines.het_te._base
```

```{autodoc2-docstring} factor_factory.engines.het_te._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HetTeResult <factor_factory.engines.het_te._base.HetTeResult>`
  - ```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult
    :summary:
    ```
* - {py:obj}`HetTeEngine <factor_factory.engines.het_te._base.HetTeEngine>`
  -
````

### API

`````{py:class} HetTeResult
:canonical: factor_factory.engines.het_te._base.HetTeResult

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult
```

````{py:attribute} method
:canonical: factor_factory.engines.het_te._base.HetTeResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.method
```

````

````{py:attribute} ate
:canonical: factor_factory.engines.het_te._base.HetTeResult.ate
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.ate
```

````

````{py:attribute} ate_std_error
:canonical: factor_factory.engines.het_te._base.HetTeResult.ate_std_error
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.ate_std_error
```

````

````{py:attribute} cate_predictions
:canonical: factor_factory.engines.het_te._base.HetTeResult.cate_predictions
:type: numpy.ndarray | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.cate_predictions
```

````

````{py:attribute} cate_std_errors
:canonical: factor_factory.engines.het_te._base.HetTeResult.cate_std_errors
:type: numpy.ndarray | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.cate_std_errors
```

````

````{py:attribute} treatment_effect_heterogeneity_pvalue
:canonical: factor_factory.engines.het_te._base.HetTeResult.treatment_effect_heterogeneity_pvalue
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.treatment_effect_heterogeneity_pvalue
```

````

````{py:attribute} feature_importances
:canonical: factor_factory.engines.het_te._base.HetTeResult.feature_importances
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.feature_importances
```

````

````{py:attribute} nuisance_learner_scores
:canonical: factor_factory.engines.het_te._base.HetTeResult.nuisance_learner_scores
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.nuisance_learner_scores
```

````

````{py:attribute} n_units
:canonical: factor_factory.engines.het_te._base.HetTeResult.n_units
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.n_units
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.het_te._base.HetTeResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.het_te._base.HetTeResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.het_te._base.HetTeResult.to_dict

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.het_te._base.HetTeResult.summary_table

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeResult.summary_table
```

````

`````

`````{py:class} HetTeEngine
:canonical: factor_factory.engines.het_te._base.HetTeEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.het_te._base.HetTeEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str = 'treatment', covariates: tuple[str, ...] = (), **engine_specific_kwargs: typing.Any) -> factor_factory.engines.het_te._base.HetTeResult
:canonical: factor_factory.engines.het_te._base.HetTeEngine.fit

```{autodoc2-docstring} factor_factory.engines.het_te._base.HetTeEngine.fit
```

````

`````
