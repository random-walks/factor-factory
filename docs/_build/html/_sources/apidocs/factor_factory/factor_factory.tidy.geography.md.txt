# {py:mod}`factor_factory.tidy.geography`

```{py:module} factor_factory.tidy.geography
```

```{autodoc2-docstring} factor_factory.tidy.geography
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BoundaryFeature <factor_factory.tidy.geography.BoundaryFeature>`
  - ```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryFeature
    :summary:
    ```
* - {py:obj}`BoundaryCollection <factor_factory.tidy.geography.BoundaryCollection>`
  - ```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryCollection
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`register_boundary_source <factor_factory.tidy.geography.register_boundary_source>`
  - ```{autodoc2-docstring} factor_factory.tidy.geography.register_boundary_source
    :summary:
    ```
* - {py:obj}`load_boundaries <factor_factory.tidy.geography.load_boundaries>`
  - ```{autodoc2-docstring} factor_factory.tidy.geography.load_boundaries
    :summary:
    ```
* - {py:obj}`centroids_from_boundaries <factor_factory.tidy.geography.centroids_from_boundaries>`
  - ```{autodoc2-docstring} factor_factory.tidy.geography.centroids_from_boundaries
    :summary:
    ```
* - {py:obj}`distance_matrix <factor_factory.tidy.geography.distance_matrix>`
  - ```{autodoc2-docstring} factor_factory.tidy.geography.distance_matrix
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BoundarySourceAdapter <factor_factory.tidy.geography.BoundarySourceAdapter>`
  - ```{autodoc2-docstring} factor_factory.tidy.geography.BoundarySourceAdapter
    :summary:
    ```
````

### API

`````{py:class} BoundaryFeature
:canonical: factor_factory.tidy.geography.BoundaryFeature

```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryFeature
```

````{py:attribute} geography_value
:canonical: factor_factory.tidy.geography.BoundaryFeature.geography_value
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryFeature.geography_value
```

````

````{py:attribute} geometry
:canonical: factor_factory.tidy.geography.BoundaryFeature.geometry
:type: dict[str, typing.Any]
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryFeature.geometry
```

````

````{py:attribute} properties
:canonical: factor_factory.tidy.geography.BoundaryFeature.properties
:type: dict[str, typing.Any] | None
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryFeature.properties
```

````

`````

`````{py:class} BoundaryCollection
:canonical: factor_factory.tidy.geography.BoundaryCollection

```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryCollection
```

````{py:attribute} features
:canonical: factor_factory.tidy.geography.BoundaryCollection.features
:type: tuple[factor_factory.tidy.geography.BoundaryFeature, ...]
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryCollection.features
```

````

````{py:attribute} geography
:canonical: factor_factory.tidy.geography.BoundaryCollection.geography
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryCollection.geography
```

````

````{py:attribute} source
:canonical: factor_factory.tidy.geography.BoundaryCollection.source
:type: str
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.geography.BoundaryCollection.source
```

````

`````

````{py:data} BoundarySourceAdapter
:canonical: factor_factory.tidy.geography.BoundarySourceAdapter
:value: >
   None

```{autodoc2-docstring} factor_factory.tidy.geography.BoundarySourceAdapter
```

````

````{py:function} register_boundary_source(name: str, adapter: factor_factory.tidy.geography.BoundarySourceAdapter) -> None
:canonical: factor_factory.tidy.geography.register_boundary_source

```{autodoc2-docstring} factor_factory.tidy.geography.register_boundary_source
```
````

````{py:function} load_boundaries(layer: str, *, source: str = 'nyc_geo_toolkit') -> factor_factory.tidy.geography.BoundaryCollection
:canonical: factor_factory.tidy.geography.load_boundaries

```{autodoc2-docstring} factor_factory.tidy.geography.load_boundaries
```
````

````{py:function} centroids_from_boundaries(collection: factor_factory.tidy.geography.BoundaryCollection) -> dict[str, tuple[float, float]]
:canonical: factor_factory.tidy.geography.centroids_from_boundaries

```{autodoc2-docstring} factor_factory.tidy.geography.centroids_from_boundaries
```
````

````{py:function} distance_matrix(centroids: dict[str, tuple[float, float]]) -> pandas.DataFrame
:canonical: factor_factory.tidy.geography.distance_matrix

```{autodoc2-docstring} factor_factory.tidy.geography.distance_matrix
```
````
