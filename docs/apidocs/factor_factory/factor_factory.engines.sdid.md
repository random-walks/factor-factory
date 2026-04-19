# {py:mod}`factor_factory.engines.sdid`

```{py:module} factor_factory.engines.sdid
```

```{autodoc2-docstring} factor_factory.engines.sdid
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.sdid.arkhangelsky
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SdidResults <factor_factory.engines.sdid.SdidResults>`
  - ```{autodoc2-docstring} factor_factory.engines.sdid.SdidResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.sdid.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.sdid.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.sdid.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.sdid.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.sdid.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.sdid._base.SdidEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.sdid.registry
```

````

`````{py:class} SdidResults(results: list[factor_factory.engines.sdid._base.SdidResult])
:canonical: factor_factory.engines.sdid.SdidResults

```{autodoc2-docstring} factor_factory.engines.sdid.SdidResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.sdid.SdidResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.sdid.SdidResults.to_records

```{autodoc2-docstring} factor_factory.engines.sdid.SdidResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('sdid', ), outcome: str | None = None, treatment: str = 'treatment', cluster: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.sdid.SdidResults
:canonical: factor_factory.engines.sdid.estimate

```{autodoc2-docstring} factor_factory.engines.sdid.estimate
```
````
