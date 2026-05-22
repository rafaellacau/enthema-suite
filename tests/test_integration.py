# -*- coding: utf-8 -*-
"""
Enthema Suite V2.0 - Suite de Pruebas de Integración Extremo a Extremo
"""
import unittest
import os
import sys
import pandas as pd
import numpy as np
import io

# Asegurar que el path local esté disponible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.investigador.models import (
    ResearcherProfile, 
    ConsortiumProfile, 
    QualitativeDatabase, 
    QuantitativeDatabase,
    CodedSemanticUnit,
    VariableMetadata
)
from modules.investigador.profile_builder import CognitiveInterviewer, PassiveProfileExtractor
from modules.investigador.db_builder import QualitativeEncoder, DueDiligenceEncoder, FinancialFeasibilityProfiler, QuantitativeProfiler
from modules.investigador.network_analyst import SemanticGraphEngine
from modules.investigador.impact_translator import PatentingTranslator, InvestmentMemorandumTranslator, STEAMProjections, ResearchDisseminator

class TestEnthemaSuiteIntegration(unittest.TestCase):
    
    def setUp(self):
        """Inicializar perfiles y datos de prueba base."""
        self.classic_profile_base = ResearcherProfile(
            id="INV-TEST-001",
            name="Dr. Test Intec",
            institution="INTEC",
            epistemologic_stance="Constructivista",
            user_role="classic_researcher",
            core_research_lines=["Quelación de metales pesados en sargazo"],
            methodology_preferences=["Cualitativo inductivo"],
            influences_authors=["Charles Darwin"],
            local_keywords=["sargazo", "metales_pesados"]
        )
        
        self.consultant_profile_base = ResearcherProfile(
            id="CONS-TEST-002",
            name="Ing. Test Rosario",
            institution="Rosario Partners",
            epistemologic_stance="Mixed_Methods",
            user_role="investment_consultant",
            core_research_lines=["Sostenibilidad y ESG"],
            methodology_preferences=["Estudio de impacto social y financiero"],
            influences_authors=["IFC Standards"],
            local_keywords=["esg", "finanzas", "bid", "samaná"]
        )

    def test_phase_1_passive_profile_extraction(self):
        """Verifica la ingesta pasiva de perfiles desde Obsidian markdown, Zotero RIS y Zotero BibTeX."""
        # 1. Test Obsidian Ingestion
        obsidian_content = """---
nombre: "Dra. Test Obsidian"
institución: "UNIBE"
rol: "classic_researcher"
postura: "Positivista"
---
## Líneas de Investigación
- Valorización bioquímica de macroalgas

## Influencias y Autores
- Dr. Woodward

## Palabras Clave
- sargazo
- química
"""
        test_profile = ResearcherProfile(
            id="PAS-TEST-001", name="", institution="", core_research_lines=[], 
            methodology_preferences=[], influences_authors=[], local_keywords=[]
        )
        up_profile, ok, msg = PassiveProfileExtractor.parse_obsidian_markdown(obsidian_content, test_profile)
        self.assertTrue(ok)
        self.assertEqual(up_profile.name, "Dra. Test Obsidian")
        self.assertEqual(up_profile.epistemologic_stance, "Positivista")
        self.assertIn("sargazo", up_profile.local_keywords)
        self.assertIn("Valorización bioquímica de macroalgas", up_profile.core_research_lines)

        # 2. Test Zotero RIS Ingestion
        ris_content = """TY  - JOUR
AU  - Margulis, Lynn
TI  - Cybernetic biopolymers in coastal sargazo
KW  - climate_regression
KW  - statistical_models
ER  - """
        test_profile_ris = ResearcherProfile(
            id="PAS-TEST-002", name="", institution="", core_research_lines=[], 
            methodology_preferences=[], influences_authors=[], local_keywords=[]
        )
        up_profile_ris, ok, msg = PassiveProfileExtractor.parse_zotero_ris(ris_content, test_profile_ris)
        self.assertTrue(ok)
        self.assertIn("Margulis, Lynn", up_profile_ris.influences_authors)
        self.assertIn("climate_regression", up_profile_ris.local_keywords)

        # 3. Test Zotero BibTeX Ingestion
        bibtex_content = """@article{test2026,
  author = {Sarah Jenkins},
  title = {Quantitative risk assessment in Caribbean loans},
  keywords = {esg, finance, irr, npv},
  journal = {Journal of Finance}
}"""
        test_profile_bib = ResearcherProfile(
            id="PAS-TEST-003", name="", institution="", user_role="investment_consultant", 
            core_research_lines=[], methodology_preferences=[], influences_authors=[], local_keywords=[]
        )
        up_profile_bib, ok, msg = PassiveProfileExtractor.parse_zotero_bibtex(bibtex_content, test_profile_bib)
        self.assertTrue(ok)
        self.assertIn("Sarah Jenkins", up_profile_bib.influences_authors)
        self.assertIn("esg", up_profile_bib.local_keywords)

        # 4. Test Jupyter Notebook (.ipynb) Ingestion
        jupyter_content = """{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Dr. Francisco González\\n",
    "## Institución: Instituto Tecnológico de Santo Domingo (INTEC)\\n",
    "## Rol: classic_researcher\\n",
    "## Postura: Positivista\\n",
    "## Orcid: 0000-0002-1823-4567\\n",
    "## DOIs: 10.1016/j.jbiomech.2014.12.013\\n",
    "\\n",
    "### Líneas de Investigación\\n",
    "- Diseño y simulación paramétrica de prótesis articulares personalizadas"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\\n",
    "import numpy as np\\n",
    "print('Loaded')"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 2
}"""
        test_profile_jup = ResearcherProfile(
            id="PAS-TEST-004", name="", institution="", user_role="classic_researcher", 
            core_research_lines=[], methodology_preferences=[], influences_authors=[], local_keywords=[]
        )
        up_profile_jup, ok, msg = PassiveProfileExtractor.parse_jupyter_notebook(jupyter_content, test_profile_jup)
        self.assertTrue(ok)
        self.assertEqual(up_profile_jup.name, "Dr. Francisco González")
        self.assertEqual(up_profile_jup.institution, "Instituto Tecnológico de Santo Domingo (INTEC)")
        self.assertIn("Pandas", up_profile_jup.methodology_preferences)
        self.assertIn("NumPy", up_profile_jup.methodology_preferences)

    def test_phase_2_empirical_databases_encoding(self):

        """Verifica la codificación temática cualitativa, profiler cuantitativo y auditorías ESG."""
        # 1. Grounded Theory Qualitative Encoding
        transcript = "El sargazo llega de golpe e interfiere con la pesca en Barahona. El plomo y cadmio causan toxicidad."
        qual_db = QualitativeEncoder.encode_text("Sargazo Barahona", "transcripcion.txt", transcript)
        self.assertEqual(qual_db.project_title, "Sargazo Barahona")
        self.assertTrue(len(qual_db.coded_units) > 0)
        self.assertTrue(any("plomo" in unit.text_segment.lower() or "cadmio" in unit.text_segment.lower() for unit in qual_db.coded_units))

        # 2. Quantitative Profiler (Tomographic Winsorization and Imputation)
        csv_data = """Muestra,Plomo_ppm,Cadmio_ppm
M1,1.2,0.4
M2,1.5,0.5
M3,1.1,
M4,-0.5,0.4
M5,20.0,0.6
"""
        df = pd.read_csv(io.StringIO(csv_data))
        quant_db, df_clean = QuantitativeProfiler.profile_dataframe("Química Sargazo", df, "CSV")
        self.assertEqual(quant_db.project_title, "Química Sargazo")
        self.assertFalse(df_clean.isnull().values.any())  # Imputación completada
        self.assertTrue((df_clean["Plomo_ppm"] >= 0).all())  # Valor negativo -0.5 corregido
        self.assertTrue(df_clean["Plomo_ppm"].max() < 20.0)  # Winsorization del outlier 20.0

        # 3. ESG Due Diligence
        esg_text = "Riesgo E: Deforestación y pérdida de biodiversidad. Riesgo S: Desplazamiento forzado de familias de agricultores sin consulta previa."
        qual_db_esg = DueDiligenceEncoder.encode_consultancy_text("Samaná ESG", "esg.txt", esg_text)
        self.assertEqual(qual_db_esg.project_title, "Samaná ESG")
        self.assertTrue(len(qual_db_esg.coded_units) > 0)
        self.assertTrue(any("ambiental" in code.lower() or "social" in code.lower() for unit in qual_db_esg.coded_units for code in unit.codes))

    def test_phase_3_financial_feasibility_newton_raphson(self):
        """Prueba de cálculo financiero multiperiodo TIR y VAN usando el solver Newton-Raphson."""
        cash_flow = """Periodo,Ingresos,Egresos
Año 0,0,100000
Año 1,40000,10000
Año 2,45000,11000
Año 3,50000,12000
Año 4,55000,13000
Año 5,60000,14000
"""
        df = pd.read_csv(io.StringIO(cash_flow))
        discount_rate = 0.10
        quant_db, df_clean, van, tir, dictamen = FinancialFeasibilityProfiler.profile_financials(
            "Finanzas Proyecto", df, discount_rate
        )
        self.assertGreater(van, 0)
        self.assertGreater(tir, 0)
        self.assertIn("VIABLE", dictamen)
        self.assertTrue(len(quant_db.variables) > 0)

    def test_phase_4_semantic_graph_consortium_engine(self):
        """Verifica la construcción del grafo del consorcio semántico y vacíos estructurales."""
        bio_profile = ResearcherProfile(
            id="INV-BIO-TEST",
            name="Dra. Bio Test",
            institution="UNIBE",
            epistemologic_stance="Positivista",
            core_research_lines=["Quelación de metales pesados en sargazo", "Extracción bioquímica de macroalgas"],
            methodology_preferences=["Experimental cromatográfica"],
            influences_authors=["Dr. Woodward"],
            local_keywords=["sargazo", "química", "cromatografía"]
        )
        
        consortium = ConsortiumProfile(
            project_title="Proyecto Colectivo Sargazo",
            funding_agency="FONDOCYT",
            lead_researcher_id=self.classic_profile_base.id,
            members=[self.classic_profile_base, bio_profile],
            synergy_nodes=[],
            detected_gaps=[],
            total_budget_usd=120000.0,
            duration_months=12
        )
        
        G, synergies, gaps = SemanticGraphEngine.build_consortium_graph(consortium)
        self.assertGreater(G.number_of_nodes(), 0)
        self.assertGreater(G.number_of_edges(), 0)
        self.assertTrue(len(synergies) > 0)
        self.assertTrue(any(s.lower() == "sargazo" for s in synergies))

    def test_phase_5_translators_and_steam_abm_generation(self):
        """Prueba de acoplamiento de salidas: patente ONAPI, memorando, difusor y simulación ABM enriquecida."""
        # 1. Patent Draft
        qual_db = QualitativeDatabase(
            project_title="Patente Sargazo",
            coded_units=[
                CodedSemanticUnit(
                    id="1",
                    text_segment="Metales pesados en costas dominicanas",
                    codes=["metales_pesados", "sargazo"],
                    category="Contaminación",
                    source_document="data.txt"
                )
            ],
            theme_network={},
            esg_issues=[]
        )
        quant_db = QuantitativeDatabase(
            project_title="Datos Patente",
            dataset_format="CSV",
            total_records=1,
            variables=[
                VariableMetadata(
                    name="densidad_osea",
                    data_type="float",
                    description="Densidad ósea",
                    valid_range="0-2",
                    missing_count=0
                )
            ],
            anomalies_detected=[]
        )
        patent = PatentingTranslator.generate_patent_draft("Valorización Sargazo", qual_db, quant_db, "Constructivista")
        self.assertTrue(len(patent["title"]) > 0)
        self.assertTrue(len(patent["abstract"]) > 0)
        self.assertTrue(len(patent["description"]) > 0)
        self.assertTrue(len(patent["claims"]) > 0)

        # 2. Investment Memorandum
        memo = InvestmentMemorandumTranslator.generate_investment_memorandum(
            "Proyecto Samaná", qual_db, quant_db, 2000000.0, "BID", "Rosario", 450000.0, 0.22, "VIABLE"
        )
        self.assertIn("MEMORANDO", memo["title"])
        self.assertIn("VIABLE", memo["brief"])

        # 3. STEAM Projections (Mesa Agent Code Generator)
        steam = STEAMProjections.catalyze_projections("Dinámicas Sociales Sargazo", qual_db, quant_db, "Constructivista")
        self.assertEqual(steam["domain"], "Ciencias Sociales (Estudios de Agentes y Políticas)")
        self.assertIn("HogarAgente", steam["code_snippet"])
        self.assertIn("PymeAgente", steam["code_snippet"])
        self.assertIn("ejecutar_simulacion", steam["code_snippet"])
        self.assertIn("fondocyt_subsidio", steam["code_snippet"])

        # 4. Disseminator (Abstract, Pitch, Social Media)
        dissemination = ResearchDisseminator.generate_dissemination_channels(
            "Proyecto Difusión", self.classic_profile_base, qual_db, quant_db, 150000.0
        )
        self.assertIn("ARTÍCULO CIENTÍFICO", dissemination["abstract_title"])
        self.assertTrue(len(dissemination["hilo_x"]) >= 3)
        self.assertTrue(len(dissemination["pitch_deck"]) >= 4)
        self.assertIn("COMUNICADO DE PRENSA", dissemination["press_release"])

    def test_art_and_humanities_onda_translation(self):
        """Verifica la generación del Manifiesto Estético y Registro ONDA para proyectos de Arte."""
        qual_db = QualitativeDatabase(
            project_title="Análisis de la vanguardia pictórica caribeña",
            coded_units=[
                CodedSemanticUnit(
                    id="1",
                    text_segment="La composición formal en la pintura vanguardista muestra una ruptura cromática",
                    codes=["vanguardia", "estética", "pintura"],
                    category="Estética",
                    source_document="critica.txt"
                )
            ],
            theme_network={},
            esg_issues=[]
        )
        quant_db = QuantitativeDatabase(
            project_title="Métricas Estéticas",
            dataset_format="CSV",
            total_records=10,
            variables=[
                VariableMetadata(
                    name="Composición_Aurea",
                    data_type="float",
                    description="Proporción áurea de encuadres",
                    valid_range="0-1",
                    missing_count=0
                )
            ],
            anomalies_detected=[]
        )
        
        # Test 1: Hermeneutic stance triggers is_art
        patent = PatentingTranslator.generate_patent_draft("Estudio Crítico", qual_db, quant_db, "Hermenéutica")
        self.assertTrue(patent.get("is_art", False))
        self.assertIn("ONDA", patent["title"])
        self.assertIn("Manifiesto", patent["description"])
        self.assertIn("Originalidad", patent["claims"])
        
        # Test 2: Art keywords in title trigger is_art even in generic stance
        patent_keywords = PatentingTranslator.generate_patent_draft("Análisis Fílmico y Pintura de Vanguardia", qual_db, quant_db, "Positivista")
        self.assertTrue(patent_keywords.get("is_art", False))
        self.assertIn("ONDA", patent_keywords["title"])
        self.assertIn("fílmico", patent_keywords["abstract"].lower())
        
        # Test 3: STEAM projection for art domain
        steam = STEAMProjections.catalyze_projections("Instalación Cromática Vanguardista", qual_db, quant_db, "Hermenéutica")
        self.assertEqual(steam["domain"], "Artes y Humanidades (Práctica Creativa y Narrativa)")
        self.assertIn("Adafruit_NeoPixel", steam["code_snippet"])

    def test_legal_act_and_cloud_db_persistence(self):
        """Verifica la persistencia física local y el mock de base de datos NoSQL cloud para las actas firmadas."""
        from modules.investigador.ethical_declaration import archive_signed_legal_act
        import json
        import shutil

        # 1. Asegurar limpieza o estado inicial
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        legal_dir = os.path.join(BASE_DIR, "output", "legal")
        if os.path.exists(legal_dir):
            shutil.rmtree(legal_dir)

        self.assertFalse(os.path.exists(legal_dir))

        # 2. Generar datos ficticios
        profile = ResearcherProfile(
            id="INV-LEGAL-TEST",
            name="Dr. Francisco González",
            institution="INTEC",
            epistemologic_stance="Constructivista",
            user_role="classic_researcher",
            research_maturity_stage="Ideación",
            target_publication_objective="ONAPI",
            legal_terms_accepted=True,
            electronic_signature_name="Dr. Francisco González (Firmado Digitalmente)",
            orcid="0000-0002-1823-4567"
        )
        project_title = "Diseño de Prótesis Paramétrica"
        qr_svg_mock = "<svg>mock qr</svg>"

        # 3. Invocar almacenamiento
        filepath, hash_proyecto, cloud_record = archive_signed_legal_act(
            profile=profile,
            project_title=project_title,
            qr_svg=qr_svg_mock,
            db_qual_hash="GT-QUAL-HASH-12345",
            db_quant_hash="GT-QUANT-HASH-67890"
        )

        # 4. Verificar que se creó la carpeta y el archivo HTML físico
        self.assertTrue(os.path.exists(legal_dir))
        self.assertTrue(os.path.exists(filepath))
        self.assertIn(hash_proyecto, filepath)

        # Verificar contenido HTML
        with open(filepath, "r", encoding="utf-8") as f:
            html_content = f.read()
            self.assertIn(hash_proyecto, html_content)
            self.assertIn("Dr. Francisco González", html_content)
            self.assertIn("GT-QUAL-HASH-12345", html_content)

        # 5. Verificar base de datos NoSQL mock persistida
        mock_db_path = os.path.join(legal_dir, "cloud_database_mock.json")
        self.assertTrue(os.path.exists(mock_db_path))

        with open(mock_db_path, "r", encoding="utf-8") as rf:
            db_data = json.load(rf)
            self.assertTrue(isinstance(db_data, list))
            self.assertTrue(len(db_data) > 0)
            
            latest_record = db_data[-1]
            self.assertEqual(latest_record["hash_proyecto"], hash_proyecto)
            self.assertEqual(latest_record["investigator"]["name"], "Dr. Francisco González")
            self.assertEqual(latest_record["database_signatures"]["qualitative_sha256"], "GT-QUAL-HASH-12345")
            self.assertEqual(latest_record["electronic_signature"]["printed_name"], "Dr. Francisco González (Firmado Digitalmente)")
            self.assertTrue(latest_record["signed_terms_checklist"]["academic_immunity"])

    def test_dynamic_monograph_compilation_per_journal(self):
        """Verifica la compilación dinámica de la monografía y los cambios de estilos bibliográficos y fórmulas."""
        from modules.investigador.monograph import ACADEMIC_MONOGRAPH
        
        # 1. STEM Profile / Nature Target
        stem_profile = ResearcherProfile(
            id="INV-STEM-001",
            name="Dr. Francisco González",
            institution="INTEC",
            epistemologic_stance="Positivista",
            user_role="classic_researcher",
            core_research_lines=["Bioingeniería"],
            target_publication_objective="Nature",
            local_keywords=["porosidad", "titanio"]
        )
        ACADEMIC_MONOGRAPH.test_profile = stem_profile
        self.assertIn("DESARROLLO DE UN SISTEMA PARAMÉTRICO DE PRÓTESIS", ACADEMIC_MONOGRAPH["title"])
        self.assertEqual(ACADEMIC_MONOGRAPH["bibliography_style_name"], "Estilo Nature")
        self.assertIn("1. Sumner, D. R.", ACADEMIC_MONOGRAPH["bibliography"][0])
        
        # 2. STEM Profile / IEEE Target
        ieee_profile = ResearcherProfile(
            id="INV-STEM-002",
            name="Dr. Francisco González",
            institution="INTEC",
            epistemologic_stance="Positivista",
            user_role="classic_researcher",
            core_research_lines=["Bioingeniería"],
            target_publication_objective="IEEE",
            local_keywords=["porosidad", "titanio"]
        )
        ACADEMIC_MONOGRAPH.test_profile = ieee_profile
        self.assertIn("DESARROLLO DE UN SISTEMA PARAMÉTRICO DE PRÓTESIS", ACADEMIC_MONOGRAPH["title"])
        self.assertEqual(ACADEMIC_MONOGRAPH["bibliography_style_name"], "Estilo IEEE")
        self.assertIn("[1] D. R. Sumner", ACADEMIC_MONOGRAPH["bibliography"][0])
        
        # 3. Social Sciences Profile / World Development Target
        social_profile = ResearcherProfile(
            id="INV-SOC-001",
            name="Dra. Altagracia Gómez",
            institution="UNIBE",
            epistemologic_stance="Constructivista",
            user_role="classic_researcher",
            core_research_lines=["Políticas Públicas"],
            target_publication_objective="World Development",
            local_keywords=["sargazo", "socioeconómica"]
        )
        ACADEMIC_MONOGRAPH.test_profile = social_profile
        self.assertIn("DISEÑO SOBERANO DE POLÍTICAS PÚBLICAS", ACADEMIC_MONOGRAPH["title"])
        self.assertEqual(ACADEMIC_MONOGRAPH["bibliography_style_name"], "Normas APA")
        self.assertIn("Gini", ACADEMIC_MONOGRAPH["chapters"]["theoretical_framework"])
        self.assertIn("Gómez, A. (2025)", ACADEMIC_MONOGRAPH["bibliography"][0])
        
        # 4. Arts & Humanities / Leonardo / Hermeneutic Target
        arts_profile = ResearcherProfile(
            id="INV-ART-001",
            name="Lic. Juan Pérez",
            institution="Bellas Artes",
            epistemologic_stance="Hermenéutica",
            user_role="classic_researcher",
            core_research_lines=["Instalación interactiva"],
            target_publication_objective="Leonardo",
            local_keywords=["estética", "neopixel"]
        )
        ACADEMIC_MONOGRAPH.test_profile = arts_profile
        self.assertIn("HERMENÉUTICA DE LA INTERACCIÓN ESTÉTICA", ACADEMIC_MONOGRAPH["title"])
        self.assertEqual(ACADEMIC_MONOGRAPH["bibliography_style_name"], "Estilo Harvard")
        self.assertIn("NeoPixel", ACADEMIC_MONOGRAPH["chapters"]["introduction"])
        self.assertIn("Lic. Juan Pérez and Gómez, A. 2025", ACADEMIC_MONOGRAPH["bibliography"][0])
        
        # 5. Business / HBR / Consultant Target
        business_profile = ResearcherProfile(
            id="INV-BUS-001",
            name="Ing. María Rosario",
            institution="Rosario Partners",
            epistemologic_stance="Positivista",
            user_role="investment_consultant",
            core_research_lines=["GTM Devices"],
            target_publication_objective="HBR",
            local_keywords=["GTM", "CAC/LTV"]
        )
        ACADEMIC_MONOGRAPH.test_profile = business_profile
        self.assertIn("MARCO DE VIABILIDAD ESTRATÉGICA", ACADEMIC_MONOGRAPH["title"])
        self.assertEqual(ACADEMIC_MONOGRAPH["bibliography_style_name"], "Estilo Chicago")
        self.assertIn("LTV", ACADEMIC_MONOGRAPH["chapters"]["theoretical_framework"])
        self.assertIn("Ing. María Rosario, and Altagracia Gómez. 2025", ACADEMIC_MONOGRAPH["bibliography"][0])
        
        # 6. Verify HTML Report compliance integration (Nivel Oro)
        from modules.investigador.impact_translator import FundingReportGenerator
        html_out = FundingReportGenerator.generate_html_report(
            project_title="Diseño de Prótesis Paramétrica",
            profile=social_profile,
            dictamen="VIABLE"
        )
        self.assertIn("WORLD DEVELOPMENT COMPLIANT", html_out)
        self.assertIn("Objetivos de Desarrollo Sostenible", html_out)
        self.assertIn("El modelado econométrico, el Coeficiente de Gini y las simulaciones", html_out)
        self.assertIn("XI. Anexo Regulador Universal de Estándares Científicos", html_out)
        
        # Clean up test profile to prevent side-effects on subsequent tests
        ACADEMIC_MONOGRAPH.test_profile = None


if __name__ == "__main__":
    unittest.main()
