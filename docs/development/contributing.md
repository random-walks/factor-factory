# Contributing

See [`CONTRIBUTING.md`](https://github.com/random-walks/factor-factory/blob/main/CONTRIBUTING.md) at the repo root. Highlights:

- Three contract invariants (Panel / Engine Protocol / Tearsheet JSON) — breaking any = major bump.
- Piggyback-first: consult [`../reference/piggyback-map.md`](../reference/piggyback-map.md) before writing math.
- Every new engine family follows the [add-an-engine flow](adding-an-engine.md).
- Pre-merge: `make lint && make test && make docs-build` green + `/contract-check` clean.
