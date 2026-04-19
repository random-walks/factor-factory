---
orphan: true
---

# {py:mod}`factor_factory.engines.event_study._base`

```{py:module} factor_factory.engines.event_study._base
```

```{autodoc2-docstring} factor_factory.engines.event_study._base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EventStudyResult <factor_factory.engines.event_study._base.EventStudyResult>`
  - ```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult
    :summary:
    ```
* - {py:obj}`EventStudyEngine <factor_factory.engines.event_study._base.EventStudyEngine>`
  - ```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyEngine
    :summary:
    ```
````

### API

`````{py:class} EventStudyResult
:canonical: factor_factory.engines.event_study._base.EventStudyResult

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult
```

````{py:attribute} method
:canonical: factor_factory.engines.event_study._base.EventStudyResult.method
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.method
```

````

````{py:attribute} n_events
:canonical: factor_factory.engines.event_study._base.EventStudyResult.n_events
:type: int
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.n_events
```

````

````{py:attribute} average_abnormal_return
:canonical: factor_factory.engines.event_study._base.EventStudyResult.average_abnormal_return
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.average_abnormal_return
```

````

````{py:attribute} car_event_window
:canonical: factor_factory.engines.event_study._base.EventStudyResult.car_event_window
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.car_event_window
```

````

````{py:attribute} car_se
:canonical: factor_factory.engines.event_study._base.EventStudyResult.car_se
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.car_se
```

````

````{py:attribute} car_t_stat
:canonical: factor_factory.engines.event_study._base.EventStudyResult.car_t_stat
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.car_t_stat
```

````

````{py:attribute} car_p_value
:canonical: factor_factory.engines.event_study._base.EventStudyResult.car_p_value
:type: float
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.car_p_value
```

````

````{py:attribute} abnormal_return_curve
:canonical: factor_factory.engines.event_study._base.EventStudyResult.abnormal_return_curve
:type: pandas.DataFrame | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.abnormal_return_curve
```

````

````{py:attribute} per_unit_car
:canonical: factor_factory.engines.event_study._base.EventStudyResult.per_unit_car
:type: dict[str, float] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.per_unit_car
```

````

````{py:attribute} estimation_window
:canonical: factor_factory.engines.event_study._base.EventStudyResult.estimation_window
:type: tuple[int, int] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.estimation_window
```

````

````{py:attribute} event_window
:canonical: factor_factory.engines.event_study._base.EventStudyResult.event_window
:type: tuple[int, int] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.event_window
```

````

````{py:attribute} diagnostics
:canonical: factor_factory.engines.event_study._base.EventStudyResult.diagnostics
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.diagnostics
```

````

````{py:attribute} meta
:canonical: factor_factory.engines.event_study._base.EventStudyResult.meta
:type: dict[str, typing.Any] | None
:value: >
   'field(...)'

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.meta
```

````

````{py:method} to_dict() -> dict[str, typing.Any]
:canonical: factor_factory.engines.event_study._base.EventStudyResult.to_dict

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.to_dict
```

````

````{py:method} summary_table() -> pandas.DataFrame
:canonical: factor_factory.engines.event_study._base.EventStudyResult.summary_table

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyResult.summary_table
```

````

`````

`````{py:class} EventStudyEngine
:canonical: factor_factory.engines.event_study._base.EventStudyEngine

Bases: {py:obj}`typing.Protocol`

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyEngine
```

````{py:attribute} name
:canonical: factor_factory.engines.event_study._base.EventStudyEngine.name
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyEngine.name
```

````

````{py:method} fit(panel: factor_factory.tidy.panel.Panel, *, outcome: str, market_col: str | None = None, estimation_window: tuple[int, int] = (-120, -20), event_window: tuple[int, int] = (-1, 1), **engine_specific_kwargs: typing.Any) -> factor_factory.engines.event_study._base.EventStudyResult
:canonical: factor_factory.engines.event_study._base.EventStudyEngine.fit

```{autodoc2-docstring} factor_factory.engines.event_study._base.EventStudyEngine.fit
```

````

`````
