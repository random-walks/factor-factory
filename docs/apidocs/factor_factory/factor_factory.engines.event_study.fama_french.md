# {py:mod}`factor_factory.engines.event_study.fama_french`

```{py:module} factor_factory.engines.event_study.fama_french
```

```{autodoc2-docstring} factor_factory.engines.event_study.fama_french
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`FamaFrenchEngine <factor_factory.engines.event_study.fama_french.FamaFrenchEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.event_study.fama_french.FamaFrenchEngine
    :summary:
    ```
````

### API

`````{py:class} FamaFrenchEngine
:canonical: factor_factory.engines.event_study.fama_french.FamaFrenchEngine

```{autodoc2-docstring} factor_factory.engines.event_study.fama_french.FamaFrenchEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.event_study.fama_french.FamaFrenchEngine.name
:value: >
   'fama_french'

```{autodoc2-docstring} factor_factory.engines.event_study.fama_french.FamaFrenchEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, event_window: tuple[int, int] = (-1, 1), estimation_window: tuple[int, int] = (-120, -20), factor_model: str = 'ff3', factor_source: str | pandas.DataFrame = 'cached', **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.event_study._base.EventStudyResult
:canonical: factor_factory.engines.event_study.fama_french.FamaFrenchEngine.fit

```{autodoc2-docstring} factor_factory.engines.event_study.fama_french.FamaFrenchEngine.fit
```

````

`````
