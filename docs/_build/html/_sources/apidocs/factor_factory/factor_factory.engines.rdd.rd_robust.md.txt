# {py:mod}`factor_factory.engines.rdd.rd_robust`

```{py:module} factor_factory.engines.rdd.rd_robust
```

```{autodoc2-docstring} factor_factory.engines.rdd.rd_robust
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RdRobustEngine <factor_factory.engines.rdd.rd_robust.RdRobustEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.rdd.rd_robust.RdRobustEngine
    :summary:
    ```
````

### API

`````{py:class} RdRobustEngine
:canonical: factor_factory.engines.rdd.rd_robust.RdRobustEngine

```{autodoc2-docstring} factor_factory.engines.rdd.rd_robust.RdRobustEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.rdd.rd_robust.RdRobustEngine.name
:value: >
   'rd_robust'

```{autodoc2-docstring} factor_factory.engines.rdd.rd_robust.RdRobustEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, running_variable: str, cutoff: float = 0.0, design: str = 'sharp', treatment: str | None = None, polynomial_order: int = 1, kernel: str = 'triangular', bwselect: str = 'mserd', covariates: tuple[str, ...] = (), cluster: str | None = None, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.rdd._base.RddResult
:canonical: factor_factory.engines.rdd.rd_robust.RdRobustEngine.fit

```{autodoc2-docstring} factor_factory.engines.rdd.rd_robust.RdRobustEngine.fit
```

````

`````
