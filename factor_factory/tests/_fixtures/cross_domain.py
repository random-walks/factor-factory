"""Cross-domain synthetic fixtures.

These exercise the Panel contract beyond the NYC-civic shape:

- :func:`finance_event_study_panel` — daily ticker × calendar date with
  an event_date that triggers abnormal returns.
- :func:`rct_longitudinal_panel` — patient × visit-week with
  multi-arm (placebo / low_dose / high_dose) categorical treatment.
- :func:`agronomic_dose_response_panel` — plot × season with
  continuous treatment intensity (fertilizer kg/ha).
- :func:`chem_assay_panel` — compound × concentration (float period_kind),
  no time dimension at all.
- :func:`staggered_did_panel` — multi-event panel with three policy
  rollouts at different dates, exercising per-event columns.

Each fixture returns a validated ``Panel``. Conformance tests
parametrize over them to ensure the framework handles every shape.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ...tidy import Panel, Provenance, TreatmentEvent
from ...tidy.contracts import PanelMetadata
from ...tidy.panel import _attach_treatment_columns

_SEED = 20260420


def finance_event_study_panel() -> Panel:
    """Daily-returns panel with a single event date.

    Shape: 30 tickers × 252 trading days. Treated tickers see a +2bp
    abnormal-return jump on the event date.
    """
    rng = np.random.default_rng(_SEED)
    tickers = [f"TKR{i:02d}" for i in range(30)]
    dates = pd.bdate_range("2024-01-02", periods=252)
    treated = tuple(tickers[:10])
    event_day_index = 126  # mid-year

    rows = []
    for tkr in tickers:
        ticker_drift = float(rng.normal(0.0001, 0.0001))
        is_treated = tkr in treated
        for i, d in enumerate(dates):
            ret = float(ticker_drift + rng.normal(0.0, 0.01))
            if is_treated and i >= event_day_index:
                ret += 0.0002  # +2 bp abnormal return
            rows.append(
                {
                    "unit_id": tkr,
                    "period": d,
                    "returns": ret,
                    "abnormal_returns": ret - ticker_drift,
                    "market_cap_mm": float(rng.uniform(500, 5000)),
                }
            )
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    metadata = PanelMetadata(
        outcome_cols=("returns", "abnormal_returns"),
        period_kind="timestamp",
        freq=None,  # business days, not month-end
        dimension="ticker",
        treatment_events=(
            TreatmentEvent(
                name="earnings_event",
                description="Synthetic earnings-announcement event",
                treated_units=treated,
                treatment_date=dates[event_day_index].date(),
                dimension="ticker",
            ),
        ),
        weights_col="market_cap_mm",
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, metadata.treatment_events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def rct_longitudinal_panel() -> Panel:
    """Multi-arm RCT: patient × visit_week with categorical treatment.

    Shape: 60 patients × 12 visit weeks. Three arms (placebo, low_dose,
    high_dose) split evenly.
    """
    rng = np.random.default_rng(_SEED + 1)
    patients = [f"PT{i:03d}" for i in range(60)]
    visit_weeks = pd.date_range("2024-03-04", periods=12, freq="W")
    enrolment_date = visit_weeks[1].date()

    arm_assignment = {
        p: ("placebo", "low_dose", "high_dose")[i % 3] for i, p in enumerate(patients)
    }
    arm_effect = {"placebo": 0.0, "low_dose": -0.5, "high_dose": -1.5}

    rows = []
    for p in patients:
        baseline = float(rng.normal(8.0, 1.0))
        arm = arm_assignment[p]
        for i, w in enumerate(visit_weeks):
            score = baseline - 0.05 * i + rng.normal(0, 0.3)
            if i >= 1:  # post-enrolment
                score += arm_effect[arm] * (i / len(visit_weeks))
            rows.append(
                {
                    "unit_id": p,
                    "period": w,
                    "symptom_score": float(score),
                    "adverse_events": int(rng.poisson(0.1 if arm == "high_dose" else 0.05)),
                }
            )
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    metadata = PanelMetadata(
        outcome_cols=("symptom_score", "adverse_events"),
        period_kind="timestamp",
        freq="W",
        dimension="patient_id",
        treatment_events=(
            TreatmentEvent(
                name="low_dose",
                treated_units=tuple(p for p, a in arm_assignment.items() if a == "low_dose"),
                treatment_date=enrolment_date,
                dimension="patient_id",
                kind="categorical",
                arm="low_dose",
            ),
            TreatmentEvent(
                name="high_dose",
                treated_units=tuple(p for p, a in arm_assignment.items() if a == "high_dose"),
                treatment_date=enrolment_date,
                dimension="patient_id",
                kind="categorical",
                arm="high_dose",
            ),
        ),
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            ethics_note="Synthetic data; no human subjects.",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, metadata.treatment_events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def agronomic_dose_response_panel() -> Panel:
    """Plot × season with continuous treatment intensity (kg/ha).

    Shape: 40 plots × 6 seasons. Treated plots receive variable
    fertilizer doses; outcome is yield in tons/ha.
    """
    rng = np.random.default_rng(_SEED + 2)
    plots = [f"PLOT-{i:03d}" for i in range(40)]
    seasons = pd.date_range("2022-09-30", periods=6, freq="6ME")
    treatment_start = seasons[2].date()
    treated = tuple(plots[:20])
    dose_kg_per_ha = 80.0

    rows = []
    for plot in plots:
        soil_quality = float(rng.normal(5.0, 0.7))
        is_treated = plot in treated
        plot_area = float(rng.uniform(0.5, 3.0))
        for i, s in enumerate(seasons):
            base_yield = soil_quality + 0.1 * i + rng.normal(0, 0.3)
            if is_treated and i >= 2:
                base_yield += 0.012 * dose_kg_per_ha
            rows.append(
                {
                    "unit_id": plot,
                    "period": s,
                    "yield_tons_per_ha": float(base_yield),
                    "plot_area_ha": plot_area,
                }
            )
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    metadata = PanelMetadata(
        outcome_cols=("yield_tons_per_ha",),
        period_kind="timestamp",
        freq="6ME",
        dimension="plot_id",
        treatment_events=(
            TreatmentEvent(
                name="fertilizer_program",
                treated_units=treated,
                treatment_date=treatment_start,
                dimension="plot_id",
                kind="continuous",
                intensity=dose_kg_per_ha,
            ),
        ),
        weights_col="plot_area_ha",
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, metadata.treatment_events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def chem_assay_panel() -> Panel:
    """Compound × concentration (float period_kind), no time dimension.

    Shape: 12 compounds × 8 concentration levels. Period is dose
    concentration (μM), period_kind='float'. No treatment events
    (this is a pure dose-response panel).
    """
    rng = np.random.default_rng(_SEED + 3)
    compounds = [f"CMP-{i:02d}" for i in range(12)]
    concentrations = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]

    rows = []
    for c in compounds:
        ic50 = float(rng.uniform(0.5, 5.0))
        emax = float(rng.uniform(0.7, 1.0))
        for conc in concentrations:
            response = emax * conc / (conc + ic50) + rng.normal(0, 0.03)
            rows.append({"unit_id": c, "period": conc, "response_fraction": float(response)})
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    metadata = PanelMetadata(
        outcome_cols=("response_fraction",),
        period_kind="float",
        freq=None,
        dimension="compound_id",
        treatment_events=(),
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            citation="factor-factory cross-domain fixture",
        ),
    )
    return Panel(df.sort_index(), metadata)


def staggered_did_panel() -> Panel:
    """Three policy rollouts at different dates — exercises per-event columns.

    Shape: 90 units × 36 months. Three policies (alpha, beta, gamma)
    each treat a disjoint third of the units at different dates.
    """
    rng = np.random.default_rng(_SEED + 4)
    units = [f"U{i:03d}" for i in range(90)]
    months = pd.date_range("2022-01-31", periods=36, freq="ME")

    pol_alpha_units = tuple(units[0:30])
    pol_beta_units = tuple(units[30:60])
    pol_gamma_units = tuple(units[60:90])
    pol_alpha_date = months[6].date()
    pol_beta_date = months[12].date()
    pol_gamma_date = months[18].date()

    treatment_effects = {
        pol_alpha_units: (pol_alpha_date, 3.0),
        pol_beta_units: (pol_beta_date, 1.5),
        pol_gamma_units: (pol_gamma_date, 5.0),
    }

    rows = []
    for u in units:
        unit_fe = float(rng.normal(0, 1))
        for i, m in enumerate(months):
            outcome = 10.0 + unit_fe + 0.05 * i + rng.normal(0, 0.8)
            for treated_set, (start_date, eff) in treatment_effects.items():
                if u in treated_set and m.date() >= start_date:
                    outcome += eff
            rows.append({"unit_id": u, "period": m, "outcome": float(outcome)})
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    events = (
        TreatmentEvent(
            name="alpha",
            treated_units=pol_alpha_units,
            treatment_date=pol_alpha_date,
            dimension="unit",
        ),
        TreatmentEvent(
            name="beta",
            treated_units=pol_beta_units,
            treatment_date=pol_beta_date,
            dimension="unit",
        ),
        TreatmentEvent(
            name="gamma",
            treated_units=pol_gamma_units,
            treatment_date=pol_gamma_date,
            dimension="unit",
        ),
    )
    metadata = PanelMetadata(
        outcome_cols=("outcome",),
        period_kind="timestamp",
        freq="ME",
        dimension="unit",
        treatment_events=events,
        record_count=len(df),
    )
    df = _attach_treatment_columns(df, events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


__all__ = [
    "agronomic_dose_response_panel",
    "chem_assay_panel",
    "finance_event_study_panel",
    "rct_longitudinal_panel",
    "staggered_did_panel",
]
