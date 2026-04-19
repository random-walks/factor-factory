# {py:mod}`factor_factory.engines.climate`

```{py:module} factor_factory.engines.climate
```

```{autodoc2-docstring} factor_factory.engines.climate
:allowtitles:
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ClimateResult <factor_factory.engines.climate.ClimateResult>`
  - ```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult
    :summary:
    ```
* - {py:obj}`ClimateEngine <factor_factory.engines.climate.ClimateEngine>`
  -
* - {py:obj}`MannKendallEngine <factor_factory.engines.climate.MannKendallEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.climate.MannKendallEngine
    :summary:
    ```
* - {py:obj}`ClimateResults <factor_factory.engines.climate.ClimateResults>`
  - ```{autodoc2-docstring} factor_factory.engines.climate.ClimateResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.climate.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.climate.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.climate.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.climate.registry
    :summary:
    ```
````

### API

`````{py:class} ClimateResult
:canonical: factor_factory.engines.climate.ClimateResult

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult
```

````{py:attribute} method
:canonical: factor_factory.engines.climate.ClimateResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.method
```

````

````{py:attribute} statistic
:canonical: factor_factory.engines.climate.ClimateResult.statistic
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.statistic
```

````

````{py:attribute} p_value
:canonical: factor_factory.engines.climate.ClimateResult.p_value
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.p_value
```

````

````{py:attribute} trend
:canonical: factor_factory.engines.climate.ClimateResult.trend
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.trend
```

````

````{py:attribute} slope
:canonical: factor_factory.engines.climate.ClimateResult.slope
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.slope
```

````

````{py:attribute} intercept
:canonical: factor_factory.engines.climate.ClimateResult.intercept
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.intercept
```

````

````{py:attribute} index_name
:canonical: factor_factory.engines.climate.ClimateResult.index_name
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.index_name
```

````

````{py:attribute} index_values
:canonical: factor_factory.engines.climate.ClimateResult.index_values
:type: pandas.Series | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.index_values
```

````

````{py:attribute} n_observations
:canonical: factor_factory.engines.climate.ClimateResult.n_observations
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.n_observations
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.climate.ClimateResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.climate.ClimateResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.climate.ClimateResult.to_dict

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.climate.ClimateResult.summary_table

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResult.summary_table
```

````

`````

`````{py:class} ClimateEngine
:canonical: factor_factory.engines.climate.ClimateEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.climate.ClimateEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.climate.ClimateEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.climate.ClimateResult
:canonical: factor_factory.engines.climate.ClimateEngine.fit

```{autodoc2-docstring} factor_factory.engines.climate.ClimateEngine.fit
```

````

`````

`````{py:class} MannKendallEngine
:canonical: factor_factory.engines.climate.MannKendallEngine

```{autodoc2-docstring} factor_factory.engines.climate.MannKendallEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.climate.MannKendallEngine.name
:value: >
   'mann_kendall'

```{autodoc2-docstring} factor_factory.engines.climate.MannKendallEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, alpha: float = 0.05, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.climate.ClimateResult
:canonical: factor_factory.engines.climate.MannKendallEngine.fit

```{autodoc2-docstring} factor_factory.engines.climate.MannKendallEngine.fit
```

````

`````

````{py:data} registry
:canonical: factor_factory.engines.climate.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.climate.ClimateEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.climate.registry
```

````

`````{py:class} ClimateResults(results: list[factor_factory.engines.climate.ClimateResult])
:canonical: factor_factory.engines.climate.ClimateResults

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.climate.ClimateResults.to_records

```{autodoc2-docstring} factor_factory.engines.climate.ClimateResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('mann_kendall', ), outcome: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.climate.ClimateResults
:canonical: factor_factory.engines.climate.estimate

```{autodoc2-docstring} factor_factory.engines.climate.estimate
```
````
