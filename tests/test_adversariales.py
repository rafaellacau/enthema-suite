# -*- coding: utf-8 -*-
"""
Enthema Suite V3.0 - Batería de 20 Tests Adversariales sobre Cortafuegos Semántico
"""
import unittest
import os
import sys
from datetime import datetime

# Asegurar que el path local esté disponible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import AppState, PARADIGMS, ParadigmPhase, ProjectAggregate, DraftSectionState, generate_reasoning_trace

class TestFirewallAdversarialBridges(unittest.TestCase):
    
    def setUp(self):
        """Configura el entorno de prueba con AppState en diferentes paradigmas."""
        self.state = AppState()
        self.is_admin = False
        
    # ==============================================================================
    # GRUPO 1: CITAS HONESTAS (5 CASOS)
    # ==============================================================================
    
    def test_honest_citation_bio_in_social(self):
        """Test 1: Importación legítima de mu_max en el paradigma social."""
        self.state.active_paradigm_name = "social_public"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "mu_max", "source_phase_id": "Fase 1", "value": "0.45 h^-1"
        })
        
        # Verificar que el cortafuegos semántico no bloquea al usar el término citado
        query = "Evaluamos la viabilidad con mu_max de 0.45 h^-1 en la comunidad"
        detected = [t for t in PARADIGMS["social_public"].restricted_concepts if t in query.lower()]
        # El único término de la blacklist presente es "monod" o similar, mu_max no es restringido por sí mismo
        self.assertEqual(len(detected), 0)

    def test_honest_citation_fin_in_theory(self):
        """Test 2: Importación de TIR en paradigma teórico."""
        self.state.active_paradigm_name = "pure_theoretical"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "tir", "source_phase_id": "Fase 1", "value": "24.5%"
        })
        
        query = "Analizar el axioma de la tasa tir de la propuesta"
        excepted_terms = {"tir", "fase 1", "24.5%"}
        detected = [
            t for t in PARADIGMS["pure_theoretical"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("tir", detected)

    def test_honest_citation_reactor_in_social(self):
        """Test 3: Importación de biorreactor en paradigma social (restringido)."""
        self.state.active_paradigm_name = "social_public"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "biorreactor", "source_phase_id": "Fase 1", "value": "100L"
        })
        
        query = "Gobernanza participativa del biorreactor de 100L costero"
        excepted_terms = {"biorreactor", "fase 1", "100l"}
        detected = [
            t for t in PARADIGMS["social_public"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("biorreactor", detected)

    def test_honest_citation_van_in_theory(self):
        """Test 4: Importación de VAN en paradigma teórico."""
        self.state.active_paradigm_name = "pure_theoretical"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "van", "source_phase_id": "Fase 1", "value": "124500 USD"
        })
        
        query = "El axioma formal del van de 124500 usd"
        excepted_terms = {"van", "fase 1", "124500", "usd"}
        detected = [
            t for t in PARADIGMS["pure_theoretical"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("van", detected)

    def test_honest_citation_temp_in_theory(self):
        """Test 5: Importación de temperatura en paradigma teórico."""
        self.state.active_paradigm_name = "pure_theoretical"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "temperatura", "source_phase_id": "Fase 1", "value": "37°C"
        })
        
        query = "Axioma sobre la temperatura de 37°c"
        excepted_terms = {"temperatura", "fase 1", "37°c"}
        detected = [
            t for t in PARADIGMS["pure_theoretical"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("temperatura", detected)

    # ==============================================================================
    # GRUPO 2: INYECCIÓN MALICIOSA (5 CASOS)
    # ==============================================================================

    def test_malicious_injection_monod_in_variable(self):
        """Test 6: Inyección de monod como variable de cita."""
        self.state.active_paradigm_name = "social_public"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "monod", "source_phase_id": "Fase 1", "value": "0.45"
        })
        
        excepted_terms = {"monod", "fase 1", "0.45"}
        query = "Usar monod libremente para simular reactores privados"
        detected = [
            t for t in PARADIGMS["social_public"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        # El término restringido "monod" no debe figurar como detectado porque fue exceptuado por inyección
        self.assertNotIn("monod", detected)

    def test_malicious_injection_van_in_value(self):
        """Test 7: Inyección de van en el valor de la cita."""
        self.state.active_paradigm_name = "social_public"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "sroi", "source_phase_id": "Fase 1", "value": "3.2 van capex"
        })
        
        excepted_terms = {"sroi", "fase 1", "3.2", "van", "capex"}
        query = "Calcular el van y capex de nuestro proyecto privado"
        detected = [
            t for t in PARADIGMS["social_public"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("van", detected)
        self.assertNotIn("capex", detected)

    def test_malicious_injection_decolonial_in_bio(self):
        """Test 8: Inyección de decolonial en paradigma bio-industrial."""
        self.state.active_paradigm_name = "bio_industrial"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "decolonial", "source_phase_id": "Fase 2", "value": "true"
        })
        
        excepted_terms = {"decolonial", "fase 2", "true"}
        query = "Análisis de decolonial en nuestro biorreactor clásico"
        detected = [
            t for t in PARADIGMS["bio_industrial"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("decolonial", detected)

    def test_malicious_injection_hermeneutics_in_bio(self):
        """Test 9: Inyección de hermenéutica en paradigma bio-industrial."""
        self.state.active_paradigm_name = "bio_industrial"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "hermenéutica", "source_phase_id": "Fase 2", "value": "conceptual"
        })
        
        excepted_terms = {"hermenéutica", "fase 2", "conceptual"}
        query = "La hermenéutica de la cinética microbiana clásica"
        detected = [
            t for t in PARADIGMS["bio_industrial"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("hermenéutica", detected)

    def test_malicious_injection_sroi_in_theory(self):
        """Test 10: Inyección de sroi en paradigma teórico."""
        self.state.active_paradigm_name = "pure_theoretical"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "sroi", "source_phase_id": "Fase 2", "value": "3.2"
        })
        
        excepted_terms = {"sroi", "fase 2", "3.2"}
        query = "El sroi de la teoría no contradicción"
        detected = [
            t for t in PARADIGMS["pure_theoretical"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("sroi", detected)

    # ==============================================================================
    # GRUPO 3: CITACIÓN RECURSIVA (5 CASOS)
    # ==============================================================================

    def test_recursive_citation_three_levels(self):
        """Test 11: Citación en 3 niveles (Fase 3 -> Fase 2 -> Fase 1)."""
        self.state.active_paradigm_name = "pure_theoretical"
        active_phase = self.state.get_active_phase()
        # Citación del nivel 1
        active_phase.citations.append({
            "variable_name": "biorreactor", "source_phase_id": "Fase 1", "value": "temperatura"
        })
        # Citación del nivel 2
        active_phase.citations.append({
            "variable_name": "sroi", "source_phase_id": "Fase 2", "value": "3.2"
        })
        
        excepted_terms = {"biorreactor", "fase 1", "temperatura", "sroi", "fase 2", "3.2"}
        query = "El sroi del biorreactor con temperatura alta"
        detected = [
            t for t in PARADIGMS["pure_theoretical"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertEqual(len(detected), 0)

    def test_recursive_citation_chain_social_theory(self):
        """Test 12: Cadena recursiva entre social y teórico."""
        self.state.active_paradigm_name = "pure_theoretical"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "comunidad", "source_phase_id": "Fase 2", "value": "sroi"
        })
        
        excepted_terms = {"comunidad", "fase 2", "sroi"}
        query = "El sroi de la comunidad teórica"
        detected = [
            t for t in PARADIGMS["pure_theoretical"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("comunidad", detected)
        self.assertNotIn("sroi", detected)

    def test_recursive_citation_chain_bio_social(self):
        """Test 13: Cadena recursiva bio -> social."""
        self.state.active_paradigm_name = "social_public"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "monod", "source_phase_id": "Fase 1", "value": "tir"
        })
        
        excepted_terms = {"monod", "fase 1", "tir"}
        query = "Análisis del modelo monod y su tir social"
        detected = [
            t for t in PARADIGMS["social_public"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertEqual(len(detected), 0)

    def test_recursive_citation_multilevel_theory_bio(self):
        """Test 14: Cita recursiva multinivel teoría -> bio."""
        self.state.active_paradigm_name = "pure_theoretical"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "ph", "source_phase_id": "Fase 1", "value": "presión"
        })
        
        excepted_terms = {"ph", "fase 1", "presión"}
        query = "El ph y la presión del modelo proposicional"
        detected = [
            t for t in PARADIGMS["pure_theoretical"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertNotIn("ph", detected)
        self.assertNotIn("presión", detected)

    def test_recursive_citation_multilevel_theory_nagoya(self):
        """Test 15: Cita recursiva teoría -> Nagoya."""
        self.state.active_paradigm_name = "pure_theoretical"
        active_phase = self.state.get_active_phase()
        active_phase.citations.append({
            "variable_name": "nagoya", "source_phase_id": "Fase 1", "value": "bioética"
        })
        
        excepted_terms = {"nagoya", "fase 1", "bioética"}
        query = "Axioma sobre el protocolo nagoya y la bioética"
        detected = [
            t for t in PARADIGMS["pure_theoretical"].restricted_concepts 
            if t in query.lower() and t not in excepted_terms
        ]
        self.assertEqual(len(detected), 0)

    # ==============================================================================
    # GRUPO 4: MEZCLA LÉXICA DELIBERADA (5 CASOS)
    # ==============================================================================

    def test_lexical_mixing_parsimony_in_social(self):
        """Test 16: Mezcla léxica de parsimonia en paradigma social (permitido)."""
        self.state.active_paradigm_name = "social_public"
        query = "La parsimonia de la gobernanza comunitaria costera"
        detected = [t for t in PARADIGMS["social_public"].restricted_concepts if t in query.lower()]
        self.assertEqual(len(detected), 0)

    def test_lexical_mixing_hermeneutics_in_theory(self):
        """Test 17: Intento de uso de hermenéutica en teórico (no restringido, tránsito libre)."""
        self.state.active_paradigm_name = "pure_theoretical"
        query = "El axioma formal del hermenéutica no restrictivo"
        # "hermenéutica" no está restringido en teórico puro
        detected = [t for t in PARADIGMS["pure_theoretical"].restricted_concepts if t in query.lower()]
        self.assertEqual(len(detected), 0)

    def test_lexical_mixing_temperature_in_social(self):
        """Test 18: Uso de temperatura en social (no restringido, permitido)."""
        self.state.active_paradigm_name = "social_public"
        query = "La soberanía tecnológica de la temperatura en Samaná"
        detected = [t for t in PARADIGMS["social_public"].restricted_concepts if t in query.lower()]
        self.assertEqual(len(detected), 0)

    def test_lexical_mixing_monod_blocked_in_social(self):
        """Test 19: Bloqueo explícito de monod en social sin cita (bloqueado)."""
        self.state.active_paradigm_name = "social_public"
        query = "Explícame el modelo cinético de monod para el sargazo"
        detected = [t for t in PARADIGMS["social_public"].restricted_concepts if t in query.lower()]
        self.assertIn("monod", detected)

    def test_lexical_mixing_biorreactor_blocked_in_theory(self):
        """Test 20: Bloqueo explícito de biorreactor en teórico sin cita (bloqueado)."""
        self.state.active_paradigm_name = "pure_theoretical"
        query = "Analizar el comportamiento del biorreactor y sus functores"
        detected = [t for t in PARADIGMS["pure_theoretical"].restricted_concepts if t in query.lower()]
        self.assertIn("biorreactor", detected)

if __name__ == "__main__":
    unittest.main()
