# Core module initialization
from .virtual_patient import VirtualPatient, PatientProfile, LifestyleFactors
from .health_state import HealthState, HealthStateModel
from .temporal_engine import TemporalEvolutionEngine, Trajectory
from .health_memory import HealthMemory, HealthSnapshot

__all__ = [
    'VirtualPatient',
    'PatientProfile', 
    'LifestyleFactors',
    'HealthState',
    'HealthStateModel',
    'TemporalEvolutionEngine',
    'Trajectory',
    'HealthMemory',
    'HealthSnapshot'
]
