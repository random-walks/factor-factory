# {py:mod}`factor_factory.tidy.socrata`

```{py:module} factor_factory.tidy.socrata
```

```{autodoc2-docstring} factor_factory.tidy.socrata
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SocrataAdapter <factor_factory.tidy.socrata.SocrataAdapter>`
  - ```{autodoc2-docstring} factor_factory.tidy.socrata.SocrataAdapter
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`bulk_fetch <factor_factory.tidy.socrata.bulk_fetch>`
  - ```{autodoc2-docstring} factor_factory.tidy.socrata.bulk_fetch
    :summary:
    ```
* - {py:obj}`bulk_fetch_async <factor_factory.tidy.socrata.bulk_fetch_async>`
  - ```{autodoc2-docstring} factor_factory.tidy.socrata.bulk_fetch_async
    :summary:
    ```
````

### API

`````{py:class} SocrataAdapter
:canonical: factor_factory.tidy.socrata.SocrataAdapter

Bases: {py:obj}`typing.Protocol`

```{autodoc2-docstring} factor_factory.tidy.socrata.SocrataAdapter
```

````{py:attribute} base_url
:canonical: factor_factory.tidy.socrata.SocrataAdapter.base_url
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.socrata.SocrataAdapter.base_url
```

````

````{py:attribute} dataset_id
:canonical: factor_factory.tidy.socrata.SocrataAdapter.dataset_id
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.socrata.SocrataAdapter.dataset_id
```

````

````{py:method} fetch(*, filters: dict[str, str], start_date: datetime.date, end_date: datetime.date, cache_dir: pathlib.Path, chunk_size: int = 5000) -> list[pathlib.Path]
:canonical: factor_factory.tidy.socrata.SocrataAdapter.fetch

```{autodoc2-docstring} factor_factory.tidy.socrata.SocrataAdapter.fetch
```

````

````{py:method} load(paths: list[pathlib.Path]) -> list[dict[str, object]]
:canonical: factor_factory.tidy.socrata.SocrataAdapter.load

```{autodoc2-docstring} factor_factory.tidy.socrata.SocrataAdapter.load
```

````

`````

````{py:function} bulk_fetch(adapter: factor_factory.tidy.socrata.SocrataAdapter, *, filters: dict[str, str], start_date: datetime.date, end_date: datetime.date, cache_dir: pathlib.Path, on_progress: collections.abc.Callable[[str, int, int], None] | None = None) -> list[pathlib.Path]
:canonical: factor_factory.tidy.socrata.bulk_fetch

```{autodoc2-docstring} factor_factory.tidy.socrata.bulk_fetch
```
````

````{py:function} bulk_fetch_async(adapter: factor_factory.tidy.socrata.SocrataAdapter, *, filters: dict[str, str], start_date: datetime.date, end_date: datetime.date, cache_dir: pathlib.Path, concurrency: int = 4, on_progress: collections.abc.Callable[[str, int, int], None] | None = None) -> list[pathlib.Path]
:canonical: factor_factory.tidy.socrata.bulk_fetch_async
:async:

```{autodoc2-docstring} factor_factory.tidy.socrata.bulk_fetch_async
```
````
