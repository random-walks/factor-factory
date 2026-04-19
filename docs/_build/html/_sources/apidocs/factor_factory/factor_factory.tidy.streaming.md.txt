# {py:mod}`factor_factory.tidy.streaming`

```{py:module} factor_factory.tidy.streaming
```

```{autodoc2-docstring} factor_factory.tidy.streaming
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PanelBuilder <factor_factory.tidy.streaming.PanelBuilder>`
  - ```{autodoc2-docstring} factor_factory.tidy.streaming.PanelBuilder
    :summary:
    ```
````

### API

`````{py:class} PanelBuilder(*, dimension: str, outcome_col: str = 'n', freq: str | None = 'ME', period_kind: str = 'timestamp', treatment_events: tuple[factor_factory.tidy.contracts.TreatmentEvent, ...] = (), provenance: factor_factory.tidy.contracts.Provenance | None = None, unit_id_extractor: collections.abc.Callable[[typing.Any], typing.Any] | None = None, period_extractor: collections.abc.Callable[[typing.Any], typing.Any] | None = None)
:canonical: factor_factory.tidy.streaming.PanelBuilder

```{autodoc2-docstring} factor_factory.tidy.streaming.PanelBuilder
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.tidy.streaming.PanelBuilder.__init__
```

````{py:method} ingest(records: collections.abc.Iterable[typing.Any]) -> factor_factory.tidy.streaming.PanelBuilder
:canonical: factor_factory.tidy.streaming.PanelBuilder.ingest

```{autodoc2-docstring} factor_factory.tidy.streaming.PanelBuilder.ingest
```

````

````{py:method} build() -> factor_factory.tidy.panel.Panel
:canonical: factor_factory.tidy.streaming.PanelBuilder.build

```{autodoc2-docstring} factor_factory.tidy.streaming.PanelBuilder.build
```

````

````{py:property} n_records
:canonical: factor_factory.tidy.streaming.PanelBuilder.n_records
:type: int

```{autodoc2-docstring} factor_factory.tidy.streaming.PanelBuilder.n_records
```

````

````{py:property} n_cells
:canonical: factor_factory.tidy.streaming.PanelBuilder.n_cells
:type: int

```{autodoc2-docstring} factor_factory.tidy.streaming.PanelBuilder.n_cells
```

````

`````
