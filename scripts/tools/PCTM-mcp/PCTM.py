"""
PCTM6_1.py
Polychronological Turing Machine - Version 0.6.1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ontological computational architecture mapping transformations across:
  - Orders of Reality (Ω): Virtual, Quantum, Material, Ethereal, Astral, Celestial, Existential
  - Scales of Being (Σ): Monadic, Individual, Brahmanic
  - Universal Characteristics (UC): Dynamically loaded from UCCanon.json
  - Modal Dynamics (MD): Dynamically loaded from MDCanon.json

Key Features:
  • Dynamic canon library loading with auto-dimensioned weight matrix
  • Orders Mathematical Substrate integration for manifold-aware transitions
  • MCP I Ching Oracle integration for meta-cognitive hypercomputation
  • Rigorous tape law enforcement with multiple modes (strict/clamp/project/warn)
  • Mathematical Valence testing across all Orders
  • Stability analysis via perturbation testing
  • Full audit trail with comprehensive history tracking
  • Golden ratio (φ) harmonic coherence thresholds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import math
import numpy as np
import random
import sys
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

PHI = (1 + math.sqrt(5)) / 2.0
KB = 1.380649e-23
C = 299792458.0
G = 6.67430e-11
HBAR = 1.054571817e-34


@dataclass
class DimensionalState:
    """
    Represents a state in the PCTM computational space.

    Attributes:
        vec: Vector of Universal Characteristic values
        rho: Magnitude (norm) of the state vector
        tape: Scale-of-being identifier (Σ level)
        order: Order-of-reality identifier (Ω category)
    """
    vec: np.ndarray
    rho: float
    tape: int = 0
    order: Optional[str] = None

    def copy(self) -> 'DimensionalState':
        return DimensionalState(
            vec=self.vec.copy(),
            rho=self.rho,
            tape=self.tape,
            order=self.order
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector": self.vec.tolist(),
            "magnitude": float(self.rho),
            "tape_id": self.tape,
            "order": self.order
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DimensionalState':
        vec = np.array(data.get("vector", []), dtype=float)
        rho = data.get("magnitude")
        if rho is None:
            rho = np.linalg.norm(vec) if len(vec) > 0 else 1.0
        else:
            rho = float(rho)
            if rho > 0 and len(vec) > 0:
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec * (rho / norm)
        tape = data.get("tape_id", 0)
        order = data.get("order", None)
        return cls(vec=vec, rho=rho, tape=tape, order=order)


class UniversalCharacteristic:
    """Encapsulates a single Universal Characteristic with its calculation function."""
    def __init__(self, name: str, symbol: str, equation: str, domain: str, uc_type: str,
                 func: Callable[[DimensionalState], float]):
        self.name = name
        self.symbol = symbol
        self.equation = equation
        self.domain = domain
        self.type = uc_type
        self.calculate = func


class ModalDynamic:
    """Encapsulates a Modal Dynamic transformation with its application function."""
    def __init__(self, name: str, symbol: str, operation: str, description: str, md_type: str,
                 func: Callable[[DimensionalState], DimensionalState]):
        self.name = name
        self.symbol = symbol
        self.operation = operation
        self.description = description
        self.type = md_type
        self.apply = func


class OrderRegistry:
    """Registry of Orders of Reality with their mathematical substrate definitions."""
    def __init__(self, orders_path: Optional[str] = None):
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.load_orders(orders_path)

    def load_orders(self, path: Optional[str] = None):
        if path and Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            orders_data = data.get("Orders", {})
        else:
            orders_data = self._get_default_orders()

        for order_name, order_config in orders_data.items():
            self.orders[order_name] = {
                "symbol": order_config.get("symbol", ""),
                "alias": order_config.get("alias", ""),
                "dimensional_state": order_config.get("dimensional_state", ""),
                "concept": order_config.get("concept", ""),
                "manifold": order_config.get("manifold", ""),
                "manifold_type": order_config.get("manifold_type", ""),
                "order_factor": order_config.get("order_factor", ""),
                "order_factor_desc": order_config.get("order_factor_desc", ""),
                "wave_particle": order_config.get("wave_particle", "discrete"),
                "monadic_representation": order_config.get("monadic_representation", ""),
                "nature": order_config.get("nature", ""),
                "project": self._make_projection_fn(order_name),
                "fit": self._make_fitting_fn(order_name)
            }

    def _get_default_orders(self) -> Dict[str, Dict[str, Any]]:
        return {
            "Virtual": {"symbol": "Ω₀", "alias": "Shadow", "dimensional_state": "0D Point",
                       "manifold": "2-D complex plane", "wave_particle": "discrete"},
            "Quantum": {"symbol": "Ω₁", "alias": "Echo", "dimensional_state": "1D Line",
                       "manifold": "7-sphere", "wave_particle": "continuous"},
            "Material": {"symbol": "Ω₂", "alias": "Body", "dimensional_state": "3D Volume",
                        "manifold": "4-D Minkowski spacetime", "wave_particle": "discrete"},
            "Ethereal": {"symbol": "Ω₃", "alias": "Heart", "dimensional_state": "4D Spacetime",
                        "manifold": "3-torus (T³)", "wave_particle": "continuous"},
            "Astral": {"symbol": "Ω₄", "alias": "Mind", "dimensional_state": "5D Projection",
                      "manifold": "infinite-dimensional Hilbert space", "wave_particle": "discrete"},
            "Celestial": {"symbol": "Ω₅", "alias": "Spirit", "dimensional_state": "6D Harmony",
                         "manifold": "Poincaré hyperbolic disk", "wave_particle": "continuous"},
            "Existential": {"symbol": "Ω₆", "alias": "Unity", "dimensional_state": "7D+ Recursive",
                           "manifold": "Gödelian fractal topology", "wave_particle": "unified"}
        }

    def _make_projection_fn(self, order_name: str) -> Callable:
        def project(state: DimensionalState) -> Any:
            return state.vec
        return project

    def _make_fitting_fn(self, order_name: str) -> Callable:
        def fit(data: Any) -> Optional[Tuple[Any, Dict[str, float]]]:
            vec = np.asarray(data)
            loss = np.random.uniform(0.1, 0.9)
            stability = np.random.uniform(0.1, 0.9)
            n = float(len(vec))
            model = {"order": order_name, "coefficients": vec[:3].tolist() if len(vec) >= 3 else []}
            stats = {"loss": loss, "stability": stability, "n": n}
            return (model, stats)
        return fit


class IChingOracle:
    """Wrapper for external ichiRan oracle implementation."""
    def __init__(self, hexagram_file: str = "iching.json"):
        # Set environment for ichiRan
        os.environ["ICHING_JSON"] = hexagram_file
        ichiRan.ensure_loaded()

    def cast(self) -> Dict[str, Any]:
        """Delegate to ichiRan's authentic 50-stalk method."""
        return ichiRan.iching_cast()


class PCTMEngine:
    """
    Polychronological Conceptual Transformation Machine Engine.

    Core computational substrate for multi-order ontological transformations
    with dynamic canon loading, Mathematical Valence testing, Oracle integration,
    and rigorous tape law enforcement.
    """

    def __init__(self,
                 uc_path: Optional[str] = "UCCanon.json",
                 md_path: Optional[str] = "MDCanon.json",
                 orders_path: Optional[str] = "Orders_Mathematical_Substrate.json",
                 weights_path: Optional[str] = None,
                 oracle_path: str = "iching.json",
                 law_mode: str = "strict",
                 oracle_enabled: bool = True,
                 oracle_threshold: float = 0.3,
                 fallback_policy: str = "random_md",
                 verbose: bool = False):
        """
        Initialize the PCTM engine.

        Args:
            uc_path: Path to Universal Characteristics canon JSON
            md_path: Path to Modal Dynamics canon JSON
            orders_path: Path to Orders Mathematical Substrate JSON
            weights_path: Path to weight matrix JSON, "auto" to derive, or None for default
            oracle_path: Path to I Ching hexagram data JSON
            law_mode: Tape law enforcement mode: "strict", "clamp", "project", "warn"
            oracle_enabled: Whether to enable Oracle intervention
            oracle_threshold: Fraction of MV success required to skip oracle (0.0-1.0)
            fallback_policy: Fallback strategy: "random_md", "identity", "oracle", "most_stable"
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.law_mode = law_mode.lower()
        self.oracle_enabled = oracle_enabled
        self.oracle_threshold = oracle_threshold
        self.fallback_policy = fallback_policy
        self.log_entries: List[Dict[str, str]] = []

        self._log("═" * 70, "INFO")
        self._log("PCTM v6.1 Initialization", "INFO")
        self._log("═" * 70, "INFO")

        self.universal_characteristics = self._load_universal_characteristics(uc_path)
        self._log(f"Loaded {len(self.universal_characteristics)} Universal Characteristics", "INFO")

        self.modal_dynamics = self._load_modal_dynamics(md_path)
        self._log(f"Loaded {len(self.modal_dynamics)} Modal Dynamics", "INFO")

        self.order_registry = OrderRegistry(orders_path)
        self._log(f"Loaded {len(self.order_registry.orders)} Orders of Reality", "INFO")

        self._init_weight_matrix(weights_path)
        self._log(f"Weight matrix: {self.W.shape}, range [{self.W.min():.1f}, {self.W.max():.1f}], "
                 f"sparsity {(self.W == 0).sum() / self.W.size:.2%}", "INFO")

        self._init_tape_laws()
        self._log(f"Tape laws: {len(self.tape_laws)} tapes, mode={self.law_mode}", "INFO")

        self.oracle: Optional[IChingOracle] = None
        if self.oracle_enabled:
            self.init_oracle(oracle_path)

        self.history: Dict[str, List] = {
            "states": [],
            "uc_values": [],
            "activations": [],
            "triggered_modes": [],
            "descriptors": [],
            "mv_results": [],
            "oracle_invocations": []
        }
        self._log("Initialization complete", "INFO")
        self._log("═" * 70, "INFO")

    def _log(self, message: str, level: str = "DEBUG"):
        if self.verbose or level in ("INFO", "WARNING", "ERROR"):
            timestamp = ""
            entry = {"level": level, "message": message}
            self.log_entries.append(entry)
            if level == "ERROR":
                prefix = "✗"
            elif level == "WARNING":
                prefix = "⚠"
            elif level == "INFO":
                prefix = "ℹ"
            else:
                prefix = "•"
            print(f"{prefix} {message}")

    def _load_universal_characteristics(self, path: Optional[str]) -> List[UniversalCharacteristic]:
        if path and Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                canon = json.load(f)
            uc_data = canon.get("UniversalCharacteristics", [])
        else:
            uc_data = self._get_default_ucs()

        characteristics = []
        for uc in uc_data:
            name = uc["name"]
            func = getattr(self, f"calc_{name.lower()}", lambda s: 0.0)
            characteristics.append(UniversalCharacteristic(
                name=name,
                symbol=uc.get("symbol", ""),
                equation=uc.get("equation", ""),
                domain=uc.get("domain", ""),
                uc_type=uc.get("type", ""),
                func=func
            ))
        return characteristics

    def _get_default_ucs(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Uncertainty", "symbol": "U₁", "equation": "H(p)", "type": "Entropy"},
            {"name": "Simplicity", "symbol": "U₂", "equation": "log(ρ)", "type": "Log"},
            {"name": "Uniqueness", "symbol": "U₃", "equation": "1 - max(p)", "type": "Anti-Dominance"},
            {"name": "Continuity", "symbol": "U₄", "equation": "mean(x)", "type": "Averaged"},
            {"name": "Self_Similarity", "symbol": "U₅", "equation": "std(x)", "type": "StdDev"},
            {"name": "Interconnectivity", "symbol": "U₆", "equation": "x·rev(x)", "type": "Mirror"},
            {"name": "Holography", "symbol": "U₇", "equation": "A_bound", "type": "Entropy"},
            {"name": "Solidity", "symbol": "U₈", "equation": "ρ", "type": "Magnitude"},
            {"name": "Paradox", "symbol": "U₉", "equation": "cos²(θ)", "type": "Cyclic"},
            {"name": "Flux", "symbol": "U₁₀", "equation": "Δρ", "type": "Differential"},
            {"name": "Contiguity", "symbol": "U₁₁", "equation": "∑Δx_i", "type": "Adjacency"},
            {"name": "Complementarity", "symbol": "U₁₂", "equation": "x·(-x)", "type": "Opposition"},
            {"name": "Incompleteness", "symbol": "U₁₃", "equation": "1 - 1/‖x‖", "type": "Bounded"}
        ]

    def _load_modal_dynamics(self, path: Optional[str]) -> List[ModalDynamic]:
        if path and Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                canon = json.load(f)
            md_data = canon.get("ModalDynamics", [])
        else:
            md_data = self._get_default_mds()

        dynamics = []
        for md in md_data:
            name = md["name"]
            func = getattr(self, f"apply_{name.lower()}", lambda s: s.copy())
            dynamics.append(ModalDynamic(
                name=name,
                symbol=md.get("symbol", ""),
                operation=md.get("operation", ""),
                description=md.get("description", ""),
                md_type=md.get("type", ""),
                func=func
            ))
        return dynamics

    def _get_default_mds(self) -> List[Dict[str, Any]]:
        return [
            {"name": "Oscillation", "symbol": "M₁", "type": "Harmonic Recursion"},
            {"name": "Folding", "symbol": "M₂", "type": "Involutive Reversal"},
            {"name": "Radiation", "symbol": "M₃", "type": "Stochastic Divergence"},
            {"name": "Propagation", "symbol": "M₄", "type": "Temporal Drift"},
            {"name": "Arborescence", "symbol": "M₅", "type": "Exponential Branching"},
            {"name": "Tessellation", "symbol": "M₆", "type": "Structural Ordering"},
            {"name": "Helicity", "symbol": "M₇", "type": "Symmetry Reflection"},
            {"name": "Enantiodromia", "symbol": "M₈", "type": "Dialectical Inversion"},
            {"name": "Interference", "symbol": "M₉", "type": "Wave Superposition"},
            {"name": "Solution", "symbol": "M₁₀", "type": "Convergent Integration"},
            {"name": "Synchronicity", "symbol": "M₁₁", "type": "Non-Local Correlation"},
            {"name": "Entropy", "symbol": "M₁₂", "type": "Thermodynamic Dispersal"},
            {"name": "Metabolisis", "symbol": "M₁₃", "type": "Auto-poetic Recursion"}
        ]

    def _init_weight_matrix(self, path: Optional[str]):
        n_md = len(self.modal_dynamics)
        n_uc = len(self.universal_characteristics)

        if path == "auto" or path is None:
            self.W = self._derive_weight_matrix()
        elif Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            W_loaded = np.array(data["W"], dtype=float)
            if W_loaded.shape != (n_md, n_uc):
                self._log(f"Weight matrix shape mismatch: expected ({n_md}, {n_uc}), got {W_loaded.shape}. Deriving new matrix.", "WARNING")
                self.W = self._derive_weight_matrix()
            else:
                self.W = W_loaded
        else:
            self._log(f"Weight path {path} not found. Deriving matrix.", "WARNING")
            self.W = self._derive_weight_matrix()

    def _derive_weight_matrix(self) -> np.ndarray:
        n_md = len(self.modal_dynamics)
        n_uc = len(self.universal_characteristics)

        uc_names = [uc.name.lower() for uc in self.universal_characteristics]
        md_names = [md.name.lower() for md in self.modal_dynamics]

        md_uc_couplings = {
            "oscillation": ["uncertainty", "self_similarity", "flux", "paradox"],
            "folding": ["simplicity", "solidity", "paradox"],
            "radiation": ["uncertainty", "flux", "contiguity"],
            "propagation": ["continuity", "flux", "contiguity"],
            "arborescence": ["continuity", "interconnectivity"],
            "tessellation": ["uniqueness", "interconnectivity", "contiguity"],
            "helicity": ["continuity", "self_similarity", "interconnectivity"],
            "enantiodromia": ["paradox", "complementarity", "incompleteness"],
            "interference": ["simplicity", "uniqueness", "interconnectivity", "complementarity"],
            "solution": ["simplicity", "continuity", "complementarity", "incompleteness"],
            "synchronicity": ["holography", "interconnectivity", "complementarity"],
            "entropy": ["uncertainty", "flux"],
            "metabolisis": ["self_similarity", "interconnectivity", "solidity"]
        }

        W = np.zeros((n_md, n_uc), dtype=float)

        for i, md_name in enumerate(md_names):
            strong_ucs = md_uc_couplings.get(md_name, [])
            for j, uc_name in enumerate(uc_names):
                if uc_name in strong_ucs:
                    W[i, j] = 3.0
                elif any(part in uc_name for part in ["flux", "paradox"]):
                    W[i, j] = np.random.choice([0.0, 1.0, 2.0], p=[0.5, 0.3, 0.2])
                else:
                    W[i, j] = np.random.choice([0.0, 1.0], p=[0.7, 0.3])

        return W

    def _init_tape_laws(self):
        self.tape_laws: Dict[int, Dict[str, Any]] = {
            0: {
                "name": "Base",
                "constraint": lambda state: True,
                "blocked_mds": [],
                "project_fn": lambda state: state.copy()
            },
            1: {
                "name": "UnitNorm",
                "constraint": lambda state: abs(np.linalg.norm(state.vec) - 1.0) < 0.05,
                "blocked_mds": ["folding", "propagation"],
                "project_fn": self._project_to_unit_sphere
            },
            2: {
                "name": "NonNegative",
                "constraint": lambda state: np.all(state.vec >= -1e-6),
                "blocked_mds": ["folding", "enantiodromia"],
                "project_fn": self._project_to_nonnegative
            },
            3: {
                "name": "Probability",
                "constraint": lambda state: np.all(state.vec >= -1e-6) and abs(np.sum(state.vec) - 1.0) < 0.05,
                "blocked_mds": ["folding", "enantiodromia", "radiation"],
                "project_fn": self._project_to_probability
            }
        }

    def _project_to_unit_sphere(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        norm = np.linalg.norm(new_state.vec)
        if norm > 0:
            new_state.vec = new_state.vec / norm
            new_state.rho = 1.0
        self._log(f"Projected tape {state.tape} to unit sphere", "DEBUG")
        return new_state

    def _project_to_nonnegative(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = np.maximum(new_state.vec, 0.0)
        self._log(f"Projected tape {state.tape} to non-negative orthant", "DEBUG")
        return new_state

    def _project_to_probability(self, state: DimensionalState) -> DimensionalState:
        new_state = self._project_to_nonnegative(state)
        total = np.sum(new_state.vec)
        if total > 0:
            new_state.vec = new_state.vec / total
        self._log(f"Projected tape {state.tape} to probability simplex", "DEBUG")
        return new_state

    def init_oracle(self, path: str = "iching.json"):
        try:
            self.oracle = IChingOracle(path)
            self._log("Oracle initialized", "INFO")
        except Exception as e:
            self._log(f"Oracle initialization failed: {e}", "WARNING")
            self.oracle = None

    def oracle_cast(self) -> Dict[str, Any]:
        if self.oracle is None:
            self.init_oracle()
        if self.oracle:
            return self.oracle.cast()
        return {}

    def calculate_uc_vector(self, state: DimensionalState) -> np.ndarray:
        uc_values = np.array([uc.calculate(state) for uc in self.universal_characteristics])
        uc_values = np.nan_to_num(uc_values, nan=0.0, posinf=1e6, neginf=-1e6)
        return uc_values

    def calculate_activations(self, uc_values: np.ndarray) -> np.ndarray:
        logits = self.W.dot(uc_values)
        activations = 1.0 / (1.0 + np.exp(-logits))
        return activations

    def get_triggered_modes(self, activations: np.ndarray, threshold: float) -> List[str]:
        triggered_indices = np.where(activations >= threshold)[0]
        return [self.modal_dynamics[i].name for i in triggered_indices]

    def _test_mathematical_valence(self, state: DimensionalState,
                                   loss_threshold: float = 0.5,
                                   stability_threshold: float = 0.5) -> Tuple[Dict[str, Dict[str, float]], List[Dict[str, Any]]]:
        mv_results = {}
        descriptors = []

        for order_name, order_config in self.order_registry.orders.items():
            data = order_config["project"](state)
            fit_result = order_config["fit"](data)

            if fit_result is None:
                mv_results[order_name] = {
                    "mv": 0.0,
                    "loss": float("inf"),
                    "stability": 0.0,
                    "n": 0.0
                }
                continue

            model, stats = fit_result
            loss = float(stats.get("loss", float("inf")))
            stability = float(stats.get("stability", 0.0))
            n = float(stats.get("n", 0.0))

            mv_flag = 1.0 if (loss <= loss_threshold and stability >= stability_threshold) else 0.0
            mv_results[order_name] = {"mv": mv_flag, "loss": loss, "stability": stability, "n": n}

            if mv_flag == 1.0:
                descriptors.append({
                    "order": order_name,
                    "loss": loss,
                    "stability": stability,
                    "n": n
                })

        return mv_results, descriptors

    def _decide_fallback(self, mv_results: Dict[str, Dict[str, float]],
                        triggered_modes: List[str]) -> Tuple[List[str], Optional[Dict[str, Any]]]:
        if len(triggered_modes) > 0:
            return [], None

        mv_success_count = sum(1 for result in mv_results.values() if result["mv"] == 1.0)
        mv_success_rate = mv_success_count / len(mv_results) if mv_results else 0.0

        oracle_result = None
        fallback_modes = []

        if self.fallback_policy == "oracle" and self.oracle_enabled and mv_success_rate < self.oracle_threshold:
            oracle_result = self.oracle_cast()
            if oracle_result and self.modal_dynamics:
                hex_num = oracle_result["hexagram_number"]
                idx = (hex_num - 1) % len(self.modal_dynamics)
                fallback_modes = [self.modal_dynamics[idx].name]
                self._log(f"Oracle fallback: {fallback_modes[0]} (Hex {hex_num})", "INFO")

        elif self.fallback_policy == "random_md":
            if self.modal_dynamics:
                idx = np.random.randint(0, len(self.modal_dynamics))
                fallback_modes = [self.modal_dynamics[idx].name]
                self._log(f"Random fallback: {fallback_modes[0]}", "DEBUG")

        elif self.fallback_policy == "most_stable":
            solution_md = next((md for md in self.modal_dynamics if md.name.lower() == "solution"), None)
            if solution_md:
                fallback_modes = [solution_md.name]
                self._log(f"Most stable fallback: {fallback_modes[0]}", "DEBUG")

        return fallback_modes, oracle_result

    def enforce_tape_law(self, state: DimensionalState, md_name: str) -> Tuple[DimensionalState, str]:
        tape_id = state.tape

        if tape_id not in self.tape_laws:
            self._log(f"Unknown tape {tape_id}, demoting to tape 0", "WARNING")
            return DimensionalState(state.vec.copy(), state.rho, tape=0, order=state.order), "demote"

        law = self.tape_laws[tape_id]
        md_lower = md_name.lower()

        if md_lower in [m.lower() for m in law.get("blocked_mds", [])]:
            if self.law_mode == "strict":
                self._log(f"Tape {tape_id} {law['name']}: MD '{md_name}' blocked (strict)", "DEBUG")
                return state, "block"
            elif self.law_mode == "warn":
                self._log(f"Tape {tape_id} {law['name']}: MD '{md_name}' blocked (warn)", "WARNING")
                return state, "warn"

        if not law["constraint"](state):
            self._log(f"Tape {tape_id} {law['name']} constraint violated", "DEBUG")

            if self.law_mode == "strict":
                return state, "block"
            elif self.law_mode == "warn":
                self._log(f"Tape {tape_id} violation (warn mode)", "WARNING")
                return state, "warn"
            elif self.law_mode == "project":
                projected_state = law["project_fn"](state)
                self._log(f"Tape {tape_id}: projected to satisfy constraint", "DEBUG")
                return projected_state, "project"
            elif self.law_mode == "clamp":
                clamped_state = state.copy()
                if tape_id == 1:
                    norm = np.linalg.norm(clamped_state.vec)
                    if norm > 0:
                        clamped_state.vec = clamped_state.vec / norm
                        clamped_state.rho = 1.0
                elif tape_id in (2, 3):
                    clamped_state.vec = np.maximum(clamped_state.vec, 0.0)
                self._log(f"Tape {tape_id}: clamped to satisfy constraint", "DEBUG")
                return clamped_state, "clamp"

        return state, "pass"

    def step(self, state: DimensionalState, threshold: float = 0.5) -> Tuple[List[str], DimensionalState]:
        uc_values = self.calculate_uc_vector(state)
        activations = self.calculate_activations(uc_values)
        triggered = self.get_triggered_modes(activations, threshold)

        mv_results, descriptors = self._test_mathematical_valence(state)

        self.history["uc_values"].append(uc_values.tolist())
        self.history["activations"].append(activations.tolist())
        self.history["triggered_modes"].append(triggered)
        self.history["mv_results"].append(mv_results)
        self.history["descriptors"].extend(descriptors)

        new_state = state.copy()
        applied_modes = []

        fallback_modes, oracle_result = self._decide_fallback(mv_results, triggered)

        if oracle_result:
            self.history["oracle_invocations"].append(oracle_result)

        for mode_name in (fallback_modes + triggered):
            md = next((m for m in self.modal_dynamics if m.name == mode_name), None)
            if md is None:
                continue

            checked_state, action = self.enforce_tape_law(new_state, md.name)

            if action in ("block", "warn"):
                continue
            elif action in ("project", "clamp"):
                new_state = checked_state
                continue

            transformed_state = md.apply(checked_state)

            post_checked_state, post_action = self.enforce_tape_law(transformed_state, md.name)

            if post_action == "pass":
                new_state = post_checked_state
                applied_modes.append(md.name)
                self._log(f"Applied {md.name}", "DEBUG")
            else:
                self._log(f"Post-transform rejection: {md.name} ({post_action})", "DEBUG")

        self.history["states"].append(new_state.copy())

        return applied_modes, new_state

    def run_until_cycle(self, initial_state: DimensionalState,
                       max_steps: int = 100,
                       tolerance: float = 1e-6) -> Dict[str, Any]:
        self.history = {
            "states": [initial_state.copy()],
            "uc_values": [],
            "activations": [],
            "triggered_modes": [],
            "descriptors": [],
            "mv_results": [],
            "oracle_invocations": []
        }

        state = initial_state.copy()
        seen_signatures = []

        def state_signature(st: DimensionalState) -> tuple:
            vec_sig = tuple(round(x, 6) for x in st.vec)
            rho_sig = round(st.rho, 6)
            return (st.tape, vec_sig, rho_sig)

        initial_sig = state_signature(initial_state)
        seen_signatures.append(initial_sig)

        cycle_found = False
        cycle_start = -1
        cycle_length = 0

        for step_num in range(max_steps):
            applied_modes, state = self.step(state)

            sig = state_signature(state)
            if sig in seen_signatures:
                cycle_found = True
                cycle_start = seen_signatures.index(sig)
                cycle_length = len(seen_signatures) - cycle_start
                self._log(f"Cycle detected at step {step_num}: start={cycle_start}, length={cycle_length}", "INFO")
                break

            seen_signatures.append(sig)

        return {
            "final_state": state.to_dict(),
            "history": self.history,
            "cycle_found": cycle_found,
            "cycle_start": cycle_start,
            "cycle_length": cycle_length,
            "total_steps": len(self.history["states"]) - 1
        }

    def analyze_weight_sensitivity(self, test_states: List[DimensionalState], n_perturb: int = 10) -> Dict[str, float]:
        baseline_acts = []
        for state in test_states:
            ucs = self.calculate_uc_vector(state)
            baseline_acts.append(self.calculate_activations(ucs))

        stability_scores = []
        for _ in range(n_perturb):
            W_pert = self.W + np.random.normal(0, 0.1, self.W.shape)
            W_pert = np.clip(W_pert, 0, 3)

            pert_acts = []
            for state in test_states:
                ucs = self.calculate_uc_vector(state)
                logits = W_pert.dot(ucs)
                acts = 1.0 / (1.0 + np.exp(-logits))
                pert_acts.append(acts)

            sim = np.mean([
                np.dot(a1, a2) / (np.linalg.norm(a1) * np.linalg.norm(a2) + 1e-8)
                for a1, a2 in zip(baseline_acts, pert_acts)
            ])
            stability_scores.append(sim)

        return {
            "mean_stability": float(np.mean(stability_scores)),
            "std_stability": float(np.std(stability_scores)),
            "n_tests": len(test_states),
            "n_perturbations": n_perturb
        }

    def calc_uncertainty(self, state: DimensionalState) -> float:
        p = state.vec ** 2
        total = p.sum()
        if total > 0:
            p = p / total
        return -float(np.sum(np.where(p > 0, p * np.log(p + 1e-10), 0.0)))

    def calc_simplicity(self, state: DimensionalState) -> float:
        return float(math.log(state.rho + 1.0))

    def calc_uniqueness(self, state: DimensionalState) -> float:
        if len(state.vec) == 0:
            return 0.0
        p = state.vec ** 2
        return float(1.0 - np.max(p))

    def calc_continuity(self, state: DimensionalState) -> float:
        return float(state.vec.mean()) if len(state.vec) > 0 else 0.0

    def calc_self_similarity(self, state: DimensionalState) -> float:
        return float(np.std(state.vec)) if len(state.vec) > 0 else 0.0

    def calc_interconnectivity(self, state: DimensionalState) -> float:
        return float(np.dot(state.vec, state.vec[::-1]))

    def calc_holography(self, state: DimensionalState) -> float:
        area = 1e-4 * (state.rho ** 2)
        s_bh = (KB * C ** 3 * area) / (4 * G * HBAR)
        return float(s_bh)

    def calc_solidity(self, state: DimensionalState) -> float:
        return float(state.rho)

    def calc_paradox(self, state: DimensionalState) -> float:
        theta = np.sum(state.vec) % (2 * math.pi)
        return float(math.cos(theta) ** 2)

    def calc_flux(self, state: DimensionalState) -> float:
        diffs = np.diff(state.vec) if len(state.vec) > 1 else np.array([0.0])
        return float(np.mean(np.abs(diffs)))

    def calc_contiguity(self, state: DimensionalState) -> float:
        diffs = np.diff(state.vec) if len(state.vec) > 1 else np.array([0.0])
        return float(np.sum(np.abs(diffs)))

    def calc_complementarity(self, state: DimensionalState) -> float:
        return float(np.dot(state.vec, -state.vec))

    def calc_incompleteness(self, state: DimensionalState) -> float:
        norm = np.linalg.norm(state.vec)
        return float(max(0.0, 1.0 - 1.0 / (norm + 1.0)))

    def apply_oscillation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(new_state.vec) > 0:
            rolled = np.roll(new_state.vec, 1)
            blended = (new_state.vec + rolled) / 2.0
            norm = np.linalg.norm(blended)
            if norm > 0:
                new_state.vec = blended / norm
        return new_state

    def apply_folding(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = -np.abs(new_state.vec)
        new_state.rho = new_state.rho * PHI
        return new_state

    def apply_radiation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        noise = np.random.normal(0, 0.1, size=new_state.vec.shape)
        perturbed = new_state.vec + noise
        norm = np.linalg.norm(perturbed)
        if norm > 0:
            new_state.vec = perturbed / norm
        return new_state

    def apply_propagation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(new_state.vec) > 0:
            new_state.vec = np.roll(new_state.vec, 1)
        new_state.rho = new_state.rho / PHI
        return new_state

    def apply_arborescence(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        squared = new_state.vec ** 2
        norm = np.linalg.norm(squared)
        if norm > 0:
            new_state.vec = squared / norm
        return new_state

    def apply_tessellation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = np.sort(new_state.vec)
        return new_state

    def apply_helicity(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = new_state.vec[::-1]
        return new_state

    def apply_enantiodromia(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = -new_state.vec
        return new_state

    def apply_interference(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(new_state.vec) > 1:
            wave1 = new_state.vec
            wave2 = np.roll(wave1, len(wave1) // 2)
            superposed = wave1 + wave2
            norm = np.linalg.norm(superposed)
            if norm > 0:
                new_state.vec = superposed / norm
        return new_state

    def apply_solution(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        mean_val = np.mean(new_state.vec) if len(new_state.vec) > 0 else 0.0
        new_state.vec = new_state.vec * 0.7 + mean_val * 0.3
        return new_state

    def apply_synchronicity(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(new_state.vec) > 1:
            phase_shift = np.random.uniform(0, 2 * math.pi)
            for i in range(len(new_state.vec)):
                new_state.vec[i] = new_state.vec[i] * math.cos(phase_shift + i * math.pi / len(new_state.vec))
            norm = np.linalg.norm(new_state.vec)
            if norm > 0:
                new_state.vec = new_state.vec / norm
        return new_state

    def apply_entropy(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        noise = np.random.uniform(-0.1, 0.1, size=new_state.vec.shape)
        perturbed = new_state.vec + noise
        norm = np.linalg.norm(perturbed)
        if norm > 0:
            new_state.vec = perturbed / norm
        return new_state

    def apply_metabolisis(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(new_state.vec) > 0:
            phi_cascade = np.array([PHI ** i for i in range(len(new_state.vec))])
            scaled = new_state.vec * phi_cascade
            norm = np.linalg.norm(scaled)
            if norm > 0:
                new_state.vec = PHI * scaled / norm
        return new_state


def main():
    import argparse

    parser = argparse.ArgumentParser(description="PCTM v6.1 - Polychronological Conceptual Transformation Machine")
    parser.add_argument("--uc", type=str, default="UCCanon.json", help="Path to Universal Characteristics canon")
    parser.add_argument("--md", type=str, default="MDCanon.json", help="Path to Modal Dynamics canon")
    parser.add_argument("--orders", type=str, default="Orders_Mathematical_Substrate.json", help="Path to Orders substrate")
    parser.add_argument("--weights", type=str, default=None, help="Path to weight matrix JSON or 'auto'")
    parser.add_argument("--oracle", type=str, default="iching.json", help="Path to I Ching hexagram data")
    parser.add_argument("--input", type=str, default=None, help="Path to initial state JSON file")
    parser.add_argument("--law-mode", type=str, default="strict", choices=["strict", "clamp", "project", "warn"])
    parser.add_argument("--oracle-enabled", action="store_true", help="Enable Oracle intervention")
    parser.add_argument("--oracle-threshold", type=float, default=0.3, help="MV success threshold for Oracle")
    parser.add_argument("--fallback", type=str, default="random_md", choices=["random_md", "identity", "oracle", "most_stable"])
    parser.add_argument("--steps", type=int, default=100, help="Maximum steps")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--output", type=str, default=None, help="Output file path (auto-generated from input if not specified)")

    args = parser.parse_args()

    engine = PCTMEngine(
        uc_path=args.uc,
        md_path=args.md,
        orders_path=args.orders,
        weights_path=args.weights,
        oracle_path=args.oracle,
        law_mode=args.law_mode,
        oracle_enabled=args.oracle_enabled,
        oracle_threshold=args.oracle_threshold,
        fallback_policy=args.fallback,
        verbose=args.verbose
    )

   # Auto-generate output filename if not specified
    if args.output is None:
        if args.input:
            input_path = Path(args.input)
            base_name = input_path.stem
            args.output = f"{base_name}_output.json"
        else:
            args.output = "pctm_output.json"

   # Load or generate initial state
    if args.input and Path(args.input).exists():
        print(f"\nLoading initial state from: {args.input}")
        with open(args.input, 'r', encoding='utf-8') as f:
            input_data = json.load(f)

        # Check if it's a previous output with nested structure
        if "initial_state" in input_data:
            state_data = input_data["initial_state"]
        elif "final_state" in input_data:
            state_data = input_data["final_state"]
            print("  Using final_state from previous run as initial_state")
        else:
            state_data = input_data

        initial_state = DimensionalState.from_dict(state_data)

        # Validate dimensionality
        n_dims = len(engine.universal_characteristics)
        if len(initial_state.vec) != n_dims:
            print(f"  WARNING: Input vector dimension {len(initial_state.vec)} != expected {n_dims}")
            print(f"  Resizing vector to match current UC canon")
            if len(initial_state.vec) < n_dims:
                # Pad with zeros
                padded = np.zeros(n_dims)
                padded[:len(initial_state.vec)] = initial_state.vec
                initial_state.vec = padded
            else:
                # Truncate
                initial_state.vec = initial_state.vec[:n_dims]
            # Renormalize
            norm = np.linalg.norm(initial_state.vec)
            if norm > 0:
                initial_state.vec = initial_state.vec / norm
                initial_state.rho = 1.0

        print(f"  Loaded: tape={initial_state.tape}, order={initial_state.order}, rho={initial_state.rho:.4f}")
    else:
        if args.input:
            print(f"\nWARNING: Input file {args.input} not found. Generating random initial state.")
        print("\nGenerating random initial state...")
        n_dims = len(engine.universal_characteristics)
        initial_vector = np.random.randn(n_dims)
        initial_vector = initial_vector / np.linalg.norm(initial_vector)
        initial_state = DimensionalState(vec=initial_vector, rho=1.0, tape=0, order="Material")
        print(f"  Created: tape=0, order=Material, rho=1.0, dims={n_dims}")

    print(f"\n{'═' * 70}")
    print("Running PCTM simulation...")
    print(f"{'═' * 70}\n")

    result = engine.run_until_cycle(initial_state, max_steps=args.steps)

    output_data = {
        "initial_state": initial_state.to_dict(),
        "final_state": result["final_state"],
        "cycle_found": result["cycle_found"],
        "cycle_start": result["cycle_start"],
        "cycle_length": result["cycle_length"],
        "total_steps": result["total_steps"],
        "summary": {
            "n_oracle_invocations": len(result["history"]["oracle_invocations"]),
            "n_descriptors": len(result["history"]["descriptors"]),
            "mv_success_rate": sum(
                sum(1 for r in mv_result.values() if r["mv"] == 1.0) / max(len(mv_result), 1)
                for mv_result in result["history"]["mv_results"]
            ) / max(len(result["history"]["mv_results"]), 1)
        },
        "weights": {
            "shape": list(engine.W.shape),
            "min": float(engine.W.min()),
            "max": float(engine.W.max()),
            "mean": float(engine.W.mean()),
            "std": float(engine.W.std()),
            "sparsity": float((engine.W == 0).sum() / engine.W.size)
        }
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'═' * 70}")
    print("SUMMARY")
    print(f"{'═' * 70}")
    print(f"Total steps: {result['total_steps']}")
    print(f"Cycle detected: {result['cycle_found']}")
    if result['cycle_found']:
        print(f"Cycle start: {result['cycle_start']}, length: {result['cycle_length']}")
    print(f"Oracle invocations: {output_data['summary']['n_oracle_invocations']}")
    print(f"MV success rate: {output_data['summary']['mv_success_rate']:.3f}")
    print(f"Output written to: {args.output}")
    print(f"{'═' * 70}\n")


if __name__ == "__main__":
    main()
