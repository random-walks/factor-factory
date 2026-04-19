# {py:mod}`factor_factory.engines.reporting_bias`

```{py:module} factor_factory.engines.reporting_bias
```

```{autodoc2-docstring} factor_factory.engines.reporting_bias
:allowtitles:
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ReportingBiasResult <factor_factory.engines.reporting_bias.ReportingBiasResult>`
  - ```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult
    :summary:
    ```
* - {py:obj}`ReportingBiasEngine <factor_factory.engines.reporting_bias.ReportingBiasEngine>`
  -
* - {py:obj}`LatentEmEngine <factor_factory.engines.reporting_bias.LatentEmEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.reporting_bias.LatentEmEngine
    :summary:
    ```
* - {py:obj}`ReportingBiasResults <factor_factory.engines.reporting_bias.ReportingBiasResults>`
  - ```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.reporting_bias.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.reporting_bias.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.reporting_bias.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.reporting_bias.registry
    :summary:
    ```
````

### API

`````{py:class} ReportingBiasResult
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult
```

````{py:attribute} method
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.method
```

````

````{py:attribute} p_reporter
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.p_reporter
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.p_reporter
```

````

````{py:attribute} p_non_reporter
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.p_non_reporter
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.p_non_reporter
```

````

````{py:attribute} pi_reporter
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.pi_reporter
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.pi_reporter
```

````

````{py:attribute} inferred_true_rate
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.inferred_true_rate
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.inferred_true_rate
```

````

````{py:attribute} observed_rate
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.observed_rate
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.observed_rate
```

````

````{py:attribute} n_units
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.n_units
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.n_units
```

````

````{py:attribute} n_em_iterations
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.n_em_iterations
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.n_em_iterations
```

````

````{py:attribute} log_likelihood
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.log_likelihood
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.log_likelihood
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.to_dict

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResult.summary_table

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResult.summary_table
```

````

`````

`````{py:class} ReportingBiasEngine
:canonical: factor_factory.engines.reporting_bias.ReportingBiasEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.reporting_bias.ReportingBiasEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, exposure: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.reporting_bias.ReportingBiasResult
:canonical: factor_factory.engines.reporting_bias.ReportingBiasEngine.fit

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasEngine.fit
```

````

`````

`````{py:class} LatentEmEngine
:canonical: factor_factory.engines.reporting_bias.LatentEmEngine

```{autodoc2-docstring} factor_factory.engines.reporting_bias.LatentEmEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.reporting_bias.LatentEmEngine.name
:value: >
   'latent_em'

```{autodoc2-docstring} factor_factory.engines.reporting_bias.LatentEmEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, exposure: str | None = None, max_iter: int = 100, tol: float = 1e-06, random_state: int = 42, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.reporting_bias.ReportingBiasResult
:canonical: factor_factory.engines.reporting_bias.LatentEmEngine.fit

```{autodoc2-docstring} factor_factory.engines.reporting_bias.LatentEmEngine.fit
```

````

`````

````{py:data} registry
:canonical: factor_factory.engines.reporting_bias.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.reporting_bias.ReportingBiasEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.reporting_bias.registry
```

````

`````{py:class} ReportingBiasResults(results: list[factor_factory.engines.reporting_bias.ReportingBiasResult])
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResults

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.reporting_bias.ReportingBiasResults.to_records

```{autodoc2-docstring} factor_factory.engines.reporting_bias.ReportingBiasResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('latent_em', ), outcome: str | None = None, exposure: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.reporting_bias.ReportingBiasResults
:canonical: factor_factory.engines.reporting_bias.estimate

```{autodoc2-docstring} factor_factory.engines.reporting_bias.estimate
```
````
