# Data — __PROJECT__

This directory holds raw + tidied data for the project.

## Layout

```
data/
├── README.md          ← this file
├── raw/               ← raw records (cached fetches; gitignored)
└── panel.parquet      ← validated factor-factory Panel
```

## Where the Panel comes from

The scaffolded notebook (`notebooks/01_load.py`) builds a synthetic
panel out of the box so the project runs without a data source. To
swap in real data:

1. Implement a fetcher in `_helpers.py` (or use a domain package's
   adapter — e.g., `nyc311.io.NYC311SocrataAdapter`).
2. In `01_load.py`, replace the synthetic-records block with:
   ```python
   from _helpers import load_records
   records = load_records()
   panel = Panel.from_records(records, geography="...", freq="ME", ...)
   ```
3. Re-run `pnpm showcase:run` (or `jellycell run`).

## Escape hatches

- **Live fetch on every run**: not recommended for long pipelines;
  use a cached + dedup'd `raw/` directory.
- **Pre-built panel**: drop a `panel.parquet` here directly; the
  notebook reads it via `Panel.from_parquet`.

See `docs/getting-started.md` in factor-factory for more.
