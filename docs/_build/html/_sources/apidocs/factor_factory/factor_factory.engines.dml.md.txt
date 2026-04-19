# {py:mod}`factor_factory.engines.dml`

```{py:module} factor_factory.engines.dml
```

```{autodoc2-docstring} factor_factory.engines.dml
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.dml.plr
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DmlResults <factor_factory.engines.dml.DmlResults>`
  - ```{autodoc2-docstring} factor_factory.engines.dml.DmlResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.dml.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.dml.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.dml.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.dml.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.dml.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.dml._base.DmlEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.dml.registry
```

````

`````{py:class} DmlResults(results: list[factor_factory.engines.dml._base.DmlResult])
:canonical: factor_factory.engines.dml.DmlResults

```{autodoc2-docstring} factor_factory.engines.dml.DmlResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.dml.DmlResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.dml.DmlResults.to_records

```{autodoc2-docstring} factor_factory.engines.dml.DmlResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('plr', ), outcome: str | None = None, treatment: str = 'treatment', covariates: tuple[str, ...] = (), **engine_specific_kwargs: typing.Any) -> factor_factory.engines.dml.DmlResults
:canonical: factor_factory.engines.dml.estimate

```{autodoc2-docstring} factor_factory.engines.dml.estimate
```
````
