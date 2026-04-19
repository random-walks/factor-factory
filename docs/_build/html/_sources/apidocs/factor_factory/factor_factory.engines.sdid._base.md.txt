---
orphan: true
---

# {py:mod}`factor_factory.engines.sdid._base`

```{py:module} factor_factory.engines.sdid._base
```

```{autodoc2-docstring} factor_factory.engines.sdid._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SdidResult <factor_factory.engines.sdid._base.SdidResult>`
  - ```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult
    :summary:
    ```
* - {py:obj}`SdidEngine <factor_factory.engines.sdid._base.SdidEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidEngine
    :summary:
    ```
````

### API

`````{py:class} SdidResult
:canonical: factor_factory.engines.sdid._base.SdidResult

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult
```

````{py:attribute} method
:canonical: factor_factory.engines.sdid._base.SdidResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.method
```

````

````{py:attribute} att
:canonical: factor_factory.engines.sdid._base.SdidResult.att
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.att
```

````

````{py:attribute} se
:canonical: factor_factory.engines.sdid._base.SdidResult.se
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.se
```

````

````{py:attribute} ci_95
:canonical: factor_factory.engines.sdid._base.SdidResult.ci_95
:type: tuple[float, float]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.ci_95
```

````

````{py:attribute} p_value
:canonical: factor_factory.engines.sdid._base.SdidResult.p_value
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.p_value
```

````

````{py:attribute} n
:canonical: factor_factory.engines.sdid._base.SdidResult.n
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.n
```

````

````{py:attribute} unit_weights
:canonical: factor_factory.engines.sdid._base.SdidResult.unit_weights
:type: dict[typing.Any, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.unit_weights
```

````

````{py:attribute} time_weights
:canonical: factor_factory.engines.sdid._base.SdidResult.time_weights
:type: dict[typing.Any, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.time_weights
```

````

````{py:attribute} n_treated
:canonical: factor_factory.engines.sdid._base.SdidResult.n_treated
:type: int | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.n_treated
```

````

````{py:attribute} n_control
:canonical: factor_factory.engines.sdid._base.SdidResult.n_control
:type: int | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.n_control
```

````

````{py:attribute} n_pre
:canonical: factor_factory.engines.sdid._base.SdidResult.n_pre
:type: int | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.n_pre
```

````

````{py:attribute} n_post
:canonical: factor_factory.engines.sdid._base.SdidResult.n_post
:type: int | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.n_post
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.sdid._base.SdidResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.sdid._base.SdidResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.sdid._base.SdidResult.to_dict

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.sdid._base.SdidResult.summary_table

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidResult.summary_table
```

````

`````

`````{py:class} SdidEngine
:canonical: factor_factory.engines.sdid._base.SdidEngine

Bases: {py:obj}`typing.Protocol`

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.sdid._base.SdidEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str = 'treatment', cluster: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.sdid._base.SdidResult
:canonical: factor_factory.engines.sdid._base.SdidEngine.fit

```{autodoc2-docstring} factor_factory.engines.sdid._base.SdidEngine.fit
```

````

`````
