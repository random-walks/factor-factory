# Piggyback map

Factor-factory is **adapter-first**. Before writing engine math from scratch, consult this table. We wrap mature Python (or, failing that, R) packages; we only port from scratch when no maintained equivalent exists.

## Active wrappers

| Method / family | Piggyback package | Adapter location | Canonical paper |
|---|---|---|---|
| TWFE DiD | `linearmodels` | `engines.did.twfe` | — |
| Callaway-Sant'Anna DiD | `differences` | `engines.did.callaway_santanna` | Callaway & Sant'Anna 2021 (JoE) |
| Sun-Abraham DiD | `differences` (fallback: port) | `engines.did.sun_abraham` *(Batch 6)* | Sun & Abraham 2021 (JoE) |
| Borusyak-Jaravel-Spiess DiD | `differences` (fallback: port) | `engines.did.borusyak_jaravel_spiess` *(Batch 6)* | Borusyak, Jaravel & Spiess 2024 |
| Kaplan-Meier survival | `lifelines` | `engines.survival.kaplan_meier` | — |
| Cox PH | `lifelines` | `engines.survival.cox_ph` | — |
| Stratified Cox PH | `lifelines` (`strata=`) | `engines.survival.cox_ph` *(Batch 6)* | — |
| Market-adjusted event study | — (homegrown, dep-free) | `engines.event_study.market_adjusted` | MacKinlay 1997 |
| Fama-French event study | `pandas-datareader` + `statsmodels` | `engines.event_study.fama_french` *(Batch 6)* | Fama-French 1993/2015; Patell 1976; BMP 1991 |
| RDD | `rdrobust` | `engines.rdd.rd_robust` *(Batch 7)* | Calonico, Cattaneo, Titiunik 2014 |
| Synthetic Control | `pysyncon` | `engines.scm.pysyncon` *(Batch 8)* | Abadie, Diamond, Hainmueller 2010 |
| Augmented SCM | `pysyncon` (fallback: port) | `engines.scm.augmented` *(Batch 8)* | Ben-Michael, Feller, Rothstein 2021 |
| Matrix-completion SCM | `pysyncon` (fallback: port) | `engines.scm.matrix_completion` *(Batch 15)* | Athey et al. 2021 |
| Causal Forest | `econml` | `engines.het_te.causal_forest` *(Batch 9)* | Wager & Athey 2018; Athey et al. 2019 |
| X/R-learner | `econml` | `engines.het_te.x_learner`, `r_learner` *(Batch 9)* | Künzel et al. 2019; Nie & Wager 2021 |
| DoubleML (PLR + IRM) | `DoubleML` | `engines.dml.plr`, `engines.dml.irm` *(Batch 9)* | Chernozhukov et al. 2018 |
| BCF | `bcf` (R — port) | `engines.het_te.bcf` *(Batch 15)* | Hahn, Murray & Carvalho 2020 |
| Offline changepoint | `ruptures` | `engines.changepoint.ruptures_adapter` *(Batch 10)* | Truong, Oudre & Vayatis 2020 |
| Online Bayesian changepoint | `bayesloop` | `engines.changepoint.bayesloop_adapter` *(Batch 10)* | Adams & MacKay 2007 |
| STL decomposition + forecast | `sktime` | `engines.stl.sktime_stl` *(Batch 10)* | Cleveland et al. 1990 |
| Prophet forecasting | `prophet` | `engines.stl.prophet_adapter` *(Batch 10)* | Taylor & Letham 2018 |
| Panel FE regression (HDFE) | `pyfixest` | `engines.panel_reg.pyfixest_adapter` *(Batch 10)* | Correia 2016 (reghdfe) |
| Inequality decomposition | `inequality` | `engines.inequality.theil` *(Batch 11)* | Theil 1967; Atkinson 1970 |
| Spatial autocorrelation | `esda` | `engines.spatial.morans_i` *(Batch 11)* | Moran 1950; Anselin 1995 |
| Spatial regression | `spreg` | `engines.spatial.spreg_ols` *(Batch 11)* | Anselin 1988 |
| Spatial weights | `libpysal` | `engines.spatial.weights` *(Batch 11)* | — |
| Hawkes processes | `tick` | `engines.hawkes.tick_adapter` *(Batch 12)* | Hawkes 1971; Bacry et al. 2015 |
| Climate indices | `xclim` | `engines.climate.xclim_adapter` *(Batch 12)* | — |
| Mann-Kendall trend | `pymannkendall` | `engines.climate.mann_kendall` *(Batch 12)* | Mann 1945; Kendall 1948; Hamed-Rao 1998 |
| Network diffusion | `ndlib` | `engines.diffusion.ndlib_adapter` *(Batch 12)* | — |

## Anti-piggybacks (homegrown ports)

When no maintained Python equivalent exists, we port the method inline. Each anti-piggyback carries: (a) the reason the piggyback fails, (b) the canonical paper, (c) the reference R implementation URL.

| Method | Adapter | Why we port | Canonical paper |
|---|---|---|---|
| Synthetic DiD | `engines.sdid.synthetic_did` | No maintained Python equivalent. R [`synthdid`](https://synth-inference.github.io/synthdid/) is canonical; PyPI `pysdid` was lightly maintained. | Arkhangelsky et al. 2021 (AER, https://doi.org/10.1257/aer.20190159) |
| Four-way mediation decomposition | `engines.mediation.four_way` | No maintained Python equivalent. R [`CMAverse`](https://bs1125.github.io/CMAverse/) is canonical; PyPI `mediation` is stale; `statsmodels.stats.mediation` only does 2-component (NDE/NIE). | VanderWeele 2014 (Epidemiology, https://doi.org/10.1097/EDE.0000000000000121) |
| Market-adjusted event study | `engines.event_study.market_adjusted` | Trivial math (cross-sectional control mean as benchmark). No dep is justified; keeping the family dep-free for the default install. | MacKinlay 1997 |
| Latent-EM reporting-bias | `engines.reporting_bias.latent_em` *(Batch 11)* | Two-class EM for under-reporting rates is a civic-data staple with no off-the-shelf Python implementation. ~150 LOC. | — |
| SDID placebo inference | `engines.sdid.synthetic_did` *(Batch 5)* | Single-treated-unit placebo-style inference not cleanly exposed by upstream; jackknife fallback is our own. | Arkhangelsky et al. 2021 §3.4 |

## Non-piggybacks (deliberate exclusions)

| Domain | Why excluded | Where to go instead |
|---|---|---|
| GWAS / biobank-scale genetics | Scale (100M+ variants), file formats (VCF, PLINK, BGEN), ops patterns (mixed-model LMMs, reml variance components) all mismatch the Panel shape. | [hail](https://hail.is/), [pysnptools](https://fastlmm.github.io/PySnpTools/), [scikit-allel](https://scikit-allel.readthedocs.io/), [PLINK 2.0](https://www.cog-genomics.org/plink/2.0/), [BOLT-LMM](https://alkesgroup.broadinstitute.org/BOLT-LMM/). |
| Deep-learning causal estimators | Research frontier, stability insufficient for production wrapping. Revisit post-v2.0. | [causalML](https://causalml.readthedocs.io/) for heads-up on what's mature. |
| Streaming engine fits (online learning) | All our estimators assume the Panel fits in memory. Out of scope until someone needs it. | [river](https://riverml.xyz/) for online learning primitives. |

## Updating this map

Any new adapter PR must add a row. The `engine-reviewer` agent checks this. If you think a row is wrong (upstream package has been unmaintained for ≥1 year, license changed, API broke), file an issue — don't silently swap to a different package without discussion.
