import math
import numpy as np
import json
from typing import List, Dict, Tuple, Optional, Callable

# Physical constants
KB = 1.380649e-23       # Boltzmann constant
C = 299792458           # Speed of light (m/s)
G = 6.67430e-11         # Gravitational constant (m^3/kg s^2)
HBAR = 1.054571817e-34  # Reduced Planck constant (J·s)
PHI = 1.61803398875     # Golden ratio (for scaling dynamics)

# Orders of Reality represented in the system
ORDERS_OF_REALITY = [
    "VIRTUAL",
    "QUANTUM",
    "MATERIAL",
    "ETHEREAL",
    "ASTRAL",
    "CELESTIAL",
    "EXISTENTIAL",
]

# Total number of reality orders
NUM_ORDERS = len(ORDERS_OF_REALITY)

# Mapping of modal dynamics to order transitions. A positive value
# moves to a higher order, a negative value to a lower order.
mode_transition_map = {
    "Oscillation": 0,
    "Folding": 1,
    "Radiation": 1,
    "Propagation": 0,
    "Arborescence": 1,
    "Tessellation": 0,
    "Helicity": 0,
    "Enantiodromia": -1,
    "Exteriority": -1,
    "Solution": 0,
    "ORACLE_ADJUST": 0,
}

class DimensionalState:
    """State with a vector and associated parameters (order, frequency, scale)."""
    def __init__(self, vec: np.ndarray, order: int = 0, freq: float = 1.0, rho: float = 1.0):
        self.vec = vec / np.linalg.norm(vec) if np.linalg.norm(vec) != 0 else np.copy(vec)
        self.order = order
        self.freq = freq
        self.rho = rho
    def copy(self) -> 'DimensionalState':
        return DimensionalState(self.vec.copy(), self.order, self.freq, self.rho)
    def __repr__(self) -> str:
        return f"DimensionalState(dim={len(self.vec)}, order={self.order}, freq={self.freq}, rho={self.rho})"

class UniversalCharacteristic:
    """A universal characteristic (UC) with its calculation function."""
    def __init__(self, name: str, symbol: str, equation: str, domain: str, type_: str,
                 func: Callable[['DimensionalState'], float]):
        self.name = name
        self.symbol = symbol
        self.equation = equation
        self.domain = domain
        self.type = type_
        self.func = func
    def calculate(self, state: DimensionalState) -> float:
        return self.func(state)
    def __repr__(self) -> str:
        return f"{self.name} ({self.symbol}): {self.equation}"

class ModalDynamic:
    """A modal dynamic (MD) with its transformation function."""
    def __init__(self, name: str, symbol: str, operation: str, description: str, type_: str,
                 func: Callable[['DimensionalState'], 'DimensionalState']):
        self.name = name
        self.symbol = symbol
        self.operation = operation
        self.description = description
        self.type = type_
        self.func = func
    def apply(self, state: DimensionalState) -> DimensionalState:
        return self.func(state)
    def __repr__(self) -> str:
        return f"{self.name} ({self.symbol}): {self.operation}"

class CanonLoader:
    """Loads canonical definitions from JSON files."""
    @staticmethod
    def load_uc_canon(filepath: str) -> List[Dict]:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data.get("UniversalCharacteristics", [])
    @staticmethod
    def load_md_canon(filepath: str) -> List[Dict]:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data.get("ModalDynamics", [])
    @staticmethod
    def load_consolidated_canon(filepath: str) -> List[Dict]:
        with open(filepath, 'r') as f:
            return json.load(f)
    @staticmethod
    def load_extracted_formulae(filepath: str) -> List[Dict]:
        with open(filepath, 'r') as f:
            data = json.load(f)
        for item in data:
            if "ExtractedFormulae" in item:
                return item["ExtractedFormulae"]
        return []

class FormulaicOperator:
    """Applies formulaic operations from the canon (risk analysis, duality, etc.)."""
    def __init__(self, formulae_data: List[Dict]):
        self.formulae = { (f.get('Category') or f.get('title') or str(i)): f
                          for i,f in enumerate(formulae_data) }
    def calculate_existential_risk(self, hazards: np.ndarray, theta: np.ndarray, M: np.ndarray) -> float:
        z = theta.dot(hazards) + hazards.dot(M.dot(hazards))
        return 1.0 / (1.0 + math.exp(-z))
    def gradient_existential_risk(self, hazards: np.ndarray, theta: np.ndarray, M: np.ndarray) -> np.ndarray:
        z = theta.dot(hazards) + hazards.dot(M.dot(hazards))
        s = math.exp(-z) / ((1 + math.exp(-z))**2)
        return s * (theta + 2 * M.dot(hazards))
    def apply_meta_ontological_duality(self, material: np.ndarray, immaterial: np.ndarray,
                                       interaction: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        mat_inf = interaction.dot(immaterial)
        imm_inf = interaction.T.dot(material)
        new_material = material + 0.1 * mat_inf
        new_immaterial = immaterial + 0.1 * imm_inf
        if np.linalg.norm(new_material) != 0:
            new_material /= np.linalg.norm(new_material)
        if np.linalg.norm(new_immaterial) != 0:
            new_immaterial /= np.linalg.norm(new_immaterial)
        return new_material, new_immaterial

class PCTMEngine:
    """Core engine for the Process-Centric Topological Machine."""
    def __init__(self, uc_path: Optional[str] = None, md_path: Optional[str] = None, formulae_path: Optional[str] = None):
        # Load definitions from provided canon or default to built-in
        if formulae_path:
            canon = CanonLoader.load_consolidated_canon(formulae_path)
            uc_data = next((item["UniversalCharacteristics"] for item in canon
                            if "UniversalCharacteristics" in item), [])
            md_data = next((item["ModalDynamics"] for item in canon
                            if "ModalDynamics" in item), [])
            extracted = CanonLoader.load_extracted_formulae(formulae_path)
            self.formulaic_operator = FormulaicOperator(extracted)
        else:
            if not uc_path and not md_path:
                # Use default built-in UCs and MDs
                uc_data = [
                    {"name": "Uncertainty",       "symbol": "U1",  "equation": "H(p) = -∑ pᵢ log(pᵢ)",
                     "domain": "pᵢ = xᵢ², ∑ pᵢ = 1",      "type": "Entropy"},
                    {"name": "Simplicity",        "symbol": "U2",  "equation": "",
                     "domain": "ρ ∈ ℝ⁺",                 "type": "Logarithmic Coherence"},
                    {"name": "Uniqueness",        "symbol": "U3",  "equation": "",
                     "domain": "pᵢ = xᵢ²",               "type": "Anti-Dominance"},
                    {"name": "Continuity",        "symbol": "U4",  "equation": "",
                     "domain": "x ∈ ℝⁿ",                 "type": "Averaged Value"},
                    {"name": "Self_Similarity",   "symbol": "U5",  "equation": "",
                     "domain": "x ∈ ℝⁿ",                 "type": "Standard Deviation"},
                    {"name": "Interconnectivity", "symbol": "U6",  "equation": "",
                     "domain": "x reversed dot product", "type": "Mirror Coupling"},
                    {"name": "Holography",        "symbol": "U7",  "equation": "",
                     "domain": "A = surface area",       "type": "Entropic Bound"},
                    {"name": "Solidity",          "symbol": "U8",  "equation": "",
                     "domain": "x ∈ ℝⁿ",                 "type": "Vector Magnitude"},
                    {"name": "Paradox",           "symbol": "U9",  "equation": "",
                     "domain": "x ∈ ℝⁿ",                 "type": "Deviation from Unity"},
                    {"name": "Flux",              "symbol": "U10", "equation": "",
                     "domain": "Δx ∈ ℝⁿ⁻¹",             "type": "Finite Variation"}
                ]
                md_data = [
                    {"name": "Oscillation",   "symbol": "M1",  "operation": "Rotate+Blend",      "description": "Cyclic permutation of state",    "type": "Harmonic Recursion"},
                    {"name": "Folding",       "symbol": "M2",  "operation": "Absolute Inversion","description": "Fold and invert state",          "type": "Involutive Reversal"},
                    {"name": "Radiation",     "symbol": "M3",  "operation": "Add Noise",         "description": "Inject stochastic perturbation", "type": "Stochastic Divergence"},
                    {"name": "Propagation",   "symbol": "M4",  "operation": "Shift Vector",      "description": "Translate state cyclically",     "type": "Temporal Drift"},
                    {"name": "Arborescence",  "symbol": "M5",  "operation": "Square Components", "description": "Nonlinear branching amplification","type": "Exponential Branching"},
                    {"name": "Tessellation",  "symbol": "M6",  "operation": "Sort Values",       "description": "Impose structural order",        "type": "Structural Reordering"},
                    {"name": "Helicity",      "symbol": "M7",  "operation": "Reverse Vector",    "description": "Reflect state vector",           "type": "Inversion Symmetry"},
                    {"name": "Enantiodromia", "symbol": "M8",  "operation": "Negate Vector",     "description": "Invert sign of all components",  "type": "Dialectical Opposition"},
                    {"name": "Exteriority",   "symbol": "M9",  "operation": "Radiate Outward",   "description": "Emanate outward uniformly",      "type": "Emanation"},
                    {"name": "Solution",      "symbol": "M10", "operation": "Neighbor Average",  "description": "Smooth via local averaging",     "type": "Continuity Enforcement"}
                ]
                self.formulaic_operator = None
            else:
                if not uc_path or not md_path:
                    raise ValueError("Both uc_path and md_path must be provided if formulae_path is None.")
                uc_data = CanonLoader.load_uc_canon(uc_path)
                md_data = CanonLoader.load_md_canon(md_path)
                self.formulaic_operator = None
        # Initialize Universal Characteristics (UCs)
        self.universal_characteristics: List[UniversalCharacteristic] = []
        for uc in uc_data:
            func = getattr(self, f"calc_{uc['name'].lower()}", lambda s: 0.0)
            self.universal_characteristics.append(
                UniversalCharacteristic(uc['name'], uc.get('symbol',''), uc.get('equation',''),
                                         uc.get('domain',''), uc.get('type',''), func)
            )
        # Initialize Modal Dynamics (MDs)
        self.modal_dynamics: List[ModalDynamic] = []
        for md in md_data:
            func = getattr(self, f"apply_{md['name'].lower()}", lambda s: s)
            self.modal_dynamics.append(
                ModalDynamic(md['name'], md.get('symbol',''), md.get('operation',''),
                             md.get('description',''), md.get('type',''), func)
            )
        # Derive weight matrix W and bias b for mode activation coupling
        n_uc = len(self.universal_characteristics)
        n_md = len(self.modal_dynamics)
        rng = np.random.RandomState(42)
        self.W = np.zeros((n_md, n_uc))
        for i in range(n_md):
            if n_uc > 0:
                # link each MD to 3 random UCs with small weights
                idx_choices = rng.choice(n_uc, size=min(3, n_uc), replace=False)
                for uc_idx in idx_choices:
                    self.W[i, uc_idx] = float(rng.randint(1, 4))
        self.b = np.zeros(n_md)
        # History tracking
        self.history: Dict[str, list] = {'states': [], 'uc_values': [], 'activations': [], 'triggered_modes': []}
    # Universal Characteristic calculations (valence measures)
    def calc_uncertainty(self, state: DimensionalState) -> float:
        p = state.vec**2
        if p.sum() != 0:
            p = p / p.sum()
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
        area = 1e-4 * (state.rho ** 2)
        return float(KB * C**3 * area / (4 * G * HBAR))
    def calc_solidity(self, state: DimensionalState) -> float:
        return float(np.linalg.norm(state.vec))
    def calc_paradox(self, state: DimensionalState) -> float:
        return float(abs(1.0 - np.linalg.norm(state.vec)**2))
    def calc_flux(self, state: DimensionalState) -> float:
        return float(np.linalg.norm(np.diff(state.vec))) if len(state.vec) >= 2 else 0.0
    # Modal Dynamic transformations
    def apply_oscillation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(state.vec) > 0:
            r = np.roll(state.vec, 1)
            new_state.vec = (state.vec + r) / np.linalg.norm(state.vec + r)
        return new_state
    def apply_folding(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = -np.abs(state.vec)
        new_state.rho *= PHI
        if np.linalg.norm(new_state.vec) != 0:
            new_state.vec /= np.linalg.norm(new_state.vec)
        return new_state
    def apply_radiation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        noise = np.random.normal(0, 0.01, size=state.vec.shape)
        new_state.vec = state.vec + noise
        if np.linalg.norm(new_state.vec) != 0:
            new_state.vec /= np.linalg.norm(new_state.vec)
        return new_state
    def apply_propagation(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(state.vec) > 0:
            new_state.vec = np.roll(state.vec, 1)
        new_state.rho /= PHI
        return new_state
    def apply_arborescence(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        new_state.vec = state.vec ** 2
        if np.linalg.norm(new_state.vec) != 0:
            new_state.vec /= np.linalg.norm(new_state.vec)
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
        if np.linalg.norm(new_state.vec) != 0:
            new_state.vec /= np.linalg.norm(new_state.vec)
        return new_state
    def apply_solution(self, state: DimensionalState) -> DimensionalState:
        new_state = state.copy()
        if len(state.vec) > 1:
            fwd = np.roll(state.vec, 1)
            bck = np.roll(state.vec, -1)
            new_state.vec = (fwd + bck) / 2.0
            if np.linalg.norm(new_state.vec) != 0:
                new_state.vec /= np.linalg.norm(new_state.vec)
        return new_state
    # Utility methods for computing UC vector and MD activations
    def calculate_uc_vector(self, state: DimensionalState) -> np.ndarray:
        return np.array([uc.calculate(state) for uc in self.universal_characteristics], float)
    def calculate_activations(self, uc_values: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-(self.W.dot(uc_values) + self.b)))
    def get_triggered_modes(self, activations: np.ndarray, threshold: float = 0.5) -> List[str]:
        return [md.name for md, act in zip(self.modal_dynamics, activations) if act > threshold]
    # Perform one simulation step
    def step(self, state: DimensionalState) -> Tuple[List[str], DimensionalState]:
        uc_vals = self.calculate_uc_vector(state)
        activations = self.calculate_activations(uc_vals)
        modes = self.get_triggered_modes(activations)
        # Oracle intervention if no mode triggers (halts)
        if len(modes) == 0 and self.formulaic_operator:
            vec = state.vec
            if len(vec) >= 2:
                half = len(vec) // 2
                mat = vec[:half].copy()
                imm = vec[half:].copy()
                if len(mat) != len(imm):
                    k = min(len(mat), len(imm))
                    mat = mat[:k]; imm = imm[:k]
                if np.linalg.norm(mat) != 0:
                    mat /= np.linalg.norm(mat)
                if np.linalg.norm(imm) != 0:
                    imm /= np.linalg.norm(imm)
                interaction = np.eye(len(mat)) * 0.5
                new_mat, new_imm = self.formulaic_operator.apply_meta_ontological_duality(mat, imm, interaction)
                new_vec = np.concatenate([new_mat, new_imm])
                new_state = DimensionalState(new_vec, state.order, state.freq, state.rho)
                modes = ["ORACLE_ADJUST"]
            else:
                new_state = state.copy()
        else:
            new_state = state.copy()
            for mode_name in modes:
                for md in self.modal_dynamics:
                    if md.name.lower() == mode_name.lower():
                        new_state = md.apply(new_state)
                        if np.linalg.norm(new_state.vec) != 0:
                            new_state.vec /= np.linalg.norm(new_state.vec)
                        break
                delta = mode_transition_map.get(mode_name, 0)
                new_state.order = (state.order + delta) % NUM_ORDERS

        # Log history
        self.history['states'].append(state.copy())
        self.history['uc_values'].append(uc_vals)
        self.history['activations'].append(activations)
        self.history['triggered_modes'].append(modes)
        return modes, new_state

class PCTMAnalyzer:
    """Analyzes PCTM behavior and trajectories."""
    def __init__(self, engine: PCTMEngine):
        self.engine = engine
    def run_simulation(self, initial_state: DimensionalState, steps: int) -> Dict[str, List]:
        state = initial_state.copy()
        states = [state.copy()]
        uc_trajectory: List[np.ndarray] = []
        mode_sequence: List[List[str]] = []
        for _ in range(steps):
            uc_vals = self.engine.calculate_uc_vector(state)
            activations = self.engine.calculate_activations(uc_vals)
            modes, state = self.engine.step(state)
            uc_trajectory.append(uc_vals)
            mode_sequence.append(modes)
            states.append(state.copy())
        return {"states": states, "uc_values": uc_trajectory, "modes": mode_sequence}

# Example usage: run a short simulation and print state vector and valence profiles
if __name__ == "__main__":
    engine = PCTMEngine(uc_path=None, md_path=None, formulae_path=None)
    init_vector = np.random.RandomState(0).rand(10)
    state = DimensionalState(init_vector, order=0, freq=1.0, rho=1.0)
    print(f"Initial State 0: vector={np.round(state.vec,4).tolist()}, valence={np.round(engine.calculate_uc_vector(state),4).tolist()}")
    for t in range(1, 6):
        triggered, new_state = engine.step(state)
        activations = engine.history['activations'][-1]
        print(f"Transition {t-1}->{t}: triggered_modes={triggered}, activation_vals={np.round(activations,4).tolist()}")
        uc_vals = engine.history['uc_values'][-1]
        print(f"State {t}: vector={np.round(new_state.vec,4).tolist()}, valence={np.round(uc_vals,4).tolist()}")
        state = new_state
