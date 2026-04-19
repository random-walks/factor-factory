# {py:mod}`factor_factory.engines.spatial`

```{py:module} factor_factory.engines.spatial
```

```{autodoc2-docstring} factor_factory.engines.spatial
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.spatial.morans_i
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SpatialResults <factor_factory.engines.spatial.SpatialResults>`
  - ```{autodoc2-docstring} factor_factory.engines.spatial.SpatialResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.spatial.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.spatial.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.spatial.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.spatial.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.spatial.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.spatial._base.SpatialEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.spatial.registry
```

````

`````{py:class} SpatialResults(results: list[factor_factory.engines.spatial._base.SpatialResult])
:canonical: factor_factory.engines.spatial.SpatialResults

```{autodoc2-docstring} factor_factory.engines.spatial.SpatialResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.spatial.SpatialResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.spatial.SpatialResults.to_records

```{autodoc2-docstring} factor_factory.engines.spatial.SpatialResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('morans_i', ), outcome: str | None = None, coordinates: tuple[str, str] = ('latitude', 'longitude'), **engine_specific_kwargs: typing.Any) -> factor_factory.engines.spatial.SpatialResults
:canonical: factor_factory.engines.spatial.estimate

```{autodoc2-docstring} factor_factory.engines.spatial.estimate
```
````
