# {py:mod}`factor_factory.engines.dml.plr`

```{py:module} factor_factory.engines.dml.plr
```

```{autodoc2-docstring} factor_factory.engines.dml.plr
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DmlPlrEngine <factor_factory.engines.dml.plr.DmlPlrEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.dml.plr.DmlPlrEngine
    :summary:
    ```
````

### API

`````{py:class} DmlPlrEngine
:canonical: factor_factory.engines.dml.plr.DmlPlrEngine

```{autodoc2-docstring} factor_factory.engines.dml.plr.DmlPlrEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.dml.plr.DmlPlrEngine.name
:value: >
   'plr'

```{autodoc2-docstring} factor_factory.engines.dml.plr.DmlPlrEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str = 'treatment', covariates: tuple[str, ...] = (), n_folds: int = 5, score: str = 'partialling out', **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.dml._base.DmlResult
:canonical: factor_factory.engines.dml.plr.DmlPlrEngine.fit

```{autodoc2-docstring} factor_factory.engines.dml.plr.DmlPlrEngine.fit
```

````

`````
