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

from typing import Any

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

    Shape: 120 units × 36 months. Three policies (alpha, beta, gamma)
    each treat a disjoint quarter of the units at different dates;
    the remaining quarter are never-treated controls (required by
    Callaway-Sant'Anna with ``control_group="never_treated"``).
    """
    rng = np.random.default_rng(_SEED + 4)
    units = [f"U{i:03d}" for i in range(120)]
    months = pd.date_range("2022-01-31", periods=36, freq="ME")

    pol_alpha_units = tuple(units[0:30])
    pol_beta_units = tuple(units[30:60])
    pol_gamma_units = tuple(units[60:90])
    # units[90:120] are never-treated controls
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


def survival_oncology_panel() -> Panel:
    """Single-arm oncology cohort with right-censored survival.

    Shape: 200 patients × 1 row each, with ``duration`` (months from
    enrolment to death/last-followup) and ``event`` (1 if death
    observed, 0 if right-censored). Two covariates: ``age`` and
    ``ecog_score`` (0-2 performance status).

    True median survival ≈ 18 months; older + higher-ECOG patients
    have higher hazard.
    """
    rng = np.random.default_rng(_SEED + 5)
    n = 200
    patients = [f"PT{i:04d}" for i in range(n)]
    age = rng.normal(65, 10, n).clip(40, 90)
    ecog = rng.choice([0, 1, 2], n, p=[0.5, 0.35, 0.15])
    # Hazard: baseline + age effect + ECOG effect
    log_hazard = -3.5 + 0.02 * (age - 60) + 0.5 * ecog
    rate = np.exp(log_hazard)
    true_survival_time = rng.exponential(1.0 / rate, n)
    # Right-censor at 36 months
    censored_at = 36.0
    duration = np.minimum(true_survival_time, censored_at)
    event = (true_survival_time <= censored_at).astype(int)

    rows = []
    enrol_date = pd.Timestamp("2022-01-31")
    for i, p in enumerate(patients):
        rows.append(
            {
                "unit_id": p,
                "period": enrol_date,  # single observation per patient
                "duration": float(duration[i]),
                "event": int(event[i]),
                "age": float(age[i]),
                "ecog_score": int(ecog[i]),
            }
        )
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    metadata = PanelMetadata(
        outcome_cols=("duration",),
        period_kind="timestamp",
        freq="ME",  # nominal — single period per unit, freq irrelevant
        dimension="patient_id",
        treatment_events=(),
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            ethics_note="Synthetic data; no human subjects.",
            citation="factor-factory cross-domain fixture",
        ),
    )
    return Panel(df.sort_index(), metadata)


def climate_anomaly_panel() -> Panel:
    """Station × month temperature anomaly relative to a 1991-2020 baseline.

    Shape: 20 weather stations × 60 months. Treatment event = a
    'heat dome' year with elevated anomalies for half the stations.
    Outcome is temperature anomaly (°C).
    """
    rng = np.random.default_rng(_SEED + 6)
    stations = [f"STN{i:03d}" for i in range(20)]
    months = pd.date_range("2020-01-31", periods=60, freq="ME")
    treated = tuple(stations[:10])
    heat_dome_start = months[36].date()  # year 4 onward

    rows = []
    for s in stations:
        baseline_offset = float(rng.normal(0.0, 0.3))
        is_treated = s in treated
        for i, m in enumerate(months):
            seasonal = 0.5 * np.sin(2 * np.pi * i / 12)
            anomaly = baseline_offset + seasonal + 0.005 * i + rng.normal(0, 0.4)
            if is_treated and m.date() >= heat_dome_start:
                anomaly += 1.2
            rows.append({"unit_id": s, "period": m, "temp_anomaly_c": float(anomaly)})
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    events = (
        TreatmentEvent(
            name="heat_dome",
            treated_units=treated,
            treatment_date=heat_dome_start,
            dimension="station",
        ),
    )
    metadata = PanelMetadata(
        outcome_cols=("temp_anomaly_c",),
        period_kind="timestamp",
        freq="ME",
        dimension="station",
        treatment_events=events,
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            citation="factor-factory cross-domain fixture",
            dataset_version="2024-baseline-1991-2020",
        ),
    )
    df = _attach_treatment_columns(df, events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def education_value_added_panel() -> Panel:
    """Student × test-period scores with a tutoring intervention rolled out mid-year.

    Shape: 80 students × 8 quarterly assessments. Treated students
    receive supplemental tutoring after period 3.
    """
    rng = np.random.default_rng(_SEED + 7)
    students = [f"S{i:04d}" for i in range(80)]
    periods = pd.date_range("2023-03-31", periods=8, freq="QE")
    treated = tuple(students[:40])
    intervention = periods[3].date()

    rows = []
    for s in students:
        ability = float(rng.normal(0.0, 0.5))
        is_treated = s in treated
        for i, p in enumerate(periods):
            score = 70 + 5 * ability + 0.5 * i + rng.normal(0, 4)
            if is_treated and p.date() >= intervention:
                score += 6.0
            rows.append({"unit_id": s, "period": p, "test_score": float(score)})
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    events = (
        TreatmentEvent(
            name="tutoring",
            treated_units=treated,
            treatment_date=intervention,
            dimension="student_id",
        ),
    )
    metadata = PanelMetadata(
        outcome_cols=("test_score",),
        period_kind="timestamp",
        freq="QE",
        dimension="student_id",
        treatment_events=events,
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            ethics_note="Synthetic data; no human subjects.",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def energy_consumption_panel() -> Panel:
    """Household × month electricity consumption with a smart-meter rebate program.

    Shape: 100 households × 24 months. Half the households opt into a
    rebate program at month 12; outcome is kWh / month.
    """
    rng = np.random.default_rng(_SEED + 8)
    households = [f"H{i:04d}" for i in range(100)]
    months = pd.date_range("2023-01-31", periods=24, freq="ME")
    treated = tuple(households[:50])
    rebate_start = months[12].date()

    rows = []
    for h in households:
        baseline = float(rng.uniform(400, 1200))
        is_treated = h in treated
        for i, m in enumerate(months):
            seasonal = 100 * np.cos(2 * np.pi * i / 12)  # winter peak
            consumption = baseline + seasonal + rng.normal(0, 50)
            if is_treated and m.date() >= rebate_start:
                consumption *= 0.92  # 8% reduction
            rows.append({"unit_id": h, "period": m, "kwh": float(consumption), "rate_zone": "A"})
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    events = (
        TreatmentEvent(
            name="rebate_program",
            treated_units=treated,
            treatment_date=rebate_start,
            dimension="household_id",
        ),
    )
    metadata = PanelMetadata(
        outcome_cols=("kwh",),
        period_kind="timestamp",
        freq="ME",
        dimension="household_id",
        treatment_events=events,
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def marketing_uplift_panel() -> Panel:
    """User × week conversion rates from an A/B test of two campaign creatives.

    Shape: 500 users × 8 weeks. Multi-arm: control / variant_a /
    variant_b assigned at week 0. Outcome is conversion count per
    week (integer).
    """
    rng = np.random.default_rng(_SEED + 9)
    users = [f"U{i:05d}" for i in range(500)]
    weeks = pd.date_range("2024-01-07", periods=8, freq="W")
    arm_assignment = {u: ("control", "variant_a", "variant_b")[i % 3] for i, u in enumerate(users)}
    arm_lift = {"control": 0.0, "variant_a": 0.20, "variant_b": 0.45}
    enrolment_date = weeks[0].date()

    rows = []
    for u in users:
        propensity = float(rng.uniform(0.05, 0.20))
        arm = arm_assignment[u]
        for w in weeks:
            lifted_p = min(propensity * (1 + arm_lift[arm]), 0.95)
            conv = int(rng.binomial(1, lifted_p))
            rows.append({"unit_id": u, "period": w, "conversions": conv})
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    events = (
        TreatmentEvent(
            name="variant_a",
            treated_units=tuple(u for u, a in arm_assignment.items() if a == "variant_a"),
            treatment_date=enrolment_date,
            dimension="user_id",
            kind="categorical",
            arm="variant_a",
        ),
        TreatmentEvent(
            name="variant_b",
            treated_units=tuple(u for u, a in arm_assignment.items() if a == "variant_b"),
            treatment_date=enrolment_date,
            dimension="user_id",
            kind="categorical",
            arm="variant_b",
        ),
    )
    metadata = PanelMetadata(
        outcome_cols=("conversions",),
        period_kind="timestamp",
        freq="W",
        dimension="user_id",
        treatment_events=events,
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic A/B test",
            license="MIT",
            ethics_note="No PII; user IDs are synthetic.",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def macroeconomic_country_panel() -> Panel:
    """Country × year GDP-growth panel with a policy-shock event.

    Shape: 25 countries × 20 years. Subset of countries adopt a
    fiscal-tightening policy at year 10; outcome is real GDP growth.
    """
    rng = np.random.default_rng(_SEED + 10)
    countries = [f"C{i:02d}" for i in range(25)]
    years = pd.date_range("2005-12-31", periods=20, freq="YE")
    treated = tuple(countries[:10])
    policy_year = years[10].date()

    rows = []
    for c in countries:
        country_fe = float(rng.normal(2.0, 0.7))
        is_treated = c in treated
        for i, y in enumerate(years):
            shock = rng.normal(0, 1.5)
            growth = country_fe + 0.03 * i + shock
            if is_treated and y.date() >= policy_year:
                growth -= 0.8  # contractionary policy
            rows.append(
                {
                    "unit_id": c,
                    "period": y,
                    "gdp_growth": float(growth),
                    "population_mil": float(rng.uniform(5, 80)),
                }
            )
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    events = (
        TreatmentEvent(
            name="fiscal_tightening",
            treated_units=treated,
            treatment_date=policy_year,
            dimension="country",
        ),
    )
    metadata = PanelMetadata(
        outcome_cols=("gdp_growth",),
        period_kind="timestamp",
        freq="YE",
        dimension="country",
        treatment_events=events,
        weights_col="population_mil",
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def ecology_biodiversity_panel() -> Panel:
    """Site × year species-richness with conservation intervention.

    Shape: 30 sites × 12 years. Half the sites enter conservation
    management at year 5; outcome is species count.
    """
    rng = np.random.default_rng(_SEED + 11)
    sites = [f"SITE{i:03d}" for i in range(30)]
    years = pd.date_range("2013-12-31", periods=12, freq="YE")
    treated = tuple(sites[:15])
    intervention = years[5].date()

    rows = []
    for s in sites:
        baseline_richness = int(rng.uniform(20, 60))
        is_treated = s in treated
        for y in years:
            count = baseline_richness + int(rng.normal(0, 3))
            if is_treated and y.date() >= intervention:
                count += int(8 + rng.normal(0, 2))
            rows.append(
                {
                    "unit_id": s,
                    "period": y,
                    "species_richness": int(max(0, count)),
                    "site_area_ha": float(rng.uniform(50, 500)),
                }
            )
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    events = (
        TreatmentEvent(
            name="conservation_program",
            treated_units=treated,
            treatment_date=intervention,
            dimension="site",
        ),
    )
    metadata = PanelMetadata(
        outcome_cols=("species_richness",),
        period_kind="timestamp",
        freq="YE",
        dimension="site",
        treatment_events=events,
        weights_col="site_area_ha",
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def network_diffusion_panel() -> Panel:
    """User × week adoption of a feature spreading via social network.

    Shape: 200 users × 16 weeks. Influence cascade: 10 'seed' users
    adopt at week 0; rest adopt with probability proportional to
    their treated-neighbor count. Outcome is binary adopted flag.
    """
    rng = np.random.default_rng(_SEED + 12)
    n = 200
    users = [f"N{i:04d}" for i in range(n)]
    weeks = pd.date_range("2024-01-07", periods=16, freq="W")
    seeds = tuple(users[:10])
    seed_date = weeks[0].date()
    # Random sparse network: each user knows ~5 others
    neighbors: dict[str, list[str]] = {u: list(rng.choice(users, 5, replace=False)) for u in users}

    adoption_period: dict[str, pd.Timestamp | None] = {
        u: weeks[0] if u in seeds else None for u in users
    }

    rows: list[dict[str, Any]] = []
    for w in weeks:
        for u in users:
            adopted = adoption_period[u] is not None and adoption_period[u] <= w
            rows.append({"unit_id": u, "period": w, "adopted": int(adopted)})
        # Update adoptions for next week
        for u in users:
            if adoption_period[u] is None:
                n_adopted_neighbors = sum(
                    1
                    for n in neighbors[u]
                    if adoption_period[n] is not None and adoption_period[n] <= w
                )
                p = 0.05 * n_adopted_neighbors
                if rng.random() < p:
                    adoption_period[u] = w
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    events = (
        TreatmentEvent(
            name="seed_cohort",
            treated_units=seeds,
            treatment_date=seed_date,
            dimension="user_id",
        ),
    )
    metadata = PanelMetadata(
        outcome_cols=("adopted",),
        period_kind="timestamp",
        freq="W",
        dimension="user_id",
        treatment_events=events,
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic SI cascade",
            license="MIT",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def sdid_block_treatment_panel() -> Panel:
    """Single-block treatment panel for Synthetic DiD.

    Shape: 50 units × 30 years. Five treated units adopt a policy at
    year 20; remaining 45 are never-treated controls. True ATT = 4.0.
    Pre-treatment trends differ across units (heterogeneous fixed
    effects + linear trends) so vanilla DiD is biased; SDID's
    re-weighting recovers the true effect.
    """
    rng = np.random.default_rng(_SEED + 13)
    units = [f"S{i:02d}" for i in range(50)]
    years = pd.date_range("1995-12-31", periods=30, freq="YE")
    treated = tuple(units[:5])
    onset_year = years[20].date()
    true_att = 4.0

    rows = []
    for u in units:
        unit_fe = float(rng.normal(0.0, 2.0))
        unit_trend = float(rng.normal(0.05, 0.02))
        is_treated = u in treated
        for i, y in enumerate(years):
            outcome = 10.0 + unit_fe + unit_trend * i + rng.normal(0.0, 1.0)
            if is_treated and y.date() >= onset_year:
                outcome += true_att
            rows.append({"unit_id": u, "period": y, "outcome": float(outcome)})
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    events = (
        TreatmentEvent(
            name="block_policy",
            treated_units=treated,
            treatment_date=onset_year,
            dimension="state",
        ),
    )
    metadata = PanelMetadata(
        outcome_cols=("outcome",),
        period_kind="timestamp",
        freq="YE",
        dimension="state",
        treatment_events=events,
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            citation="factor-factory cross-domain fixture",
        ),
    )
    df = _attach_treatment_columns(df, events, period_kind="timestamp")
    return Panel(df.sort_index(), metadata)


def mediation_panel() -> Panel:
    """Cross-sectional mediation analysis: A → M → Y with known coefficients.

    Shape: 1000 subjects × 1 row each. Binary treatment ``A``,
    continuous mediator ``M``, continuous outcome ``Y`` plus one
    covariate. True parameters (so the four-way decomposition can be
    sanity-checked):

    Mediator:  M = 0.5 + 1.5 · A + 0.2 · C + ε  (β₁ = 1.5)
    Outcome:   Y = 1.0 + 2.0 · A + 1.0 · M + 0.3 · A·M + 0.1 · C + ε
               (θ₁ = 2.0, θ₂ = 1.0, θ₃ = 0.3)

    Closed-form true components (per VanderWeele 2014, linear-linear):

    - CDE(0)  = θ₁ = 2.0
    - PIE     = θ₂ · β₁ = 1.5
    - INTmed  = θ₃ · β₁ = 0.45
    - INTref  = θ₃ · E[M | A=0, C̄] ≈ 0.3 · (0.5 + 0.2 · 0) = 0.15
    - Total   = 2.0 + 0.15 + 0.45 + 1.5 = 4.10
    """
    rng = np.random.default_rng(_SEED + 14)
    n = 1000
    subjects = [f"SUBJ{i:05d}" for i in range(n)]
    A = rng.integers(0, 2, size=n).astype(float)
    C = rng.normal(0.0, 1.0, size=n)
    M = 0.5 + 1.5 * A + 0.2 * C + rng.normal(0.0, 0.5, size=n)
    Y = 1.0 + 2.0 * A + 1.0 * M + 0.3 * A * M + 0.1 * C + rng.normal(0.0, 0.5, size=n)
    enrol_date = pd.Timestamp("2024-01-31")

    rows = []
    for i, subj in enumerate(subjects):
        rows.append(
            {
                "unit_id": subj,
                "period": enrol_date,
                "treatment": int(A[i]),
                "mediator": float(M[i]),
                "outcome": float(Y[i]),
                "covariate": float(C[i]),
            }
        )
    df = pd.DataFrame(rows).set_index(["unit_id", "period"]).sort_index()

    metadata = PanelMetadata(
        outcome_cols=("outcome",),
        period_kind="timestamp",
        freq="ME",
        dimension="subject_id",
        treatment_events=(),
        record_count=len(df),
        provenance=Provenance(
            data_source="synthetic",
            license="MIT",
            ethics_note="Synthetic data; no human subjects.",
            citation=(
                "factor-factory cross-domain fixture; truth-tracking "
                "VanderWeele 2014 four-way decomposition."
            ),
        ),
    )
    return Panel(df.sort_index(), metadata)


__all__ = [
    "agronomic_dose_response_panel",
    "chem_assay_panel",
    "climate_anomaly_panel",
    "ecology_biodiversity_panel",
    "education_value_added_panel",
    "energy_consumption_panel",
    "finance_event_study_panel",
    "macroeconomic_country_panel",
    "marketing_uplift_panel",
    "mediation_panel",
    "network_diffusion_panel",
    "rct_longitudinal_panel",
    "sdid_block_treatment_panel",
    "staggered_did_panel",
    "survival_oncology_panel",
]
