# {py:mod}`factor_factory.engines.survival.kaplan_meier`

```{py:module} factor_factory.engines.survival.kaplan_meier
```

```{autodoc2-docstring} factor_factory.engines.survival.kaplan_meier
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`KaplanMeierEngine <factor_factory.engines.survival.kaplan_meier.KaplanMeierEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.survival.kaplan_meier.KaplanMeierEngine
    :summary:
    ```
````

### API

`````{py:class} KaplanMeierEngine
:canonical: factor_factory.engines.survival.kaplan_meier.KaplanMeierEngine

```{autodoc2-docstring} factor_factory.engines.survival.kaplan_meier.KaplanMeierEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.survival.kaplan_meier.KaplanMeierEngine.name
:value: >
   'kaplan_meier'

```{autodoc2-docstring} factor_factory.engines.survival.kaplan_meier.KaplanMeierEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, duration_col: str = 'duration', event_col: str = 'event', covariates: tuple[str, ...] = (), cluster: str | None = None, alpha: float = 0.05, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.survival._base.SurvivalResult
:canonical: factor_factory.engines.survival.kaplan_meier.KaplanMeierEngine.fit

```{autodoc2-docstring} factor_factory.engines.survival.kaplan_meier.KaplanMeierEngine.fit
```

````

`````
