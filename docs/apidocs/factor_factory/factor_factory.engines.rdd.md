# {py:mod}`factor_factory.engines.rdd`

```{py:module} factor_factory.engines.rdd
```

```{autodoc2-docstring} factor_factory.engines.rdd
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.rdd.rd_robust
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RddResults <factor_factory.engines.rdd.RddResults>`
  - ```{autodoc2-docstring} factor_factory.engines.rdd.RddResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.rdd.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.rdd.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.rdd.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.rdd.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.rdd.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.rdd._base.RddEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.rdd.registry
```

````

`````{py:class} RddResults(results: list[factor_factory.engines.rdd._base.RddResult])
:canonical: factor_factory.engines.rdd.RddResults

```{autodoc2-docstring} factor_factory.engines.rdd.RddResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.rdd.RddResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.rdd.RddResults.to_records

```{autodoc2-docstring} factor_factory.engines.rdd.RddResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('rd_robust', ), outcome: str | None = None, running_variable: str, cutoff: float = 0.0, design: str = 'sharp', treatment: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.rdd.RddResults
:canonical: factor_factory.engines.rdd.estimate

```{autodoc2-docstring} factor_factory.engines.rdd.estimate
```
````
