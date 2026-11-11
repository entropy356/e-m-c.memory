"""Rate-based recurrent network with long text attached to neuronal assemblies.

An external encoder supplies language semantics. This module studies recurrent
memory dynamics rather than replacing the LLM or its raw conversation context.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable, Mapping, Sequence
import numpy as np


@dataclass(frozen=True)
class MemoryConfig:
    neurons: int = 128
    assembly_size: int = 12
    embedding_dim: int = 16
    seed: int = 7
    beta: float = 7.0
    threshold: float = 0.55
    min_threshold: float = 0.15
    max_threshold: float = 0.95
    inhibition: float = 0.4
    learning_rate: float = 1.8
    synaptic_budget: float = 3.0
    threshold_adaptation: float = 0.015
    allocation_activity: float = 0.7
    allocation_noise: float = 0.02
    time_step: float = 0.4
    recall_threshold: float = 0.35

    def __post_init__(self) -> None:
        if not (2 <= self.assembly_size < self.neurons):
            raise ValueError("assembly_size must be in [2, neurons)")
        if self.embedding_dim < 1 or not 0 < self.time_step <= 1:
            raise ValueError("invalid embedding_dim or time_step")
        if not (0 <= self.min_threshold <= self.threshold <= self.max_threshold):
            raise ValueError("invalid threshold limits")
        for key in ("beta", "inhibition", "learning_rate", "synaptic_budget",
                    "threshold_adaptation", "allocation_activity", "allocation_noise"):
            x = getattr(self, key)
            if not np.isfinite(x) or x < 0:
                raise ValueError(f"{key} must be finite and nonnegative")
        if not -1 <= self.recall_threshold <= 1:
            raise ValueError("invalid recall threshold")


@dataclass(frozen=True)
class MemoryHit:
    memory_id: str
    text: str
    score: float


@dataclass
class _Record:
    memory_id: str
    text: str
    pattern: np.ndarray


class EngramMemory:
    """Overlapping neuronal assemblies, synaptic plasticity, and text recall."""

    def __init__(self, config: MemoryConfig,
                 encoder: Callable[[str], Sequence[float]]) -> None:
        self.config, self.encoder = config, encoder
        self.rng = np.random.default_rng(config.seed)
        n = config.neurons
        self.projection = self.rng.normal(0, 1, (n, config.embedding_dim))
        self.weights = np.zeros((n, n), dtype=float)
        self.activity = np.zeros(n, dtype=float)
        self.thresholds = np.full(n, config.threshold, dtype=float)
        self.records: list[_Record] = []

    def _stimulus(self, text: str) -> np.ndarray:
        z = np.asarray(self.encoder(text), dtype=float)
        if z.shape != (self.config.embedding_dim,) or not np.all(np.isfinite(z)):
            raise ValueError("invalid encoder output")
        norm = np.linalg.norm(z)
        if norm <= 0:
            raise ValueError("zero embedding")
        return self.projection @ (z / norm)

    def write(self, text: str) -> str:
        if not text.strip():
            raise ValueError("blank memory")
        c = self.config
        score = (self._stimulus(text) + c.allocation_activity * self.activity
                 - self.thresholds + self.rng.normal(0, c.allocation_noise, c.neurons))
        selected = np.argsort(score)[-c.assembly_size:]
        xi = np.zeros(c.neurons, dtype=float)
        xi[selected] = 1.0
        self.weights += (c.learning_rate / (c.assembly_size - 1)) * np.outer(xi, xi)
        np.fill_diagonal(self.weights, 0.0)
        sums = self.weights.sum(axis=1)
        r = np.minimum(1.0, c.synaptic_budget / np.maximum(sums, 1e-12))
        self.weights *= np.minimum(r[:, None], r[None, :])
        self.thresholds = np.clip(
            self.thresholds + c.threshold_adaptation * (xi - c.assembly_size / c.neurons),
            c.min_threshold, c.max_threshold,
        )
        self.activity = np.maximum(self.activity * 0.25, xi)
        memory_id = f"m{len(self.records)}"
        self.records.append(_Record(memory_id, text, xi))
        return memory_id

    def advance(self, steps: int = 1, stimulus: np.ndarray | None = None) -> None:
        if steps < 0:
            raise ValueError("negative steps")
        c = self.config
        current = np.zeros(c.neurons) if stimulus is None else np.asarray(stimulus, dtype=float)
        if current.shape != (c.neurons,) or not np.all(np.isfinite(current)):
            raise ValueError("invalid stimulus")
        for _ in range(steps):
            inhibition = c.inhibition * self.activity.sum() / c.assembly_size
            logits = c.beta * (self.weights @ self.activity + current - self.thresholds - inhibition)
            target = 1.0 / (1.0 + np.exp(-np.clip(logits, -60, 60)))
            self.activity += c.time_step * (target - self.activity)

    def clear_activity(self) -> None:
        self.activity.fill(0.0)

    def read(self, threshold: float | None = None) -> list[MemoryHit]:
        cutoff = self.config.recall_threshold if threshold is None else threshold
        if not np.isfinite(cutoff):
            raise ValueError("invalid threshold")
        n, k = self.config.neurons, self.config.assembly_size
        total = self.activity.sum()
        hits = []
        for record in self.records:
            inside = float(record.pattern @ self.activity)
            score = inside / k - (total - inside) / (n - k)
            if score >= cutoff:
                hits.append(MemoryHit(record.memory_id, record.text, score))
        return sorted(hits, key=lambda h: (-h.score, h.memory_id))

    def recall(self, cue: str, drive_steps: int = 8, settle_steps: int = 0,
               reset_activity: bool = False, threshold: float | None = None) -> list[MemoryHit]:
        # Read immediately after the driven phase by default. With current
        # weights, a stimulus-free settle phase decays toward a nearly silent
        # fixed point and erases cue-specific activity (Issue #10).
        # Explicit settle_steps > 0 remains available for dynamical experiments.
        if reset_activity:
            self.clear_activity()
        self.advance(drive_steps, self._stimulus(cue))
        self.advance(settle_steps)
        return self.read(threshold)

    def snapshot(self) -> dict:
        """JSON-compatible state; the caller must preserve the external encoder."""
        return {
            "version": 1, "config": asdict(self.config),
            "projection": self.projection.tolist(),
            "weights": self.weights.tolist(),
            "activity": self.activity.tolist(),
            "thresholds": self.thresholds.tolist(),
            "records": [{"id": r.memory_id, "text": r.text, "pattern": r.pattern.tolist()}
                        for r in self.records],
            "rng_state": self.rng.bit_generator.state,
        }

    @classmethod
    def restore(cls, state: Mapping,
                encoder: Callable[[str], Sequence[float]]) -> EngramMemory:
        """Restore trusted snapshots created by this version."""
        if state.get("version") != 1:
            raise ValueError("unknown snapshot version")
        model = cls(MemoryConfig(**state["config"]), encoder)
        n = model.config.neurons
        model.projection = np.asarray(state["projection"], dtype=float)
        model.weights = np.asarray(state["weights"], dtype=float)
        model.activity = np.asarray(state["activity"], dtype=float)
        model.thresholds = np.asarray(state["thresholds"], dtype=float)
        if (model.projection.shape != (n, model.config.embedding_dim)
                or model.weights.shape != (n, n)
                or model.activity.shape != (n,)
                or model.thresholds.shape != (n,)):
            raise ValueError("incompatible snapshot shape")
        if not all(np.all(np.isfinite(x)) for x in (
                model.projection, model.weights, model.activity, model.thresholds)):
            raise ValueError("nonfinite snapshot")
        model.records = []
        for item in state["records"]:
            xi = np.asarray(item["pattern"], dtype=float)
            if (xi.shape != (n,) or not np.all(np.isin(xi, [0.0, 1.0]))
                    or xi.sum() != model.config.assembly_size):
                raise ValueError("invalid assembly")
            model.records.append(_Record(item["id"], item["text"], xi))
        model.rng.bit_generator.state = state["rng_state"]
        return model
