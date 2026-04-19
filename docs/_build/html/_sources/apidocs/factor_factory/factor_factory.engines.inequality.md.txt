# {py:mod}`factor_factory.engines.inequality`

```{py:module} factor_factory.engines.inequality
```

```{autodoc2-docstring} factor_factory.engines.inequality
:allowtitles:
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`InequalityResult <factor_factory.engines.inequality.InequalityResult>`
  - ```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult
    :summary:
    ```
* - {py:obj}`InequalityEngine <factor_factory.engines.inequality.InequalityEngine>`
  -
* - {py:obj}`TheilEngine <factor_factory.engines.inequality.TheilEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.inequality.TheilEngine
    :summary:
    ```
* - {py:obj}`InequalityResults <factor_factory.engines.inequality.InequalityResults>`
  - ```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.inequality.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.inequality.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.inequality.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.inequality.registry
    :summary:
    ```
````

### API

`````{py:class} InequalityResult
:canonical: factor_factory.engines.inequality.InequalityResult

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult
```

````{py:attribute} method
:canonical: factor_factory.engines.inequality.InequalityResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.method
```

````

````{py:attribute} overall
:canonical: factor_factory.engines.inequality.InequalityResult.overall
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.overall
```

````

````{py:attribute} between
:canonical: factor_factory.engines.inequality.InequalityResult.between
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.between
```

````

````{py:attribute} within
:canonical: factor_factory.engines.inequality.InequalityResult.within
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.within
```

````

````{py:attribute} groups
:canonical: factor_factory.engines.inequality.InequalityResult.groups
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.groups
```

````

````{py:attribute} n_observations
:canonical: factor_factory.engines.inequality.InequalityResult.n_observations
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.n_observations
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.inequality.InequalityResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.inequality.InequalityResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.inequality.InequalityResult.to_dict

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.inequality.InequalityResult.summary_table

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResult.summary_table
```

````

`````

`````{py:class} InequalityEngine
:canonical: factor_factory.engines.inequality.InequalityEngine

Bases: {py:obj}`typing.Protocol`

````{py:attribute} name
:canonical: factor_factory.engines.inequality.InequalityEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, group_col: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.inequality.InequalityResult
:canonical: factor_factory.engines.inequality.InequalityEngine.fit

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityEngine.fit
```

````

`````

`````{py:class} TheilEngine
:canonical: factor_factory.engines.inequality.TheilEngine

```{autodoc2-docstring} factor_factory.engines.inequality.TheilEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.inequality.TheilEngine.name
:value: >
   'theil_t'

```{autodoc2-docstring} factor_factory.engines.inequality.TheilEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, group_col: str | None = None, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.inequality.InequalityResult
:canonical: factor_factory.engines.inequality.TheilEngine.fit

```{autodoc2-docstring} factor_factory.engines.inequality.TheilEngine.fit
```

````

`````

````{py:data} registry
:canonical: factor_factory.engines.inequality.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.inequality.InequalityEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.inequality.registry
```

````

`````{py:class} InequalityResults(results: list[factor_factory.engines.inequality.InequalityResult])
:canonical: factor_factory.engines.inequality.InequalityResults

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.inequality.InequalityResults.to_records

```{autodoc2-docstring} factor_factory.engines.inequality.InequalityResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('theil_t', ), outcome: str | None = None, group_col: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.inequality.InequalityResults
:canonical: factor_factory.engines.inequality.estimate

```{autodoc2-docstring} factor_factory.engines.inequality.estimate
```
````
