---
orphan: true
---

# {py:mod}`factor_factory.engines.scm._base`

```{py:module} factor_factory.engines.scm._base
```

```{autodoc2-docstring} factor_factory.engines.scm._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ScmResult <factor_factory.engines.scm._base.ScmResult>`
  - ```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult
    :summary:
    ```
* - {py:obj}`ScmEngine <factor_factory.engines.scm._base.ScmEngine>`
  -
````

### API

`````{py:class} ScmResult
:canonical: factor_factory.engines.scm._base.ScmResult

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult
```

````{py:attribute} method
:canonical: factor_factory.engines.scm._base.ScmResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.method
```

````

````{py:attribute} att
:canonical: factor_factory.engines.scm._base.ScmResult.att
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.att
```

````

````{py:attribute} std_error
:canonical: factor_factory.engines.scm._base.ScmResult.std_error
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.std_error
```

````

````{py:attribute} pre_period_rmspe
:canonical: factor_factory.engines.scm._base.ScmResult.pre_period_rmspe
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.pre_period_rmspe
```

````

````{py:attribute} post_period_rmspe
:canonical: factor_factory.engines.scm._base.ScmResult.post_period_rmspe
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.post_period_rmspe
```

````

````{py:attribute} donor_weights
:canonical: factor_factory.engines.scm._base.ScmResult.donor_weights
:type: dict[typing.Any, float]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.donor_weights
```

````

````{py:attribute} predictor_weights
:canonical: factor_factory.engines.scm._base.ScmResult.predictor_weights
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.predictor_weights
```

````

````{py:attribute} placebo_pvalue
:canonical: factor_factory.engines.scm._base.ScmResult.placebo_pvalue
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.placebo_pvalue
```

````

````{py:attribute} n_donor
:canonical: factor_factory.engines.scm._base.ScmResult.n_donor
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.n_donor
```

````

````{py:attribute} n_pre
:canonical: factor_factory.engines.scm._base.ScmResult.n_pre
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.n_pre
```

````

````{py:attribute} n_post
:canonical: factor_factory.engines.scm._base.ScmResult.n_post
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.n_post
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.scm._base.ScmResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.scm._base.ScmResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.scm._base.ScmResult.to_dict

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.scm._base.ScmResult.summary_table

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmResult.summary_table
```

````

`````

`````{py:class} ScmEngine
:canonical: factor_factory.engines.scm._base.ScmEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.scm._base.ScmEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str = 'treatment', **engine_specific_kwargs: typing.Any) -> factor_factory.engines.scm._base.ScmResult
:canonical: factor_factory.engines.scm._base.ScmEngine.fit

```{autodoc2-docstring} factor_factory.engines.scm._base.ScmEngine.fit
```

````

`````
