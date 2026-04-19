"""Generic engine registry — runtime discovery + extension hook."""

from __future__ import annotations


class EngineRegistry[E]:
    """Lazy-loading engine registry.

    Engines that depend on missing optional packages should be skipped
    at registration time (the package's ``__init__.py`` does the
    try/except dance), so the registry only ever holds engines that are
    actually callable.

    Downstream packages can register their own engines at runtime via
    ``registry.register("name", MyEngine())``.
    """

    def __init__(self, engines: dict[str, E] | None = None) -> None:
        self._engines: dict[str, E] = dict(engines or {})

    def __getitem__(self, name: str) -> E:
        if name not in self._engines:
            raise KeyError(f"Unknown engine '{name}'. Available: {sorted(self._engines)}")
        return self._engines[name]

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._engines

    def register(self, name: str, engine: E) -> None:
        """Register a new engine at runtime (e.g., from a downstream package)."""
        self._engines[name] = engine

    def available(self) -> list[str]:
        return sorted(self._engines)

    def __repr__(self) -> str:
        return f"EngineRegistry(available={self.available()!r})"
