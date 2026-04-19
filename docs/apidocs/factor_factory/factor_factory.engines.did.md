# {py:mod}`factor_factory.engines.did`

```{py:module} factor_factory.engines.did
```

```{autodoc2-docstring} factor_factory.engines.did
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.did.callaway_santanna
factor_factory.engines.did.borusyak_jaravel_spiess
factor_factory.engines.did.twfe
factor_factory.engines.did.sun_abraham
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DidResults <factor_factory.engines.did.DidResults>`
  - ```{autodoc2-docstring} factor_factory.engines.did.DidResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.did.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.did.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.did.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.did.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.did.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.did._base.DidEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.did.registry
```

````

`````{py:class} DidResults(results: list[factor_factory.engines.did._base.DidResult])
:canonical: factor_factory.engines.did.DidResults

```{autodoc2-docstring} factor_factory.engines.did.DidResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.did.DidResults.__init__
```

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.did.DidResults.summary_table

```{autodoc2-docstring} factor_factory.engines.did.DidResults.summary_table
```

````

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.did.DidResults.to_records

```{autodoc2-docstring} factor_factory.engines.did.DidResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('twfe', ), outcome: str | None = None, treatment: str = 'treatment', cluster: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.did.DidResults
:canonical: factor_factory.engines.did.estimate

```{autodoc2-docstring} factor_factory.engines.did.estimate
```
````
