# {py:mod}`factor_factory.engines.scm`

```{py:module} factor_factory.engines.scm
```

```{autodoc2-docstring} factor_factory.engines.scm
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.scm.matrix_completion
factor_factory.engines.scm.augmented
factor_factory.engines.scm.pysyncon_adapter
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ScmResults <factor_factory.engines.scm.ScmResults>`
  - ```{autodoc2-docstring} factor_factory.engines.scm.ScmResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.scm.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.scm.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.scm.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.scm.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.scm.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.scm._base.ScmEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.scm.registry
```

````

`````{py:class} ScmResults(results: list[factor_factory.engines.scm._base.ScmResult])
:canonical: factor_factory.engines.scm.ScmResults

```{autodoc2-docstring} factor_factory.engines.scm.ScmResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.scm.ScmResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.scm.ScmResults.to_records

```{autodoc2-docstring} factor_factory.engines.scm.ScmResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('augmented', ), outcome: str | None = None, treatment: str = 'treatment', **engine_specific_kwargs: typing.Any) -> factor_factory.engines.scm.ScmResults
:canonical: factor_factory.engines.scm.estimate

```{autodoc2-docstring} factor_factory.engines.scm.estimate
```
````
