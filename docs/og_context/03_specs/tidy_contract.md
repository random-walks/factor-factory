# Spec: Tidy contract

The `factor_factory.tidy.*` modules own the path from raw records to
a validated `Panel`. This spec pins the API.

## Top-level surface

```python
from factor_factory.tidy import (
    Panel,                   # see panel_contract.md
    TreatmentEvent,          # see panel_contract.md
    RecordView,              # see panel_contract.md
)

from factor_factory.tidy.geography import (
    load_boundaries,         # any layer name; see Geography below
    centroids_from_boundaries,
    distance_matrix,         # haversine pairwise km
)

from factor_factory.tidy.socrata import (
    SocrataAdapter,          # configurable; downstream packages register their own
    bulk_fetch,              # convenience wrapper
)
```

## Geography helpers

```python
def load_boundaries(layer: str,
                    *,
                    source: str = "nyc_geo_toolkit") -> "BoundaryCollection":
    """Load a named geographic boundary layer.

    Parameters
    ----------
    layer : str
        Layer name. Common values: "community_district", "tract",
        "ntab", "council_district". Source-specific layers are also
        accepted (e.g., "subway_station").
    source : str, default "nyc_geo_toolkit"
        Which adapter to use. The default is the NYC-specific adapter
        from `nyc_geo_toolkit`. Other adapters (e.g., Census TIGER)
        can be registered.

    Returns
    -------
    BoundaryCollection
        Iterable of BoundaryFeature objects with `.geometry` (shapely)
        and `.geography_value` (str unit_id).
    """
```

Boundary collection shape:

```python
@dataclass(frozen=True)
class BoundaryFeature:
    geography_value: str          # opaque unit_id (e.g., "MANHATTAN 01")
    geometry: dict                # GeoJSON-style dict (use shapely.shape() to convert)
    properties: dict | None = None

@dataclass(frozen=True)
class BoundaryCollection:
    features: tuple[BoundaryFeature, ...]
    geography: str
    source: str
```

```python
def centroids_from_boundaries(
    collection: BoundaryCollection,
) -> dict[str, tuple[float, float]]:
    """Extract (lon, lat) centroids keyed by geography_value."""
```

```python
def distance_matrix(
    centroids: dict[str, tuple[float, float]],
) -> pd.DataFrame:
    """Pairwise haversine distance in kilometers; symmetric DataFrame
    with unit_id labels on both axes."""
```

## Socrata adapter

The Socrata fetch is the most-duplicated bit across `nyc311` and
`subway-access`. The adapter contract:

```python
from typing import Protocol

class SocrataAdapter(Protocol):
    """Protocol for fetching records from a Socrata-style open data API."""

    base_url: str
    dataset_id: str

    def fetch(self,
              *,
              filters: dict[str, str],
              start_date: date,
              end_date: date,
              cache_dir: Path,
              chunk_size: int = 5000) -> list[Path]:
        """Fetch records matching `filters` and date range, cache as CSV.
        Returns list of cached file paths (one per chunk)."""
        ...

    def load(self, paths: list[Path]) -> list[dict]:
        """Load cached CSVs as a flat list of record dicts."""
        ...
```

Downstream packages register their own adapters:

```python
# nyc311 example (in nyc311.io)
from factor_factory.tidy.socrata import SocrataAdapter

class NYC311Adapter:
    base_url = "https://data.cityofnewyork.us"
    dataset_id = "erm2-nwe9"

    def fetch(self, *, filters, start_date, end_date, cache_dir, chunk_size=5000):
        # ... implementation that knows about NYC 311 schema
        ...

    def load(self, paths):
        # ... loads as ServiceRequestRecord objects
        ...
```

Convenience wrapper for the common case:

```python
def bulk_fetch(
    adapter: SocrataAdapter,
    *,
    filters: dict[str, str],
    start_date: date,
    end_date: date,
    cache_dir: Path,
    on_progress: Callable[[str, int, int], None] | None = None,
) -> list[Path]:
    """Bulk-fetch + cache + dedup. Calls adapter.fetch under the hood."""
```

## Panel construction

```python
class Panel:
    @classmethod
    def from_records(cls,
                     records: Sequence[Any],
                     *,
                     geography: str,
                     freq: str = "ME",
                     treatment_events: tuple[TreatmentEvent, ...] = (),
                     outcome_col: str = "complaint_count",
                     record_view: bool = False,
                     # advanced:
                     unit_id_extractor: Callable[[Any], str] | None = None,
                     period_extractor: Callable[[Any], date] | None = None,
                     latlon_extractor: Callable[[Any], tuple[float, float] | None] | None = None,
                     ) -> "Panel":
        """Build a balanced panel from a sequence of records.

        Parameters
        ----------
        records : sequence of records
            Each record must expose attributes the extractors can
            read. Default extractors assume nyc311.ServiceRequestRecord-shaped
            records; pass custom extractors for other shapes.
        geography : str
            Spatial unit (community_district, tract, station, etc.).
            Used to resolve records to unit_ids if unit_id_extractor
            is None.
        freq : str, default "ME"
            Pandas frequency string for period binning. "ME" = month-end.
        treatment_events : tuple of TreatmentEvent, optional
            If non-empty, the panel includes treated_unit / post /
            treatment columns derived from each event.
        outcome_col : str, default "complaint_count"
            Name of the outcome column in the resulting panel.
        record_view : bool, default False
            If True, attach a RecordView companion with per-record
            lat/lon. Required for record-level RDD via rdrobust.
        unit_id_extractor / period_extractor / latlon_extractor : callable
            Optional overrides for record-shape adaptation.

        Returns
        -------
        Panel
            Validated, balanced panel with the requested columns.
        """
```

## Period binning

`freq="ME"` produces month-end timestamps. Other supported values
(via pandas `pd.PeriodIndex`):

- `"D"` — daily
- `"W"` — weekly (Sun-end)
- `"ME"` — month-end (default)
- `"QE"` — quarter-end
- `"YE"` — year-end

The `period` index level is `pd.Timestamp` (not `Period`) for
compatibility with `linearmodels.PanelOLS`.

## Deduplication policy

Records that share `(unit_id, period, record_id)` are deduplicated
on construction. If `record_id` is unavailable, falls back to
`(unit_id, period, created_date, complaint_type)` for nyc311-style
records. Configurable via:

```python
@dataclass
class TidyConfig:
    dedup_keys: tuple[str, ...] = ("record_id",)
    on_duplicate: Literal["first", "last", "raise"] = "first"
```

## Open questions

- **Streaming construction**: very large panels (>10M records) would
  benefit from chunked construction. Defer to Phase 2.
- **Multi-geography panels**: a panel with both CD-level and
  station-level units? Currently unsupported; users would build two
  separate panels. Revisit if needed.
- **Async fetching**: `bulk_fetch` is synchronous. Should we add an
  async variant for very long fetches? Defer; current fetches are
  ~30s for ~50MB of data, fast enough synchronously.
