# {py:mod}`factor_factory.tidy.record_view`

```{py:module} factor_factory.tidy.record_view
```

```{autodoc2-docstring} factor_factory.tidy.record_view
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RecordView <factor_factory.tidy.record_view.RecordView>`
  - ```{autodoc2-docstring} factor_factory.tidy.record_view.RecordView
    :summary:
    ```
````

### API

`````{py:class} RecordView
:canonical: factor_factory.tidy.record_view.RecordView

```{autodoc2-docstring} factor_factory.tidy.record_view.RecordView
```

````{py:attribute} df
:canonical: factor_factory.tidy.record_view.RecordView.df
:type: pandas.DataFrame
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.record_view.RecordView.df
```

````

````{py:attribute} schema_version
:canonical: factor_factory.tidy.record_view.RecordView.schema_version
:type: int
:value: >
   1

```{autodoc2-docstring} factor_factory.tidy.record_view.RecordView.schema_version
```

````

````{py:attribute} REQUIRED_COLUMNS
:canonical: factor_factory.tidy.record_view.RecordView.REQUIRED_COLUMNS
:value: >
   ('unit_id', 'period')

```{autodoc2-docstring} factor_factory.tidy.record_view.RecordView.REQUIRED_COLUMNS
```

````

````{py:property} has_latlon
:canonical: factor_factory.tidy.record_view.RecordView.has_latlon
:type: bool

```{autodoc2-docstring} factor_factory.tidy.record_view.RecordView.has_latlon
```

````

````{py:method} filter(*, period_start: datetime.date | pandas.Timestamp | int | float | None = None, period_end: datetime.date | pandas.Timestamp | int | float | None = None, unit_ids: tuple[typing.Any, ...] | None = None) -> factor_factory.tidy.record_view.RecordView
:canonical: factor_factory.tidy.record_view.RecordView.filter

```{autodoc2-docstring} factor_factory.tidy.record_view.RecordView.filter
```

````

````{py:method} distance_to_point(lon: float, lat: float) -> pandas.Series
:canonical: factor_factory.tidy.record_view.RecordView.distance_to_point

```{autodoc2-docstring} factor_factory.tidy.record_view.RecordView.distance_to_point
```

````

`````
