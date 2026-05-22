# -*- coding: utf-8 -*-
"""
Enthema Suite V2.0 - Core Engine Simulation Runner
Módulo de Formulación & Auditoría (Investigador V2.0)
"""
import sys
import os
import pandas as pd
import numpy as np
import io

# Asegurar que el path local esté disponible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.investigador.models import ResearcherProfile, ConsortiumProfile, QualitativeDatabase, QuantitativeDatabase
from modules.investigador.profile_builder import CognitiveInterviewer, PassiveProfileExtractor
from modules.investigador.db_builder import QualitativeEncoder, DueDiligenceEncoder, FinancialFeasibilityProfiler, QuantitativeProfiler
from modules.investigador.network_analyst import SemanticGraphEngine
from modules.investigador.impact_translator import PatentingTranslator, InvestmentMemorandumTranslator, STEAMProjections, ResearchDisseminator

# Emojis y colores de terminal
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
CYAN = "\033[96m"
END = "\033[0m"

def print_header(title):
    print(f"\n{BOLD}{CYAN}================================================================================{END}")
    print(f"{BOLD}{BLUE} 🧬 {title.upper()} {END}")
    print(f"{BOLD}{CYAN}================================================================================{END}\n")

def print_subheader(title):
    print(f"\n{BOLD}{YELLOW}--- {title} ---{END}\n")

def simulate():
    print_header("Simulación de Funcionamiento Completo - Enthema Suite V2.0")
    
    # -------------------------------------------------------------
    # FASE 1: SIMULACIÓN DE ONBOARDING COGNITIVO SOCRÁTICO
    # -------------------------------------------------------------
    print_header("Fase 1: Onboarding Conversacional Socrático (Construcción D0)")
    
    # Sendero A: Investigador Clásico
    print_subheader("Sendero A: Investigador Clásico (Ciencia Pura & Académica)")
    classic_profile = ResearcherProfile(
        id="INV-001",
        name="",
        institution="",
        epistemologic_stance="Mixed_Methods",
        user_role="classic_researcher",
        core_research_lines=[],
        methodology_preferences=[],
        influences_authors=[],
        local_keywords=[]
    )
    
    chat_sequence_classic = [
        "Me llamo Dr. Francisco González de INTEC",
        "Prefiero la investigación constructivista con significados cualitativos",
        "Trabajo en la valorización bioquímica de sargazo y metales pesados en costas dominicanas",
        "Charles Darwin, Robert Woodward y el Protocolo de Nagoya"
    ]
    
    profile = classic_profile
    for idx, ans in enumerate(chat_sequence_classic):
        q = CognitiveInterviewer.get_next_question(profile)
        print(f"{BOLD}Pregunta Coach IA:{END} {q}")
        print(f"{BOLD}Respuesta Usuario:{END} {ans}")
        profile, completed, next_msg = CognitiveInterviewer.process_answer(profile, ans)
        print(f"{GREEN}Resultado del paso {idx+1}:{END} {next_msg}\n")
    
    print(f"{BOLD}{GREEN}✔ Perfil de Investigador Clásico Consolidado (D0):{END}")
    print(profile.model_dump_json(indent=2))
    
    classic_profile_final = profile

    # Sendero B: Consultor de Inversión
    print_subheader("Sendero B: Consultor de Financiamiento (Organismos Multilaterales/Privados)")
    consultant_profile = ResearcherProfile(
        id="CONS-002",
        name="",
        institution="",
        epistemologic_stance="Mixed_Methods",
        user_role="investment_consultant",
        core_research_lines=[],
        methodology_preferences=[],
        influences_authors=[],
        local_keywords=[]
    )
    
    chat_sequence_consultant = [
        "Me llamo Ing. Mateo Rosario de Rosario & Partners Consultores",
        "Este financiamiento se enfoca en transición ecológica y sostenibilidad (ESG/Sostenible)",
        "Estructuramos el proyecto para el Gobierno de Samaná buscando un monto total de $2,800,000 USD que evaluará el Banco Interamericano de Desarrollo",
        "Normas de Desempeño de la IFC y las Salvaguardas Ambientales y Sociales del BID"
    ]
    
    profile = consultant_profile
    for idx, ans in enumerate(chat_sequence_consultant):
        q = CognitiveInterviewer.get_next_question(profile)
        print(f"{BOLD}Pregunta Coach IA:{END} {q}")
        print(f"{BOLD}Respuesta Usuario:{END} {ans}")
        profile, completed, next_msg = CognitiveInterviewer.process_answer(profile, ans)
        print(f"{GREEN}Resultado del paso {idx+1}:{END} {next_msg}\n")
        
    print(f"{BOLD}{GREEN}✔ Perfil de Consultor de Inversiones Consolidado (D0):{END}")
    print(profile.model_dump_json(indent=2))
    
    consultant_profile_final = profile

    # Sendero C: Ingesta de Perfil Pasiva
    print_subheader("Sendero C: Ingesta de Perfil Pasiva (Obsidian, RIS y BibTeX)")
    
    # 1. Obsidian Test
    print(f"{BOLD}Simulando Ingesta de Nota de Obsidian Markdown...{END}")
    obsidian_content = """---
nombre: "Dra. Altagracia Gómez"
institución: "UNIBE / Instituto de Biotecnología"
rol: "classic_researcher"
postura: "Positivista"
---
## Líneas de Investigación
- Extracción bioquímica de compuestos orgánicos en macroalgas
- Quelación de metales pesados en sargazo

## Influencias y Autores
- Dr. Charles Darwin
- Dr. Robert Woodward

## Palabras Clave
- sargazo
- metales_pesados
- química
- cromatografía"""

    test_profile = ResearcherProfile(
        id="PAS-001", name="", institution="", core_research_lines=[], 
        methodology_preferences=[], influences_authors=[], local_keywords=[]
    )
    up_profile, ok, msg = PassiveProfileExtractor.parse_obsidian_markdown(obsidian_content, test_profile)
    print(f"Resultado Ingesta Obsidian: {ok} | {msg}")
    print(f"Perfil Ingestado (Obsidian): Name='{up_profile.name}', Epistemology='{up_profile.epistemologic_stance}', Lines={up_profile.core_research_lines}\n")
    
    # 2. RIS Test
    print(f"{BOLD}Simulando Ingesta de Exportación Zotero RIS...{END}")
    ris_content = """TY  - JOUR
AU  - Lovelock, James
AU  - Margulis, Lynn
TI  - The quantitative feedback of cybernetic systems in coastal sargazo biopolymers
KW  - climate_regression
KW  - statistical_models
KW  - outliers_analysis
ER  - """
    test_profile_ris = ResearcherProfile(
        id="PAS-002", name="", institution="", core_research_lines=[], 
        methodology_preferences=[], influences_authors=[], local_keywords=[]
    )
    up_profile_ris, ok, msg = PassiveProfileExtractor.parse_zotero_ris(ris_content, test_profile_ris)
    print(f"Resultado Ingesta RIS: {ok} | {msg}")
    print(f"Perfil Ingestado (RIS): Name='{up_profile_ris.name}', Epistemology='{up_profile_ris.epistemologic_stance}', Authors={up_profile_ris.influences_authors}\n")

    # 3. BibTeX Test
    print(f"{BOLD}Simulando Ingesta de Entrada Zotero BibTeX...{END}")
    bibtex_content = """@article{rosario2026esg,
  author = {Ing. Mateo Rosario and Sarah Jenkins},
  title = {Quantitative risk assessment and ESG safeguards in Caribbean loans},
  keywords = {esg, finance, risk_mitigation, irr, npv, due_diligence},
  journal = {Journal of Development Finance}
}"""
    test_profile_bib = ResearcherProfile(
        id="PAS-003", name="", institution="", user_role="investment_consultant", 
        core_research_lines=[], methodology_preferences=[], influences_authors=[], local_keywords=[]
    )
    up_profile_bib, ok, msg = PassiveProfileExtractor.parse_zotero_bibtex(bibtex_content, test_profile_bib)
    print(f"Resultado Ingesta BibTeX: {ok} | {msg}")
    print(f"Perfil Ingestado (BibTeX): Name='{up_profile_bib.name}', Epistemology='{up_profile_bib.epistemologic_stance}', Keywords={up_profile_bib.local_keywords}\n")

    # -------------------------------------------------------------
    # FASE 2: INGESTA Y CODIFICACIÓN EMPÍRICA (CUALI Y CUANTI)
    # -------------------------------------------------------------
    print_header("Fase 2: Ingesta e Inferencia de Bases de Datos Empíricas")
    
    # 2.1 ATLAS.ti agéntico del Investigador Clásico
    print_subheader("2.1 Grounded Theory Cualitativa (Investigador Clásico)")
    mock_transcript = """
    Pescador: "El sargazo llega de golpe y cubre toda la costa de Barahona. Ya no podemos pescar por las algas."
    Bióloga: "En los análisis rápidos detectamos metales pesados en el sargazo costero, específicamente plomo y cadmio, que pueden causar toxicidad."
    Investigador: "Proponemos convertir esto en biofertilizante para aumentar el rendimiento agrícola de los tomates locales."
    """
    print(f"{BOLD}Ingestando transcripción cualitativa:{END}\n{mock_transcript}")
    qual_db_classic = QualitativeEncoder.encode_text(
        "Valorización del Sargazo", "entrevista_pescadores_barahona.txt", mock_transcript
    )
    print(f"\n{BOLD}{GREEN}✔ Base de Datos Cualitativa Estructurada (Categories & Codes):{END}")
    print(qual_db_classic.model_dump_json(indent=2))

    # 2.2 Curación Cuantitativa del Investigador Clásico (Con atípicos y nulos)
    print_subheader("2.2 Quantitative Profiler (Investigador Clásico)")
    mock_csv_sargazo = """Muestra,Plomo_ppm,Cadmio_ppm,Arsenico_ppm
M1,1.2,0.45,2.1
M2,1.5,0.50,2.3
M3,1.1,0.42,
M4,-0.5,0.48,2.0
M5,1.8,,2.8
M6,15.0,0.55,2.5
"""
    print(f"{BOLD}Dataset experimental crudo (con nulos y negativos):{END}\n{mock_csv_sargazo}")
    df_sargazo = pd.read_csv(io.StringIO(mock_csv_sargazo))
    quant_db_classic, df_sargazo_clean = QuantitativeProfiler.profile_dataframe(
        "Muestras Químicas de Sargazo", df_sargazo, "CSV"
    )
    print(f"\n{BOLD}{GREEN}✔ Dataset Curado e Imputado (Pandas):{END}")
    print(df_sargazo_clean.to_string())
    print(f"\n{BOLD}{GREEN}✔ Metadata Cuantitativa y Alertas Estadísticas Detectadas:{END}")
    print(quant_db_classic.model_dump_json(indent=2))

    # 2.3 Due Diligence de Salvaguardas ESG (Consultor)
    print_subheader("2.3 ESG Due Diligence Encoder (Consultor de Inversión)")
    mock_esg_text = """
    Riesgo E: Se identificó que la construcción causará deforestación en Samaná y dañará los hábitats silvestres locales.
    Riesgo S: El plan exige el desplazamiento y expropiación involuntaria de 12 familias de agricultores rurales locales sin consulta previa.
    Riesgo G: El proyecto carece de la licencia ambiental formal exigida por el Ministerio de Medio Ambiente dominicano.
    """
    print(f"{BOLD}Estudio cualitativo de impacto socioambiental a escanear:{END}\n{mock_esg_text}")
    qual_db_consultant = DueDiligenceEncoder.encode_consultancy_text(
        "Planta de Compostaje Sostenible Samaná", "estudio_impacto_esg_samana.txt", mock_esg_text
    )
    print(f"\n{BOLD}{GREEN}✔ Alertas de Salvaguardas ESG Inferred (Environmental, Social, Governance):{END}")
    print(qual_db_consultant.model_dump_json(indent=2))

    # 2.4 Viabilidad Financiera Cuantitativa VAN/TIR (Consultor)
    print_subheader("2.4 Financial Feasibility Profiler - Solver Newton-Raphson (Consultor)")
    mock_cash_flow = """Periodo,Ingresos,Egresos
Año 0,0,1000000
Año 1,400000,100000
Año 2,450000,110000
Año 3,500000,120000
Año 4,550000,130000
Año 5,600000,140000
"""
    print(f"{BOLD}Flujos de caja plurianuales crudos:{END}\n{mock_cash_flow}")
    df_cash = pd.read_csv(io.StringIO(mock_cash_flow))
    discount_rate = 0.10 # 10%
    print(f"Tasa de descuento de referencia configurada por el Consultor: {discount_rate*100:.1f}%\n")
    
    quant_db_consultant, df_cash_clean, van, tir, dictamen = FinancialFeasibilityProfiler.profile_financials(
        "Análisis de Factibilidad Financiera Compostaje Samaná", df_cash, discount_rate
    )
    print(f"{BOLD}{GREEN}✔ Resultados Financieros de Viabilidad:{END}")
    print(f"  - Valor Actual Neto (VAN):  {BOLD}${van:,.2f} USD{END}")
    print(f"  - Tasa Interna de Retorno (TIR): {BOLD}{tir*100:.2f}%{END}")
    print(f"  - Dictamen Ejecutivo:       {BOLD}{CYAN if 'VIABLE' in dictamen else RED}{dictamen}{END}")
    print(f"\n{BOLD}{GREEN}✔ Metadata del Dataset Financiero Curado:{END}")
    print(quant_db_consultant.model_dump_json(indent=2))

    # -------------------------------------------------------------
    # FASE 3: ANÁLISIS DE GRAFOS DE CONSORCIOS (NETWORKX)
    # -------------------------------------------------------------
    print_header("Fase 3: Análisis Topológico de Grafos y Vacíos de Capacidades")
    
    # Creación del Consorcio Multidisciplinar
    bio_profile = ResearcherProfile(
        id="INV-BIO",
        name="Dra. Altagracia Gómez",
        institution="UNIBE / Instituto de Biotecnología",
        epistemologic_stance="Positivista",
        core_research_lines=["Extracción bioquímica de compuestos orgánicos en macroalgas", "Quelación de metales pesados en sargazo"],
        methodology_preferences=["Experimental cromatográfica", "Espectrometría HPLC"],
        influences_authors=["Dr. Charles Darwin", "Dr. Robert Woodward"],
        local_keywords=["sargazo", "metales_pesados", "química", "cromatografía"]
    )
    
    # Integramos el perfil consolidado del investigador clásico anterior y el bio-investigador
    consortium = ConsortiumProfile(
        project_title="Valorización Integral del Sargazo en el Caribe y su Impacto en el Ecosistema Dominicano",
        funding_agency="FONDOCYT",
        lead_researcher_id=classic_profile_final.id,
        members=[classic_profile_final, bio_profile],
        synergy_nodes=[],
        detected_gaps=[],
        total_budget_usd=0.0,
        duration_months=18
    )
    
    print(f"{BOLD}Construyendo grafo del consorcio semántico para:{END} '{consortium.project_title}'")
    print(f"Miembros: {', '.join([m.name for m in consortium.members])}")
    
    G, synergies, gaps = SemanticGraphEngine.build_consortium_graph(consortium)
    
    print(f"\n{BOLD}{GREEN}✔ Nodos de Sinergias (Intersecciones de capacidades):{END}")
    for syn in synergies:
        print(f"  - Node: '{syn}' (Punto de confluencia entre los investigadores)")
        
    print(f"\n{BOLD}{RED}✔ Agujeros Estructurales y Vacíos de Competencias (FONDOCYT):{END}")
    for gap in gaps:
        print(f"  - {gap}")
        
    print(f"\n{BOLD}{CYAN}✔ Propiedades Topológicas del Grafo:{END}")
    print(f"  - Número total de Nodos: {G.number_of_nodes()}")
    print(f"  - Número total de Enlaces: {G.number_of_edges()}")

    # -------------------------------------------------------------
    # FASE 4: TRANSFERENCIA DE IMPACTO, MEMORANDOS & SIMULACIONES
    # -------------------------------------------------------------
    print_header("Fase 4: Catalizador de Impacto, Transferencia y Simulación ABM")
    
    # 4.1 Generador de Solicitud de Patente de Invención (Clásico)
    print_subheader("4.1 Borrador de Memoria Técnica de Patente ONAPI (Clásico)")
    patent_draft = PatentingTranslator.generate_patent_draft(
        consortium.project_title,
        qual_db_classic,
        quant_db_classic,
        classic_profile_final.epistemologic_stance
    )
    print(f"{BOLD}{GREEN}✔ Título de la Patente:{END} {patent_draft['title']}")
    print(f"\n{BOLD}Resumen de la Invención (Abstract):{END}\n{patent_draft['abstract']}")
    print(f"\n{patent_draft['description'][:300]}...\n")
    print(f"{patent_draft['claims'][:300]}...\n")

    # 4.2 Generador de Memorando de Inversión (Consultor)
    print_subheader("4.2 Investment Memorandum Ejecutivo para Comité de Crédito (Consultor)")
    memo = InvestmentMemorandumTranslator.generate_investment_memorandum(
        "Planta Sostenible Compostaje Samaná",
        qual_db_consultant,
        quant_db_consultant,
        consultant_profile_final.target_fund_usd,
        consultant_profile_final.funding_institution,
        consultant_profile_final.consultancy_client,
        van,
        tir,
        dictamen
    )
    print(f"{BOLD}{GREEN}✔ Título del Memorando:{END} {memo['title']}")
    print(f"\n{BOLD}Breve Introducción:{END}\n{memo['brief']}")
    print(f"\n{BOLD}Debido Proceso y Salvaguardas ESG:{END}\n{memo['esg_due_diligence']}")
    print(f"\n{BOLD}Justificación Socioeconómica:{END}\n{memo['justification']}")

    # 4.3 Catalizador STEAM - Proyección de Simulación en Agentes Mesa (Socioeconómico)
    print_subheader("4.3 Catalizador de Proyecciones STEAM - Script de Simulación de Agentes (Mesa)")
    steam_proj = STEAMProjections.catalyze_projections(
        consortium.project_title,
        qual_db_classic,
        quant_db_classic,
        classic_profile_final.epistemologic_stance
    )
    print(f"{BOLD}{GREEN}✔ Categoría de Impacto STEAM:{END} {steam_proj['domain']}")
    print(f"{BOLD}{GREEN}✔ Título de la Simulación:{END} {steam_proj['suggestion_title']}")
    print(f"{BOLD}Detalle del Experimento:{END}\n{steam_proj['suggestion_desc']}\n")
    print(f"{BOLD}Código Generado en Agentes (Mesa Python):{END}")
    print(f"{BOLD}{CYAN}--------------------------------------------------------------------------------{END}")
    # Mostrar las primeras 30 líneas del código de agentes
    code_lines = steam_proj['code_snippet'].split("\n")
    for line in code_lines[:30]:
        print(line)
    print(f"... [{len(code_lines) - 30} líneas adicionales omitidas en consola] ...")
    print(f"{BOLD}{CYAN}--------------------------------------------------------------------------------{END}")

    # 4.4 Agente Difusor - Canales de Diseminación Multiformato
    print_subheader("4.4 Agente Difusor - Canales de Diseminación Multiformato (Salida)")
    dissemination = ResearchDisseminator.generate_dissemination_channels(
        project_title=consortium.project_title,
        profile=classic_profile_final,
        qual_db=qual_db_classic,
        quant_db=quant_db_classic,
        budget_usd=150000.0
    )
    print(f"{BOLD}{GREEN}✔ Título del Abstract Académico:{END} {dissemination['abstract_title']}")
    print(f"\n{BOLD}Abstract Académico:{END}\n{dissemination['abstract']}")
    print(f"\n{BOLD}Estructura del Pitch Deck (Primeras Diapositivas):{END}")
    for slide in dissemination['pitch_deck'][:2]:
        print(f"  - {slide['title']}: {slide['content'][:120]}...")
    print(f"\n{BOLD}Hilo de X (Twitter) - Primeros Tweets:{END}")
    for tweet in dissemination['hilo_x'][:2]:
        print(f"  - {tweet}")
    print(f"\n{BOLD}Comunicado de Prensa (Fragmento):{END}\n{dissemination['press_release'][:400]}...")

    print_header("Simulación de Funcionamiento de Enthema Suite V2.0 Completada Exitosamente!")

if __name__ == "__main__":
    simulate()
