import numpy as np
import random
import math
from typing import List, Dict, Tuple, Optional, Any

# Global constants and parameters
PHI = (1.0 + 5**0.5) / 2.0  # Golden ratio (~1.618)
# Constants for Holography UC calculation
KB = 1.38e-23   # Boltzmann constant
C = 3.0e8      # Speed of light
G = 6.67e-11   # Gravitational constant
HBAR = 1.05e-34  # Planck's reduced constant

class DimensionalState:
    """Represents the state on a tape, including state vector, magnitude (rho), and tape identifier."""
    def __init__(self, vec: np.ndarray, rho: float = 1.0, tape_id: int = 0):
        self.vec = np.array(vec, dtype=float)
        self.rho = float(rho)
        self.tape = tape_id  # identifies which tape (dimension) this state belongs to

    def copy(self) -> 'DimensionalState':
        """Create a copy of this state (with a separate copy of the vector)."""
        return DimensionalState(self.vec.copy(), self.rho, self.tape)

class UniversalCharacteristic:
    """Encapsulates a Universal Characteristic definition and its calculation function."""
    def __init__(self, name: str, symbol: str, equation: str, domain: str, uc_type: str, func):
        self.name = name
        self.symbol = symbol
        self.equation = equation
        self.domain = domain
        self.type = uc_type
        # `func` is a function that calculates this characteristic given a state
        self.calculate = func

class ModalDynamic:
    """Encapsulates a Modal Dynamic definition and its state-transform function."""
    def __init__(self, name: str, symbol: str, operation: str, description: str, md_type: str, func):
        self.name = name
        self.symbol = symbol
        self.operation = operation
        self.description = description
        self.type = md_type
        # `func` is a function that applies this dynamic to a state and returns a new state
        self.apply = func

class IChingOracle:
    """
    Oracle for casting I Ching hexagrams to guide transitions.
    Provides a cast() method that returns a random hexagram result.
    """
    def __init__(self, hexagram_file: str = "iching.json"):
        try:
            import json
            with open(hexagram_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.hexagrams = data.get("hexagrams", [])
        except Exception:
            # If file not found or parse fails, proceed with only casting lines and hex number
            self.hexagrams = []

    def fifty_stick_cast(self) -> List[int]:
        """Perform a six-line cast using the traditional yarrow-stalk probabilities. Returns a list of 6 lines."""
        # Possible line values: 6 = old yin, 7 = young yang, 8 = young yin, 9 = old yang
        choices = [6, 7, 8, 9]
        weights = [1, 5, 7, 3]  # relative frequencies of each line type
        def cast_line():
            return random.choices(choices, weights=weights, k=1)[0]
        return [cast_line() for _ in range(6)]

    def lines_to_hexagram_number(self, lines: List[int]) -> int:
        """Convert 6 cast lines to a hexagram number (1-64). Yang (odd) -> 1, Yin (even) -> 0 in binary (bottom line is LSB)."""
        binary_str = ''.join(['1' if line % 2 == 1 else '0' for line in reversed(lines)])
        return int(binary_str, 2) + 1

    def cast(self) -> Dict[str, Any]:
        """
        Perform a full oracle cast: returns a dict with cast lines, resulting hexagram number,
        and if available, the corresponding hexagram data (name, commentary, etc.).
        """
        lines = self.fifty_stick_cast()
        hex_num = self.lines_to_hexagram_number(lines)
        hex_info = None
        for h in self.hexagrams:
            if h.get("hexagram_number") == hex_num:
                hex_info = h
                break
        return {"cast_lines": lines, "hexagram_number": hex_num, "hexagram": hex_info}

class PCTMEngine:
    """
    Core engine for the Polychronological Turing Machine.
    Manages Universal Characteristics, Modal Dynamics, and the logic for state transitions across tapes.
    """
    def __init__(self, uc_path: Optional[str] = None, md_path: Optional[str] = None, formulae_path: Optional[str] = None):
        """
        Initialize the PCTM Engine with canonical definitions.
        - If a consolidated formulaic canon JSON is provided, load UCs and MDs from it.
        - Otherwise, load separate UC and MD JSON definitions from given file paths.
        """
        # Load canonical definitions for UCs and MDs
        if formulae_path:
            import json
            with open(formulae_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            json_text = raw_text.strip()
            if json_text.startswith("{["):
                # Remove wrapping braces if present around the list
                start_idx = json_text.find('[')
                end_idx = json_text.rfind(']')
                if start_idx != -1 and end_idx != -1:
                    json_text = json_text[start_idx:end_idx+1]
                    # Remove any trailing brace after the closing bracket
                    trailing = raw_text[end_idx+1:].strip()
                    if trailing.startswith('}'):
                        json_text = json_text.strip()
            canon = json.loads(json_text)
            # Expect canon to be a list of sections (dicts) for UCs, MDs, etc.
            uc_data = []
            md_data = []
            for section in canon:
                if isinstance(section, dict):
                    if "UniversalCharacteristics" in section:
                        uc_data = section["UniversalCharacteristics"]
                    if "ModalDynamics" in section:
                        md_data = section["ModalDynamics"]
            # Set formulaic operator if needed (not utilized in core transitions here)
            self.formulaic_operator = None
        else:
            if not uc_path or not md_path:
                raise ValueError("Must provide either formulae_path or both uc_path and md_path for UC/MD definitions.")
            import json
            with open(uc_path, 'r', encoding='utf-8') as f:
                uc_data = json.load(f)
            with open(md_path, 'r', encoding='utf-8') as f:
                md_data = json.load(f)
            self.formulaic_operator = None

        # Initialize Universal Characteristic objects using corresponding calculation methods
        self.universal_characteristics: List[UniversalCharacteristic] = []
        for uc in uc_data:
            name = uc.get('name')
            calc_func = getattr(self, f"calc_{name.lower()}", None)
            if calc_func is None:
                calc_func = lambda s: 0.0  # default no-op if not defined
            uc_obj = UniversalCharacteristic(name, uc.get('symbol', ''), uc.get('equation', ''),
                                            uc.get('domain', ''), uc.get('type', ''), calc_func)
            self.universal_characteristics.append(uc_obj)

        # Initialize Modal Dynamic objects using corresponding state-transform methods
        self.modal_dynamics: List[ModalDynamic] = []
        for md in md_data:
            name = md.get('name')
            apply_func = getattr(self, f"apply_{name.lower()}", None)
            if apply_func is None:
                apply_func = lambda state: state.copy()
            md_obj = ModalDynamic(name, md.get('symbol', ''), md.get('operation', ''),
                                   md.get('description', ''), md.get('type', ''), apply_func)
            self.modal_dynamics.append(md_obj)

        # Initialize canonical valence weight matrix and bias for UC->MD mapping (activation heuristics)
        # Rows correspond to Modal Dynamics, columns correspond to UCs.
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
        ], dtype=float)  # This matrix can be tuned or derived from equation-based behavior
        self.b = np.zeros(len(self.modal_dynamics))

        # Oracle (for optional override in transitions) will be initialized on first use
        self.oracle: Optional[IChingOracle] = None

        # History tracking for analysis (populated during simulation)
        self.history: Dict[str, List] = {'states': [], 'uc_values': [], 'activations': [], 'triggered_modes': []}

    def init_oracle(self, hexagram_file: str = "iching.json"):
        """Initialize the I Ching oracle with the given hexagram definitions file."""
        self.oracle = IChingOracle(hexagram_file)

    # --- Universal Characteristic (UC) calculation methods (U1 through U13) ---
    def calc_uncertainty(self, state: DimensionalState) -> float:
        """U1: Uncertainty – Entropy of the normalized squared vector (p_i = x_i^2)."""
        p = state.vec**2
        total = p.sum()
        if total == 0:
            return 0.0
        p = p / total
        entropy = -np.sum(np.where(p > 0, p * np.log(p), 0.0))
        return float(entropy)

    def calc_simplicity(self, state: DimensionalState) -> float:
        """U2: Simplicity – log(ρ / ρ0), with ρ0 = 1.0 (reference magnitude)."""
        if state.rho <= 0:
            return float('inf')  # undefined if rho <= 0, treat as infinitely complex
        return math.log(state.rho / 1.0)

    def calc_uniqueness(self, state: DimensionalState) -> float:
        """U3: Uniqueness – 1 - max(p_i), where p_i = x_i^2 (measure of dominance of the largest component)."""
        if state.vec.size == 0:
            return 0.0
        p = state.vec**2
        return float(1.0 - np.max(p))

    def calc_continuity(self, state: DimensionalState) -> float:
        """U4: Continuity – mean(x_i), the average value of components (coarse continuity of state)."""
        if state.vec.size == 0:
            return 0.0
        return float(np.mean(state.vec))

    def calc_self_similarity(self, state: DimensionalState) -> float:
        """U5: Self-Similarity – standard deviation of components (how much the state varies internally)."""
        if state.vec.size == 0:
            return 0.0
        return float(np.std(state.vec))

    def calc_interconnectivity(self, state: DimensionalState) -> float:
        """U6: Interconnectivity – mean of elementwise product of vector with its reverse (palindromic coupling)."""
        n = state.vec.size
        if n == 0:
            return 0.0
        rev = state.vec[::-1]
        return float(np.mean(state.vec * rev))

    def calc_holography(self, state: DimensionalState) -> float:
        """U7: Holography – (k * c^3 * A) / (4 * G * ħ), an entropic bound (using a fixed small area A)."""
        A = 1e-4  # example surface area
        H_val = KB * (C**3) * A / (4 * G * HBAR)
        return float(H_val)

    def calc_solidity(self, state: DimensionalState) -> float:
        """U8: Solidity – Euclidean norm of the state vector (||x||)."""
        return float(np.linalg.norm(state.vec))

    def calc_paradox(self, state: DimensionalState) -> float:
        """U9: Paradox – |1 - ||x||^2|, deviation of the vector's squared norm from unity (measure of paradoxical inconsistency)."""
        norm_sq = np.linalg.norm(state.vec)**2
        return float(abs(1.0 - norm_sq))

    def calc_flux(self, state: DimensionalState) -> float:
        """U10: Flux – Norm of successive differences (||Δx||)."""
        if state.vec.size <= 1:
            return 0.0
        delta_x = np.diff(state.vec)
        return float(np.linalg.norm(delta_x))

    def calc_contiguity(self, state: DimensionalState) -> float:
        """U11: Contiguity – Count of adjacent differences below a small threshold (local smoothness)."""
        if state.vec.size <= 1:
            return 0.0
        diffs = np.abs(np.diff(state.vec))
        return float(np.sum(diffs < 0.1))

    def calc_complementarity(self, state: DimensionalState) -> float:
        """U12: Complementarity – ∑ x_i * (1 - x_i), assuming components normalized in [0,1] range (measures internal complementary parts)."""
        x_clamped = np.clip(state.vec, 0.0, 1.0)
        return float(np.sum(x_clamped * (1.0 - x_clamped)))

    def calc_incompleteness(self, state: DimensionalState) -> float:
        """U13: Incompleteness – 1 - 1/||x||, for ||x|| > 0 (indicates how far the state is from being fully 'complete')."""
        norm_val = np.linalg.norm(state.vec)
        if norm_val == 0:
            return float('inf')
        return float(1.0 - 1.0/norm_val)

    # --- Modal Dynamic (MD) transformation methods (M1 through M10) ---
    def apply_oscillation(self, state: DimensionalState) -> DimensionalState:
        """M1: Oscillation – Cyclic blending with a one-position roll (feedback resonance)."""
        new_state = state.copy()
        if new_state.vec.size > 0:
            rolled = np.roll(new_state.vec, 1)
            new_state.vec = new_state.vec + rolled
            # Normalize the resulting vector
            norm = np.linalg.norm(new_state.vec)
            if norm != 0:
                new_state.vec /= norm
        return new_state

    def apply_folding(self, state: DimensionalState) -> DimensionalState:
        """M2: Folding – Invert to negative absolute values (self-negation) and multiply rho by φ (densification)."""
        new_state = state.copy()
        new_state.vec = -np.abs(new_state.vec)
        new_state.rho *= PHI
        return new_state

    def apply_radiation(self, state: DimensionalState) -> DimensionalState:
        """M3: Radiation – Add small Gaussian noise to the vector (outward diffusion) and renormalize."""
        new_state = state.copy()
        if new_state.vec.size > 0:
            noise = np.random.normal(0, 0.1, size=new_state.vec.shape)
            new_state.vec += noise
            norm = np.linalg.norm(new_state.vec)
            if norm != 0:
                new_state.vec /= norm
        return new_state

    def apply_propagation(self, state: DimensionalState) -> DimensionalState:
        """M4: Propagation – Rotate (roll) the vector elements forward and divide rho by φ (dilative propagation)."""
        new_state = state.copy()
        if new_state.vec.size > 0:
            new_state.vec = np.roll(new_state.vec, 1)
        new_state.rho /= PHI
        return new_state

    def apply_arborescence(self, state: DimensionalState) -> DimensionalState:
        """M5: Arborescence – Square each component (branching expansion) and renormalize the vector."""
        new_state = state.copy()
        new_state.vec = new_state.vec ** 2
        norm = np.linalg.norm(new_state.vec)
        if norm != 0:
            new_state.vec /= norm
        return new_state

    def apply_tessellation(self, state: DimensionalState) -> DimensionalState:
        """M6: Tessellation – Sort components (introduce structural regularity)."""
        new_state = state.copy()
        new_state.vec = np.sort(new_state.vec)
        return new_state

    def apply_helicity(self, state: DimensionalState) -> DimensionalState:
        """M7: Helicity – Reverse the component order (mirror image of state)."""
        new_state = state.copy()
        new_state.vec = new_state.vec[::-1]
        return new_state

    def apply_enantiodromia(self, state: DimensionalState) -> DimensionalState:
        """M8: Enantiodromia – Flip the sign of all components (total polarity inversion)."""
        new_state = state.copy()
        new_state.vec = -new_state.vec
        return new_state

    def apply_exteriority(self, state: DimensionalState) -> DimensionalState:
        """M9: Exteriority – Push state outward by a small uniform increment and renormalize (expanding outward)."""
        new_state = state.copy()
        if new_state.vec.size > 0:
            eps = 0.01
            new_state.vec = new_state.vec + eps
            norm = np.linalg.norm(new_state.vec)
            if norm != 0:
                new_state.vec /= norm
        return new_state

    def apply_solution(self, state: DimensionalState) -> DimensionalState:
        """M10: Solution – Smooth state by averaging each element with its neighbors (circularly) and renormalize."""
        new_state = state.copy()
        n = new_state.vec.size
        if n > 0:
            rolled_fwd = np.roll(new_state.vec, 1)
            rolled_bwd = np.roll(new_state.vec, -1)
            new_state.vec = (rolled_fwd + rolled_bwd) / 2.0
            norm = np.linalg.norm(new_state.vec)
            if norm != 0:
                new_state.vec /= norm
        return new_state

    # --- Core PCTM functional methods ---
    def calculate_uc_vector(self, state: DimensionalState) -> np.ndarray:
        """Compute the vector of all Universal Characteristic values for the given state."""
        return np.array([uc.calculate(state) for uc in self.universal_characteristics], dtype=float)

    def calculate_activations(self, uc_values: np.ndarray) -> np.ndarray:
        """Compute activation levels for each Modal Dynamic using a sigmoid on weighted UC vector (valence gating)."""
        z = self.W.dot(uc_values) + self.b  # linear combination
        activations = 1.0 / (1.0 + np.exp(-z))  # logistic sigmoid
        return activations

    def get_triggered_modes(self, activations: np.ndarray, threshold: float = 0.5) -> List[str]:
        """Determine which Modal Dynamics are triggered (activations above the given threshold)."""
        triggered = []
        for i, md in enumerate(self.modal_dynamics):
            if i < len(activations) and activations[i] > threshold:
                triggered.append(md.name)
        return triggered

    def check_viability(self, state: DimensionalState, md_name: str) -> bool:
        """
        Check if applying the given Modal Dynamic on the current tape is allowed by that tape's dimensional law.
        (Encodes tape-specific constraints on transitions.)
        """
        tape = state.tape
        # Define ontological constraints per tape (example rules):
        if tape == 1:
            # Tape 1 (e.g., a constrained dimension where norm must remain ~1):
            # Disallow dynamics that significantly alter magnitude.
            if md_name.lower() in ["folding", "propagation"]:
                return False
        if tape == 2:
            # Tape 2 (e.g., a domain requiring non-negativity of state vector):
            if md_name.lower() in ["folding", "enantiodromia"]:
                return False
        # (Additional tape rules can be defined similarly for tape 3,4,... if needed)
        return True

    def oracle_cast(self) -> Dict[str, Any]:
        """
        Use the I Ching oracle to get a hexagram cast result.
        Initializes the oracle on first use. Returns a dictionary with oracle output.
        """
        if self.oracle is None:
            self.init_oracle()
        return self.oracle.cast()

    def step(self, state: DimensionalState, threshold: float = 0.5) -> Tuple[List[str], DimensionalState]:
        """
        Execute a single transition step from the given state.
        Returns (applied_mode_names, new_state) after applying one or more modal dynamics (possibly none or oracle-based).
        """
        # Compute UC values and MD activation levels for the current state
        uc_values = self.calculate_uc_vector(state)
        activations = self.calculate_activations(uc_values)
        triggered = self.get_triggered_modes(activations, threshold)
        new_state = state.copy()
        applied_modes: List[str] = []

        # Determine if we should invoke oracle override (no viable mode or paradox constraint)
        paradox_val = None
        # Check if Paradox UC exists and evaluate it
        for uc in self.universal_characteristics:
            if uc.name.lower() == "paradox":
                paradox_val = uc.calculate(state)
                break

        # Oracle override condition: if no mode triggers, or if a paradox value is high (indicating ontological paradox)
        if not triggered or (paradox_val is not None and paradox_val > 0.8):
            # Use the oracle to guide the transition
            oracle_result = self.oracle_cast()
            hex_num = oracle_result["hexagram_number"]
            # Choose a modal dynamic index based on the hexagram (e.g., mod by number of MDs)
            if len(self.modal_dynamics) > 0:
                md_index = (hex_num - 1) % len(self.modal_dynamics)  # hexagram_number is 1-indexed
            else:
                md_index = 0
            if 0 <= md_index < len(self.modal_dynamics):
                md = self.modal_dynamics[md_index]
                new_state = md.apply(new_state)  # apply the chosen MD unconditionally (oracle-driven)
                applied_modes.append(f"{md.name} (oracle)")
            else:
                # If no MD available, oracle yields no operation
                applied_modes.append("oracle_noop")
        else:
            # Filter triggered modes by viability on the current tape
            viable_modes = [m for m in triggered if self.check_viability(state, m)]
            if not viable_modes and triggered:
                # If some modes triggered but none are viable in this tape's dimension,
                # shift to a more permissive tape (e.g., tape 0 as base domain) and allow all triggered.
                new_state.tape = 0
                viable_modes = triggered.copy()
            # Apply each viable modal dynamic in sequence
            for mode_name in viable_modes:
                for md in self.modal_dynamics:
                    if md.name.lower() == mode_name.lower():
                        new_state = md.apply(new_state)
                        applied_modes.append(md.name)
                        break

        # After applying MDs, enforce tape-specific laws and possibly adjust tape assignment
        current_tape = new_state.tape
        # Example enforcement: If tape 1 (constant-norm domain) and norm deviated significantly, move to base tape 0
        if current_tape == 1:
            norm_val = np.linalg.norm(new_state.vec)
            if abs(norm_val - 1.0) > 1e-6:
                current_tape = 0
        # If tape 2 (non-negative domain) and state now has negative components, move to base tape 0
        if current_tape == 2:
            if np.any(new_state.vec < 0):
                current_tape = 0
        new_state.tape = current_tape

        # Record the transition in history
        self.history['states'].append(new_state.copy())
        self.history['uc_values'].append(uc_values)
        self.history['activations'].append(activations)
        self.history['triggered_modes'].append(applied_modes)
        return applied_modes, new_state

    def run_until_cycle(self, initial_state: DimensionalState, max_steps: int = 100, tolerance: float = 1e-6) -> Dict[str, Any]:
        """
        Run the PCTM from an initial state until a state repeats (cycle detected) or until max_steps reached.
        Returns a summary dictionary with cycle information and the history of the run.
        """
        # Reset history at start
        self.history = {'states': [], 'uc_values': [], 'activations': [], 'triggered_modes': []}
        state = initial_state.copy()
        self.history['states'].append(state.copy())
        seen_signatures = []  # track seen state signatures for cycle detection
        # Use rounded state vector and tape/rho for signature to account for tolerance
        def state_signature(st: DimensionalState):
            return (st.tape, tuple(np.round(st.vec, 6)), round(st.rho, 6))
        seen_signatures.append(state_signature(state))
        cycle_found = False
        cycle_start = -1
        cycle_length = -1

        for step in range(max_steps):
            modes, state = self.step(state)
            # Save new state and compute signature
            sig = state_signature(state)
            self.history['states'].append(state.copy())
            if sig in seen_signatures:
                cycle_found = True
                cycle_start = seen_signatures.index(sig)
                cycle_length = len(seen_signatures) - cycle_start
                break
            seen_signatures.append(sig)
        return {
            "cycle_found": cycle_found,
            "cycle_start": cycle_start,
            "cycle_length": cycle_length,
            "total_steps": len(seen_signatures) - 1,
            "history": self.history
        }

class FormulaicOperator:
    """
    Operator for advanced formulaic computations (from extracted formulae).
    Integrates additional analytical transformations (e.g., existential risk, meta-ontological duality).
    """
    def __init__(self):
        pass

    def calculate_existential_risk(self, H: np.ndarray, theta: np.ndarray, M: np.ndarray, theta0: float = 0.0) -> float:
        """
        Calculate existential risk: R(H) = σ(θ0 + θᵀ H + Hᵀ M H),
        where σ is the logistic function.
        """
        z = theta0 + H.dot(theta) + H.dot(M.dot(H))
        return 1.0 / (1.0 + math.exp(-z))

    def gradient_existential_risk(self, H: np.ndarray, theta: np.ndarray, M: np.ndarray, theta0: float = 0.0) -> np.ndarray:
        """
        Gradient of existential risk: ∇_H R = σ'(z) * [θ + 2 M H],
        where σ'(z) = σ(z)*(1-σ(z)).
        """
        R = self.calculate_existential_risk(H, theta, M, theta0)
        sigma_prime = R * (1 - R)
        grad = sigma_prime * (theta + 2 * M.dot(H))
        return grad

    def apply_meta_ontological_duality(self, material_vec: np.ndarray, immaterial_vec: np.ndarray, interaction_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply a meta-ontological duality transform: combine material and immaterial vectors via an interaction matrix.
        (This is a placeholder; real implementation would reflect meta-ontological relationships.)
        """
        mat = material_vec.copy()
        imm = immaterial_vec.copy()
        if mat.size != imm.size:
            # Pad the smaller vector with zeros to match lengths
            n = max(mat.size, imm.size)
            mat = np.pad(mat, (0, n - mat.size))
            imm = np.pad(imm, (0, n - imm.size))
        # Simple combination: each becomes influenced by the other through the interaction matrix
        new_material = mat + interaction_matrix.dot(imm)
        new_immaterial = imm + interaction_matrix.dot(mat)
        # Normalize outputs
        if np.linalg.norm(new_material) != 0:
            new_material = new_material / np.linalg.norm(new_material)
        if np.linalg.norm(new_immaterial) != 0:
            new_immaterial = new_immaterial / np.linalg.norm(new_immaterial)
        return new_material, new_immaterial
