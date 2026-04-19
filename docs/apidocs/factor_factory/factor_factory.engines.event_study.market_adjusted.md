# {py:mod}`factor_factory.engines.event_study.market_adjusted`

```{py:module} factor_factory.engines.event_study.market_adjusted
```

```{autodoc2-docstring} factor_factory.engines.event_study.market_adjusted
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MarketAdjustedEngine <factor_factory.engines.event_study.market_adjusted.MarketAdjustedEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.event_study.market_adjusted.MarketAdjustedEngine
    :summary:
    ```
````

### API

`````{py:class} MarketAdjustedEngine
:canonical: factor_factory.engines.event_study.market_adjusted.MarketAdjustedEngine

```{autodoc2-docstring} factor_factory.engines.event_study.market_adjusted.MarketAdjustedEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.event_study.market_adjusted.MarketAdjustedEngine.name
:value: >
   'market_adjusted'

```{autodoc2-docstring} factor_factory.engines.event_study.market_adjusted.MarketAdjustedEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, market_col: str | None = None, estimation_window: tuple[int, int] = (-120, -20), event_window: tuple[int, int] = (-1, 1), **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.event_study._base.EventStudyResult
:canonical: factor_factory.engines.event_study.market_adjusted.MarketAdjustedEngine.fit

```{autodoc2-docstring} factor_factory.engines.event_study.market_adjusted.MarketAdjustedEngine.fit
```

````

`````
