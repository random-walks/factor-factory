# {py:mod}`factor_factory.engines.survival.cox_ph`

```{py:module} factor_factory.engines.survival.cox_ph
```

```{autodoc2-docstring} factor_factory.engines.survival.cox_ph
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CoxPHEngine <factor_factory.engines.survival.cox_ph.CoxPHEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.survival.cox_ph.CoxPHEngine
    :summary:
    ```
````

### API

`````{py:class} CoxPHEngine
:canonical: factor_factory.engines.survival.cox_ph.CoxPHEngine

```{autodoc2-docstring} factor_factory.engines.survival.cox_ph.CoxPHEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.survival.cox_ph.CoxPHEngine.name
:value: >
   'cox_ph'

```{autodoc2-docstring} factor_factory.engines.survival.cox_ph.CoxPHEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, duration_col: str = 'duration', event_col: str = 'event', covariates: tuple[str, ...] = (), cluster: str | None = None, strata: str | tuple[str, ...] | None = None, run_proportional_hazards_test: bool = True, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.survival._base.SurvivalResult
:canonical: factor_factory.engines.survival.cox_ph.CoxPHEngine.fit

```{autodoc2-docstring} factor_factory.engines.survival.cox_ph.CoxPHEngine.fit
```

````

`````
