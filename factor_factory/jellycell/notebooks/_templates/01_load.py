# /// script
# requires-python = ">=3.12"
# dependencies = ["factor-factory[did]"]
# ///

# %% [markdown]
# # __PROJECT__ — load
#
# Build a synthetic panel via ``factor_factory.tidy.Panel.from_records``,
# save a summary artifact, and emit a parallel-trends figure. Replace
# the synthetic generator with a real ``Panel.from_records(real_records, ...)``
# call once you've wired in your data source (e.g., a Socrata adapter).

# %% tags=["jc.load", "name=panel"]
from factor_factory.jellycell.cells import setup

ns = setup(also=("matplotlib.pyplot as plt",))
jc, pd, np, plt, Image = ns["jc"], ns["pd"], ns["np"], ns["plt"], ns["Image"]

from datetime import date

from factor_factory.tidy import Panel, TreatmentEvent

rng = np.random.default_rng(20260419)
units = [f"unit-{i:02d}" for i in range(20)]
periods = pd.date_range("2023-01-31", periods=24, freq="ME")
treated_units = tuple(units[:10])

records = []
for unit in units:
    is_treated = unit in treated_units
    for p in periods:
        post = int(p >= pd.Timestamp("2024-06-30"))
        base = 50.0 + (5.0 if is_treated else 0.0) + rng.normal(0, 2.0)
        effect = 5.0 if is_treated and post else 0.0
        n = max(0, int(round(base + effect)))
        for _ in range(n):
            records.append(
                {"community_district": unit, "created_date": p, "latitude": 40.7, "longitude": -74.0}
            )

panel = Panel.from_records(
    records,
    geography="community_district",
    freq="ME",
    treatment_events=(
        TreatmentEvent(
            name="example_pilot",
            treated_units=treated_units,
            treatment_date=date(2024, 6, 1),
            geography="community_district",
        ),
    ),
    outcome_col="complaint_count",
)
panel.to_parquet("data/panel.parquet")
jc.save(
    {
        "n_units": len(panel.unit_ids),
        "n_periods": len(panel.periods),
        "outcome_col": panel.outcome_col,
    },
    "artifacts/panel_summary.json",
    caption="Synthetic panel summary",
)


# %% tags=["jc.step", "name=did", "deps=panel"]
from factor_factory.jellycell.cells import setup

ns = setup()
jc, pd, np = ns["jc"], ns["pd"], ns["np"]

from factor_factory.engines.did import estimate
from factor_factory.tidy import Panel

panel = Panel.from_parquet("data/panel.parquet")
results = estimate(panel, methods=("twfe",), cluster="unit_id")
jc.save(results.to_records(), "artifacts/did_results.json", caption="DiD ATT (TWFE)")
print(results.summary_table())


# %% tags=["jc.step", "name=trends", "deps=panel"]
from factor_factory.jellycell.cells import setup

ns = setup(also=("matplotlib.pyplot as plt",))
jc, pd, np, plt = ns["jc"], ns["pd"], ns["np"], ns["plt"]

from factor_factory.diagnostics import parallel_trends_plot
from factor_factory.tidy import Panel

panel = Panel.from_parquet("data/panel.parquet")
fig = parallel_trends_plot(panel)
fig.savefig("artifacts/figures/parallel_trends.png", dpi=120)
plt.close(fig)
print("saved artifacts/figures/parallel_trends.png")


# %% tags=["jc.step", "name=tearsheets", "deps=did,trends"]
from factor_factory.jellycell.cells import setup

ns = setup()
jc = ns["jc"]

from factor_factory.jellycell import tearsheets

for name in ("methodology", "diagnostics", "findings", "manuscript", "audit"):
    out = getattr(tearsheets, name)("__PROJECT__", overwrite=True)
    print(f"wrote {out}")
