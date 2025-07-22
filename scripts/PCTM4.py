import numpy as np
import json
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import IntEnum

# Constants
PHI = 1.61803398875  # Golden ratio
PHI_INV = 1 / PHI
KB = 1.380649e-23    # Boltzmann constant
C = 299792458        # Speed of light
G = 6.67430e-11      # Gravitational constant
HBAR = 1.054571817e-34  # Reduced Planck constant

# Orders of Reality (Ω)
class OmegaOrder(IntEnum):
    VIRTUAL = 0      # Shadow/Potential Order
    QUANTUM = 1      # Quantum Order
    MATERIAL = 2     # Material/Physical Order
    ETHEREAL = 3     # Ethereal/Energetic Order
    ASTRAL = 4       # Astral/Mental Order
    CELESTIAL = 5    # Celestial/Spiritual Order
    EXISTENTIAL = 6  # Existential/Cosmic Order

# Scales of Being (Σ)
class SigmaScale(IntEnum):
    MONADIC = 0     # Fundamental unit scale
    INDIVIDUAL = 1   # Individual entity scale
    BRAHMANIC = 2    # Universal/cosmic scale

@dataclass
class DimensionalState:
    """Represents a state in the 13-dimensional UC space."""
    vec: np.ndarray
    order: int
    freq: float
    rho: float = 1.0

    def __post_init__(self):
        # Normalize vector
        norm = np.linalg.norm(self.vec)
        if norm > 0:
            self.vec = self.vec / norm

    def copy(self):
        return DimensionalState(
            vec=self.vec.copy(),
            order=self.order,
            freq=self.freq,
            rho=self.rho
        )

class UniversalCharacteristics:
    """13 Universal Characteristics that define the state space."""

    @staticmethod
    def uncertainty(vec: np.ndarray) -> float:
        """U₁: Entropy of probability distribution."""
        p = vec**2
        p = p / np.sum(p)
        return -np.sum(np.where(p > 0, p * np.log(p), 0))

    @staticmethod
    def simplicity(rho: float) -> float:
        """U₂: Logarithmic measure of density."""
        return np.log(rho) if rho > 0 else -np.inf

    @staticmethod
    def uniqueness(vec: np.ndarray) -> float:
        """U₃: Deviation from maximum probability."""
        p = vec**2
        return 1.0 - np.max(p)

    @staticmethod
    def continuity(vec: np.ndarray) -> float:
        """U₄: Mean value representing smoothness."""
        return np.mean(vec)

    @staticmethod
    def self_similarity(vec: np.ndarray) -> float:
        """U₅: Standard deviation as scale invariance measure."""
        return np.std(vec)

    @staticmethod
    def interconnectivity(vec: np.ndarray) -> float:
        """U₆: Correlation with reversed self."""
        return np.mean(vec * vec[::-1])

    @staticmethod
    def holography(area: float = 1e-4) -> float:
        """U₇: Holographic entropy bound."""
        return (KB * C**3 * area) / (4 * G * HBAR)

    @staticmethod
    def solidity(vec: np.ndarray) -> float:
        """U₈: Euclidean norm as substantiality measure."""
        return np.linalg.norm(vec)

    @staticmethod
    def paradox(vec: np.ndarray) -> float:
        """U₉: Deviation from unit norm."""
        return abs(1 - np.linalg.norm(vec)**2)

    @staticmethod
    def flux(vec: np.ndarray) -> float:
        """U₁₀: Rate of change measure."""
        if len(vec) <= 1:
            return 0.0
        return np.linalg.norm(np.diff(vec))

    @staticmethod
    def contiguity(vec: np.ndarray, epsilon: float = 0.1) -> float:
        """U₁₁: Local continuity count."""
        if len(vec) <= 1:
            return 0.0
        return float(np.sum(np.abs(np.diff(vec)) < epsilon))

    @staticmethod
    def complementarity(vec: np.ndarray) -> float:
        """U₁₂: Self-complementary measure."""
        clipped = np.clip(vec, 0, 1)
        return np.sum(clipped * (1 - clipped))

    @staticmethod
    def incompleteness(vec: np.ndarray) -> float:
        """U₁₃: Gödelian incompleteness measure."""
        norm = np.linalg.norm(vec)
        return 1.0 - 1.0/norm if norm > 1e-10 else 1.0

class ModalDynamics:
    """10 Modal Dynamic operators for state transformation."""

    @staticmethod
    def oscillation(state: DimensionalState) -> DimensionalState:
        """M₁: Cyclic blending with lagged self."""
        new = state.copy()
        rolled = np.roll(new.vec, 1)
        new.vec = (new.vec + rolled) / np.linalg.norm(new.vec + rolled)
        return new

    @staticmethod
    def folding(state: DimensionalState) -> DimensionalState:
        """M₂: Inverts and densifies via self-negation."""
        new = state.copy()
        new.vec = -np.abs(new.vec)
        new.vec = new.vec / np.linalg.norm(new.vec)
        new.rho *= PHI
        return new

    @staticmethod
    def radiation(state: DimensionalState, sigma: float = 0.1) -> DimensionalState:
        """M₃: Diffusive outward perturbation."""
        new = state.copy()
        noise = np.random.normal(0, sigma, size=new.vec.shape)
        new.vec = new.vec + noise
        new.vec = new.vec / np.linalg.norm(new.vec)
        return new

    @staticmethod
    def propagation(state: DimensionalState) -> DimensionalState:
        """M₄: Translational motion through rotation."""
        new = state.copy()
        new.vec = np.roll(new.vec, 1)
        new.rho /= PHI
        return new

    @staticmethod
    def arborescence(state: DimensionalState) -> DimensionalState:
        """M₅: Self-expansion by squaring."""
        new = state.copy()
        new.vec = new.vec ** 2
        new.vec = new.vec / np.linalg.norm(new.vec)
        return new

    @staticmethod
    def tessellation(state: DimensionalState) -> DimensionalState:
        """M₆: Regularizes by sorting."""
        new = state.copy()
        new.vec = np.sort(new.vec)
        return new

    @staticmethod
    def helicity(state: DimensionalState) -> DimensionalState:
        """M₇: Mirrors the structure."""
        new = state.copy()
        new.vec = new.vec[::-1]
        return new

    @staticmethod
    def enantiodromia(state: DimensionalState) -> DimensionalState:
        """M₈: Total polarity reversal."""
        new = state.copy()
        new.vec = -new.vec
        return new

    @staticmethod
    def exteriority(state: DimensionalState, epsilon: float = 0.01) -> DimensionalState:
        """M₉: Pushes state outward."""
        new = state.copy()
        new.vec = new.vec + epsilon
        new.vec = new.vec / np.linalg.norm(new.vec)
        return new

    @staticmethod
    def solution(state: DimensionalState) -> DimensionalState:
        """M₁₀: Averaging across neighborhood."""
        new = state.copy()
        avg = (np.roll(new.vec, 1) + np.roll(new.vec, -1)) / 2.0
        new.vec = avg / np.linalg.norm(avg)
        return new

class Oracle:
    """I Ching-based oracle for hypercomputational intervention."""
    def detect_halt_conditions(uc_vector):
    halt_flags = []
    if uc_vector["uncertainty"] > 0.9:
        halt_flags.append("entropy_spike")
    if uc_vector["paradox"] > 0.85:
        halt_flags.append("paradox_detected")
    if uc_vector["incompleteness"] > 0.95:
        halt_flags.append("incompleteness_crisis")
    if is_phi_resonant(uc_vector):
        halt_flags.append("phi_resonance")

    return {"halt": bool(halt_flags), "halt_reasons": halt_flags}

    def is_phi_resonant(uc_vector):
    phi = (1 + 5 ** 0.5) / 2
    values = list(uc_vector.values())
    for i in range(len(values) - 1):
        if abs(values[i] / values[i + 1] - phi) < 0.05:
            return True
    return False

    def __init__(self):
        self.hexagrams = self._initialize_hexagrams()
        self.transformation_map = self._create_transformation_map()

    def _initialize_hexagrams(self) -> Dict[int, Dict[str, Any]]:
        """Initialize 64 I Ching hexagrams with interpretations."""
        hexagrams = {}
        names = [
            "Creative", "Receptive", "Difficulty", "Youthful Folly", "Waiting", "Conflict",
            "Army", "Holding Together", "Small Taming", "Treading", "Peace", "Standstill",
            "Fellowship", "Great Possession", "Modesty", "Enthusiasm", "Following", "Corruption",
            "Approach", "Contemplation", "Biting Through", "Grace", "Splitting Apart", "Return",
            "Innocence", "Great Taming", "Nourishment", "Great Exceeding", "Abysmal", "Clinging",
            "Influence", "Duration", "Retreat", "Great Power", "Progress", "Darkening",
            "Family", "Opposition", "Obstruction", "Deliverance", "Decrease", "Increase",
            "Breakthrough", "Coming to Meet", "Gathering", "Pushing Upward", "Oppression", "Well",
            "Revolution", "Cauldron", "Arousing", "Keeping Still", "Development", "Marrying Maiden",
            "Abundance", "Wanderer", "Gentle", "Joyous", "Dispersion", "Limitation",
            "Inner Truth", "Small Exceeding", "After Completion", "Before Completion"
        ]

        for i, name in enumerate(names):
            hexagrams[i] = {
                'number': i + 1,
                'name': name,
                'binary': format(i, '06b'),
                'transformation': self._hexagram_to_transformation(i)
            }
        return hexagrams

    def _hexagram_to_transformation(self, hex_num: int) -> str:
        """Map hexagram number to transformation type."""
        transformations = {
            0: "oscillation+radiation",     # Creative - expansive energy
            1: "folding+solution",          # Receptive - inward consolidation
            50: "enantiodromia+oscillation", # Arousing/Shock - reversal
            29: "propagation+radiation",     # Abysmal - flowing through danger
            51: "arborescence+tessellation", # Development - growth and order
            48: "solution+exteriority",      # Well - nourishment and expansion
            49: "enantiodromia+folding",     # Revolution - transformation
            63: "helicity+solution"          # After Completion - reflection
        }

        # Default transformation based on binary pattern
        if hex_num not in transformations:
            binary = format(hex_num, '06b')
            if binary.count('1') > 3:
                return "radiation+propagation"
            else:
                return "folding+solution"

        return transformations.get(hex_num, "oscillation")

    def _create_transformation_map(self) -> Dict[str, List[str]]:
        """Create mapping from transformation names to modal dynamics."""
        return {
            "oscillation": ["oscillation"],
            "folding": ["folding"],
            "radiation": ["radiation"],
            "propagation": ["propagation"],
            "arborescence": ["arborescence"],
            "tessellation": ["tessellation"],
            "helicity": ["helicity"],
            "enantiodromia": ["enantiodromia"],
            "exteriority": ["exteriority"],
            "solution": ["solution"]
        }

    def cast_hexagram(self, state: DimensionalState, omega: int) -> Dict[str, Any]:
        """Cast hexagram based on state and ontological level."""
        # Use state vector and omega to generate hexagram
        seed = int(np.sum(state.vec * 1000) + omega * 100) % (2**32)
        np.random.seed(seed)

        # Generate 6 lines (0 or 1) for hexagram
        lines = np.random.randint(0, 2, 6)
        hex_num = int(''.join(map(str, lines)), 2)

        return self.hexagrams[hex_num]

    def interpret_hexagram(self, hexagram: Dict[str, Any], state: DimensionalState) -> Optional[DimensionalState]:
        """Interpret hexagram and apply transformation."""
        transformation_str = hexagram['transformation']
        transformations = transformation_str.split('+')

        new_state = state.copy()
        modal = ModalDynamics()

        for trans in transformations:
            if hasattr(modal, trans):
                transform_func = getattr(modal, trans)
                new_state = transform_func(new_state)

        # Adjust order based on hexagram insight
        if 'shock' in hexagram['name'].lower():
            new_state.order = min(new_state.order + 1, 6)
        elif 'return' in hexagram['name'].lower():
            new_state.order = max(new_state.order - 1, 0)

        return new_state

    def intervene(self, state: DimensionalState, omega: int) -> Dict[str, Any]:
        """Perform oracle intervention when computation halts."""
        hexagram = self.cast_hexagram(state, omega)
        new_state = self.interpret_hexagram(hexagram, state)

        resolved = new_state is not None

        return {
            'hexagram': hexagram,
            'resolved': resolved,
            'new_state': new_state,
            'intervention': hexagram['transformation'],
            'oracle_message': f"Hexagram {hexagram['number']}: {hexagram['name']}"
        }

class PCTM4Engine:
    """Polychronological Symphonic Turing Machine v4 Engine."""

    def __init__(self):
        self.ontology_tensor = self._initialize_ontology_tensor()
        self.uc_valences = self._initialize_uc_valences()
        self.modal_dynamics = self._initialize_modal_dynamics()
        self.oracle = Oracle()
        self.uc = UniversalCharacteristics()
        self.history = []

    def _initialize_ontology_tensor(self) -> np.ndarray:
        """Initialize Ω×Σ tensor mapping to UC weight profiles."""
        # 7 orders × 3 scales × 13 UC dimensions
        tensor = np.zeros((7, 3, 13))

        # Virtual Order - high uncertainty, paradox, low solidity
        tensor[OmegaOrder.VIRTUAL] = np.array([
            [0.8, 0.2, 0.7, 0.3, 0.5, 0.4, 0.1, 0.1, 0.9, 0.6, 0.2, 0.8, 0.9],  # Monadic
            [0.7, 0.3, 0.8, 0.4, 0.4, 0.5, 0.2, 0.2, 0.8, 0.5, 0.3, 0.7, 0.8],  # Individual
            [0.6, 0.4, 0.9, 0.5, 0.3, 0.6, 0.3, 0.3, 0.7, 0.4, 0.4, 0.6, 0.7]   # Brahmanic
        ])

        # Quantum Order - superposition, flux, complementarity
        tensor[OmegaOrder.QUANTUM] = np.array([
            [0.7, 0.3, 0.6, 0.4, 0.6, 0.5, 0.3, 0.3, 0.7, 0.8, 0.3, 0.9, 0.6],
            [0.6, 0.4, 0.5, 0.5, 0.7, 0.6, 0.4, 0.4, 0.6, 0.7, 0.4, 0.8, 0.5],
            [0.5, 0.5, 0.4, 0.6, 0.8, 0.7, 0.5, 0.5, 0.5, 0.6, 0.5, 0.7, 0.4]
        ])

        # Material Order - high solidity, continuity, low paradox
        tensor[OmegaOrder.MATERIAL] = np.array([
            [0.2, 0.8, 0.3, 0.8, 0.3, 0.7, 0.7, 0.9, 0.2, 0.3, 0.8, 0.3, 0.2],
            [0.3, 0.7, 0.2, 0.7, 0.4, 0.8, 0.8, 0.8, 0.3, 0.4, 0.7, 0.4, 0.3],
            [0.4, 0.6, 0.1, 0.6, 0.5, 0.9, 0.9, 0.7, 0.4, 0.5, 0.6, 0.5, 0.4]
        ])

        # Ethereal Order - high flux, interconnectivity
        tensor[OmegaOrder.ETHEREAL] = np.array([
            [0.5, 0.5, 0.5, 0.6, 0.7, 0.8, 0.5, 0.5, 0.5, 0.8, 0.6, 0.6, 0.5],
            [0.6, 0.4, 0.6, 0.5, 0.6, 0.9, 0.6, 0.6, 0.4, 0.7, 0.7, 0.7, 0.4],
            [0.7, 0.3, 0.7, 0.4, 0.5, 1.0, 0.7, 0.7, 0.3, 0.6, 0.8, 0.8, 0.3]
        ])

        # Astral Order - high self-similarity, holography
        tensor[OmegaOrder.ASTRAL] = np.array([
            [0.6, 0.4, 0.7, 0.5, 0.8, 0.7, 0.8, 0.6, 0.6, 0.5, 0.5, 0.5, 0.6],
            [0.5, 0.5, 0.8, 0.6, 0.9, 0.8, 0.7, 0.5, 0.5, 0.6, 0.6, 0.6, 0.5],
            [0.4, 0.6, 0.9, 0.7, 1.0, 0.9, 0.6, 0.4, 0.4, 0.7, 0.7, 0.7, 0.4]
        ])

        # Celestial Order - balance, high holography, low uncertainty
        tensor[OmegaOrder.CELESTIAL] = np.array([
            [0.3, 0.7, 0.8, 0.7, 0.7, 0.7, 0.9, 0.7, 0.3, 0.3, 0.7, 0.3, 0.3],
            [0.2, 0.8, 0.9, 0.8, 0.8, 0.8, 1.0, 0.6, 0.2, 0.2, 0.8, 0.2, 0.2],
            [0.1, 0.9, 1.0, 0.9, 0.9, 0.9, 0.9, 0.5, 0.1, 0.1, 0.9, 0.1, 0.1]
        ])

        # Existential Order - maximum integration, minimal paradox
        tensor[OmegaOrder.EXISTENTIAL] = np.array([
            [0.1, 0.9, 0.9, 0.9, 0.9, 0.9, 1.0, 0.8, 0.1, 0.1, 0.9, 0.1, 0.1],
            [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.0, 0.0, 1.0, 0.0, 0.0],
            [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        ])

        return tensor

    def _initialize_uc_valences(self) -> Dict[str, callable]:
        """Map UC names to their calculation functions."""
        return {
            'uncertainty': self.uc.uncertainty,
            'simplicity': lambda vec: self.uc.simplicity(1.0),  # Using default rho
            'uniqueness': self.uc.uniqueness,
            'continuity': self.uc.continuity,
            'self_similarity': self.uc.self_similarity,
            'interconnectivity': self.uc.interconnectivity,
            'holography': lambda vec: self.uc.holography(),
            'solidity': self.uc.solidity,
            'paradox': self.uc.paradox,
            'flux': self.uc.flux,
            'contiguity': self.uc.contiguity,
            'complementarity': self.uc.complementarity,
            'incompleteness': self.uc.incompleteness
        }

    def _initialize_modal_dynamics(self) -> Dict[int, List[callable]]:
        """Initialize modal dynamics per ontological order."""
        md = ModalDynamics()

        return {
            OmegaOrder.VIRTUAL: [md.oscillation, md.radiation, md.paradox],
            OmegaOrder.QUANTUM: [md.folding, md.propagation, md.complementarity],
            OmegaOrder.MATERIAL: [md.tessellation, md.solution, md.exteriority],
            OmegaOrder.ETHEREAL: [md.radiation, md.propagation, md.flux],
            OmegaOrder.ASTRAL: [md.arborescence, md.helicity, md.self_similarity],
            OmegaOrder.CELESTIAL: [md.oscillation, md.solution, md.holography],
            OmegaOrder.EXISTENTIAL: [md.enantiodromia, md.folding, md.integration]
        }

    def initialize_state(self, omega: int, sigma: int) -> DimensionalState:
        """Initialize dimensional state using ontology tensor."""
        weights = self.ontology_tensor[omega][sigma]

        # Create initial random vector
        vec = np.random.randn(13)

        # Weight by ontological profile
        vec = vec * weights

        # Normalize
        vec = vec / np.linalg.norm(vec)

        return DimensionalState(
            vec=vec,
            order=omega,
            freq=1.0,
            rho=1.0
        )

    def calculate_uc_vector(self, state: DimensionalState) -> np.ndarray:
        """Calculate the 13-dimensional UC values for current state."""
        uc_values = []

        # Calculate each UC value
        uc_values.append(self.uc.uncertainty(state.vec))
        uc_values.append(self.uc.simplicity(state.rho))
        uc_values.append(self.uc.uniqueness(state.vec))
        uc_values.append(self.uc.continuity(state.vec))
        uc_values.append(self.uc.self_similarity(state.vec))
        uc_values.append(self.uc.interconnectivity(state.vec))
        uc_values.append(self.uc.holography())
        uc_values.append(self.uc.solidity(state.vec))
        uc_values.append(self.uc.paradox(state.vec))
        uc_values.append(self.uc.flux(state.vec))
        uc_values.append(self.uc.contiguity(state.vec))
        uc_values.append(self.uc.complementarity(state.vec))
        uc_values.append(self.uc.incompleteness(state.vec))

        return np.array(uc_values)

    def check_halt_conditions(self, state: DimensionalState) -> Dict[str, bool]:
        """Check if oracle intervention is needed."""
        uc_vec = self.calculate_uc_vector(state)

        # Coherence collapse: high paradox and uncertainty together
        coherence_collapse = (uc_vec[8] > 0.8 and uc_vec[0] > 0.7)

        # Entropy spike: extremely high uncertainty
        entropy_spike = uc_vec[0] > 0.9

        # Paradox detection: high paradox value
        paradox_detected = uc_vec[8] > 0.85

        # Incompleteness crisis: near maximum incompleteness
        incompleteness_crisis = uc_vec[12] > 0.95

        # Golden ratio harmony check
        phi_resonance = False
        for i in range(len(uc_vec)-1):
            ratio = uc_vec[i] / (uc_vec[i+1] + 1e-10)
            if abs(ratio - PHI) < 0.1 or abs(ratio - PHI_INV) < 0.1:
                phi_resonance = True
                break

        return {
            'coherence_collapse': coherence_collapse,
            'entropy_spike': entropy_spike,
            'paradox_detected': paradox_detected,
            'incompleteness_crisis': incompleteness_crisis,
            'phi_resonance': phi_resonance,
            'halt': any([coherence_collapse, entropy_spike, paradox_detected, incompleteness_crisis])
        }

    def _attempt_tape_transition(self, state: DimensionalState, omega: int) -> Dict[str, Any]:
        """Apply modal dynamics for given ontological order."""
        dynamics = self.modal_dynamics.get(omega, [])

        # Check halt conditions first
        halt_check = self.check_halt_conditions(state)
        if halt_check['halt']:
            return {
                'omega': omega,
                'status': 'halted',
                'state': state,
                'halt_reason': halt_check
            }

        # Try each dynamic in sequence
        for i, dynamic in enumerate(dynamics):
            try:
                # Apply golden ratio threshold
                threshold = PHI_INV ** (i + 1) * (1 + state.rho / PHI)
                activation = np.mean(state.vec)

                if activation > threshold:
                    new_state = dynamic(state)
                    return {
                        'omega': omega,
                        'status': 'complete',
                        'state': new_state,
                        'dynamic_applied': dynamic.__name__
                    }
            except Exception as e:
                continue

        # If no dynamics succeeded, return with current state
        return {
            'omega': omega,
            'status': 'no_transition',
            'state': state
        }

    def process(self, initial_state: DimensionalState, max_steps: int = 100) -> List[Dict[str, Any]]:
        """Process computation across all 7 ontological tapes."""
        state = initial_state.copy()
        transcript = []

        for step in range(max_steps):
            step_record = {
                'step': step,
                'transitions': []
            }

            # Attempt transitions across all omega levels
            for omega in range(7):
                result = self._attempt_tape_transition(state, omega)
                step_record['transitions'].append(result)

                if result['status'] == 'halted':
                    # Oracle intervention needed
                    oracle_result = self.oracle.intervene(state, omega)
                    step_record['transitions'].append({
                        'omega': omega,
                        'oracle_intervention': oracle_result
                    })

                    if oracle_result['resolved']:
                        state = oracle_result['new_state']
                    else:
                        # Unresolvable halt
                        transcript.append(step_record)
                        return transcript

                elif result['status'] == 'complete':
                    state = result['state']

            # Record UC vector at end of step
            step_record['uc_vector'] = self.calculate_uc_vector(state).tolist()
            step_record['final_state'] = {
                'vec': state.vec.tolist(),
                'order': state.order,
                'freq': state.freq,
                'rho': state.rho
            }

            transcript.append(step_record)

            # Check for global convergence
            if step > 0:
                prev_vec = np.array(transcript[-2]['uc_vector'])
                curr_vec = np.array(transcript[-1]['uc_vector'])
                if np.allclose(prev_vec, curr_vec, atol=1e-6):
                    break

        return transcript

    def run_experiment(self, omega_start: int = 0, sigma_start: int = 1, steps: int = 50) -> Dict[str, Any]:
        """Run a complete PCTM4 experiment."""
        # Initialize starting state
        initial_state = self.initialize_state(omega_start, sigma_start)

        # Process through the engine
        transcript = self.process(initial_state, max_steps=steps)

        # Analyze results
        analysis = {
            'total_steps': len(transcript),
            'oracle_interventions': sum(
                1 for step in transcript
                for trans in step['transitions']
                if 'oracle_intervention' in trans
            ),
            'final_omega': transcript[-1]['final_state']['order'] if transcript else omega_start,
            'convergence_achieved': len(transcript) < steps,
            'transcript': transcript
        }

        return analysis

# Example usage
if __name__ == "__main__":
    # Create PCTM4 engine
    engine = PCTM4Engine()

    # Run experiment starting from Quantum order at Individual scale
    result = engine.run_experiment(
        omega_start=OmegaOrder.QUANTUM,
        sigma_start=SigmaScale.INDIVIDUAL,
        steps=30
    )

    print(f"PCTM4 Experiment Results:")
    print(f"Total steps: {result['total_steps']}")
    print(f"Oracle interventions: {result['oracle_interventions']}")
    print(f"Final omega level: {result['final_omega']}")
    print(f"Convergence achieved: {result['convergence_achieved']}")

    # Print first few steps
    for i, step in enumerate(result['transcript'][:3]):
        print(f"\nStep {i}:")
        for trans in step['transitions']:
            if 'dynamic_applied' in trans:
                print(f"  Omega {trans['omega']}: Applied {trans['dynamic_applied']}")
            elif 'oracle_intervention' in trans:
                oracle = trans['oracle_intervention']
                print(f"  Omega {trans['omega']}: Oracle - {oracle['oracle_message']}")import numpy as np
import json
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import IntEnum

# Constants
PHI = 1.61803398875  # Golden ratio
PHI_INV = 1 / PHI
KB = 1.380649e-23    # Boltzmann constant
C = 299792458        # Speed of light
G = 6.67430e-11      # Gravitational constant
HBAR = 1.054571817e-34  # Reduced Planck constant

# Orders of Reality (Ω)
class OmegaOrder(IntEnum):
    VIRTUAL = 0      # Shadow/Potential Order
    QUANTUM = 1      # Quantum Order
    MATERIAL = 2     # Material/Physical Order
    ETHEREAL = 3     # Ethereal/Energetic Order
    ASTRAL = 4       # Astral/Mental Order
    CELESTIAL = 5    # Celestial/Spiritual Order
    EXISTENTIAL = 6  # Existential/Cosmic Order

# Scales of Being (Σ)
class SigmaScale(IntEnum):
    MONADIC = 0     # Fundamental unit scale
    INDIVIDUAL = 1   # Individual entity scale
    BRAHMANIC = 2    # Universal/cosmic scale

@dataclass
class DimensionalState:
    """Represents a state in the 13-dimensional UC space."""
    vec: np.ndarray
    order: int
    freq: float
    rho: float = 1.0

    def __post_init__(self):
        # Normalize vector
        norm = np.linalg.norm(self.vec)
        if norm > 0:
            self.vec = self.vec / norm

    def copy(self):
        return DimensionalState(
            vec=self.vec.copy(),
            order=self.order,
            freq=self.freq,
            rho=self.rho
        )

class UniversalCharacteristics:
    """13 Universal Characteristics that define the state space."""

    @staticmethod
    def uncertainty(vec: np.ndarray) -> float:
        """U₁: Entropy of probability distribution."""
        p = vec**2
        p = p / np.sum(p)
        return -np.sum(np.where(p > 0, p * np.log(p), 0))

    @staticmethod
    def simplicity(rho: float) -> float:
        """U₂: Logarithmic measure of density."""
        return np.log(rho) if rho > 0 else -np.inf

    @staticmethod
    def uniqueness(vec: np.ndarray) -> float:
        """U₃: Deviation from maximum probability."""
        p = vec**2
        return 1.0 - np.max(p)

    @staticmethod
    def continuity(vec: np.ndarray) -> float:
        """U₄: Mean value representing smoothness."""
        return np.mean(vec)

    @staticmethod
    def self_similarity(vec: np.ndarray) -> float:
        """U₅: Standard deviation as scale invariance measure."""
        return np.std(vec)

    @staticmethod
    def interconnectivity(vec: np.ndarray) -> float:
        """U₆: Correlation with reversed self."""
        return np.mean(vec * vec[::-1])

    @staticmethod
    def holography(area: float = 1e-4) -> float:
        """U₇: Holographic entropy bound."""
        return (KB * C**3 * area) / (4 * G * HBAR)

    @staticmethod
    def solidity(vec: np.ndarray) -> float:
        """U₈: Euclidean norm as substantiality measure."""
        return np.linalg.norm(vec)

    @staticmethod
    def paradox(vec: np.ndarray) -> float:
        """U₉: Deviation from unit norm."""
        return abs(1 - np.linalg.norm(vec)**2)

    @staticmethod
    def flux(vec: np.ndarray) -> float:
        """U₁₀: Rate of change measure."""
        if len(vec) <= 1:
            return 0.0
        return np.linalg.norm(np.diff(vec))

    @staticmethod
    def contiguity(vec: np.ndarray, epsilon: float = 0.1) -> float:
        """U₁₁: Local continuity count."""
        if len(vec) <= 1:
            return 0.0
        return float(np.sum(np.abs(np.diff(vec)) < epsilon))

    @staticmethod
    def complementarity(vec: np.ndarray) -> float:
        """U₁₂: Self-complementary measure."""
        clipped = np.clip(vec, 0, 1)
        return np.sum(clipped * (1 - clipped))

    @staticmethod
    def incompleteness(vec: np.ndarray) -> float:
        """U₁₃: Gödelian incompleteness measure."""
        norm = np.linalg.norm(vec)
        return 1.0 - 1.0/norm if norm > 1e-10 else 1.0

class ModalDynamics:
    """10 Modal Dynamic operators for state transformation."""

    @staticmethod
    def oscillation(state: DimensionalState) -> DimensionalState:
        """M₁: Cyclic blending with lagged self."""
        new = state.copy()
        rolled = np.roll(new.vec, 1)
        new.vec = (new.vec + rolled) / np.linalg.norm(new.vec + rolled)
        return new

    @staticmethod
    def folding(state: DimensionalState) -> DimensionalState:
        """M₂: Inverts and densifies via self-negation."""
        new = state.copy()
        new.vec = -np.abs(new.vec)
        new.vec = new.vec / np.linalg.norm(new.vec)
        new.rho *= PHI
        return new

    @staticmethod
    def radiation(state: DimensionalState, sigma: float = 0.1) -> DimensionalState:
        """M₃: Diffusive outward perturbation."""
        new = state.copy()
        noise = np.random.normal(0, sigma, size=new.vec.shape)
        new.vec = new.vec + noise
        new.vec = new.vec / np.linalg.norm(new.vec)
        return new

    @staticmethod
    def propagation(state: DimensionalState) -> DimensionalState:
        """M₄: Translational motion through rotation."""
        new = state.copy()
        new.vec = np.roll(new.vec, 1)
        new.rho /= PHI
        return new

    @staticmethod
    def arborescence(state: DimensionalState) -> DimensionalState:
        """M₅: Self-expansion by squaring."""
        new = state.copy()
        new.vec = new.vec ** 2
        new.vec = new.vec / np.linalg.norm(new.vec)
        return new

    @staticmethod
    def tessellation(state: DimensionalState) -> DimensionalState:
        """M₆: Regularizes by sorting."""
        new = state.copy()
        new.vec = np.sort(new.vec)
        return new

    @staticmethod
    def helicity(state: DimensionalState) -> DimensionalState:
        """M₇: Mirrors the structure."""
        new = state.copy()
        new.vec = new.vec[::-1]
        return new

    @staticmethod
    def enantiodromia(state: DimensionalState) -> DimensionalState:
        """M₈: Total polarity reversal."""
        new = state.copy()
        new.vec = -new.vec
        return new

    @staticmethod
    def exteriority(state: DimensionalState, epsilon: float = 0.01) -> DimensionalState:
        """M₉: Pushes state outward."""
        new = state.copy()
        new.vec = new.vec + epsilon
        new.vec = new.vec / np.linalg.norm(new.vec)
        return new

    @staticmethod
    def solution(state: DimensionalState) -> DimensionalState:
        """M₁₀: Averaging across neighborhood."""
        new = state.copy()
        avg = (np.roll(new.vec, 1) + np.roll(new.vec, -1)) / 2.0
        new.vec = avg / np.linalg.norm(avg)
        return new

class Oracle:
    """I Ching-based oracle for hypercomputational intervention."""

    def __init__(self):
        self.hexagrams = self._initialize_hexagrams()
        self.transformation_map = self._create_transformation_map()

    def _initialize_hexagrams(self) -> Dict[int, Dict[str, Any]]:
        """Initialize 64 I Ching hexagrams with interpretations."""
        hexagrams = {}
        names = [
            "Creative", "Receptive", "Difficulty", "Youthful Folly", "Waiting", "Conflict",
            "Army", "Holding Together", "Small Taming", "Treading", "Peace", "Standstill",
            "Fellowship", "Great Possession", "Modesty", "Enthusiasm", "Following", "Corruption",
            "Approach", "Contemplation", "Biting Through", "Grace", "Splitting Apart", "Return",
            "Innocence", "Great Taming", "Nourishment", "Great Exceeding", "Abysmal", "Clinging",
            "Influence", "Duration", "Retreat", "Great Power", "Progress", "Darkening",
            "Family", "Opposition", "Obstruction", "Deliverance", "Decrease", "Increase",
            "Breakthrough", "Coming to Meet", "Gathering", "Pushing Upward", "Oppression", "Well",
            "Revolution", "Cauldron", "Arousing", "Keeping Still", "Development", "Marrying Maiden",
            "Abundance", "Wanderer", "Gentle", "Joyous", "Dispersion", "Limitation",
            "Inner Truth", "Small Exceeding", "After Completion", "Before Completion"
        ]

        for i, name in enumerate(names):
            hexagrams[i] = {
                'number': i + 1,
                'name': name,
                'binary': format(i, '06b'),
                'transformation': self._hexagram_to_transformation(i)
            }
        return hexagrams

    def _hexagram_to_transformation(self, hex_num: int) -> str:
        """Map hexagram number to transformation type."""
        transformations = {
            0: "oscillation+radiation",     # Creative - expansive energy
            1: "folding+solution",          # Receptive - inward consolidation
            50: "enantiodromia+oscillation", # Arousing/Shock - reversal
            29: "propagation+radiation",     # Abysmal - flowing through danger
            51: "arborescence+tessellation", # Development - growth and order
            48: "solution+exteriority",      # Well - nourishment and expansion
            49: "enantiodromia+folding",     # Revolution - transformation
            63: "helicity+solution"          # After Completion - reflection
        }

        # Default transformation based on binary pattern
        if hex_num not in transformations:
            binary = format(hex_num, '06b')
            if binary.count('1') > 3:
                return "radiation+propagation"
            else:
                return "folding+solution"

        return transformations.get(hex_num, "oscillation")

    def _create_transformation_map(self) -> Dict[str, List[str]]:
        """Create mapping from transformation names to modal dynamics."""
        return {
            "oscillation": ["oscillation"],
            "folding": ["folding"],
            "radiation": ["radiation"],
            "propagation": ["propagation"],
            "arborescence": ["arborescence"],
            "tessellation": ["tessellation"],
            "helicity": ["helicity"],
            "enantiodromia": ["enantiodromia"],
            "exteriority": ["exteriority"],
            "solution": ["solution"]
        }

    def cast_hexagram(self, state: DimensionalState, omega: int) -> Dict[str, Any]:
        """Cast hexagram based on state and ontological level."""
        # Use state vector and omega to generate hexagram
        seed = int(np.sum(state.vec * 1000) + omega * 100) % (2**32)
        np.random.seed(seed)

        # Generate 6 lines (0 or 1) for hexagram
        lines = np.random.randint(0, 2, 6)
        hex_num = int(''.join(map(str, lines)), 2)

        return self.hexagrams[hex_num]

    def interpret_hexagram(self, hexagram: Dict[str, Any], state: DimensionalState) -> Optional[DimensionalState]:
        """Interpret hexagram and apply transformation."""
        transformation_str = hexagram['transformation']
        transformations = transformation_str.split('+')

        new_state = state.copy()
        modal = ModalDynamics()

        for trans in transformations:
            if hasattr(modal, trans):
                transform_func = getattr(modal, trans)
                new_state = transform_func(new_state)

        # Adjust order based on hexagram insight
        if 'shock' in hexagram['name'].lower():
            new_state.order = min(new_state.order + 1, 6)
        elif 'return' in hexagram['name'].lower():
            new_state.order = max(new_state.order - 1, 0)

        return new_state

    def intervene(self, state: DimensionalState, omega: int) -> Dict[str, Any]:
        """Perform oracle intervention when computation halts."""
        hexagram = self.cast_hexagram(state, omega)
        new_state = self.interpret_hexagram(hexagram, state)

        resolved = new_state is not None

        return {
            'hexagram': hexagram,
            'resolved': resolved,
            'new_state': new_state,
            'intervention': hexagram['transformation'],
            'oracle_message': f"Hexagram {hexagram['number']}: {hexagram['name']}"
        }

class PCTM4Engine:
    """Polychronological Symphonic Turing Machine v4 Engine."""

    def __init__(self):
        self.ontology_tensor = self._initialize_ontology_tensor()
        self.uc_valences = self._initialize_uc_valences()
        self.modal_dynamics = self._initialize_modal_dynamics()
        self.oracle = Oracle()
        self.uc = UniversalCharacteristics()
        self.history = []

    def _initialize_ontology_tensor(self) -> np.ndarray:
        """Initialize Ω×Σ tensor mapping to UC weight profiles."""
        # 7 orders × 3 scales × 13 UC dimensions
        tensor = np.zeros((7, 3, 13))

        # Virtual Order - high uncertainty, paradox, low solidity
        tensor[OmegaOrder.VIRTUAL] = np.array([
            [0.8, 0.2, 0.7, 0.3, 0.5, 0.4, 0.1, 0.1, 0.9, 0.6, 0.2, 0.8, 0.9],  # Monadic
            [0.7, 0.3, 0.8, 0.4, 0.4, 0.5, 0.2, 0.2, 0.8, 0.5, 0.3, 0.7, 0.8],  # Individual
            [0.6, 0.4, 0.9, 0.5, 0.3, 0.6, 0.3, 0.3, 0.7, 0.4, 0.4, 0.6, 0.7]   # Brahmanic
        ])

        # Quantum Order - superposition, flux, complementarity
        tensor[OmegaOrder.QUANTUM] = np.array([
            [0.7, 0.3, 0.6, 0.4, 0.6, 0.5, 0.3, 0.3, 0.7, 0.8, 0.3, 0.9, 0.6],
            [0.6, 0.4, 0.5, 0.5, 0.7, 0.6, 0.4, 0.4, 0.6, 0.7, 0.4, 0.8, 0.5],
            [0.5, 0.5, 0.4, 0.6, 0.8, 0.7, 0.5, 0.5, 0.5, 0.6, 0.5, 0.7, 0.4]
        ])

        # Material Order - high solidity, continuity, low paradox
        tensor[OmegaOrder.MATERIAL] = np.array([
            [0.2, 0.8, 0.3, 0.8, 0.3, 0.7, 0.7, 0.9, 0.2, 0.3, 0.8, 0.3, 0.2],
            [0.3, 0.7, 0.2, 0.7, 0.4, 0.8, 0.8, 0.8, 0.3, 0.4, 0.7, 0.4, 0.3],
            [0.4, 0.6, 0.1, 0.6, 0.5, 0.9, 0.9, 0.7, 0.4, 0.5, 0.6, 0.5, 0.4]
        ])

        # Ethereal Order - high flux, interconnectivity
        tensor[OmegaOrder.ETHEREAL] = np.array([
            [0.5, 0.5, 0.5, 0.6, 0.7, 0.8, 0.5, 0.5, 0.5, 0.8, 0.6, 0.6, 0.5],
            [0.6, 0.4, 0.6, 0.5, 0.6, 0.9, 0.6, 0.6, 0.4, 0.7, 0.7, 0.7, 0.4],
            [0.7, 0.3, 0.7, 0.4, 0.5, 1.0, 0.7, 0.7, 0.3, 0.6, 0.8, 0.8, 0.3]
        ])

        # Astral Order - high self-similarity, holography
        tensor[OmegaOrder.ASTRAL] = np.array([
            [0.6, 0.4, 0.7, 0.5, 0.8, 0.7, 0.8, 0.6, 0.6, 0.5, 0.5, 0.5, 0.6],
            [0.5, 0.5, 0.8, 0.6, 0.9, 0.8, 0.7, 0.5, 0.5, 0.6, 0.6, 0.6, 0.5],
            [0.4, 0.6, 0.9, 0.7, 1.0, 0.9, 0.6, 0.4, 0.4, 0.7, 0.7, 0.7, 0.4]
        ])

        # Celestial Order - balance, high holography, low uncertainty
        tensor[OmegaOrder.CELESTIAL] = np.array([
            [0.3, 0.7, 0.8, 0.7, 0.7, 0.7, 0.9, 0.7, 0.3, 0.3, 0.7, 0.3, 0.3],
            [0.2, 0.8, 0.9, 0.8, 0.8, 0.8, 1.0, 0.6, 0.2, 0.2, 0.8, 0.2, 0.2],
            [0.1, 0.9, 1.0, 0.9, 0.9, 0.9, 0.9, 0.5, 0.1, 0.1, 0.9, 0.1, 0.1]
        ])

        # Existential Order - maximum integration, minimal paradox
        tensor[OmegaOrder.EXISTENTIAL] = np.array([
            [0.1, 0.9, 0.9, 0.9, 0.9, 0.9, 1.0, 0.8, 0.1, 0.1, 0.9, 0.1, 0.1],
            [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.0, 0.0, 1.0, 0.0, 0.0],
            [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        ])

        return tensor

    def _initialize_uc_valences(self) -> Dict[str, callable]:
        """Map UC names to their calculation functions."""
        return {
            'uncertainty': self.uc.uncertainty,
            'simplicity': lambda vec: self.uc.simplicity(1.0),  # Using default rho
            'uniqueness': self.uc.uniqueness,
            'continuity': self.uc.continuity,
            'self_similarity': self.uc.self_similarity,
            'interconnectivity': self.uc.interconnectivity,
            'holography': lambda vec: self.uc.holography(),
            'solidity': self.uc.solidity,
            'paradox': self.uc.paradox,
            'flux': self.uc.flux,
            'contiguity': self.uc.contiguity,
            'complementarity': self.uc.complementarity,
            'incompleteness': self.uc.incompleteness
        }

    def _initialize_modal_dynamics(self) -> Dict[int, List[callable]]:
        """Initialize modal dynamics per ontological order."""
        md = ModalDynamics()

        return {
            OmegaOrder.VIRTUAL: [md.oscillation, md.radiation, md.paradox],
            OmegaOrder.QUANTUM: [md.folding, md.propagation, md.complementarity],
            OmegaOrder.MATERIAL: [md.tessellation, md.solution, md.exteriority],
            OmegaOrder.ETHEREAL: [md.radiation, md.propagation, md.flux],
            OmegaOrder.ASTRAL: [md.arborescence, md.helicity, md.self_similarity],
            OmegaOrder.CELESTIAL: [md.oscillation, md.solution, md.holography],
            OmegaOrder.EXISTENTIAL: [md.enantiodromia, md.folding, md.integration]
        }

    def initialize_state(self, omega: int, sigma: int) -> DimensionalState:
        """Initialize dimensional state using ontology tensor."""
        weights = self.ontology_tensor[omega][sigma]

        # Create initial random vector
        vec = np.random.randn(13)

        # Weight by ontological profile
        vec = vec * weights

        # Normalize
        vec = vec / np.linalg.norm(vec)

        return DimensionalState(
            vec=vec,
            order=omega,
            freq=1.0,
            rho=1.0
        )

    def calculate_uc_vector(self, state: DimensionalState) -> np.ndarray:
        """Calculate the 13-dimensional UC values for current state."""
        uc_values = []

        # Calculate each UC value
        uc_values.append(self.uc.uncertainty(state.vec))
        uc_values.append(self.uc.simplicity(state.rho))
        uc_values.append(self.uc.uniqueness(state.vec))
        uc_values.append(self.uc.continuity(state.vec))
        uc_values.append(self.uc.self_similarity(state.vec))
        uc_values.append(self.uc.interconnectivity(state.vec))
        uc_values.append(self.uc.holography())
        uc_values.append(self.uc.solidity(state.vec))
        uc_values.append(self.uc.paradox(state.vec))
        uc_values.append(self.uc.flux(state.vec))
        uc_values.append(self.uc.contiguity(state.vec))
        uc_values.append(self.uc.complementarity(state.vec))
        uc_values.append(self.uc.incompleteness(state.vec))

        return np.array(uc_values)

    def check_halt_conditions(self, state: DimensionalState) -> Dict[str, bool]:
        """Check if oracle intervention is needed."""
        uc_vec = self.calculate_uc_vector(state)

        # Coherence collapse: high paradox and uncertainty together
        coherence_collapse = (uc_vec[8] > 0.8 and uc_vec[0] > 0.7)

        # Entropy spike: extremely high uncertainty
        entropy_spike = uc_vec[0] > 0.9

        # Paradox detection: high paradox value
        paradox_detected = uc_vec[8] > 0.85

        # Incompleteness crisis: near maximum incompleteness
        incompleteness_crisis = uc_vec[12] > 0.95

        # Golden ratio harmony check
        phi_resonance = False
        for i in range(len(uc_vec)-1):
            ratio = uc_vec[i] / (uc_vec[i+1] + 1e-10)
            if abs(ratio - PHI) < 0.1 or abs(ratio - PHI_INV) < 0.1:
                phi_resonance = True
                break

        return {
            'coherence_collapse': coherence_collapse,
            'entropy_spike': entropy_spike,
            'paradox_detected': paradox_detected,
            'incompleteness_crisis': incompleteness_crisis,
            'phi_resonance': phi_resonance,
            'halt': any([coherence_collapse, entropy_spike, paradox_detected, incompleteness_crisis])
        }

    def _attempt_tape_transition(self, state: DimensionalState, omega: int) -> Dict[str, Any]:
        """Apply modal dynamics for given ontological order."""
        dynamics = self.modal_dynamics.get(omega, [])

        # Check halt conditions first
        halt_check = self.check_halt_conditions(state)
        if halt_check['halt']:
            return {
                'omega': omega,
                'status': 'halted',
                'state': state,
                'halt_reason': halt_check
            }

        # Try each dynamic in sequence
        for i, dynamic in enumerate(dynamics):
            try:
                # Apply golden ratio threshold
                threshold = PHI_INV ** (i + 1) * (1 + state.rho / PHI)
                activation = np.mean(state.vec)

                if activation > threshold:
                    new_state = dynamic(state)
                    return {
                        'omega': omega,
                        'status': 'complete',
                        'state': new_state,
                        'dynamic_applied': dynamic.__name__
                    }
            except Exception as e:
                continue

        # If no dynamics succeeded, return with current state
        return {
            'omega': omega,
            'status': 'no_transition',
            'state': state
        }

    def process(self, initial_state: DimensionalState, max_steps: int = 100) -> List[Dict[str, Any]]:
        """Process computation across all 7 ontological tapes."""
        state = initial_state.copy()
        transcript = []

        for step in range(max_steps):
            step_record = {
                'step': step,
                'transitions': []
            }

            # Attempt transitions across all omega levels
            for omega in range(7):
                result = self._attempt_tape_transition(state, omega)
                step_record['transitions'].append(result)

                if result['status'] == 'halted':
                    # Oracle intervention needed
                    oracle_result = self.oracle.intervene(state, omega)
                    step_record['transitions'].append({
                        'omega': omega,
                        'oracle_intervention': oracle_result
                    })

                    if oracle_result['resolved']:
                        state = oracle_result['new_state']
                    else:
                        # Unresolvable halt
                        transcript.append(step_record)
                        return transcript

                elif result['status'] == 'complete':
                    state = result['state']

            # Record UC vector at end of step
            step_record['uc_vector'] = self.calculate_uc_vector(state).tolist()
            step_record['final_state'] = {
                'vec': state.vec.tolist(),
                'order': state.order,
                'freq': state.freq,
                'rho': state.rho
            }

            transcript.append(step_record)

            # Check for global convergence
            if step > 0:
                prev_vec = np.array(transcript[-2]['uc_vector'])
                curr_vec = np.array(transcript[-1]['uc_vector'])
                if np.allclose(prev_vec, curr_vec, atol=1e-6):
                    break

        return transcript

    def run_experiment(self, omega_start: int = 0, sigma_start: int = 1, steps: int = 50) -> Dict[str, Any]:
        """Run a complete PCTM4 experiment."""
        # Initialize starting state
        initial_state = self.initialize_state(omega_start, sigma_start)

        # Process through the engine
        transcript = self.process(initial_state, max_steps=steps)

        # Analyze results
        analysis = {
            'total_steps': len(transcript),
            'oracle_interventions': sum(
                1 for step in transcript
                for trans in step['transitions']
                if 'oracle_intervention' in trans
            ),
            'final_omega': transcript[-1]['final_state']['order'] if transcript else omega_start,
            'convergence_achieved': len(transcript) < steps,
            'transcript': transcript
        }

        return analysis

# Example usage
if __name__ == "__main__":
    # Create PCTM4 engine
    engine = PCTM4Engine()

    # Run experiment starting from Quantum order at Individual scale
    result = engine.run_experiment(
        omega_start=OmegaOrder.QUANTUM,
        sigma_start=SigmaScale.INDIVIDUAL,
        steps=30
    )

    print(f"PCTM4 Experiment Results:")
    print(f"Total steps: {result['total_steps']}")
    print(f"Oracle interventions: {result['oracle_interventions']}")
    print(f"Final omega level: {result['final_omega']}")
    print(f"Convergence achieved: {result['convergence_achieved']}")

    # Print first few steps
    for i, step in enumerate(result['transcript'][:3]):
        print(f"\nStep {i}:")
        for trans in step['transitions']:
            if 'dynamic_applied' in trans:
                print(f"  Omega {trans['omega']}: Applied {trans['dynamic_applied']}")
            elif 'oracle_intervention' in trans:
                oracle = trans['oracle_intervention']
                print(f"  Omega {trans['omega']}: Oracle - {oracle['oracle_message']}")
