# {py:mod}`factor_factory.engines.hawkes`

```{py:module} factor_factory.engines.hawkes
```

```{autodoc2-docstring} factor_factory.engines.hawkes
:allowtitles:
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HawkesResult <factor_factory.engines.hawkes.HawkesResult>`
  - ```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult
    :summary:
    ```
* - {py:obj}`HawkesEngine <factor_factory.engines.hawkes.HawkesEngine>`
  -
* - {py:obj}`TickHawkesEngine <factor_factory.engines.hawkes.TickHawkesEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.hawkes.TickHawkesEngine
    :summary:
    ```
* - {py:obj}`HawkesResults <factor_factory.engines.hawkes.HawkesResults>`
  - ```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.hawkes.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.hawkes.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.hawkes.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.hawkes.registry
    :summary:
    ```
````

### API

`````{py:class} HawkesResult
:canonical: factor_factory.engines.hawkes.HawkesResult

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult
```

````{py:attribute} method
:canonical: factor_factory.engines.hawkes.HawkesResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.method
```

````

````{py:attribute} baseline_intensities
:canonical: factor_factory.engines.hawkes.HawkesResult.baseline_intensities
:type: numpy.ndarray
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.baseline_intensities
```

````

````{py:attribute} excitation_matrix
:canonical: factor_factory.engines.hawkes.HawkesResult.excitation_matrix
:type: numpy.ndarray
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.excitation_matrix
```

````

````{py:attribute} branching_ratio
:canonical: factor_factory.engines.hawkes.HawkesResult.branching_ratio
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.branching_ratio
```

````

````{py:attribute} log_likelihood
:canonical: factor_factory.engines.hawkes.HawkesResult.log_likelihood
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.log_likelihood
```

````

````{py:attribute} n_events
:canonical: factor_factory.engines.hawkes.HawkesResult.n_events
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.n_events
```

````

````{py:attribute} n_dimensions
:canonical: factor_factory.engines.hawkes.HawkesResult.n_dimensions
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.n_dimensions
```

````

````{py:attribute} kernel
:canonical: factor_factory.engines.hawkes.HawkesResult.kernel
:type: str
:value: >
   'exp'

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.kernel
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.hawkes.HawkesResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.hawkes.HawkesResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.hawkes.HawkesResult.to_dict

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.hawkes.HawkesResult.summary_table

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResult.summary_table
```

````

`````

`````{py:class} HawkesEngine
:canonical: factor_factory.engines.hawkes.HawkesEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.hawkes.HawkesEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, timestamp_col: str = 'timestamp', **engine_specific_kwargs: typing.Any) -> factor_factory.engines.hawkes.HawkesResult
:canonical: factor_factory.engines.hawkes.HawkesEngine.fit

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesEngine.fit
```

````

`````

`````{py:class} TickHawkesEngine
:canonical: factor_factory.engines.hawkes.TickHawkesEngine

```{autodoc2-docstring} factor_factory.engines.hawkes.TickHawkesEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.hawkes.TickHawkesEngine.name
:value: >
   'tick'

```{autodoc2-docstring} factor_factory.engines.hawkes.TickHawkesEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, timestamp_col: str = 'timestamp', decay: float = 1.0, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.hawkes.HawkesResult
:canonical: factor_factory.engines.hawkes.TickHawkesEngine.fit

```{autodoc2-docstring} factor_factory.engines.hawkes.TickHawkesEngine.fit
```

````

`````

````{py:data} registry
:canonical: factor_factory.engines.hawkes.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.hawkes.HawkesEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.hawkes.registry
```

````

`````{py:class} HawkesResults(results: list[factor_factory.engines.hawkes.HawkesResult])
:canonical: factor_factory.engines.hawkes.HawkesResults

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.hawkes.HawkesResults.to_records

```{autodoc2-docstring} factor_factory.engines.hawkes.HawkesResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('tick', ), timestamp_col: str = 'timestamp', **engine_specific_kwargs: typing.Any) -> factor_factory.engines.hawkes.HawkesResults
:canonical: factor_factory.engines.hawkes.estimate

```{autodoc2-docstring} factor_factory.engines.hawkes.estimate
```
````
