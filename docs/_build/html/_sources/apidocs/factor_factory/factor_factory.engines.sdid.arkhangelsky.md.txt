# {py:mod}`factor_factory.engines.sdid.arkhangelsky`

```{py:module} factor_factory.engines.sdid.arkhangelsky
```

```{autodoc2-docstring} factor_factory.engines.sdid.arkhangelsky
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SyntheticDidEngine <factor_factory.engines.sdid.arkhangelsky.SyntheticDidEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.sdid.arkhangelsky.SyntheticDidEngine
    :summary:
    ```
````

### API

`````{py:class} SyntheticDidEngine
:canonical: factor_factory.engines.sdid.arkhangelsky.SyntheticDidEngine

```{autodoc2-docstring} factor_factory.engines.sdid.arkhangelsky.SyntheticDidEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.sdid.arkhangelsky.SyntheticDidEngine.name
:value: >
   'sdid'

```{autodoc2-docstring} factor_factory.engines.sdid.arkhangelsky.SyntheticDidEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, treatment: str = 'treatment', cluster: str | None = None, n_jackknife_max: int = 200, inference: str = 'jackknife', n_placebo: int = 200, placebo_seed: int = 42, **_engine_specific_kwargs: typing.Any) -> factor_factory.engines.sdid._base.SdidResult
:canonical: factor_factory.engines.sdid.arkhangelsky.SyntheticDidEngine.fit

```{autodoc2-docstring} factor_factory.engines.sdid.arkhangelsky.SyntheticDidEngine.fit
```

````

`````
