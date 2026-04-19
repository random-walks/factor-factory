---
orphan: true
---

# {py:mod}`factor_factory.engines._registry`

```{py:module} factor_factory.engines._registry
```

```{autodoc2-docstring} factor_factory.engines._registry
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EngineRegistry <factor_factory.engines._registry.EngineRegistry>`
  - ```{autodoc2-docstring} factor_factory.engines._registry.EngineRegistry
    :summary:
    ```
````

### API

`````{py:class} EngineRegistry(engines: dict[str, E] | None = None)
:canonical: factor_factory.engines._registry.EngineRegistry

```{autodoc2-docstring} factor_factory.engines._registry.EngineRegistry
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.engines._registry.EngineRegistry.__init__
```

````{py:method} register(name: str, engine: E) -> None
:canonical: factor_factory.engines._registry.EngineRegistry.register

```{autodoc2-docstring} factor_factory.engines._registry.EngineRegistry.register
```

````

````{py:method} available() -> list[str]
:canonical: factor_factory.engines._registry.EngineRegistry.available

```{autodoc2-docstring} factor_factory.engines._registry.EngineRegistry.available
```

````

`````
