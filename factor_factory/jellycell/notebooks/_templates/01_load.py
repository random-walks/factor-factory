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
    dimension="community_district",
    freq="ME",
    treatment_events=(
        TreatmentEvent(
            name="example_pilot",
            treated_units=treated_units,
            treatment_date=date(2024, 6, 1),
            dimension="community_district",
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


# %% tags=["jc.step", "name=tearsheets", "deps=did", "deps=trends"]
# Canonical five — fixed-schema manuscripts driven from on-disk artifacts.
# Use these for the standard showcase deliverables.
from factor_factory.jellycell.cells import setup

ns = setup()
jc = ns["jc"]

from factor_factory.jellycell import tearsheets

for name in ("methodology", "diagnostics", "findings", "manuscript", "audit"):
    out = getattr(tearsheets, name)("__PROJECT__", overwrite=True)
    print(f"wrote {out}")


# %% tags=["jc.step", "name=adhoc_tearsheets", "deps=did"]
# Complement to the fixed five above: the upstream `jellycell.tearsheets.*`
# API (jellycell 1.4.0+) is a generic in-memory renderer good for ad-hoc
# tearsheets that live outside the canonical manuscripts — e.g., per-
# subgroup findings, per-sensitivity audit pages, or one-off methodology
# callouts. The output participates in the jellycell cache graph because
# it runs inside a `jc.step`-tagged cell.
#
# Rule of thumb:
#   - factor_factory.jellycell.tearsheets.* -> the five canonical showcase
#     manuscripts (METHODOLOGY, DIAGNOSTICS_CHECKLIST, FINDINGS,
#     MANUSCRIPT, AUDIT). Jinja2 templates; `<!-- tearsheet:freeze -->`
#     splice marker for hand-edited sections.
#   - jellycell.tearsheets.*                 -> anything else. Dict in,
#     markdown out; no filesystem layout assumed.
from factor_factory.jellycell.cells import setup

ns = setup()
jc = ns["jc"]

import json
from pathlib import Path

import jellycell.tearsheets as jt

did_records = json.loads(Path("artifacts/did_results.json").read_text())
# Re-shape list-of-records -> {estimator: {metric: value}} for jt.findings.
did_by_method: dict[str, dict[str, object]] = {
    rec.get("method", f"est_{i}"): {
        k: v for k, v in rec.items() if k != "method" and isinstance(v, (int, float, str))
    }
    for i, rec in enumerate(did_records)
}

jt.findings(
    results=did_by_method,
    out_path="manuscripts/_adhoc/findings_inline.md",
    project="__PROJECT__",
    template_overrides={"author": "__PROJECT__"},
)

jt.methodology(
    spec={
        "Design": "Two-way fixed effects on a synthetic panel (demo scaffold).",
        "Identification": "Parallel-trends assumption — see DIAGNOSTICS_CHECKLIST.md for the visual check.",
        "Estimator": "`factor_factory.engines.did.estimate(methods=('twfe',))` (wraps `linearmodels`).",
    },
    out_path="manuscripts/_adhoc/methodology_inline.md",
    project="__PROJECT__",
    template_overrides={"author": "__PROJECT__"},
)

print("wrote manuscripts/_adhoc/{findings_inline,methodology_inline}.md")
