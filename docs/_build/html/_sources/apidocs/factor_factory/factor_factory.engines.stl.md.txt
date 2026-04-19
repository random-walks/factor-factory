# {py:mod}`factor_factory.engines.stl`

```{py:module} factor_factory.engines.stl
```

```{autodoc2-docstring} factor_factory.engines.stl
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.stl.sktime_stl
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`StlResults <factor_factory.engines.stl.StlResults>`
  - ```{autodoc2-docstring} factor_factory.engines.stl.StlResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.stl.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.stl.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.stl.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.stl.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.stl.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.stl._base.StlEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.stl.registry
```

````

`````{py:class} StlResults(results: list[factor_factory.engines.stl._base.StlResult])
:canonical: factor_factory.engines.stl.StlResults

```{autodoc2-docstring} factor_factory.engines.stl.StlResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.stl.StlResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.stl.StlResults.to_records

```{autodoc2-docstring} factor_factory.engines.stl.StlResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('sktime_stl', ), outcome: str | None = None, seasonal_period: int = 12, forecast_horizon: int = 0, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.stl.StlResults
:canonical: factor_factory.engines.stl.estimate

```{autodoc2-docstring} factor_factory.engines.stl.estimate
```
````
