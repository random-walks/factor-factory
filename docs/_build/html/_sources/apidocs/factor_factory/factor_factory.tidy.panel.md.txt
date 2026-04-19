# {py:mod}`factor_factory.tidy.panel`

```{py:module} factor_factory.tidy.panel
```

```{autodoc2-docstring} factor_factory.tidy.panel
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Panel <factor_factory.tidy.panel.Panel>`
  - ```{autodoc2-docstring} factor_factory.tidy.panel.Panel
    :summary:
    ```
````

### API

`````{py:class} Panel(df: pandas.DataFrame, metadata: factor_factory.tidy.contracts.PanelMetadata, record_view: factor_factory.tidy.record_view.RecordView | None = None, *, validate: bool = True)
:canonical: factor_factory.tidy.panel.Panel

```{autodoc2-docstring} factor_factory.tidy.panel.Panel
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.__init__
```

````{py:property} outcome_col
:canonical: factor_factory.tidy.panel.Panel.outcome_col
:type: str

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.outcome_col
```

````

````{py:property} outcome_cols
:canonical: factor_factory.tidy.panel.Panel.outcome_cols
:type: tuple[str, ...]

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.outcome_cols
```

````

````{py:property} freq
:canonical: factor_factory.tidy.panel.Panel.freq
:type: str | None

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.freq
```

````

````{py:property} dimension
:canonical: factor_factory.tidy.panel.Panel.dimension
:type: str

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.dimension
```

````

````{py:property} geography
:canonical: factor_factory.tidy.panel.Panel.geography
:type: str

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.geography
```

````

````{py:property} period_kind
:canonical: factor_factory.tidy.panel.Panel.period_kind
:type: str

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.period_kind
```

````

````{py:property} treatment_events
:canonical: factor_factory.tidy.panel.Panel.treatment_events
:type: tuple[factor_factory.tidy.contracts.TreatmentEvent, ...]

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.treatment_events
```

````

````{py:property} weights_col
:canonical: factor_factory.tidy.panel.Panel.weights_col
:type: str | None

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.weights_col
```

````

````{py:property} weights
:canonical: factor_factory.tidy.panel.Panel.weights
:type: pandas.Series | None

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.weights
```

````

````{py:property} provenance
:canonical: factor_factory.tidy.panel.Panel.provenance
:type: factor_factory.tidy.contracts.Provenance

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.provenance
```

````

````{py:property} record_view
:canonical: factor_factory.tidy.panel.Panel.record_view
:type: factor_factory.tidy.record_view.RecordView

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.record_view
```

````

````{py:property} has_record_view
:canonical: factor_factory.tidy.panel.Panel.has_record_view
:type: bool

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.has_record_view
```

````

````{py:property} unit_ids
:canonical: factor_factory.tidy.panel.Panel.unit_ids
:type: tuple[typing.Any, ...]

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.unit_ids
```

````

````{py:property} periods
:canonical: factor_factory.tidy.panel.Panel.periods
:type: pandas.Index

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.periods
```

````

````{py:method} from_records(records: collections.abc.Sequence[typing.Any] | collections.abc.Iterable[typing.Any], *, dimension: str | None = None, geography: str | None = None, freq: str | None = 'ME', period_kind: str = 'timestamp', treatment_events: tuple[factor_factory.tidy.contracts.TreatmentEvent, ...] = (), outcome_col: str = 'n', record_view: bool = False, record_view_columns: tuple[str, ...] = ('latitude', 'longitude'), weights_col: str | None = None, provenance: factor_factory.tidy.contracts.Provenance | None = None, unit_id_extractor: collections.abc.Callable[[typing.Any], typing.Any] | None = None, period_extractor: collections.abc.Callable[[typing.Any], typing.Any] | None = None, record_extra_extractor: collections.abc.Callable[[typing.Any], dict[str, typing.Any]] | None = None) -> factor_factory.tidy.panel.Panel
:canonical: factor_factory.tidy.panel.Panel.from_records
:classmethod:

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.from_records
```

````

````{py:method} validate(*, strict: bool = True) -> None
:canonical: factor_factory.tidy.panel.Panel.validate

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.validate
```

````

````{py:method} to_dataframe() -> pandas.DataFrame
:canonical: factor_factory.tidy.panel.Panel.to_dataframe

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.to_dataframe
```

````

````{py:method} balance(*, fill_value: float = 0.0) -> factor_factory.tidy.panel.Panel
:canonical: factor_factory.tidy.panel.Panel.balance

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.balance
```

````

````{py:method} attach_treatment_columns(events: tuple[factor_factory.tidy.contracts.TreatmentEvent, ...] | None = None, *, replace: bool = False) -> factor_factory.tidy.panel.Panel
:canonical: factor_factory.tidy.panel.Panel.attach_treatment_columns

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.attach_treatment_columns
```

````

````{py:method} summary() -> dict[str, typing.Any]
:canonical: factor_factory.tidy.panel.Panel.summary

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.summary
```

````

````{py:method} per_event_columns(event_name: str) -> tuple[str, str, str]
:canonical: factor_factory.tidy.panel.Panel.per_event_columns

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.per_event_columns
```

````

````{py:method} to_parquet(path: str | pathlib.Path) -> pathlib.Path
:canonical: factor_factory.tidy.panel.Panel.to_parquet

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.to_parquet
```

````

````{py:method} from_parquet(path: str | pathlib.Path) -> factor_factory.tidy.panel.Panel
:canonical: factor_factory.tidy.panel.Panel.from_parquet
:classmethod:

```{autodoc2-docstring} factor_factory.tidy.panel.Panel.from_parquet
```

````

`````
