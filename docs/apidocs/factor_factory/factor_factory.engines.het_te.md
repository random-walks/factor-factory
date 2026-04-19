# {py:mod}`factor_factory.engines.het_te`

```{py:module} factor_factory.engines.het_te
```

```{autodoc2-docstring} factor_factory.engines.het_te
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.het_te.bcf
factor_factory.engines.het_te.causal_forest
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HetTeResults <factor_factory.engines.het_te.HetTeResults>`
  - ```{autodoc2-docstring} factor_factory.engines.het_te.HetTeResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.het_te.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.het_te.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.het_te.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.het_te.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.het_te.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.het_te._base.HetTeEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.het_te.registry
```

````

`````{py:class} HetTeResults(results: list[factor_factory.engines.het_te._base.HetTeResult])
:canonical: factor_factory.engines.het_te.HetTeResults

```{autodoc2-docstring} factor_factory.engines.het_te.HetTeResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.het_te.HetTeResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.het_te.HetTeResults.to_records

```{autodoc2-docstring} factor_factory.engines.het_te.HetTeResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('causal_forest', ), outcome: str | None = None, treatment: str = 'treatment', covariates: tuple[str, ...] = (), **engine_specific_kwargs: typing.Any) -> factor_factory.engines.het_te.HetTeResults
:canonical: factor_factory.engines.het_te.estimate

```{autodoc2-docstring} factor_factory.engines.het_te.estimate
```
````
