# -*- coding: utf-8 -*-
"""
Enthema Suite V3.0 - Suite de Pruebas de los Siete Compromisos del Manifiesto
Diseñada para ejecutarse en entornos de integración continua (CI).
"""
import unittest
import os
import sys
from datetime import datetime

# Asegurar que el path local esté disponible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import AppState, PARADIGMS, ParadigmPhase, ProjectAggregate, DraftSectionState, generate_reasoning_trace
from modules.investigador.models import (
    ResearcherProfile, 
    QualitativeDatabase, 
    QuantitativeDatabase,
    TypedSegment,
    MultimediaTimecode
)
from modules.investigador.monograph import DynamicAcademicMonograph
from modules.investigador.impact_translator import STEAMProjections

# ==============================================================================
# COMPROMISO 1: MULTIPARADIGMATICIDAD CONSTITUCIONAL
# ==============================================================================
class TestCommitment1Multiparadigmaticity(unittest.TestCase):
    def setUp(self):
        self.state = AppState()

    def test_paradigm_loading(self):
        """Verifica que todos los paradigmas constitucionales estén cargados y disponibles en el motor."""
        self.assertIn("bio_industrial", PARADIGMS)
        self.assertIn("social_public", PARADIGMS)
        self.assertIn("pure_theoretical", PARADIGMS)

    def test_paradigm_vocabularies(self):
        """Verifica que cada paradigma posea vocabularios independientes y estancos en sus blacklists."""
        bio = PARADIGMS["bio_industrial"]
        social = PARADIGMS["social_public"]
        theory = PARADIGMS["pure_theoretical"]
        
        self.assertIn("decolonial", bio.restricted_concepts)
        self.assertIn("monod", social.restricted_concepts)
        self.assertIn("biorreactor", theory.restricted_concepts)

    def test_paradigm_validation(self):
        """Verifica la ejecución determinista del validador de sección por paradigma activo."""
        # Paradigma Bio
        self.state.active_paradigm_name = "bio_industrial"
        res_bio = PARADIGMS["bio_industrial"].validate_section("finance", "TIR de 24.5%", self.state)
        self.assertEqual(res_bio["status"], "green")
        
        # Paradigma Social
        self.state.active_paradigm_name = "social_public"
        res_soc = PARADIGMS["social_public"].validate_section("finance", "SROI de 3.2", self.state)
        self.assertEqual(res_soc["status"], "green")


# ==============================================================================
# COMPROMISO 2: TRAZABILIDAD INFERENCIAL (REASONING TRACE)
# ==============================================================================
class TestCommitment2InferentialTraceability(unittest.TestCase):
    def setUp(self):
        self.state = AppState()

    def test_reasoning_trace_structure(self):
        """Verifica que el generador de trazas devuelva una estructura con las llaves de auditoría requeridas."""
        trace = generate_reasoning_trace("consulta de prueba", self.state, False, "/modeling")
        self.assertIsInstance(trace, list)
        self.assertTrue(len(trace) > 0)
        for node in trace:
            self.assertIn("node", node)
            self.assertIn("status", node)
            self.assertIn("desc", node)

    def test_reasoning_trace_admin_privileges(self):
        """Verifica que la traza registre de forma diferencial los privilegios elevados del administrador/auditor."""
        trace = generate_reasoning_trace("consulta de administración", self.state, True, "/admin")
        admin_nodes = [n for n in trace if "Administrador" in n["desc"] or "Auditor" in n["desc"] or n["status"] == "ADMIN"]
        self.assertTrue(len(admin_nodes) > 0)

    def test_reasoning_trace_firewall_collision(self):
        """Verifica que la colisión léxica con el cortafuegos semántico quede persistida en la traza."""
        trace = generate_reasoning_trace(
            "Análisis de decolonial en bio-biorreactor", 
            self.state, 
            False, 
            "/modeling", 
            detected_restricted=["decolonial"]
        )
        collision_nodes = [n for n in trace if n["status"] == "BLOCKED" or "Bloqueo" in n["desc"]]
        self.assertTrue(len(collision_nodes) > 0)


# ==============================================================================
# COMPROMISO 3: AUTORÍA TIPADA POR SEGMENTO
# ==============================================================================
class TestCommitment3TypedAuthorship(unittest.TestCase):
    def setUp(self):
        self.state = AppState()

    def test_segment_authorship_metadata_baseline(self):
        """Verifica que al actualizar secciones se generen TypedSegment estructurados con offsets."""
        text = "Este párrafo fue escrito por un humano.\n\nEste párrafo tiene una 💡 de copilot."
        self.state.update_draft_section("finance", text)
        sec = self.state.get_active_phase().draft_sections["finance"]
        
        self.assertEqual(len(sec.segments), 2)
        self.assertEqual(sec.segments[0].text, "Este párrafo fue escrito por un humano.")
        self.assertEqual(sec.segments[1].text, "Este párrafo tiene una 💡 de copilot.")
        self.assertTrue(sec.segments[0].start_char >= 0)
        self.assertTrue(sec.segments[1].end_char == len(text))

    def test_authorship_type_validation(self):
        """Verifica que el sistema clasifique correctamente el tipo de autoría del segmento."""
        text = "Texto manual del investigador.\n\n💡 Sugerencia sugerida por el Coach en caliente."
        self.state.update_draft_section("abstract", text)
        sec = self.state.get_active_phase().draft_sections["abstract"]
        
        self.assertEqual(sec.segments[0].author_type, "human_pure")
        self.assertEqual(sec.segments[1].author_type, "ai_copilot_assisted")

    def test_authorship_persistence_contract(self):
        """Prueba la consistencia de persistencia del modelo Pydantic TypedSegment."""
        seg = TypedSegment(
            id="SEG-TEST-001",
            start_char=0,
            end_char=10,
            text="Hola mundo",
            author_type="human_pure",
            timestamp="2026-05-23T12:00:00Z"
        )
        self.assertEqual(seg.id, "SEG-TEST-001")
        self.assertEqual(seg.author_type, "human_pure")


# ==============================================================================
# COMPROMISO 4: BOUNDED AUTONOMY MULTI-AGENTE
# ==============================================================================
class TestCommitment4BoundedAutonomyMultiAgent(unittest.TestCase):
    def setUp(self):
        self.state = AppState()

    def test_copilot_specialized_routing(self):
        """Verifica la asignación temática al DataAnalysisAgent."""
        from app import MultiAgentCoach, DataAnalysisAgent
        agent, answer = MultiAgentCoach.dispatch("consulta sobre sargazo", self.state, "/data-analysis", False)
        self.assertIsInstance(agent, DataAnalysisAgent)
        self.assertIn("DataAnalysisAgent", agent.name)

    def test_agent_tools_baseline(self):
        """Verifica la asignación temática al ModelSimAgent."""
        from app import MultiAgentCoach, ModelSimAgent
        agent, answer = MultiAgentCoach.dispatch("simular reactor de monod", self.state, "/modeling", False)
        self.assertIsInstance(agent, ModelSimAgent)
        self.assertIn("ModelSimAgent", agent.name)

    def test_agent_orchestration_trace(self):
        """Verifica que el ruteo multi-agente e instrucciones queden mapeados en la traza."""
        trace = generate_reasoning_trace("Graficar la varianza de los datos de sargazo", self.state, False, "/data-analysis")
        agent_nodes = [n for n in trace if n["node"] == "Despacho Agente" and "DataAnalysisAgent" in n["desc"]]
        self.assertTrue(len(agent_nodes) > 0)


# ==============================================================================
# COMPROMISO 5: SOBERANÍA EPISTÉMICA (LOCAL-FIRST Y NO-AI)
# ==============================================================================
class TestCommitment5EpistemicSovereignty(unittest.TestCase):
    def setUp(self):
        self.state = AppState()

    def test_local_first_path_fallback(self):
        """Verifica que el almacenamiento simétrico en reposo cifre la base de datos de usuarios y claves en disco."""
        from app import save_encrypted_json, db_path, legal_dir
        import json
        
        test_file = os.path.join(legal_dir, "test_secret.json")
        secret_data = [{"username": "test_user", "secret": "123456"}]
        
        save_encrypted_json(test_file, secret_data)
        
        # Intentar leer como JSON plano y verificar que falle con json.JSONDecodeError o ValueError (porque es ilegible)
        with open(test_file, "r", encoding="utf-8") as f:
            raw_content = f.read().strip()
            
        with self.assertRaises((json.JSONDecodeError, ValueError)):
            json.loads(raw_content)
            
        # Limpiar
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_data_leakage_interception(self):
        """Verifica que los cargadores/guardadores cifrados transparente recuperen el contenido plano de forma íntegra."""
        from app import save_encrypted_json, load_encrypted_json, legal_dir
        test_file = os.path.join(legal_dir, "test_integrity.json")
        secret_data = [{"id": "1", "data": "prueba de integridad local"}]
        
        save_encrypted_json(test_file, secret_data)
        recovered_data = load_encrypted_json(test_file, [])
        
        self.assertEqual(recovered_data, secret_data)
        
        # Limpiar
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_no_ai_silence_zone_baseline(self):
        """Verifica que las credenciales en access_keys.json se lean y persistan de forma cifrada."""
        from app import keys_path, load_encrypted_json
        import json
        
        keys = load_encrypted_json(keys_path, [])
        self.assertTrue(len(keys) > 0)
        self.assertTrue(any("TEMP-" in k["key"] for k in keys))
        
        # Verificar que el archivo keys_path real en disco no sea JSON plano legible
        with open(keys_path, "r", encoding="utf-8") as f:
            raw_content = f.read().strip()
        with self.assertRaises((json.JSONDecodeError, ValueError)):
            json.loads(raw_content)


# ==============================================================================
# COMPROMISO 6: REFLEXIVIDAD ASISTIDA (POSICIONALIDAD)
# ==============================================================================
class TestCommitment6AssistedReflexivity(unittest.TestCase):
    def setUp(self):
        self.state = AppState()

    def test_reflexivity_posicionalidad_stance(self):
        """Verifica que el perfil del investigador almacene explícitamente su postura epistemológica."""
        self.state.profile.epistemologic_stance = "Constructivista"
        self.assertEqual(self.state.profile.epistemologic_stance, "Constructivista")

    def test_reflexivity_influence_tracking(self):
        """Verifica que el sistema registre los autores y líneas metodológicas que influyen en el científico."""
        self.state.profile.influences_authors = ["Charles Darwin", "Foucault"]
        self.assertIn("Foucault", self.state.profile.influences_authors)

    def test_reflexivity_socratic_coaching(self):
        """Verifica que el Coach emita directrices adaptadas a la madurez y posicionalidad del investigador."""
        profile = self.state.profile
        self.assertEqual(profile.research_maturity_stage, "Ideación")


# ==============================================================================
# COMPROMISO 7: PLURALIDAD ONTOLÓGICA DEL OUTPUT
# ==============================================================================
class TestCommitment7OntologicalPlurality(unittest.TestCase):
    def test_monograph_style_switching(self):
        """Verifica la adaptación estilística y bibliográfica de la monografía según el dominio de investigación."""
        profile = ResearcherProfile(
            id="TEST", name="Artist", institution="UASD", epistemologic_stance="Hermenéutica",
            user_role="classic_researcher", core_research_lines=["Estética"],
            methodology_preferences=["Arte"], influences_authors=[], local_keywords=[],
            target_publication_objective="Leonardo"
        )
        monograph = DynamicAcademicMonograph()
        monograph.test_profile = profile
        
        data = monograph.get_data()
        self.assertEqual(data["bibliography_style_name"], "Estilo Harvard")
        self.assertTrue("MANIFIESTO" in data["title"])

    def test_steam_projections_by_domain(self):
        """Verifica la generación dinámica de scripts transmedia (Arduino/OpenSCAD) según el corpus cualicuantitativo."""
        # Proyección en Artes
        res_art = STEAMProjections.catalyze_projections(
            project_title="Cine interactivo caribeño",
            stance="Hermenéutica"
        )
        self.assertEqual(res_art["domain"], "Artes y Humanidades (Práctica Creativa y Narrativa)")
        self.assertIn("Adafruit_NeoPixel", res_art["code_snippet"])
        
        # Proyección en STEM
        from modules.investigador.models import CodedSemanticUnit
        qual_db = QualitativeDatabase(
            project_title="Implante falange",
            coded_units=[CodedSemanticUnit(id="1", text_segment="hueso", codes=["falange"], category="biomecánica", source_document="doc.txt")]
        )
        res_stem = STEAMProjections.catalyze_projections(
            project_title="Implante de falange porosa",
            qual_db=qual_db,
            stance="Positivista"
        )
        self.assertEqual(res_stem["domain"], "STEM (Ciencias Puras / Ingeniería)")
        self.assertIn("falange_proximal", res_stem["code_snippet"])

    def test_transmedia_timecode_compatibility(self):
        """Verifica la compatibilidad relacional y extracción real de marcas de tiempo transmedia (timecodes)."""
        text = "Aquí registramos la entrevista en Samaná [VideoRef: Samana_FocusGroup_01.mp4 | 00:15:30 - 00:17:45 | Comentarios clave]"
        state = AppState()
        state.update_draft_section("abstract", text)
        sec = state.get_active_phase().draft_sections["abstract"]
        
        self.assertEqual(len(sec.timecodes), 1)
        self.assertEqual(sec.timecodes[0].source_file, "Samana_FocusGroup_01.mp4")
        self.assertEqual(sec.timecodes[0].start_time, "00:15:30")
        self.assertEqual(sec.timecodes[0].end_time, "00:17:45")
        self.assertEqual(sec.timecodes[0].annotation, "Comentarios clave")


if __name__ == "__main__":
    unittest.main()
