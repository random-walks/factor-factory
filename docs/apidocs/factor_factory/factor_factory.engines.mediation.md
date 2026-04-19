# {py:mod}`factor_factory.engines.mediation`

```{py:module} factor_factory.engines.mediation
```

```{autodoc2-docstring} factor_factory.engines.mediation
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.mediation.four_way
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MediationResults <factor_factory.engines.mediation.MediationResults>`
  - ```{autodoc2-docstring} factor_factory.engines.mediation.MediationResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.mediation.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.mediation.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.mediation.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.mediation.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.mediation.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.mediation._base.MediationEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.mediation.registry
```

````

`````{py:class} MediationResults(results: list[factor_factory.engines.mediation._base.MediationResult])
:canonical: factor_factory.engines.mediation.MediationResults

```{autodoc2-docstring} factor_factory.engines.mediation.MediationResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.mediation.MediationResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.mediation.MediationResults.to_records

```{autodoc2-docstring} factor_factory.engines.mediation.MediationResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('four_way', ), outcome: str | None = None, treatment: str = 'treatment', mediator: str = 'mediator', covariates: tuple[str, ...] = (), n_bootstrap: int = 1000, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.mediation.MediationResults
:canonical: factor_factory.engines.mediation.estimate

```{autodoc2-docstring} factor_factory.engines.mediation.estimate
```
````
