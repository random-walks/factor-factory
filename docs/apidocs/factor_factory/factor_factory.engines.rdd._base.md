---
orphan: true
---

# {py:mod}`factor_factory.engines.rdd._base`

```{py:module} factor_factory.engines.rdd._base
```

```{autodoc2-docstring} factor_factory.engines.rdd._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RddResult <factor_factory.engines.rdd._base.RddResult>`
  - ```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult
    :summary:
    ```
* - {py:obj}`RddEngine <factor_factory.engines.rdd._base.RddEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.rdd._base.RddEngine
    :summary:
    ```
````

### API

`````{py:class} RddResult
:canonical: factor_factory.engines.rdd._base.RddResult

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult
```

````{py:attribute} method
:canonical: factor_factory.engines.rdd._base.RddResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.method
```

````

````{py:attribute} design
:canonical: factor_factory.engines.rdd._base.RddResult.design
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.design
```

````

````{py:attribute} cutoff
:canonical: factor_factory.engines.rdd._base.RddResult.cutoff
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.cutoff
```

````

````{py:attribute} estimate
:canonical: factor_factory.engines.rdd._base.RddResult.estimate
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.estimate
```

````

````{py:attribute} std_error
:canonical: factor_factory.engines.rdd._base.RddResult.std_error
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.std_error
```

````

````{py:attribute} ci_95
:canonical: factor_factory.engines.rdd._base.RddResult.ci_95
:type: tuple[float, float]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.ci_95
```

````

````{py:attribute} p_value
:canonical: factor_factory.engines.rdd._base.RddResult.p_value
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.p_value
```

````

````{py:attribute} bandwidth
:canonical: factor_factory.engines.rdd._base.RddResult.bandwidth
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.bandwidth
```

````

````{py:attribute} kernel
:canonical: factor_factory.engines.rdd._base.RddResult.kernel
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.kernel
```

````

````{py:attribute} polynomial_order
:canonical: factor_factory.engines.rdd._base.RddResult.polynomial_order
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.polynomial_order
```

````

````{py:attribute} n_effective
:canonical: factor_factory.engines.rdd._base.RddResult.n_effective
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.n_effective
```

````

````{py:attribute} n_total
:canonical: factor_factory.engines.rdd._base.RddResult.n_total
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.n_total
```

````

````{py:attribute} first_stage_f
:canonical: factor_factory.engines.rdd._base.RddResult.first_stage_f
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.first_stage_f
```

````

````{py:attribute} covariate_balance_pvalues
:canonical: factor_factory.engines.rdd._base.RddResult.covariate_balance_pvalues
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.covariate_balance_pvalues
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.rdd._base.RddResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.rdd._base.RddResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.rdd._base.RddResult.to_dict

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.rdd._base.RddResult.summary_table

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddResult.summary_table
```

````

`````

`````{py:class} RddEngine
:canonical: factor_factory.engines.rdd._base.RddEngine

Bases: {py:obj}`typing.Protocol`

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.rdd._base.RddEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, running_variable: str, cutoff: float = 0.0, design: str = 'sharp', treatment: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.rdd._base.RddResult
:canonical: factor_factory.engines.rdd._base.RddEngine.fit

```{autodoc2-docstring} factor_factory.engines.rdd._base.RddEngine.fit
```

````

`````
