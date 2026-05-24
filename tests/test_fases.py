import sys
import os
from datetime import datetime

# Agregar la ruta base al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import AppState, PARADIGMS, ParadigmPhase, ProjectAggregate, DraftSectionState

def test_state_initialization():
    state = AppState()
    assert state.project_aggregate.active_phase_id == "Fase 1"
    assert len(state.project_aggregate.phases) == 1
    assert state.active_paradigm_name == "bio_industrial"
    assert "abstract" in state.draft_sections
    print("✓ Inicialización de AppState exitosa.")

def test_phase_properties():
    state = AppState()
    # Cambiar paradigma en caliente mediante propiedad (retrocompatibilidad)
    state.active_paradigm_name = "social_public"
    assert state.active_paradigm_name == "social_public"
    
    # Verificar que la fase activa en el agregado se actualizó
    active_phase = state.get_active_phase()
    assert active_phase.paradigm_name == "social_public"
    print("✓ Propiedades dinámicas de AppState operando con retrocompatibilidad.")

if __name__ == "__main__":
    print("=== Iniciando Pruebas de Bounded Contexts ===")
    test_state_initialization()
    test_phase_properties()
    print("=== Todas las pruebas pasaron con éxito ===")
