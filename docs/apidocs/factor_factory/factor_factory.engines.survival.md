# {py:mod}`factor_factory.engines.survival`

```{py:module} factor_factory.engines.survival
```

```{autodoc2-docstring} factor_factory.engines.survival
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.survival.kaplan_meier
factor_factory.engines.survival.cox_ph
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SurvivalResults <factor_factory.engines.survival.SurvivalResults>`
  - ```{autodoc2-docstring} factor_factory.engines.survival.SurvivalResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.survival.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.survival.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.survival.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.survival.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.survival.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.survival._base.SurvivalEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.survival.registry
```

````

`````{py:class} SurvivalResults(results: list[factor_factory.engines.survival._base.SurvivalResult])
:canonical: factor_factory.engines.survival.SurvivalResults

```{autodoc2-docstring} factor_factory.engines.survival.SurvivalResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.survival.SurvivalResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.survival.SurvivalResults.to_records

```{autodoc2-docstring} factor_factory.engines.survival.SurvivalResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('kaplan_meier', ), duration_col: str = 'duration', event_col: str = 'event', covariates: tuple[str, ...] = (), cluster: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.survival.SurvivalResults
:canonical: factor_factory.engines.survival.estimate

```{autodoc2-docstring} factor_factory.engines.survival.estimate
```
````
