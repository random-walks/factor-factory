---
orphan: true
---

# {py:mod}`factor_factory.engines.dml._base`

```{py:module} factor_factory.engines.dml._base
```

```{autodoc2-docstring} factor_factory.engines.dml._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DmlResult <factor_factory.engines.dml._base.DmlResult>`
  - ```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult
    :summary:
    ```
* - {py:obj}`DmlEngine <factor_factory.engines.dml._base.DmlEngine>`
  -
````

### API

`````{py:class} DmlResult
:canonical: factor_factory.engines.dml._base.DmlResult

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult
```

````{py:attribute} method
:canonical: factor_factory.engines.dml._base.DmlResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.method
```

````

````{py:attribute} coef
:canonical: factor_factory.engines.dml._base.DmlResult.coef
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.coef
```

````

````{py:attribute} std_error
:canonical: factor_factory.engines.dml._base.DmlResult.std_error
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.std_error
```

````

````{py:attribute} t_stat
:canonical: factor_factory.engines.dml._base.DmlResult.t_stat
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.t_stat
```

````

````{py:attribute} p_value
:canonical: factor_factory.engines.dml._base.DmlResult.p_value
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.p_value
```

````

````{py:attribute} ci_95
:canonical: factor_factory.engines.dml._base.DmlResult.ci_95
:type: tuple[float, float]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.ci_95
```

````

````{py:attribute} n_units
:canonical: factor_factory.engines.dml._base.DmlResult.n_units
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.n_units
```

````

````{py:attribute} n_folds
:canonical: factor_factory.engines.dml._base.DmlResult.n_folds
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.n_folds
```

````

````{py:attribute} nuisance_rmse
:canonical: factor_factory.engines.dml._base.DmlResult.nuisance_rmse
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.nuisance_rmse
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.dml._base.DmlResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.dml._base.DmlResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.dml._base.DmlResult.to_dict

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.dml._base.DmlResult.summary_table

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlResult.summary_table
```

````

`````

`````{py:class} DmlEngine
:canonical: factor_factory.engines.dml._base.DmlEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.dml._base.DmlEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str = 'treatment', covariates: tuple[str, ...] = (), **engine_specific_kwargs: typing.Any) -> factor_factory.engines.dml._base.DmlResult
:canonical: factor_factory.engines.dml._base.DmlEngine.fit

```{autodoc2-docstring} factor_factory.engines.dml._base.DmlEngine.fit
```

````

`````
