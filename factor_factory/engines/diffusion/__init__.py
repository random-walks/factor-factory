"""Network-diffusion engines — SI, SIR, IC, threshold cascades via ndlib."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd

from ...tidy.panel import Panel
from .._registry import EngineRegistry


@dataclass(frozen=True)
class DiffusionResult:
    method: str  # "ndlib_sir" | "ndlib_ic" | ...
    model: str
    peak_infected_fraction: float
    peak_time: int
    final_recovered_fraction: float | None = None
    trajectory: pd.DataFrame | None = None  # per-step compartment counts
    n_nodes: int = 0
    n_edges: int = 0
    seed_nodes: list[int] | None = None
    diagnostics: dict[str, Any] | None = None
    meta: dict[str, Any] | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "model": self.model,
            "peak_infected_fraction": self.peak_infected_fraction,
            "peak_time": self.peak_time,
            "final_recovered_fraction": self.final_recovered_fraction,
            "n_nodes": self.n_nodes,
            "n_edges": self.n_edges,
            "seed_nodes": self.seed_nodes,
            "diagnostics": self.diagnostics,
        }

    def summary_table(self) -> pd.DataFrame:
        row = {
            "method": self.method,
            "model": self.model,
            "peak_infected": self.peak_infected_fraction,
            "peak_time": self.peak_time,
            "final_recovered": self.final_recovered_fraction,
            "n_nodes": self.n_nodes,
        }
        return pd.DataFrame([row]).set_index("method")


class DiffusionEngine(Protocol):
    name: str

    def simulate(
        self,
        panel: Panel,
        **engine_specific_kwargs: Any,
    ) -> DiffusionResult: ...


# Stub adapter: ndlib requires a graph object we don't have on the Panel by
# default, so this is a placeholder scaffold. Real usage needs a NetworkX
# graph passed through engine_specific_kwargs.
class NdlibEngine:
    """SI/SIR/IC/LT cascades via ndlib.

    Unlike other engines in factor-factory, diffusion simulations require
    an explicit graph object. Pass ``graph=<networkx.Graph>`` and optionally
    ``seed_nodes=<list[int]>`` through simulate().
    """

    name = "ndlib_sir"

    def simulate(
        self,
        panel: Panel,  # noqa: ARG002 — panel unused; diffusion is graph-based
        *,
        graph: Any = None,
        seed_nodes: list[int] | None = None,
        beta: float = 0.1,
        gamma: float = 0.05,
        n_iterations: int = 100,
        **_engine_specific_kwargs: Any,
    ) -> DiffusionResult:
        try:
            import ndlib.models.epidemics as ep
            import ndlib.models.ModelConfig as mc
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "NdlibEngine requires `ndlib`. Install via `pip install factor-factory[diffusion]`."
            ) from exc
        if graph is None:
            raise ValueError("NdlibEngine.simulate requires graph=<networkx.Graph>.")

        model = ep.SIRModel(graph)
        config = mc.Configuration()
        config.add_model_parameter("beta", beta)
        config.add_model_parameter("gamma", gamma)
        config.add_model_parameter("fraction_infected", 0.05)
        if seed_nodes:
            config.add_model_initial_configuration("Infected", seed_nodes)
        model.set_initial_status(config)

        iterations = model.iteration_bunch(n_iterations)
        trends = model.build_trends(iterations)

        n_nodes = graph.number_of_nodes()
        # SIR trends: list of dicts with 'trends' key.
        infected_frac = [it["node_count"][1] / n_nodes for it in iterations if "node_count" in it]
        peak_idx = int(max(range(len(infected_frac)), key=lambda i: infected_frac[i]))
        peak_frac = float(infected_frac[peak_idx]) if infected_frac else 0.0

        final_recovered_frac = (
            float(iterations[-1]["node_count"].get(2, 0)) / n_nodes
            if iterations and "node_count" in iterations[-1]
            else None
        )

        return DiffusionResult(
            method=self.name,
            model="SIR",
            peak_infected_fraction=peak_frac,
            peak_time=peak_idx,
            final_recovered_fraction=final_recovered_frac,
            n_nodes=n_nodes,
            n_edges=graph.number_of_edges(),
            seed_nodes=seed_nodes,
            diagnostics={
                "beta": beta,
                "gamma": gamma,
                "n_iterations": n_iterations,
                "trends_shape": len(trends),
            },
        )


_engines: dict[str, DiffusionEngine] = {"ndlib_sir": NdlibEngine()}
registry: EngineRegistry[DiffusionEngine] = EngineRegistry(_engines)


class DiffusionResults:
    def __init__(self, results: list[DiffusionResult]) -> None:
        self.results = results

    def __iter__(self) -> Iterable[DiffusionResult]:
        return iter(self.results)

    def __getitem__(self, key: int | str) -> DiffusionResult:
        if isinstance(key, int):
            return self.results[key]
        for r in self.results:
            if r.method == key:
                return r
        raise KeyError(key)


def estimate(
    panel: Panel,
    *,
    methods: tuple[str, ...] = ("ndlib_sir",),
    **engine_specific_kwargs: Any,
) -> DiffusionResults:
    if not methods:
        raise ValueError("methods must be non-empty.")
    return DiffusionResults(
        [registry[m].simulate(panel, **engine_specific_kwargs) for m in methods]
    )


__all__ = [
    "DiffusionEngine",
    "DiffusionResult",
    "DiffusionResults",
    "NdlibEngine",
    "estimate",
    "registry",
]
