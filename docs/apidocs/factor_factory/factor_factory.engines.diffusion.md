# {py:mod}`factor_factory.engines.diffusion`

```{py:module} factor_factory.engines.diffusion
```

```{autodoc2-docstring} factor_factory.engines.diffusion
:allowtitles:
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DiffusionResult <factor_factory.engines.diffusion.DiffusionResult>`
  - ```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult
    :summary:
    ```
* - {py:obj}`DiffusionEngine <factor_factory.engines.diffusion.DiffusionEngine>`
  -
* - {py:obj}`NdlibEngine <factor_factory.engines.diffusion.NdlibEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.diffusion.NdlibEngine
    :summary:
    ```
* - {py:obj}`DiffusionResults <factor_factory.engines.diffusion.DiffusionResults>`
  - ```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.diffusion.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.diffusion.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.diffusion.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.diffusion.registry
    :summary:
    ```
````

### API

`````{py:class} DiffusionResult
:canonical: factor_factory.engines.diffusion.DiffusionResult

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult
```

````{py:attribute} method
:canonical: factor_factory.engines.diffusion.DiffusionResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.method
```

````

````{py:attribute} model
:canonical: factor_factory.engines.diffusion.DiffusionResult.model
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.model
```

````

````{py:attribute} peak_infected_fraction
:canonical: factor_factory.engines.diffusion.DiffusionResult.peak_infected_fraction
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.peak_infected_fraction
```

````

````{py:attribute} peak_time
:canonical: factor_factory.engines.diffusion.DiffusionResult.peak_time
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.peak_time
```

````

````{py:attribute} final_recovered_fraction
:canonical: factor_factory.engines.diffusion.DiffusionResult.final_recovered_fraction
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.final_recovered_fraction
```

````

````{py:attribute} trajectory
:canonical: factor_factory.engines.diffusion.DiffusionResult.trajectory
:type: pandas.DataFrame | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.trajectory
```

````

````{py:attribute} n_nodes
:canonical: factor_factory.engines.diffusion.DiffusionResult.n_nodes
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.n_nodes
```

````

````{py:attribute} n_edges
:canonical: factor_factory.engines.diffusion.DiffusionResult.n_edges
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.n_edges
```

````

````{py:attribute} seed_nodes
:canonical: factor_factory.engines.diffusion.DiffusionResult.seed_nodes
:type: list[int] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.seed_nodes
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.diffusion.DiffusionResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.diffusion.DiffusionResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.diffusion.DiffusionResult.to_dict

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.diffusion.DiffusionResult.summary_table

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResult.summary_table
```

````

`````

`````{py:class} DiffusionEngine
:canonical: factor_factory.engines.diffusion.DiffusionEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.diffusion.DiffusionEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionEngine.name
```

````

````{py:method} simulate(panel: factor_factory.tidy.panel.Panel, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.diffusion.DiffusionResult
:canonical: factor_factory.engines.diffusion.DiffusionEngine.simulate

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionEngine.simulate
```

````

`````

`````{py:class} NdlibEngine
:canonical: factor_factory.engines.diffusion.NdlibEngine

```{autodoc2-docstring} factor_factory.engines.diffusion.NdlibEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.diffusion.NdlibEngine.name
:value: >
   'ndlib_sir'

```{autodoc2-docstring} factor_factory.engines.diffusion.NdlibEngine.name
```

````

````{py:method} simulate(panel: factor_factory.tidy.panel.Panel, *, graph: typing.Any = None, seed_nodes: list[int] | None = None, beta: float = 0.1, gamma: float = 0.05, n_iterations: int = 100, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.diffusion.DiffusionResult
:canonical: factor_factory.engines.diffusion.NdlibEngine.simulate

```{autodoc2-docstring} factor_factory.engines.diffusion.NdlibEngine.simulate
```

````

`````

````{py:data} registry
:canonical: factor_factory.engines.diffusion.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.diffusion.DiffusionEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.diffusion.registry
```

````

````{py:class} DiffusionResults(results: list[factor_factory.engines.diffusion.DiffusionResult])
:canonical: factor_factory.engines.diffusion.DiffusionResults

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.diffusion.DiffusionResults.__init__
```

````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('ndlib_sir', ), **engine_specific_kwargs: typing.Any) -> factor_factory.engines.diffusion.DiffusionResults
:canonical: factor_factory.engines.diffusion.estimate

```{autodoc2-docstring} factor_factory.engines.diffusion.estimate
```
````
