# {py:mod}`factor_factory.engines.changepoint`

```{py:module} factor_factory.engines.changepoint
```

```{autodoc2-docstring} factor_factory.engines.changepoint
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.changepoint.ruptures_adapter
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ChangepointResults <factor_factory.engines.changepoint.ChangepointResults>`
  - ```{autodoc2-docstring} factor_factory.engines.changepoint.ChangepointResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.changepoint.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.changepoint.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.changepoint.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.changepoint.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.changepoint.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.changepoint._base.ChangepointEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.changepoint.registry
```

````

`````{py:class} ChangepointResults(results: list[factor_factory.engines.changepoint._base.ChangepointResult])
:canonical: factor_factory.engines.changepoint.ChangepointResults

```{autodoc2-docstring} factor_factory.engines.changepoint.ChangepointResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.changepoint.ChangepointResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.changepoint.ChangepointResults.to_records

```{autodoc2-docstring} factor_factory.engines.changepoint.ChangepointResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('ruptures', ), outcome: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.changepoint.ChangepointResults
:canonical: factor_factory.engines.changepoint.estimate

```{autodoc2-docstring} factor_factory.engines.changepoint.estimate
```
````
