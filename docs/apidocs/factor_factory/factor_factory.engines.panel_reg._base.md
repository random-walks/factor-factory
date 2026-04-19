---
orphan: true
---

# {py:mod}`factor_factory.engines.panel_reg._base`

```{py:module} factor_factory.engines.panel_reg._base
```

```{autodoc2-docstring} factor_factory.engines.panel_reg._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PanelRegResult <factor_factory.engines.panel_reg._base.PanelRegResult>`
  - ```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult
    :summary:
    ```
* - {py:obj}`PanelRegEngine <factor_factory.engines.panel_reg._base.PanelRegEngine>`
  -
````

### API

`````{py:class} PanelRegResult
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult
```

````{py:attribute} method
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.method
```

````

````{py:attribute} coefficients
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.coefficients
:type: dict[str, float]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.coefficients
```

````

````{py:attribute} std_errors
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.std_errors
:type: dict[str, float]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.std_errors
```

````

````{py:attribute} p_values
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.p_values
:type: dict[str, float]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.p_values
```

````

````{py:attribute} confidence_intervals
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.confidence_intervals
:type: dict[str, tuple[float, float]]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.confidence_intervals
```

````

````{py:attribute} r_squared
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.r_squared
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.r_squared
```

````

````{py:attribute} n_observations
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.n_observations
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.n_observations
```

````

````{py:attribute} n_fixed_effects
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.n_fixed_effects
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.n_fixed_effects
```

````

````{py:attribute} fixed_effects
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.fixed_effects
:type: tuple[str, ...]
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.fixed_effects
```

````

````{py:attribute} cluster
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.cluster
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.cluster
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.to_dict

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.panel_reg._base.PanelRegResult.summary_table

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegResult.summary_table
```

````

`````

`````{py:class} PanelRegEngine
:canonical: factor_factory.engines.panel_reg._base.PanelRegEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.panel_reg._base.PanelRegEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, regressors: tuple[str, ...], fixed_effects: tuple[str, ...] = (), cluster: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.panel_reg._base.PanelRegResult
:canonical: factor_factory.engines.panel_reg._base.PanelRegEngine.fit

```{autodoc2-docstring} factor_factory.engines.panel_reg._base.PanelRegEngine.fit
```

````

`````
