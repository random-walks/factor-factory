---
orphan: true
---

# {py:mod}`factor_factory.engines.stl._base`

```{py:module} factor_factory.engines.stl._base
```

```{autodoc2-docstring} factor_factory.engines.stl._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`StlResult <factor_factory.engines.stl._base.StlResult>`
  - ```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult
    :summary:
    ```
* - {py:obj}`StlEngine <factor_factory.engines.stl._base.StlEngine>`
  -
````

### API

`````{py:class} StlResult
:canonical: factor_factory.engines.stl._base.StlResult

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult
```

````{py:attribute} method
:canonical: factor_factory.engines.stl._base.StlResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.method
```

````

````{py:attribute} trend
:canonical: factor_factory.engines.stl._base.StlResult.trend
:type: pandas.Series
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.trend
```

````

````{py:attribute} seasonal
:canonical: factor_factory.engines.stl._base.StlResult.seasonal
:type: pandas.Series
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.seasonal
```

````

````{py:attribute} residual
:canonical: factor_factory.engines.stl._base.StlResult.residual
:type: pandas.Series
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.residual
```

````

````{py:attribute} forecast
:canonical: factor_factory.engines.stl._base.StlResult.forecast
:type: pandas.Series | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.forecast
```

````

````{py:attribute} forecast_interval
:canonical: factor_factory.engines.stl._base.StlResult.forecast_interval
:type: pandas.DataFrame | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.forecast_interval
```

````

````{py:attribute} seasonal_period
:canonical: factor_factory.engines.stl._base.StlResult.seasonal_period
:type: int | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.seasonal_period
```

````

````{py:attribute} n_observations
:canonical: factor_factory.engines.stl._base.StlResult.n_observations
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.n_observations
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.stl._base.StlResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.stl._base.StlResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.stl._base.StlResult.to_dict

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.stl._base.StlResult.summary_table

```{autodoc2-docstring} factor_factory.engines.stl._base.StlResult.summary_table
```

````

`````

`````{py:class} StlEngine
:canonical: factor_factory.engines.stl._base.StlEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.stl._base.StlEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.stl._base.StlEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, seasonal_period: int, forecast_horizon: int = 0, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.stl._base.StlResult
:canonical: factor_factory.engines.stl._base.StlEngine.fit

```{autodoc2-docstring} factor_factory.engines.stl._base.StlEngine.fit
```

````

`````
