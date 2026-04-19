# {py:mod}`factor_factory.tidy.contracts`

```{py:module} factor_factory.tidy.contracts
```

```{autodoc2-docstring} factor_factory.tidy.contracts
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`TreatmentEvent <factor_factory.tidy.contracts.TreatmentEvent>`
  - ```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent
    :summary:
    ```
* - {py:obj}`Provenance <factor_factory.tidy.contracts.Provenance>`
  - ```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance
    :summary:
    ```
* - {py:obj}`PanelMetadata <factor_factory.tidy.contracts.PanelMetadata>`
  - ```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`TreatmentKind <factor_factory.tidy.contracts.TreatmentKind>`
  - ```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentKind
    :summary:
    ```
````

### API

````{py:data} TreatmentKind
:canonical: factor_factory.tidy.contracts.TreatmentKind
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentKind
```

````

`````{py:class} TreatmentEvent(/, **data: typing.Any)
:canonical: factor_factory.tidy.contracts.TreatmentEvent

Bases: {py:obj}`pydantic.BaseModel`

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.__init__
```

````{py:attribute} model_config
:canonical: factor_factory.tidy.contracts.TreatmentEvent.model_config
:value: >
   'ConfigDict(...)'

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.model_config
```

````

````{py:attribute} name
:canonical: factor_factory.tidy.contracts.TreatmentEvent.name
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.name
```

````

````{py:attribute} description
:canonical: factor_factory.tidy.contracts.TreatmentEvent.description
:type: str
:value: <Multiline-String>

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.description
```

````

````{py:attribute} treated_units
:canonical: factor_factory.tidy.contracts.TreatmentEvent.treated_units
:type: tuple[typing.Any, ...]
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.treated_units
```

````

````{py:attribute} treatment_date
:canonical: factor_factory.tidy.contracts.TreatmentEvent.treatment_date
:type: datetime.date | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.treatment_date
```

````

````{py:attribute} period_value
:canonical: factor_factory.tidy.contracts.TreatmentEvent.period_value
:type: float | int | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.period_value
```

````

````{py:attribute} dimension
:canonical: factor_factory.tidy.contracts.TreatmentEvent.dimension
:type: str
:value: >
   'unit'

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.dimension
```

````

````{py:attribute} kind
:canonical: factor_factory.tidy.contracts.TreatmentEvent.kind
:type: factor_factory.tidy.contracts.TreatmentKind
:value: >
   'binary'

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.kind
```

````

````{py:attribute} intensity
:canonical: factor_factory.tidy.contracts.TreatmentEvent.intensity
:type: float | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.intensity
```

````

````{py:attribute} arm
:canonical: factor_factory.tidy.contracts.TreatmentEvent.arm
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.arm
```

````

````{py:attribute} metadata
:canonical: factor_factory.tidy.contracts.TreatmentEvent.metadata
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.TreatmentEvent.metadata
```

````

`````

`````{py:class} Provenance(/, **data: typing.Any)
:canonical: factor_factory.tidy.contracts.Provenance

Bases: {py:obj}`pydantic.BaseModel`

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance.__init__
```

````{py:attribute} model_config
:canonical: factor_factory.tidy.contracts.Provenance.model_config
:value: >
   'ConfigDict(...)'

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance.model_config
```

````

````{py:attribute} data_source
:canonical: factor_factory.tidy.contracts.Provenance.data_source
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance.data_source
```

````

````{py:attribute} license
:canonical: factor_factory.tidy.contracts.Provenance.license
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance.license
```

````

````{py:attribute} ethics_note
:canonical: factor_factory.tidy.contracts.Provenance.ethics_note
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance.ethics_note
```

````

````{py:attribute} citation
:canonical: factor_factory.tidy.contracts.Provenance.citation
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance.citation
```

````

````{py:attribute} creator
:canonical: factor_factory.tidy.contracts.Provenance.creator
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance.creator
```

````

````{py:attribute} dataset_version
:canonical: factor_factory.tidy.contracts.Provenance.dataset_version
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance.dataset_version
```

````

````{py:attribute} created_at
:canonical: factor_factory.tidy.contracts.Provenance.created_at
:type: datetime.datetime | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.Provenance.created_at
```

````

`````

`````{py:class} PanelMetadata(/, **data: typing.Any)
:canonical: factor_factory.tidy.contracts.PanelMetadata

Bases: {py:obj}`pydantic.BaseModel`

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata
```

```{rubric} Initialization
```

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.__init__
```

````{py:attribute} model_config
:canonical: factor_factory.tidy.contracts.PanelMetadata.model_config
:value: >
   'ConfigDict(...)'

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.model_config
```

````

````{py:attribute} outcome_cols
:canonical: factor_factory.tidy.contracts.PanelMetadata.outcome_cols
:type: tuple[str, ...]
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.outcome_cols
```

````

````{py:attribute} period_kind
:canonical: factor_factory.tidy.contracts.PanelMetadata.period_kind
:type: typing.Literal[timestamp, integer, float, ordinal]
:value: >
   'timestamp'

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.period_kind
```

````

````{py:attribute} freq
:canonical: factor_factory.tidy.contracts.PanelMetadata.freq
:type: str | None
:value: >
   'ME'

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.freq
```

````

````{py:attribute} dimension
:canonical: factor_factory.tidy.contracts.PanelMetadata.dimension
:type: str
:value: >
   'unit'

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.dimension
```

````

````{py:attribute} treatment_events
:canonical: factor_factory.tidy.contracts.PanelMetadata.treatment_events
:type: tuple[factor_factory.tidy.contracts.TreatmentEvent, ...]
:value: >
   ()

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.treatment_events
```

````

````{py:attribute} weights_col
:canonical: factor_factory.tidy.contracts.PanelMetadata.weights_col
:type: str | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.weights_col
```

````

````{py:attribute} record_count
:canonical: factor_factory.tidy.contracts.PanelMetadata.record_count
:type: int
:value: >
   0

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.record_count
```

````

````{py:attribute} provenance
:canonical: factor_factory.tidy.contracts.PanelMetadata.provenance
:type: factor_factory.tidy.contracts.Provenance
:value: >
   'Field(...)'

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.provenance
```

````

````{py:property} outcome_col
:canonical: factor_factory.tidy.contracts.PanelMetadata.outcome_col
:type: str

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.outcome_col
```

````

````{py:property} geography
:canonical: factor_factory.tidy.contracts.PanelMetadata.geography
:type: str

```{autodoc2-docstring} factor_factory.tidy.contracts.PanelMetadata.geography
```

````

`````
