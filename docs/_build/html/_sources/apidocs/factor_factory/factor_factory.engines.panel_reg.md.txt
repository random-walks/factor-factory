# {py:mod}`factor_factory.engines.panel_reg`

```{py:module} factor_factory.engines.panel_reg
```

```{autodoc2-docstring} factor_factory.engines.panel_reg
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

factor_factory.engines.panel_reg.pyfixest_adapter
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PanelRegResults <factor_factory.engines.panel_reg.PanelRegResults>`
  - ```{autodoc2-docstring} factor_factory.engines.panel_reg.PanelRegResults
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`estimate <factor_factory.engines.panel_reg.estimate>`
  - ```{autodoc2-docstring} factor_factory.engines.panel_reg.estimate
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`registry <factor_factory.engines.panel_reg.registry>`
  - ```{autodoc2-docstring} factor_factory.engines.panel_reg.registry
    :summary:
    ```
````

### API

````{py:data} registry
:canonical: factor_factory.engines.panel_reg.registry
:type: factor_factory.engines._registry.EngineRegistry[factor_factory.engines.panel_reg._base.PanelRegEngine]
:value: >
   'EngineRegistry(...)'

```{autodoc2-docstring} factor_factory.engines.panel_reg.registry
```

````

`````{py:class} PanelRegResults(results: list[factor_factory.engines.panel_reg._base.PanelRegResult])
:canonical: factor_factory.engines.panel_reg.PanelRegResults

```{autodoc2-docstring} factor_factory.engines.panel_reg.PanelRegResults
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines.panel_reg.PanelRegResults.__init__
```

````{py:method} to_records() -> list[dict[str, typing.Any]]
:canonical: factor_factory.engines.panel_reg.PanelRegResults.to_records

```{autodoc2-docstring} factor_factory.engines.panel_reg.PanelRegResults.to_records
```

````

`````

````{py:function} estimate(panel: factor_factory.tidy.panel.Panel, *, methods: tuple[str, ...] = ('pyfixest', ), outcome: str | None = None, regressors: tuple[str, ...] = (), fixed_effects: tuple[str, ...] = (), cluster: str | None = None, **engine_specific_kwargs: typing.Any) -> factor_factory.engines.panel_reg.PanelRegResults
:canonical: factor_factory.engines.panel_reg.estimate

```{autodoc2-docstring} factor_factory.engines.panel_reg.estimate
```
````
