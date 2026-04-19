# {py:mod}`factor_factory.engines.mediation.four_way`

```{py:module} factor_factory.engines.mediation.four_way
```

```{autodoc2-docstring} factor_factory.engines.mediation.four_way
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`FourWayMediationEngine <factor_factory.engines.mediation.four_way.FourWayMediationEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.mediation.four_way.FourWayMediationEngine
    :summary:
    ```
````

### API

`````{py:class} FourWayMediationEngine
:canonical: factor_factory.engines.mediation.four_way.FourWayMediationEngine

```{autodoc2-docstring} factor_factory.engines.mediation.four_way.FourWayMediationEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.mediation.four_way.FourWayMediationEngine.name
:value: >
   'four_way'

```{autodoc2-docstring} factor_factory.engines.mediation.four_way.FourWayMediationEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str, mediator: str, covariates: tuple[str, ...] = (), n_bootstrap: int = 1000, random_state: int = 20260420, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.mediation._base.MediationResult
:canonical: factor_factory.engines.mediation.four_way.FourWayMediationEngine.fit

```{autodoc2-docstring} factor_factory.engines.mediation.four_way.FourWayMediationEngine.fit
```

````

`````
