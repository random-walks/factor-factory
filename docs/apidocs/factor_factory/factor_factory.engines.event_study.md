# {py:mod}`factor_factory.engines.event_study`

```{py:module} factor_factory.engines.event_study
```

```{autodoc2-docstring} factor_factory.engines.event_study
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.event_study.market_adjusted
factor_factory.engines.event_study.fama_french
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EventStudyResults <factor_factory.engines.event_study.EventStudyResults>`
  - ```{autodoc2-docstring} factor_factory.engines.event_study.EventStudyResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.event_study.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.event_study.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.event_study.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.event_study.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.event_study.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.event_study._base.EventStudyEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.event_study.registry
```

````

`````{py:class} EventStudyResults(results: list[factor_factory.engines.event_study._base.EventStudyResult])
:canonical: factor_factory.engines.event_study.EventStudyResults

```{autodoc2-docstring} factor_factory.engines.event_study.EventStudyResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.event_study.EventStudyResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.event_study.EventStudyResults.to_records

```{autodoc2-docstring} factor_factory.engines.event_study.EventStudyResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('market_adjusted', ), outcome: str | None = None, event_window: tuple[int, int] = (-1, 1), estimation_window: tuple[int, int] = (-120, -20), **engine_specific_kwargs: typing.Any) -> factor_factory.engines.event_study.EventStudyResults
:canonical: factor_factory.engines.event_study.estimate

```{autodoc2-docstring} factor_factory.engines.event_study.estimate
```
````
