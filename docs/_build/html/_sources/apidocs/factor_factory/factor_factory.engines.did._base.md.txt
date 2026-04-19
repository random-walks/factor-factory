---
orphan: true
---

# {py:mod}`factor_factory.engines.did._base`

```{py:module} factor_factory.engines.did._base
```

```{autodoc2-docstring} factor_factory.engines.did._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DidResult <factor_factory.engines.did._base.DidResult>`
  - ```{autodoc2-docstring} factor_factory.engines.did._base.DidResult
    :summary:
    ```
* - {py:obj}`DidEngine <factor_factory.engines.did._base.DidEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.did._base.DidEngine
    :summary:
    ```
````

### API

`````{py:class} DidResult
:canonical: factor_factory.engines.did._base.DidResult

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult
```

````{py:attribute} method
:canonical: factor_factory.engines.did._base.DidResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.method
```

````

````{py:attribute} att
:canonical: factor_factory.engines.did._base.DidResult.att
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.att
```

````

````{py:attribute} se
:canonical: factor_factory.engines.did._base.DidResult.se
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.se
```

````

````{py:attribute} ci_95
:canonical: factor_factory.engines.did._base.DidResult.ci_95
:type: tuple[float, float]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.ci_95
```

````

````{py:attribute} p_value
:canonical: factor_factory.engines.did._base.DidResult.p_value
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.p_value
```

````

````{py:attribute} n
:canonical: factor_factory.engines.did._base.DidResult.n
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.n
```

````

````{py:attribute} cohort_atts
:canonical: factor_factory.engines.did._base.DidResult.cohort_atts
:type: dict[int, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.cohort_atts
```

````

````{py:attribute} cohort_ses
:canonical: factor_factory.engines.did._base.DidResult.cohort_ses
:type: dict[int, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.cohort_ses
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.did._base.DidResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.did._base.DidResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.did._base.DidResult.to_dict

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.did._base.DidResult.summary_table

```{autodoc2-docstring} factor_factory.engines.did._base.DidResult.summary_table
```

````

`````

`````{py:class} DidEngine
:canonical: factor_factory.engines.did._base.DidEngine

Bases: {py:obj}`typing.Protocol`

```{autodoc2-docstring} factor_factory.engines.did._base.DidEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.did._base.DidEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.did._base.DidEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str = 'treatment', cluster: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.did._base.DidResult
:canonical: factor_factory.engines.did._base.DidEngine.fit

```{autodoc2-docstring} factor_factory.engines.did._base.DidEngine.fit
```

````

`````
