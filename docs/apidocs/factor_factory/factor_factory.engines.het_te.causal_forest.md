# {py:mod}`factor_factory.engines.het_te.causal_forest`

```{py:module} factor_factory.engines.het_te.causal_forest
```

```{autodoc2-docstring} factor_factory.engines.het_te.causal_forest
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CausalForestEngine <factor_factory.engines.het_te.causal_forest.CausalForestEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.het_te.causal_forest.CausalForestEngine
    :summary:
    ```
````

### API

`````{py:class} CausalForestEngine
:canonical: factor_factory.engines.het_te.causal_forest.CausalForestEngine

```{autodoc2-docstring} factor_factory.engines.het_te.causal_forest.CausalForestEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.het_te.causal_forest.CausalForestEngine.name
:value: >
   'causal_forest'

```{autodoc2-docstring} factor_factory.engines.het_te.causal_forest.CausalForestEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str = 'treatment', covariates: tuple[str, ...] = (), discrete_treatment: bool = True, n_estimators: int = 200, min_samples_leaf: int = 10, random_state: int = 42, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.het_te._base.HetTeResult
:canonical: factor_factory.engines.het_te.causal_forest.CausalForestEngine.fit

```{autodoc2-docstring} factor_factory.engines.het_te.causal_forest.CausalForestEngine.fit
```

````

`````
