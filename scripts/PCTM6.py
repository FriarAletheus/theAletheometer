import argparse
import json
import math
import random
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

PHI = 1.61803398875
KB = 1.380649e-23
C = 299792458
G = 6.67430e-11
HBAR = 1.054571817e-34

ORDERS = [
    "Virtual",
    "Quantum",
    "Material",
    "Ethereal",
    "Astral",
    "Celestial",
    "Existential",
]


def _project_identity(state: "DimensionalState") -> np.ndarray:
    return state.vec.copy()


def _fit_simple_model(data: np.ndarray) -> Optional[Tuple[Dict[str, float], Dict[str, float]]]:
    if data.size < 2:
        return None
    mean_val = float(np.mean(data))
    std_val = float(np.std(data))
    model = {"mean": mean_val, "std": std_val}
    loss = float(np.mean(np.abs(data - mean_val)))
    stability = float(1.0 / (1.0 + std_val))
    stats = {"loss": loss, "stability": stability, "n": float(data.size)}
    return model, stats


class OrderRegistry:
    def __init__(self) -> None:
        self.orders = {
            order_name: {
                "project": _project_identity,
                "fit": _fit_simple_model,
                "operators": ["mean", "std"],
            }
            for order_name in ORDERS
        }


@dataclass
class DimensionalState:
    vec: np.ndarray
    rho: float = 1.0
    tape: int = 0
    order: str = "Material"

    def copy(self) -> "DimensionalState":
        return DimensionalState(self.vec.copy(), self.rho, self.tape, self.order)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector": self.vec.tolist(),
            "magnitude": self.rho,
            "tape_id": self.tape,
            "order": self.order,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], engine: Optional["PCTMEngine"] = None) -> "DimensionalState":
        if engine:
            valid, errors = engine._validate_json_schema(data, engine.schema_path)
            if not valid:
                raise ValueError(f"Invalid input state: {'; '.join(errors)}")

        vec_raw = data.get("vector", [1.0])
        if not isinstance(vec_raw, list) or len(vec_raw) == 0:
            raise ValueError("vector must be non-empty list")

        vec = np.array(vec_raw, dtype=float)
        if np.any(np.isnan(vec)) or np.any(np.isinf(vec)):
            raise ValueError("vector contains NaN or Inf")

        rho = float(data.get("magnitude", 1.0))
        if rho <= 0:
            raise ValueError("magnitude must be positive")

        tape_id = int(data.get("tape_id", 0))
        if tape_id < 0:
            raise ValueError("tape_id must be non-negative")

        order = data.get("order", "Material")
        if order not in ORDERS:
            raise ValueError(f"order must be one of {ORDERS}")

        return cls(vec, rho, tape_id, order)


class UniversalCharacteristic:
    def __init__(self, name: str, symbol: str, equation: str, domain: str, uc_type: str,
                 func: Callable[[DimensionalState], float]):
        self.name = name
        self.symbol = symbol
        self.equation = equation
        self.domain = domain
        self.type = uc_type
        self.calculate = func


class ModalDynamic:
    def __init__(self, name: str, symbol: str, operation: str, description: str, md_type: str,
                 func: Callable[[DimensionalState], DimensionalState]):
        self.name = name
        self.symbol = symbol
        self.operation = operation
        self.description = description
        self.type = md_type
        self.apply = func


class IChingOracle:
    def __init__(self, hexagram_file: str = "iching.json"):
        with open(hexagram_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.hexagrams = data.get("hexagrams", [])

    def fifty_stick_cast(self) -> List[int]:
        choices = [6, 7, 8, 9]
        weights = [1, 5, 7, 3]
        return random.choices(choices, weights=weights, k=6)

    def lines_to_hexagram_number(self, lines: List[int]) -> int:
        binary_str = "".join(["1" if line % 2 == 1 else "0" for line in reversed(lines)])
        return int(binary_str, 2) + 1

    def cast(self) -> Dict[str, Any]:
        lines = self.fifty_stick_cast()
        hex_num = self.lines_to_hexagram_number(lines)
        hex_info = next((h for h in self.hexagrams if h.get("hexagram_number") == hex_num), None)
        return {"cast_lines": lines, "hexagram_number": hex_num, "hexagram": hex_info}


@dataclass
class PredictiveDescriptor:
    order: str
    operator_name: str
    model: Dict[str, Any]
    fit_stats: Dict[str, Any]
    bridges: List[Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order": self.order,
            "operator_name": self.operator_name,
            "model": self.model,
            "fit_stats": self.fit_stats,
            "bridges": self.bridges,
        }


class PCTMEngine:
    def __init__(
        self,
        uc_path: Optional[str] = None,
        md_path: Optional[str] = None,
        formulae_path: Optional[str] = None,
        oracle_enabled: bool = True,
        oracle_path: str = "iching.json",
        oracle_threshold: float = 0.3,
        fallback_policy: str = "random_md",
        verbose: bool = False,
        law_mode: str = "strict",
        weights_path: Optional[str] = None,
        schema_path: str = "pctm_schema.json",
    ):
        self.verbose = verbose
        self.oracle_enabled = oracle_enabled
        self.oracle_path = oracle_path
        self.oracle_threshold = oracle_threshold
        self.fallback_policy = fallback_policy
        self.schema_path = schema_path
        self.log_entries: List[Dict[str, str]] = []
        self.order_registry = OrderRegistry()

        self.universal_characteristics = self._load_universal_characteristics(uc_path, md_path, formulae_path)
        self.modal_dynamics = self._load_modal_dynamics(uc_path, md_path, formulae_path)

        if weights_path == "auto":
            self.W = self._derive_weight_matrix()
        elif weights_path:
            self.W = self._load_weight_matrix(weights_path)
        else:
            self.W = np.array([
                [3, 1, 0, 2, 0, 0, 1, 1, 0, 3, 0, 0, 0],
                [2, 0, 0, 0, 2, 0, 1, 0, 3, 2, 0, 0, 2],
                [0, 0, 0, 2, 0, 1, 2, 0, 0, 2, 1, 0, 0],
                [0, 0, 0, 3, 0, 3, 0, 0, 0, 2, 3, 0, 0],
                [0, 0, 2, 0, 0, 3, 0, 0, 0, 0, 2, 0, 0],
                [0, 0, 0, 0, 3, 2, 0, 0, 0, 0, 2, 0, 0],
                [0, 0, 0, 1, 2, 2, 0, 2, 0, 2, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 3, 2],
                [0, 1, 1, 0, 0, 1, 0, 2, 0, 0, 2, 0, 0],
                [0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2]
            ], dtype=float)

        self.b = np.zeros(len(self.modal_dynamics))
        self._log(
            f"W matrix loaded: shape {self.W.shape}, range [{self.W.min():.1f}, {self.W.max():.1f}]",
            "INFO",
        )

        self.law_mode = law_mode
        self.tape_laws = {
            0: {
                "name": "Base",
                "constraint": lambda state: True,
                "blocked_mds": [],
                "project_fn": lambda state: state.copy(),
            },
            1: {
                "name": "UnitNorm",
                "constraint": lambda state: abs(np.linalg.norm(state.vec) - 1.0) < 0.05,
                "blocked_mds": ["folding", "propagation"],
                "project_fn": self._project_to_unit_sphere,
            },
            2: {
                "name": "NonNegative",
                "constraint": lambda state: np.all(state.vec >= -1e-6),
                "blocked_mds": ["folding", "enantiodromia"],
                "project_fn": self._project_to_nonnegative,
            },
            3: {
                "name": "Probability",
                "constraint": lambda state: np.all(state.vec >= -1e-6)
                and abs(np.sum(state.vec) - 1.0) < 0.05,
                "blocked_mds": ["folding", "enantiodromia", "radiation"],
                "project_fn": self._project_to_probability,
            },
        }
        self._log(f"Tape laws loaded: {list(self.tape_laws.keys())} tapes, mode={self.law_mode}", "INFO")

        self.oracle: Optional[IChingOracle] = None

        self.history: Dict[str, List] = {
            "states": [],
            "uc_values": [],
            "activations": [],
            "triggered_modes": [],
            "descriptors": [],
            "mv_results": [],
            "oracle_invocations": [],
            "tape_enforcement": [],
        }

    def _log(self, message: str, level: str = "INFO") -> None:
        entry = {"timestamp": datetime.now().isoformat(), "level": level, "message": message}
        self.log_entries.append(entry)
        if self.verbose:
            print(f"[{entry['timestamp']}] {level}: {message}")

    def _load_universal_characteristics(
        self, uc_path: Optional[str], md_path: Optional[str], formulae_path: Optional[str]
    ) -> List[UniversalCharacteristic]:
        if formulae_path:
            with open(formulae_path, "r", encoding="utf-8") as f:
                canon = json.load(f)
            uc_data = next((item["UniversalCharacteristics"] for item in canon
                            if "UniversalCharacteristics" in item), [])
        elif uc_path:
            with open(uc_path, "r", encoding="utf-8") as f:
                uc_data = json.load(f)
        else:
            uc_data = [
                {"name": "Uncertainty", "symbol": "U1", "equation": "H(p)", "domain": "p_i", "type": "Entropy"},
                {"name": "Simplicity", "symbol": "U2", "equation": "log(ρ)", "domain": "ρ", "type": "Log"},
                {"name": "Uniqueness", "symbol": "U3", "equation": "1 - max(p)", "domain": "p_i", "type": "Anti-Dominance"},
                {"name": "Continuity", "symbol": "U4", "equation": "mean(x)", "domain": "x", "type": "Averaged"},
                {"name": "Self_Similarity", "symbol": "U5", "equation": "std(x)", "domain": "x", "type": "StdDev"},
                {"name": "Interconnectivity", "symbol": "U6", "equation": "x·rev(x)", "domain": "x", "type": "Mirror"},
                {"name": "Holography", "symbol": "U7", "equation": "A bound", "domain": "A", "type": "Entropy"},
                {"name": "Solidity", "symbol": "U8", "equation": "||x||", "domain": "x", "type": "Magnitude"},
                {"name": "Paradox", "symbol": "U9", "equation": "|1-||x||^2|", "domain": "x", "type": "Deviation"},
                {"name": "Flux", "symbol": "U10", "equation": "||Δx||", "domain": "x", "type": "Variation"},
                {"name": "Contiguity", "symbol": "U11", "equation": "count(|Δx|<ε)", "domain": "x", "type": "Continuity"},
                {"name": "Complementarity", "symbol": "U12", "equation": "∑x(1-x)", "domain": "x", "type": "Duality"},
                {"name": "Incompleteness", "symbol": "U13", "equation": "1-1/||x||", "domain": "x", "type": "Gödel"},
            ]

        characteristics: List[UniversalCharacteristic] = []
        for uc in uc_data:
            func = getattr(self, f"calc_{uc['name'].lower()}", lambda s: 0.0)
            characteristics.append(
                UniversalCharacteristic(
                    uc["name"],
                    uc.get("symbol", ""),
                    uc.get("equation", ""),
                    uc.get("domain", ""),
                    uc.get("type", ""),
                    func,
                )
            )
        return characteristics

    def _load_modal_dynamics(
        self, uc_path: Optional[str], md_path: Optional[str], formulae_path: Optional[str]
    ) -> List[ModalDynamic]:
        if formulae_path:
            with open(formulae_path, "r", encoding="utf-8") as f:
                canon = json.load(f)
            md_data = next((item["ModalDynamics"] for item in canon if "ModalDynamics" in item), [])
        elif md_path:
            with open(md_path, "r", encoding="utf-8") as f:
                md_data = json.load(f)
        else:
            md_data = [
                {"name": "Oscillation", "symbol": "M1", "operation": "Rotate+Blend", "description": "Cyclic permutation", "type": "Recursion"},
                {"name": "Folding", "symbol": "M2", "operation": "Absolute Inversion", "description": "Fold and invert", "type": "Reversal"},
                {"name": "Radiation", "symbol": "M3", "operation": "Add Noise", "description": "Inject noise", "type": "Stochastic"},
                {"name": "Propagation", "symbol": "M4", "operation": "Shift Vector", "description": "Translate", "type": "Drift"},
                {"name": "Arborescence", "symbol": "M5", "operation": "Square Components", "description": "Branching", "type": "Expansion"},
                {"name": "Tessellation", "symbol": "M6", "operation": "Sort Values", "description": "Structure", "type": "Ordering"},
                {"name": "Helicity", "symbol": "M7", "operation": "Reverse Vector", "description": "Reflect", "type": "Symmetry"},
                {"name": "Enantiodromia", "symbol": "M8", "operation": "Negate Vector", "description": "Invert", "type": "Opposition"},
                {"name": "Exteriority", "symbol": "M9", "operation": "Radiate Outward", "description": "Emanate", "type": "Emanation"},
                {"name": "Solution", "symbol": "M10", "operation": "Neighbor Average", "description": "Smooth", "type": "Continuity"},
            ]

        dynamics: List[ModalDynamic] = []
        for md in md_data:
            func = getattr(self, f"apply_{md['name'].lower()}", lambda s: s.copy())
            dynamics.append(
                ModalDynamic(
                    md["name"],
                    md.get("symbol", ""),
                    md.get("operation", ""),
                    md.get("description", ""),
                    md.get("type", ""),
                    func,
                )
            )
        return dynamics

    def _load_json(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_weight_matrix(self, path: str) -> np.ndarray:
        data = self._load_json(path)
        W = np.array(data["W"], dtype=float)
        if W.shape != (10, 13):
            raise ValueError(f"W matrix must be (10,13), got {W.shape}")
        return W

    def _derive_weight_matrix(self) -> np.ndarray:
        uc_names = [
            "uncertainty",
            "simplicity",
            "uniqueness",
            "continuity",
            "self_similarity",
            "interconnectivity",
            "holography",
            "solidity",
            "paradox",
            "flux",
            "contiguity",
            "complementarity",
            "incompleteness",
        ]

        md_profiles = {
            "oscillation": ["continuity", "self_similarity", "flux"],
            "folding": ["paradox", "solidity"],
            "radiation": ["uncertainty", "incompleteness"],
            "propagation": ["flux", "continuity"],
            "arborescence": ["solidity", "self_similarity"],
            "tessellation": ["continuity", "contiguity"],
            "helicity": ["interconnectivity"],
            "enantiodromia": ["paradox"],
            "exteriority": ["solidity", "incompleteness"],
            "solution": ["uncertainty", "self_similarity"],
        }

        W = np.zeros((10, 13), dtype=float)
        for md_idx, (md_name, uc_list) in enumerate(md_profiles.items()):
            for uc_name in uc_list:
                if uc_name in uc_names:
                    col_idx = uc_names.index(uc_name)
                    W[md_idx, col_idx] = 3.0

        row_sums = W.sum(axis=1, keepdims=True)
        W = np.divide(W, row_sums, out=np.zeros_like(W), where=row_sums != 0)
        self._log(f"Derived W matrix from {len(md_profiles)} MD profiles", "INFO")
        return W

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
                pert_acts.append(1 / (1 + np.exp(-W_pert.dot(ucs))))

            sim = np.mean([
                np.dot(a1, a2) / (np.linalg.norm(a1) * np.linalg.norm(a2) + 1e-8)
                for a1, a2 in zip(baseline_acts, pert_acts)
            ])
            stability_scores.append(sim)

        return {
            "mean_stability": float(np.mean(stability_scores)),
            "std_stability": float(np.std(stability_scores)),
            "n_tests": len(test_states),
            "n_perturbations": n_perturb,
        }

    def _project_to_unit_sphere(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        norm = np.linalg.norm(new_state.vec)
        if norm > 0:
            new_state.vec /= norm
        self._log(f"Projected tape {state.tape} to unit sphere: norm={norm:.4f}→1.0", "DEBUG")
        return new_state

    def _project_to_nonnegative(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = np.abs(new_state.vec)
        norm = np.linalg.norm(new_state.vec)
        if norm > 0:
            new_state.vec /= norm
        self._log(
            f"Projected tape {state.tape} to nonnegative: {np.sum(new_state.vec < 0)} violations→0",
            "DEBUG",
        )
        return new_state

    def _project_to_probability(self, state: DimensionalState) -> DimensionalState:
        new_state = self._project_to_nonnegative(state)
        total = np.sum(new_state.vec)
        if total > 0:
            new_state.vec /= total
        self._log(f"Projected tape {state.tape} to probability: sum={total:.4f}→1.0", "DEBUG")
        return new_state

    def _validate_json_schema(self, data: Dict[str, Any], schema_path: str = "pctm_schema.json") -> Tuple[bool, List[str]]:
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                json.load(f)
        except FileNotFoundError:
            self._log("Schema file not found, skipping validation", "WARNING")
            return True, []

        errors = []

        if "vector" not in data:
            errors.append("Missing required 'vector'")
        elif not isinstance(data["vector"], list) or len(data["vector"]) == 0:
            errors.append("'vector' must be non-empty array")
        elif not all(isinstance(x, (int, float)) and not math.isnan(x) for x in data["vector"]):
            errors.append("'vector' contains NaN/inf or non-numeric values")

        if "magnitude" in data and (data["magnitude"] <= 0 or math.isnan(data["magnitude"])):
            errors.append("'magnitude' must be positive finite number")

        if "tape_id" in data and (not isinstance(data["tape_id"], int) or data["tape_id"] < 0):
            errors.append("'tape_id' must be non-negative integer")

        if "order" in data and data["order"] not in ORDERS:
            errors.append(f"'order' must be one of: {ORDERS}")

        if "order" in data and "metadata" in data:
            order_meta = data["metadata"]
            order_rules = {
                "Material": {"units": list, "conservation_laws": list},
                "Quantum": {"basis": list},
                "Astral": {"modalities": list},
            }
            if data["order"] in order_rules:
                for field, expected_type in order_rules[data["order"]].items():
                    if field in order_meta:
                        if not isinstance(order_meta[field], expected_type):
                            errors.append(f"order='{data['order']}': '{field}' must be {expected_type}")

        valid = len(errors) == 0
        if not valid:
            self._log(f"Schema validation FAILED: {errors}", "ERROR")
        else:
            self._log("Schema validation PASSED", "INFO")

        return valid, errors

    def init_oracle(self) -> None:
        self.oracle = IChingOracle(self.oracle_path)

    def calculate_uc_vector(self, state: DimensionalState) -> np.ndarray:
        return np.array([uc.calculate(state) for uc in self.universal_characteristics], dtype=float)

    def calculate_activations(self, uc_values: np.ndarray) -> np.ndarray:
        z = self.W.dot(uc_values) + self.b
        return 1.0 / (1.0 + np.exp(-z))

    def get_triggered_modes(self, activations: np.ndarray, threshold: float = 0.5) -> List[str]:
        return [md.name for md, act in zip(self.modal_dynamics, activations) if act > threshold]

    def _test_mathematical_valence(
        self,
        state: DimensionalState,
        loss_threshold: float = 0.5,
        stability_threshold: float = 0.5,
    ) -> Tuple[Dict[str, Dict[str, float]], List[PredictiveDescriptor]]:
        mv_results: Dict[str, Dict[str, float]] = {}
        descriptors: List[PredictiveDescriptor] = []

        for order_name, cfg in self.order_registry.orders.items():
            project_fn = cfg["project"]
            fit_fn = cfg["fit"]

            data = project_fn(state)
            data = np.array(data, dtype=float)

            fit = fit_fn(data)
            if fit is None:
                mv_results[order_name] = {
                    "mv": 0.0,
                    "loss": float("inf"),
                    "stability": 0.0,
                    "n": 0.0,
                }
                continue

            model, stats = fit
            loss = float(stats.get("loss", float("inf")))
            stability = float(stats.get("stability", 0.0))
            n = float(stats.get("n", 0.0))

            mv_flag = 1.0 if (loss <= loss_threshold and stability >= stability_threshold) else 0.0

            mv_results[order_name] = {
                "mv": mv_flag,
                "loss": loss,
                "stability": stability,
                "n": n,
            }

            if mv_flag == 1.0:
                desc = PredictiveDescriptor(
                    order=order_name,
                    operator_name=",".join(cfg.get("operators", [])),
                    model=model,
                    fit_stats=stats,
                    bridges=[],
                )
                descriptors.append(desc)

        return mv_results, descriptors

    def _decide_fallback(
        self, mv_results: Dict[str, Dict[str, float]], triggered: List[str]
    ) -> Tuple[List[str], Optional[Dict[str, Any]]]:
        mv_success_count = sum(1 for r in mv_results.values() if r["mv"] == 1.0)
        mv_fraction = mv_success_count / len(mv_results) if mv_results else 0.0

        if triggered and mv_fraction >= self.oracle_threshold:
            return [], None

        self._log(
            f"Fallback triggered: MV fraction={mv_fraction:.2f} < {self.oracle_threshold}, triggered={len(triggered)}",
            "DEBUG",
        )

        fallback_modes: List[str] = []
        oracle_result = None

        if self.fallback_policy == "random_md":
            if self.modal_dynamics:
                idx = np.random.randint(0, len(self.modal_dynamics))
                fallback_modes = [self.modal_dynamics[idx].name]

        elif self.fallback_policy == "identity":
            fallback_modes = []

        elif self.fallback_policy == "most_stable":
            if any(md.name.lower() == "solution" for md in self.modal_dynamics):
                fallback_modes = ["solution"]

        elif self.fallback_policy == "oracle" and self.oracle_enabled:
            oracle_result = self.oracle_cast()
            if oracle_result and self.modal_dynamics:
                hex_num = oracle_result["hexagram_number"]
                idx = (hex_num - 1) % len(self.modal_dynamics)
                fallback_modes = [self.modal_dynamics[idx].name]

        return fallback_modes, oracle_result

    def enforce_tape_law(self, state: DimensionalState, md_name: str) -> Tuple[DimensionalState, str]:
        tape_id = state.tape
        if tape_id not in self.tape_laws:
            self._log(f"Unknown tape {tape_id}, demoting to tape 0", "WARNING")
            return DimensionalState(state.vec, state.rho, tape_id=0, order=state.order), "demote"

        law = self.tape_laws[tape_id]

        if md_name.lower() in [m.lower() for m in law["blocked_mds"]]:
            if self.law_mode == "strict":
                return state, "block"
            if self.law_mode == "warn":
                self._log(f"Tape {tape_id} {law['name']}: MD '{md_name}' blocked (warn mode)", "WARNING")
                return state, "warn"

        if not law["constraint"](state):
            self._log(f"Tape {tape_id} {law['name']} violated pre-MD", "DEBUG")

            if self.law_mode == "strict":
                return state, "block"
            if self.law_mode == "warn":
                self._log(f"Tape {tape_id} violation (warn mode): {law['name']}", "WARNING")
                return state, "warn"
            if self.law_mode == "project":
                state = law["project_fn"](state)
                self._log(f"Tape {tape_id}: projected to satisfy law", "INFO")
                return state, "project"
            if self.law_mode == "clamp":
                if tape_id == 1:
                    norm = np.linalg.norm(state.vec)
                    if norm > 0:
                        state.vec /= norm
                elif tape_id == 2:
                    state.vec = np.maximum(state.vec, 0)
                return state, "clamp"

        return state, "pass"

    def oracle_cast(self) -> Dict[str, Any]:
        if self.oracle is None:
            self.init_oracle()
        return self.oracle.cast()

    def step(self, state: DimensionalState, threshold: float = 0.5) -> Tuple[List[str], DimensionalState]:
        uc_values = self.calculate_uc_vector(state)
        activations = self.calculate_activations(uc_values)
        triggered = self.get_triggered_modes(activations, threshold)

        mv_results, descriptors = self._test_mathematical_valence(state)
        self.history["mv_results"].append(mv_results)
        self.history["descriptors"].extend(descriptors)

        new_state = state.copy()
        applied_modes: List[str] = []

        fallback_modes, oracle_result = self._decide_fallback(mv_results, triggered)

        if oracle_result:
            self.history["oracle_invocations"].append(oracle_result)
            applied_modes.extend([f"{m} (oracle)" for m in fallback_modes])
        elif fallback_modes:
            applied_modes.extend([f"{m} (fallback)" for m in fallback_modes])

        violation_count = 0

        for mode_name in fallback_modes:
            md = next((m for m in self.modal_dynamics if m.name.lower() == mode_name.lower()), None)
            if md:
                corrected_state, action = self.enforce_tape_law(new_state, md.name)
                if action == "block":
                    self._log(
                        f"Blocked {md.name} on tape {new_state.tape} "
                        f"({self.tape_laws.get(new_state.tape, {}).get('name', 'unknown')})",
                        "INFO",
                    )
                    continue
                new_state = md.apply(corrected_state)
                applied_modes.append(f"{md.name} ({action})")
                violation_count += 1 if action != "pass" else 0

        for mode_name in triggered:
            md = next((m for m in self.modal_dynamics if m.name.lower() == mode_name.lower()), None)
            if md:
                corrected_state, action = self.enforce_tape_law(new_state, md.name)
                if action == "block":
                    self._log(
                        f"Blocked {md.name} on tape {new_state.tape} "
                        f"({self.tape_laws.get(new_state.tape, {}).get('name', 'unknown')})",
                        "INFO",
                    )
                    continue
                new_state = md.apply(corrected_state)
                applied_modes.append(md.name)
                violation_count += 1 if action != "pass" else 0

        final_state, final_action = self.enforce_tape_law(new_state, "post_step")
        if final_action != "pass":
            self._log(f"Post-MD tape law enforcement: {final_action}", "INFO")
        new_state = final_state

        self.history["states"].append(new_state.copy())
        self.history["uc_values"].append(uc_values)
        self.history["activations"].append(activations)
        self.history["triggered_modes"].append(applied_modes)
        self.history["tape_enforcement"].append(violation_count)

        return applied_modes, new_state

    def run_until_cycle(
        self,
        initial_state: DimensionalState,
        max_steps: int = 100,
        tolerance: float = 1e-6,
    ) -> Dict[str, Any]:
        self.history = {
            "states": [initial_state.copy()],
            "uc_values": [],
            "activations": [],
            "triggered_modes": [],
            "descriptors": [],
            "mv_results": [],
            "oracle_invocations": [],
            "tape_enforcement": [],
        }

        state = initial_state.copy()
        seen_signatures = []

        def state_signature(st: DimensionalState) -> tuple:
            return (
                st.tape,
                tuple(np.round(st.vec, 6)),
                round(st.rho, 6),
            )

        seen_signatures.append(state_signature(state))
        cycle_found = False
        cycle_start = -1
        cycle_length = -1

        for _ in range(max_steps):
            _, state = self.step(state)

            sig = state_signature(state)
            if sig in seen_signatures:
                cycle_found = True
                cycle_start = seen_signatures.index(sig)
                cycle_length = len(seen_signatures) - cycle_start
                break

            seen_signatures.append(sig)

        return {
            "final_state": state,
            "history": self.history,
            "cycle_found": cycle_found,
            "cycle_start": cycle_start,
            "cycle_length": cycle_length,
            "total_steps": len(self.history["states"]) - 1,
        }

    def calc_uncertainty(self, state: DimensionalState) -> float:
        p = state.vec**2
        total = p.sum()
        if total != 0:
            p = p / total
        return -float(np.sum(np.where(p > 0, p * np.log(p), 0.0)))

    def calc_simplicity(self, state: DimensionalState) -> float:
        return float(math.log(state.rho + 1.0))

    def calc_uniqueness(self, state: DimensionalState) -> float:
        if len(state.vec) == 0:
            return 0.0
        p = state.vec**2
        return float(1.0 - np.max(p))

    def calc_continuity(self, state: DimensionalState) -> float:
        return float(state.vec.mean()) if len(state.vec) > 0 else 0.0

    def calc_self_similarity(self, state: DimensionalState) -> float:
        return float(np.std(state.vec)) if len(state.vec) > 0 else 0.0

    def calc_interconnectivity(self, state: DimensionalState) -> float:
        return float(np.dot(state.vec, state.vec[::-1]))

    def calc_holography(self, state: DimensionalState) -> float:
        area = 1e-4 * (state.rho**2)
        return float(KB * C**3 * area / (4 * G * HBAR))

    def calc_solidity(self, state: DimensionalState) -> float:
        return float(np.linalg.norm(state.vec))

    def calc_paradox(self, state: DimensionalState) -> float:
        return float(abs(1.0 - np.linalg.norm(state.vec) ** 2))

    def calc_flux(self, state: DimensionalState) -> float:
        return float(np.linalg.norm(np.diff(state.vec))) if len(state.vec) >= 2 else 0.0

    def calc_contiguity(self, state: DimensionalState) -> float:
        if len(state.vec) <= 1:
            return 0.0
        diffs = np.abs(np.diff(state.vec))
        return float(np.sum(diffs < 0.1))

    def calc_complementarity(self, state: DimensionalState) -> float:
        x_clamped = np.clip(state.vec, 0.0, 1.0)
        return float(np.sum(x_clamped * (1.0 - x_clamped)))

    def calc_incompleteness(self, state: DimensionalState) -> float:
        norm_val = np.linalg.norm(state.vec)
        if norm_val == 0:
            return float("inf")
        return float(1.0 - 1.0 / norm_val)

    def apply_oscillation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(state.vec) > 0:
            r = np.roll(state.vec, 1)
            combined = state.vec + r
            norm_val = np.linalg.norm(combined)
            if norm_val != 0:
                new_state.vec = combined / norm_val
        return new_state

    def apply_folding(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = -np.abs(state.vec)
        new_state.rho *= PHI
        norm_val = np.linalg.norm(new_state.vec)
        if norm_val != 0:
            new_state.vec /= norm_val
        return new_state

    def apply_radiation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        noise = np.random.normal(0, 0.01, size=state.vec.shape)
        new_state.vec = state.vec + noise
        norm_val = np.linalg.norm(new_state.vec)
        if norm_val != 0:
            new_state.vec /= norm_val
        return new_state

    def apply_propagation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(state.vec) > 0:
            new_state.vec = np.roll(state.vec, 1)
        new_state.rho /= PHI
        return new_state

    def apply_arborescence(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = state.vec**2
        norm_val = np.linalg.norm(new_state.vec)
        if norm_val != 0:
            new_state.vec /= norm_val
        return new_state

    def apply_tessellation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = np.sort(state.vec)
        return new_state

    def apply_helicity(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = state.vec[::-1]
        return new_state

    def apply_enantiodromia(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = -state.vec
        return new_state

    def apply_exteriority(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = state.vec + 0.01
        norm_val = np.linalg.norm(new_state.vec)
        if norm_val != 0:
            new_state.vec /= norm_val
        return new_state

    def apply_solution(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(state.vec) > 1:
            fwd = np.roll(state.vec, 1)
            bck = np.roll(state.vec, -1)
            averaged = (fwd + bck) / 2.0
            norm_val = np.linalg.norm(averaged)
            if norm_val != 0:
                new_state.vec = averaged / norm_val
        return new_state


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Polychronological Turing Machine v6")
    parser.add_argument("--state", required=True, help="Path to JSON file defining initial state")
    parser.add_argument("--output", default="pctm_output.json", help="Path to output JSON")
    parser.add_argument("--log", default="pctm_log.txt", help="Path to verbose log file")
    parser.add_argument("--max-steps", type=int, default=100)
    parser.add_argument("--oracle", default="iching.json", help="Path to I Ching hexagram file")
    parser.add_argument("--oracle-enabled", action="store_true", default=False)
    parser.add_argument("--oracle-threshold", type=float, default=0.3)
    parser.add_argument("--fallback", choices=["random_md", "identity", "most_stable", "oracle"], default="random_md")
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("--weights", type=str, default=None,
                        help="Path to JSON file with custom W matrix (10x13) or 'auto' for derived matrix")
    parser.add_argument("--law-mode", choices=["strict", "clamp", "project", "warn"], default="strict")
    parser.add_argument("--schema", default="pctm_schema.json", help="Path to input schema")
    parser.add_argument("--dry-run", action="store_true", help="Validate input + exit")
    parser.add_argument("--formulae", default=None, help="Path to consolidated canon JSON")
    parser.add_argument("--uc", default=None, help="Path to UC canon JSON")
    parser.add_argument("--md", default=None, help="Path to MD canon JSON")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    with open(args.state, "r", encoding="utf-8") as f:
        state_data = json.load(f)

    engine = PCTMEngine(
        uc_path=args.uc,
        md_path=args.md,
        formulae_path=args.formulae,
        oracle_enabled=args.oracle_enabled,
        oracle_path=args.oracle,
        oracle_threshold=args.oracle_threshold,
        fallback_policy=args.fallback,
        verbose=args.verbose,
        law_mode=args.law_mode,
        weights_path=args.weights,
        schema_path=args.schema,
    )

    if "oracle_enabled" in state_data:
        engine.oracle_enabled = bool(state_data["oracle_enabled"])
    if "oracle_threshold" in state_data:
        engine.oracle_threshold = float(state_data["oracle_threshold"])
    if "fallback_policy" in state_data:
        engine.fallback_policy = str(state_data["fallback_policy"])

    valid, errors = engine._validate_json_schema(state_data, args.schema)
    if not valid:
        print(f"❌ INPUT INVALID: {'; '.join(errors)}")
        sys.exit(1)

    if args.dry_run:
        print("✅ Input schema validation PASSED")
        print(f"  Vector shape: {len(state_data['vector'])}D")
        print(f"  Tape: {state_data.get('tape_id', 0)}")
        print(f"  Order: {state_data.get('order', 'Material')}")
        sys.exit(0)

    initial_state = DimensionalState.from_dict(state_data, engine)

    result = engine.run_until_cycle(initial_state, max_steps=args.max_steps)

    output_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "initial_state_file": args.state,
            "max_steps": args.max_steps,
            "cycle_found": result["cycle_found"],
            "cycle_start": result["cycle_start"],
            "cycle_length": result["cycle_length"],
            "total_steps": result["total_steps"],
            "orders_tested": len(ORDERS),
        },
        "initial_state": initial_state.to_dict(),
        "final_state": result["final_state"].to_dict(),
        "summary": {
            "total_descriptors": len(result["history"]["descriptors"]),
            "descriptors_by_order": {},
            "oracle_invocations": len(result["history"]["oracle_invocations"]),
            "mv_success_rate": (
                sum(sum(r["mv"] for r in step_results.values())
                    for step_results in result["history"]["mv_results"])
                / (len(result["history"]["mv_results"]) * len(ORDERS))
                if result["history"]["mv_results"]
                else 0.0
            ),
        },
        "history": {
            "steps": result["total_steps"],
            "descriptors": [d.to_dict() for d in result["history"]["descriptors"]],
            "oracle_invocations": result["history"]["oracle_invocations"],
            "mv_results": result["history"]["mv_results"],
            "final_tape_register": {
                f"tape_{i}": [s.to_dict() for s in result["history"]["states"] if s.tape == i]
                for i in range(10)
            },
        },
    }

    for desc in result["history"]["descriptors"]:
        order = desc.order
        if order not in output_data["summary"]["descriptors_by_order"]:
            output_data["summary"]["descriptors_by_order"][order] = []
        output_data["summary"]["descriptors_by_order"][order].append(desc.to_dict())

    w_stats = {
        "shape": list(engine.W.shape),
        "min": float(engine.W.min()),
        "max": float(engine.W.max()),
        "mean": float(engine.W.mean()),
        "std": float(engine.W.std()),
        "sparsity": float((engine.W == 0).sum() / engine.W.size),
        "top_couplings": [
            {
                "md": engine.modal_dynamics[i].name,
                "uc": engine.universal_characteristics[j].name,
                "weight": float(engine.W[i, j]),
            }
            for i in range(10)
            for j in range(13)
            if engine.W[i, j] > engine.W.mean() + engine.W.std()
        ],
    }
    output_data["weights"] = w_stats

    output_data["tape_enforcement"] = {
        "mode": engine.law_mode,
        "available_tapes": list(engine.tape_laws.keys()),
        "violations_corrected": sum(result["history"]["tape_enforcement"]),
    }

    output_data["oracle_config"] = {
        "enabled": engine.oracle_enabled,
        "threshold": engine.oracle_threshold,
        "fallback_policy": engine.fallback_policy,
        "invocations": len(result["history"]["oracle_invocations"]),
        "hexagrams_used": [r["hexagram_number"] for r in result["history"]["oracle_invocations"]],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"✓ Output JSON written: {args.output}")

    with open(args.log, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLYCHRONOLOGICAL TURING MACHINE - COMPLETE EXECUTION LOG\n")
        f.write("=" * 80 + "\n\n")

        for entry in engine.log_entries:
            f.write(f"[{entry['timestamp']}] {entry['level']}: {entry['message']}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("EXECUTION SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total steps: {result['total_steps']}\n")
        f.write(f"Cycle detected: {result['cycle_found']}\n")
        if result["cycle_found"]:
            f.write(f"Cycle start: step {result['cycle_start']}\n")
            f.write(f"Cycle length: {result['cycle_length']}\n")
        f.write(f"Total Predictive Descriptors: {len(result['history']['descriptors'])}\n")
        f.write(f"Oracle invocations: {len(result['history']['oracle_invocations'])}\n")
        f.write(f"MV success rate: {output_data['summary']['mv_success_rate']:.3f}\n")

    print(f"✓ Verbose log written: {args.log}")
    print("\nSUMMARY:")
    print(f"  Steps: {result['total_steps']}")
    print(f"  Descriptors generated: {len(result['history']['descriptors'])}")
    print(f"  Oracle calls: {len(result['history']['oracle_invocations'])}")
    print(f"  MV success rate: {output_data['summary']['mv_success_rate']:.3f}")


if __name__ == "__main__":
    main()
