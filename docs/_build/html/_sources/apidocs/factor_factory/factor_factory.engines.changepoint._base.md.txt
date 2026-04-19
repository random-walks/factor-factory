---
orphan: true
---

# {py:mod}`factor_factory.engines.changepoint._base`

```{py:module} factor_factory.engines.changepoint._base
```

```{autodoc2-docstring} factor_factory.engines.changepoint._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ChangepointResult <factor_factory.engines.changepoint._base.ChangepointResult>`
  - ```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult
    :summary:
    ```
* - {py:obj}`ChangepointEngine <factor_factory.engines.changepoint._base.ChangepointEngine>`
  -
````

### API

`````{py:class} ChangepointResult
:canonical: factor_factory.engines.changepoint._base.ChangepointResult

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult
```

````{py:attribute} method
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.method
```

````

````{py:attribute} changepoints
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.changepoints
:type: list[int]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.changepoints
```

````

````{py:attribute} regime_means
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.regime_means
:type: list[float]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.regime_means
```

````

````{py:attribute} n_regimes
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.n_regimes
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.n_regimes
```

````

````{py:attribute} model
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.model
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.model
```

````

````{py:attribute} penalty
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.penalty
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.penalty
```

````

````{py:attribute} confidence
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.confidence
:type: list[float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.confidence
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.to_dict

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.changepoint._base.ChangepointResult.summary_table

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointResult.summary_table
```

````

`````

`````{py:class} ChangepointEngine
:canonical: factor_factory.engines.changepoint._base.ChangepointEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.changepoint._base.ChangepointEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.changepoint._base.ChangepointResult
:canonical: factor_factory.engines.changepoint._base.ChangepointEngine.fit

```{autodoc2-docstring} factor_factory.engines.changepoint._base.ChangepointEngine.fit
```

````

`````
