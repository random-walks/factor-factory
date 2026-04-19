---
orphan: true
---

# {py:mod}`factor_factory.engines.spatial._base`

```{py:module} factor_factory.engines.spatial._base
```

```{autodoc2-docstring} factor_factory.engines.spatial._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SpatialResult <factor_factory.engines.spatial._base.SpatialResult>`
  - ```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult
    :summary:
    ```
* - {py:obj}`SpatialEngine <factor_factory.engines.spatial._base.SpatialEngine>`
  -
````

### API

`````{py:class} SpatialResult
:canonical: factor_factory.engines.spatial._base.SpatialResult

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult
```

````{py:attribute} method
:canonical: factor_factory.engines.spatial._base.SpatialResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.method
```

````

````{py:attribute} statistic
:canonical: factor_factory.engines.spatial._base.SpatialResult.statistic
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.statistic
```

````

````{py:attribute} p_value
:canonical: factor_factory.engines.spatial._base.SpatialResult.p_value
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.p_value
```

````

````{py:attribute} z_score
:canonical: factor_factory.engines.spatial._base.SpatialResult.z_score
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.z_score
```

````

````{py:attribute} local_statistics
:canonical: factor_factory.engines.spatial._base.SpatialResult.local_statistics
:type: pandas.Series | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.local_statistics
```

````

````{py:attribute} n_units
:canonical: factor_factory.engines.spatial._base.SpatialResult.n_units
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.n_units
```

````

````{py:attribute} weights_type
:canonical: factor_factory.engines.spatial._base.SpatialResult.weights_type
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.weights_type
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.spatial._base.SpatialResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.spatial._base.SpatialResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.spatial._base.SpatialResult.to_dict

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.spatial._base.SpatialResult.summary_table

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialResult.summary_table
```

````

`````

`````{py:class} SpatialEngine
:canonical: factor_factory.engines.spatial._base.SpatialEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.spatial._base.SpatialEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, coordinates: tuple[str, str] = ('latitude', 'longitude'), **engine_specific_kwargs: typing.Any) -> factor_factory.engines.spatial._base.SpatialResult
:canonical: factor_factory.engines.spatial._base.SpatialEngine.fit

```{autodoc2-docstring} factor_factory.engines.spatial._base.SpatialEngine.fit
```

````

`````
