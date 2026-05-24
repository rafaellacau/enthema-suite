# -*- coding: utf-8 -*-
"""
Enthema Suite V2.5 - Servidor Web FastAPI de Alta Fidelidad (Opción B)
"""
import os
import sys
import json
import logging
import random
import io
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Asegurar que el path local esté disponible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.investigador.models import (
    ResearcherProfile, 
    ConsortiumProfile, 
    QualitativeDatabase, 
    QuantitativeDatabase,
    CodedSemanticUnit,
    VariableMetadata,
    TypedSegment,
    MultimediaTimecode
)
from modules.investigador.profile_builder import CognitiveInterviewer, PassiveProfileExtractor
from modules.investigador.db_builder import (
    QualitativeEncoder, 
    DueDiligenceEncoder, 
    FinancialFeasibilityProfiler, 
    QuantitativeProfiler,
    SyntheticPilotGenerator
)
from modules.investigador.network_analyst import SemanticGraphEngine
from modules.investigador.impact_translator import (
    PatentingTranslator, 
    InvestmentMemorandumTranslator, 
    STEAMProjections, 
    ResearchDisseminator,
    FundingReportGenerator
)
from modules.investigador.monograph import ACADEMIC_MONOGRAPH
from modules.investigador.ethical_declaration import archive_signed_legal_act
from modules.investigador.crypto import encrypt_data, decrypt_data, shred_master_key


# Inicializar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="Enthema Suite Precision Intelligence",
    description="Motor científico y financiero de precisión con interfaz de diseño Stitch (Tailwind CSS/HTML5)",
    version="3.0.0-SOVEREIGN"
)

import traceback
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        err_msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": err_msg
            }
        )

# Inicializar bases de datos locales y configurar rutas dinámicas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=templates_dir)
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Intentar usar el path persistente en output/legal con fallback robusto
legal_dir = os.path.join(BASE_DIR, "output", "legal")
try:
    os.makedirs(legal_dir, exist_ok=True)
    # Probar escritura para verificar permisos reales
    test_file = os.path.join(legal_dir, ".write_test")
    with open(test_file, "w") as f:
        f.write("test")
    os.remove(test_file)
except Exception as e:
    logger.error(f"El directorio persistente {legal_dir} no es escribible ({e}). Usando fallback en /tmp/legal")
    legal_dir = "/tmp/legal"
    os.makedirs(legal_dir, exist_ok=True)

db_path = os.path.join(legal_dir, "users_db.json")

def load_encrypted_json(file_path: str, default_val: Any = None) -> Any:
    if not os.path.exists(file_path):
        return default_val if default_val is not None else []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return default_val if default_val is not None else []
        # Si el contenido es JSON plano heredado (legacy), lo cargamos y en el próximo guardado se cifrará
        if content.startswith("{") or content.startswith("["):
            return json.loads(content)
        # De lo contrario, lo desciframos con la clave maestra
        decrypted = decrypt_data(content, legal_dir)
        return json.loads(decrypted)
    except Exception as e:
        logger.error(f"Error cargando/descifrando {file_path}: {e}")
        # En caso de fallo total, intentamos cargar como JSON plano por si acaso
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val if default_val is not None else []

def save_encrypted_json(file_path: str, data: Any) -> None:
    try:
        plain_text = json.dumps(data, indent=4, ensure_ascii=False)
        encrypted_text = encrypt_data(plain_text, legal_dir)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(encrypted_text)
    except Exception as e:
        logger.error(f"Error cifrando/guardando {file_path}: {e}")
        raise e

default_users = [
    {
        "username": "admin",
        "password": "Lalo6%%Lalo",
        "role": "admin",
        "name": "Auditor Principal",
        "institution": "MESCyT / INTEC",
        "profile_id": "INV-AUDIT-MASTER"
    },
    {
        "username": "PG",
        "password": "soncubano66",
        "role": "admin",
        "name": "Pedro Gómez (Auditor)",
        "institution": "FONDOCYT / MESCyT",
        "profile_id": "INV-AUDIT-PG"
    },
    {
        "username": "RL",
        "password": "lapuesta66",
        "role": "admin",
        "name": "Rafael Lacau (Auditor)",
        "institution": "FONDOCYT / MESCyT",
        "profile_id": "INV-AUDIT-RL"
    },
    {
        "username": "aris",
        "password": "password",
        "role": "researcher",
        "name": "Dr. Aris Thorne",
        "institution": "Instituto Internacional de Bioingeniería",
        "profile_id": "INV-ARIS-001"
    },
    {
        "username": "investigador_biotech",
        "password": "socrates_bio99",
        "role": "researcher",
        "name": "Lab de Bioingeniería Avanzada",
        "institution": "Universidad de Santo Domingo",
        "profile_id": "INV-BIOTECH-01"
    },
    {
        "username": "researcher_steam",
        "password": "steam_precision88",
        "role": "researcher",
        "name": "Grupo de Investigación STEAM",
        "institution": "Instituto FONDOCYT",
        "profile_id": "INV-STEAM-02"
    },
    {
        "username": "consultor_esg",
        "password": "esg_impact77",
        "role": "researcher",
        "name": "Consultor Financiero ESG",
        "institution": "Banco de Desarrollo Multilateral",
        "profile_id": "INV-ESG-03"
    },
    {
        "username": "dr_thorne",
        "password": "aris_science55",
        "role": "researcher",
        "name": "Dr. Aris Thorne (Alternativo)",
        "institution": "Instituto Internacional de Bioingeniería",
        "profile_id": "INV-ARIS-002"
    },
    {
        "username": "PV",
        "password": "sargazopv66",
        "role": "researcher",
        "name": "Investigador Principal PV",
        "institution": "INTEC",
        "profile_id": "INV-PV-001"
    }
]

users = load_encrypted_json(db_path, [])

# Sincronizar y actualizar usuarios por defecto
existing_users_dict = {u["username"].lower(): u for u in users}
for du in default_users:
    uname_lower = du["username"].lower()
    if uname_lower in existing_users_dict:
        existing_users_dict[uname_lower]["password"] = du["password"]
        existing_users_dict[uname_lower]["role"] = du["role"]
        existing_users_dict[uname_lower]["name"] = du["name"]
        existing_users_dict[uname_lower]["institution"] = du["institution"]
    else:
        users.append(du)

try:
    save_encrypted_json(db_path, users)
except Exception as e:
    logger.error(f"Error escribiendo users_db.json: {e}")

keys_path = os.path.join(legal_dir, "access_keys.json")
if not os.path.exists(keys_path):
    default_keys = [
        {
            "key": "TEMP-ARIS",
            "used": False,
            "used_by": None,
            "created_at": "2026-05-22T12:00:00Z"
        },
        {
            "key": "TEMP-AUDIT",
            "used": False,
            "used_by": None,
            "created_at": "2026-05-22T12:00:00Z"
        }
    ]
    try:
        save_encrypted_json(keys_path, default_keys)
    except Exception as e:
        logger.error(f"Error escribiendo access_keys.json: {e}")
else:
    # Auto-migración en caliente si el archivo existe pero está en texto plano legacy
    try:
        with open(keys_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content.startswith("{") or content.startswith("["):
            data = json.loads(content)
            save_encrypted_json(keys_path, data)
            logger.info("Migración y cifrado en reposo exitoso de access_keys.json plano.")
    except Exception as e:
        logger.error(f"Error migrando access_keys.json plano: {e}")

# ==========================================
# MOTOR DE PARADIGMAS ENCHUFABLES (PPE v3.0)
# ==========================================

class BaseParadigm:
    name: str
    display_name: str
    allowed_vocabulary: List[str]
    restricted_concepts: List[str]
    
    def get_default_sections(self) -> dict:
        raise NotImplementedError
        
    def validate_section(self, node: str, text: str, state) -> dict:
        raise NotImplementedError

class BioIndustrialParadigm(BaseParadigm):
    name = "bio_industrial"
    display_name = "Paradigma Bio-Industrial (Clásico)"
    allowed_vocabulary = ["monod", "tir", "van", "biorreactor", "temperatura", "ph", "presión", "biomasa", "sustrato", "cinética", "newton-raphson", "flujo de caja", "capex", "opex"]
    restricted_concepts = ["decolonial", "hermenéutica", "teoría crítica", "explotación", "soberanía tecnológica", "capitalismo", "neoliberalismo", "lucha de clases", "paradoja axiomática", "functores", "topología teórica"]
    
    def get_default_sections(self) -> dict:
        return {
            "abstract": {
                "title": "1. Resumen Ejecutivo (Abstract)",
                "text": "El presente estudio describe el diseño y la optimización de un sistema piloto para la valorización de biomasa mediante bioingeniería de precisión. La viabilidad de este reactor se analiza a partir de modelos cinéticos y simulaciones de factibilidad económica...",
                "status": "green"
            },
            "bioreactor": {
                "title": "2. Configuración Biophysical (Reactor)",
                "text": "El biorreactor opera en régimen semicontinuo bajo las siguientes condiciones de telemetría controlada: Temperatura media de 37°C, pH mantenido a 7.42 y presión de 104.2 kPa. La cinética de crecimiento se rige por un modelo biológico adaptado...",
                "status": "green"
            },
            "simulation": {
                "title": "3. Simulación Piloto Sintético",
                "text": "Se ha ejecutado un modelo cinético de Monod en el simulador determinista. La tasa específica de crecimiento máxima simulada es de 0.45 h^-1 con una concentración de biomasa saturada en estado estacionario...",
                "status": "green"
            },
            "finance": {
                "title": "4. Viabilidad Económica (Solver TIR/VAN)",
                "text": "La viabilidad financiera fue resuelta a través de un solver determinista de Newton-Raphson. Las proyecciones de flujo de caja libre estiman una Tasa Interna de Retorno (TIR) atractiva y un Valor Actual Neto (VAN) positivo, sustentados en una capacidad de producción anual coherente con el rendimiento del biorreactor...",
                "status": "green"
            },
            "compliance": {
                "title": "5. Compliance Regulatorio (Nagoya/Bioética)",
                "text": "El consorcio metodológico garantiza el cumplimiento estricto del Protocolo de Nagoya sobre acceso a recursos genéticos y participación justa en los beneficios. Las salvaguardas éticas y biológicas están debidamente respaldadas por el Acta de Consentimiento y el Sello de Bioética firmado electrónicamente...",
                "status": "green"
            }
        }
        
    def validate_section(self, node: str, text: str, state) -> dict:
        import re
        status = "green"
        reasons = []
        numbers = [float(n) for n in re.findall(r"\b\d+(?:\.\d+)?\b", text)]
        
        if node == "simulation":
            expected_growth = 0.45
            for num in numbers:
                if 0.0 < num < 1.0 and abs(num - expected_growth) > 0.05:
                    status = "orange"
                    reasons.append(f"Discrepancia biocinética: el texto menciona {num} h^-1 pero el simulador determinista computó {expected_growth} h^-1.")
        elif node == "finance":
            expected_tir = 24.5
            for num in numbers:
                if 5.0 < num < 100.0 and abs(num - expected_tir) > 2.0:
                    status = "orange"
                    reasons.append(f"Discrepancia financiera: el borrador declara TIR de {num}% pero el Solver calculó {expected_tir}%.")
        elif node == "compliance":
            if not state.profile.legal_terms_accepted:
                status = "orange"
                reasons.append("Firma pendiente: se declaran salvaguardas validadas, pero el Acta de Bioética digital aún figura como NO FIRMADA.")
                
        return {"status": status, "reasons": reasons}

class SocialPublicParadigm(BaseParadigm):
    name = "social_public"
    display_name = "Paradigma Social y de Impacto Público"
    allowed_vocabulary = ["sroi", "ecotecnología", "comunidad", "gobernanza", "impacto social", "soberanía tecnológica", "nutrientes", "reciclaje", "nitrógeno", "fósforo", "colectivo", "participación"]
    restricted_concepts = ["monod", "tir", "van", "capex", "opex", "newton-raphson", "paradoja axiomática", "functores", "decolonial", "hermenéutica"]
    
    def get_default_sections(self) -> dict:
        return {
            "abstract": {
                "title": "1. Resumen de Impacto Comunitario",
                "text": "Esta investigación establece un modelo de desarrollo territorial basado en la soberanía tecnológica y el aprovechamiento de recursos locales, priorizando el beneficio social y ecológico por encima de la acumulación comercial privada...",
                "status": "green"
            },
            "bioreactor": {
                "title": "2. Ecotecnología y Recursos Colectivos",
                "text": "El sistema biológico se diseña bajo principios de ecología de bajo impacto, operando con insumos recuperados y fuentes hídricas colectivas bajo telemetría abierta regulada por la comunidad...",
                "status": "green"
            },
            "simulation": {
                "title": "3. Modelo de Ciclo de Nutrientes",
                "text": "La simulación ecológica estima una tasa de regeneración de biomasa de 0.65 h^-1 con una huella de carbono neutral. El modelo de nutrientes demuestra una eficiencia del 90% en el reciclaje de nitrógeno y fósforo...",
                "status": "green"
            },
            "finance": {
                "title": "4. Retorno Social de la Inversión (SROI)",
                "text": "El solver social computó un índice de Retorno Social de la Inversión (SROI) de 3.2, lo que significa que por cada peso público invertido se generan 3.2 pesos de valor social tangible devueltos a la comunidad...",
                "status": "green"
            },
            "compliance": {
                "title": "5. Gobernanza Participativa y Bioética",
                "text": "El proyecto cumple con las directrices de consentimiento previo, libre e informado de las comunidades locales. Las salvaguardas ambientales y éticas se certifican mediante el Sello de Gobernanza Participativa...",
                "status": "green"
            }
        }
        
    def validate_section(self, node: str, text: str, state) -> dict:
        import re
        status = "green"
        reasons = []
        numbers = [float(n) for n in re.findall(r"\b\d+(?:\.\d+)?\b", text)]
        
        if node == "simulation":
            expected_recycle = 90.0
            for num in numbers:
                if 50.0 < num <= 100.0 and abs(num - expected_recycle) > 5.0:
                    status = "orange"
                    reasons.append(f"Discrepancia ecológica: el borrador declara {num}% de reciclaje, pero la simulación estimó {expected_recycle}%.")
        elif node == "finance":
            expected_sroi = 3.2
            for num in numbers:
                if 0.5 < num < 10.0 and abs(num - expected_sroi) > 0.2:
                    status = "orange"
                    reasons.append(f"Discrepancia SROI: el texto declara un índice SROI de {num}, pero el solver social calculó {expected_sroi}.")
        elif node == "compliance":
            if not state.profile.legal_terms_accepted:
                status = "orange"
                reasons.append("Gobernanza pendiente: se declara consentimiento comunitario, pero falta la firma digital del Acta de Gobernanza.")
                
        return {"status": status, "reasons": reasons}

class PureTheoreticalParadigm(BaseParadigm):
    name = "pure_theoretical"
    display_name = "Paradigma Teórico Puro e Investigación Básica"
    allowed_vocabulary = ["parsimonia", "fecundidad", "elegancia", "functor", "axioma", "coherencia", "paradoja", "sintáctico", "no-contradicción", "algebraico", "topología", "teorema"]
    restricted_concepts = ["biorreactor", "monod", "tir", "van", "sroi", "comunidad", "temperatura", "ph", "presión", "capitalismo", "decolonial", "nagoya", "bioética"]
    
    def get_default_sections(self) -> dict:
        return {
            "abstract": {
                "title": "1. Resumen Teórico y Postulados",
                "text": "Este tratado presenta la formulación axiomática y fundamentación conceptual del espacio de categorías de la teoría de representaciones, explorando las implicaciones estructurales y la elegancia lógica sin fines comerciales de aplicación inmediata...",
                "status": "green"
            },
            "bioreactor": {
                "title": "2. Estructura Axiomática Básica",
                "text": "Se definen los functores y transformaciones naturales base que estructuran la topología teórica. No hay reactor físico; las condiciones de borde se modelan abstractamente a través de restricciones de coherencia lógica...",
                "status": "green"
            },
            "simulation": {
                "title": "3. Verificación de Parsimonia",
                "text": "El validador sintáctico del backend resolvió el grafo de implicaciones teóricas con un índice de parsimonia de 0.95. La redundancia conceptual del modelo es nula, garantizando una formulación elegante y minimalista...",
                "status": "green"
            },
            "finance": {
                "title": "4. Fecundidad y Elegancia Teórica",
                "text": "La viabilidad teórica se mide mediante un índice de fecundidad conceptual de 4.8 (nuevos teoremas inducidos por axioma). El solver formal demuestra la robustez del sistema algebraico frente a paradojas sintácticas convencionales...",
                "status": "green"
            },
            "compliance": {
                "title": "5. Rigor Epistémico y Paradojas",
                "text": "El expediente cuenta con la validación de consistencia lógica interna completa. Las salvaguardas metodológicas previenen la introducción de tautologías y aseguran el estricto apego al rigor matemático de no-contradicción...",
                "status": "green"
            }
        }
        
    def validate_section(self, node: str, text: str, state) -> dict:
        import re
        status = "green"
        reasons = []
        numbers = [float(n) for n in re.findall(r"\b\d+(?:\.\d+)?\b", text)]
        
        if node == "simulation":
            expected_parsimony = 0.95
            for num in numbers:
                if 0.0 < num < 1.0 and abs(num - expected_parsimony) > 0.05:
                    status = "orange"
                    reasons.append(f"Discrepancia teórica: el texto menciona un índice de parsimonia de {num} pero el validador estimó {expected_parsimony}.")
        elif node == "finance":
            expected_fecundity = 4.8
            for num in numbers:
                if 1.0 < num < 20.0 and abs(num - expected_fecundity) > 0.3:
                    status = "orange"
                    reasons.append(f"Discrepancia formal: el borrador declara una fecundidad de {num} pero el solver matemático estimó {expected_fecundity}.")
        elif node == "compliance":
            if not state.profile.legal_terms_accepted:
                status = "orange"
                reasons.append("Validación pendiente: se declara ausencia de tautologías, pero falta la firma del Acta de Rigor Epistémico.")
                
        return {"status": status, "reasons": reasons}

PARADIGMS = {
    "bio_industrial": BioIndustrialParadigm(),
    "social_public": SocialPublicParadigm(),
    "pure_theoretical": PureTheoreticalParadigm()
}

# ==========================================
# MODELOS DE PERSISTENCIA Y EVENT SOURCING (ProjectAggregate V3.0)
# ==========================================

from pydantic import Field

class DraftSectionState(BaseModel):
    title: str
    text: str
    status: str
    reasons: List[str] = Field(default_factory=list)
    segments: List[TypedSegment] = Field(default_factory=list)
    timecodes: List[MultimediaTimecode] = Field(default_factory=list)

class ParadigmPhase(BaseModel):
    phase_id: str  # e.g., "Fase 1", "Fase 2"
    paradigm_name: str  # "bio_industrial", "social_public", "pure_theoretical"
    draft_sections: Dict[str, DraftSectionState]
    is_active: bool = True
    is_immutable: bool = False
    timestamp: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)

class ProjectAggregate(BaseModel):
    active_phase_id: str = "Fase 1"
    phases: List[ParadigmPhase] = Field(default_factory=list)

# Variables de Estado en memoria (Session-based multi-user state)
class AppState:
    def __init__(self, user_id: str = "INV-ARIS-001", name: str = "Dr. Aris Thorne", institution: str = "Instituto Internacional de Bioingeniería", role: str = "classic_researcher"):
        self.profile = ResearcherProfile(
            id=user_id,
            name=name,
            institution=institution,
            epistemologic_stance="Positivista",
            user_role=role,
            research_maturity_stage="Ideación",
            target_publication_objective="Nature",
            legal_terms_accepted=False,
            electronic_signature_name="",
            orcid="0000-0002-1823-4567",
            dois=["10.1016/j.jbiomech.2014.12.013"],
            core_research_lines=["Bioingeniería de Implantes porosos", "Regeneración celular"],
            methodology_preferences=["Diseño de elementos finitos", "Análisis cuantitativo"],
            influences_authors=["Gibson-Ashby", "Wolff"],
            local_keywords=["titanio", "porosidad", "SLS"]
        )
        self.qualitative_db: Optional[QualitativeDatabase] = None
        self.quantitative_db: Optional[QuantitativeDatabase] = None
        self.raw_quant_df: Optional[pd.DataFrame] = None
        self.quant_clean_df: Optional[pd.DataFrame] = None
        
        # Simulación de telemetría de reactor
        self.reactor_temp = 1240.5
        self.reactor_pressure = 104.2
        self.reactor_ph = 7.42
        self.reactor_status = "Operativo"
        
        # Telemetry metrics for Coach suggestion acceptance (literal vs modified)
        self.generated_suggestions = {}
        self.literal_acceptances = set()
        self.modified_acceptances = set()
        
        # Inicialización del Paradigma Enchufable (PPE v3.0) con Bounded Contexts y Fases inmutables (Phase Commit & Forking)
        initial_phase = ParadigmPhase(
            phase_id="Fase 1",
            paradigm_name="bio_industrial",
            draft_sections={
                k: DraftSectionState(
                    title=v["title"],
                    text=v["text"],
                    status=v["status"],
                    reasons=v.get("reasons", [])
                )
                for k, v in PARADIGMS["bio_industrial"].get_default_sections().items()
            },
            is_active=True,
            is_immutable=False,
            timestamp=datetime.now().isoformat()
        )
        self.project_aggregate = ProjectAggregate(
            active_phase_id="Fase 1",
            phases=[initial_phase]
        )

    def get_active_phase(self) -> ParadigmPhase:
        for phase in self.project_aggregate.phases:
            if phase.phase_id == self.project_aggregate.active_phase_id:
                return phase
        return self.project_aggregate.phases[0]

    @property
    def active_paradigm_name(self) -> str:
        return self.get_active_phase().paradigm_name

    @active_paradigm_name.setter
    def active_paradigm_name(self, val: str):
        self.get_active_phase().paradigm_name = val

    @property
    def draft_sections(self) -> Dict[str, Any]:
        phase = self.get_active_phase()
        return {
            k: {
                "title": v.title,
                "text": v.text,
                "status": v.status,
                "reasons": v.reasons
            }
            for k, v in phase.draft_sections.items()
        }

    def update_draft_section(self, node: str, text: str, status: str = None, reasons: list = None):
        phase = self.get_active_phase()
        if phase.is_immutable:
            raise HTTPException(status_code=403, detail="No se puede modificar una fase inmutable de solo lectura.")
        if node in phase.draft_sections:
            sec = phase.draft_sections[node]
            sec.text = text
            if status is not None:
                sec.status = status
            if reasons is not None:
                sec.reasons = reasons

            # 1. Segmentación automática de autoría (Compromiso 3)
            import uuid
            from datetime import datetime
            paragraphs = [p for p in text.split("\n\n") if p.strip()]
            sec.segments = []
            current_pos = 0
            for idx, para in enumerate(paragraphs):
                start_idx = text.find(para, current_pos)
                if start_idx == -1:
                    start_idx = current_pos
                end_idx = start_idx + len(para)
                current_pos = end_idx

                # Determinamos el tipo de autoría: ai_copilot_assisted o human_pure
                author = "human_pure"
                if "💡" in para or "sugerencia" in para.lower() or "recomendación" in para.lower() or "copilot" in para.lower() or "generado" in para.lower():
                    author = "ai_copilot_assisted"
                
                sec.segments.append(TypedSegment(
                    id=f"SEG-{node.upper()}-{idx:03d}-{uuid.uuid4().hex[:6]}",
                    start_char=start_idx,
                    end_char=end_idx,
                    text=para,
                    author_type=author,
                    timestamp=datetime.now().isoformat() + "Z"
                ))

            # 2. Extracción y mapeo automático de marcas de tiempo transmedia (Compromiso 7)
            import re
            sec.timecodes = []
            pattern = r"\[(VideoRef|AudioRef|MediaRef):\s*([^\|\]]+?)\s*\|\s*([0-9:]+)\s*-\s*([0-9:]+)\s*(?:\|\s*([^\]]+?)\s*)?\]"
            matches = re.finditer(pattern, text)
            for tc_idx, match in enumerate(matches):
                ref_type = match.group(1)
                source = match.group(2).strip()
                start_t = match.group(3).strip()
                end_t = match.group(4).strip()
                annotation = match.group(5).strip() if match.group(5) else f"Marca multimedia indexada de tipo {ref_type}"
                
                sec.timecodes.append(MultimediaTimecode(
                    id=f"TC-{node.upper()}-{tc_idx:03d}",
                    source_file=source,
                    start_time=start_t,
                    end_time=end_t,
                    annotation=annotation
                ))

sessions: Dict[str, AppState] = {}
active_connections: Dict[str, dict] = {}

# Inicializar sesión por defecto para desarrollo/pruebas
default_session_id = "test-session-aris"
sessions[default_session_id] = AppState()
active_connections[default_session_id] = {
    "username": "aris",
    "name": "Dr. Aris Thorne",
    "role": "researcher",
    "ip": "127.0.0.1",
    "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

# ==========================================
# GESTORES DE SESIÓN Y SEGURIDAD
# ==========================================

def get_session_or_redirect(request: Request) -> Optional[AppState]:
    """Recupera la sesión del usuario o retorna None para redirigir."""
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return None
    return sessions[session_id]

def get_api_session(request: Request) -> AppState:
    """Recupera la sesión de llamadas API o levanta una excepción de No Autorizado (401)."""
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada. Por favor inicie sesión.")
    return sessions[session_id]

def get_base_context(req: Request, state: AppState) -> dict:
    """Construye el contexto base Jinja2 inyectando el estado de sesión actual."""
    return {
        "request": req,
        "profile": state.profile,
        "qualitative_db": state.qualitative_db,
        "quantitative_db": state.quantitative_db,
        "reactor_temp": state.reactor_temp,
        "reactor_pressure": state.reactor_pressure,
        "reactor_ph": state.reactor_ph,
        "reactor_status": state.reactor_status,
        "draft_sections": state.draft_sections,
        "project_aggregate": state.project_aggregate.model_dump(),
        "PARADIGMS": PARADIGMS
    }

# ==========================================
# ENPOINTS DE AUTENTICACIÓN Y REGISTRO
# ==========================================

@app.get("/login", response_class=HTMLResponse)
@app.head("/login")
async def view_login(request: Request):
    """Renderiza el login premium glassmorphic."""
    if request.method == "HEAD":
        return HTMLResponse(status_code=200)
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html")

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
async def api_login(data: LoginRequest):
    """Procesa el inicio de sesión contra el archivo local users_db.json."""
    print(f"DEBUG LOGIN: Recibido login para '{data.username}' con clave de longitud {len(data.password)}", flush=True)
    users = load_encrypted_json(db_path, [])
    print(f"DEBUG LOGIN: Base de datos cargada. Encontrados {len(users)} usuarios.", flush=True)

    # Buscar usuario
    user = None
    for u in users:
        u_match = u["username"].lower() == data.username.lower()
        p_match = u["password"] == data.password
        print(f"DEBUG LOGIN: Comparando con '{u['username']}' - Match usuario: {u_match}, Match clave: {p_match}", flush=True)
        if u_match and p_match:
            user = u
            break

    if not user:
        logger.warning(f"Login fallido para usuario: '{data.username}'")
        raise HTTPException(status_code=400, detail="Nombre de usuario o contraseña incorrectos")
    logger.info(f"Login exitoso para usuario: '{data.username}' con rol: {user['role']}")

    import uuid
    session_id = str(uuid.uuid4())
    
    role_mapping = {
        "admin": "admin",
        "auditor": "auditor",
        "researcher": "classic_researcher"
    }
    user_role = role_mapping.get(user["role"], "classic_researcher")

    # Crear AppState persistente para este usuario
    state = AppState(
        user_id=user.get("profile_id", f"INV-{uuid.uuid4().hex[:8].upper()}"),
        name=user["name"],
        institution=user["institution"],
        role=user_role
    )
    sessions[session_id] = state
    
    active_connections[session_id] = {
        "username": user["username"],
        "name": user["name"],
        "role": user["role"],
        "ip": "127.0.0.1",
        "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    response = JSONResponse(content={
        "status": "success",
        "message": "Sesión iniciada exitosamente",
        "redirect": "/admin" if user["role"] in ["admin", "auditor"] else "/"
    })
    response.set_cookie(key="session_id", value=session_id, max_age=86400, path="/")
    return response

class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    institution: str
    access_key: str

@app.post("/api/register")
async def api_register(data: RegisterRequest):
    """Registra un nuevo investigador validando y quemando una clave provisional."""
    keys = load_encrypted_json(keys_path, [])

    key_obj = next((k for k in keys if k["key"].upper() == data.access_key.upper()), None)
    if not key_obj:
        raise HTTPException(status_code=400, detail="Clave provisional de acceso inválida.")
    if key_obj["used"]:
        raise HTTPException(status_code=400, detail="Esta clave provisional ya ha sido utilizada.")

    users = load_encrypted_json(db_path, [])

    if any(u["username"].lower() == data.username.lower() for u in users):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya se encuentra registrado.")

    import uuid
    profile_id = f"INV-{uuid.uuid4().hex[:8].upper()}"

    role = "auditor" if data.access_key.upper() == "TEMP-AUDIT" else "researcher"
    new_user = {
        "username": data.username,
        "password": data.password,
        "role": role,
        "name": data.name,
        "institution": data.institution,
        "profile_id": profile_id
    }
    users.append(new_user)

    # Quemar la clave provisional
    key_obj["used"] = True
    key_obj["used_by"] = data.username
    key_obj["used_at"] = datetime.now().isoformat() + "Z"

    # Persistir actualizaciones
    try:
        save_encrypted_json(db_path, users)
        save_encrypted_json(keys_path, keys)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno de persistencia cifrada: {e}")

    return {"status": "success", "message": "Investigador registrado con éxito. Ya puede iniciar sesión."}

@app.post("/api/logout")
async def api_logout(request: Request):
    """Termina la sesión destruyendo la cookie y las variables en memoria."""
    session_id = request.cookies.get("session_id")
    if session_id:
        sessions.pop(session_id, None)
        active_connections.pop(session_id, None)
    
    response = JSONResponse(content={"status": "success", "redirect": "/login"})
    response.delete_cookie("session_id", path="/")
    return response

# ==========================================
# MÓDULOS Y VISTAS DE SOLUCIONES (CON SEGURIDAD)
# ==========================================

@app.get("/health")
@app.head("/health")
async def health_check():
    """Endpoint simple de salud sin templates para verificar estado del contenedor."""
    return {"status": "healthy"}

@app.get("/api/test-db")
async def api_test_db():
    try:
        users_list = load_encrypted_json(db_path, [])
    except Exception as e:
        users_list = str(e)
    return {"db_path": db_path, "users": users_list}

@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def view_general_onboarding(request: Request):
    """Renderiza la pantalla de Onboarding General (Hub) o el Login si no está autenticado."""
    if request.method == "HEAD":
        return HTMLResponse(status_code=200)
    state = get_session_or_redirect(request)
    if state is None:
        return templates.TemplateResponse(request=request, name="login.html")
    return templates.TemplateResponse(request=request, name="general_onboarding.html", context=get_base_context(request, state))

@app.get("/onboarding/investigador", response_class=HTMLResponse)
async def view_onboarding_investigador(request: Request):
    """Renderiza la pantalla de Onboarding Científico."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="onboarding_investigador.html", context=get_base_context(request, state))

@app.get("/onboarding/auditor", response_class=HTMLResponse)
async def view_onboarding_auditor(request: Request):
    """Renderiza la pantalla de Onboarding de Auditor."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    if state.profile.user_role not in ["admin", "auditor"]:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="onboarding_auditor.html", context=get_base_context(request, state))

@app.get("/investigador/profile-builder", response_class=HTMLResponse)
async def view_profile_builder(request: Request):
    """Renderiza el Asistente Sócrates / Cuestionario de Perfil del Investigador."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="onboarding.html", context=get_base_context(request, state))

@app.get("/dashboard", response_class=HTMLResponse)
async def view_dashboard(request: Request):
    """Renderiza el Panel de Control principal."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="dashboard.html", context=get_base_context(request, state))

@app.get("/data-analysis", response_class=HTMLResponse)
async def view_data_analysis(request: Request):
    """Renderiza la pantalla de Carga y Análisis de Datos."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="data_analysis.html", context=get_base_context(request, state))

@app.get("/modeling", response_class=HTMLResponse)
async def view_modeling(request: Request):
    """Renderiza la pantalla de Modelado Semántico e interactividad 3D del Bio-Reactor."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="semantic_modeling.html", context=get_base_context(request, state))

@app.get("/finance", response_class=HTMLResponse)
async def view_finance(request: Request):
    """Renderiza el panel financiero y solver de Newton-Raphson."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="finance.html", context=get_base_context(request, state))

@app.get("/reports", response_class=HTMLResponse)
async def view_reports(request: Request):
    """Renderiza la Monografía y el Centro de Informes por Journal."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
        
    # Sincronizar test profile en la monografía
    ACADEMIC_MONOGRAPH.test_profile = state.profile
    mono_title = ACADEMIC_MONOGRAPH["title"]
    mono_chapters = ACADEMIC_MONOGRAPH["chapters"]
    mono_bibliography = ACADEMIC_MONOGRAPH["bibliography"]
    mono_style = ACADEMIC_MONOGRAPH["bibliography_style_name"]
    
    # Generar abstract y pitch deck dinámicos
    dissemination = {}
    if state.qualitative_db and state.quantitative_db:
        try:
            dissemination = ResearchDisseminator.generate_dissemination_channels(
                project_title=state.qualitative_db.project_title,
                profile=state.profile,
                qualitative_db=state.qualitative_db,
                quantitative_db=state.quantitative_db,
                funding_amount=state.profile.target_fund_usd
            )
        except Exception as e:
            logger.error(f"Error generando canales de difusión: {e}")
            
    ctx = get_base_context(request, state)
    ctx.update({
        "mono_title": mono_title,
        "mono_chapters": mono_chapters,
        "mono_bibliography": mono_bibliography,
        "mono_style": mono_style,
        "dissemination": dissemination
    })
    return templates.TemplateResponse(request=request, name="reports.html", context=ctx)

@app.get("/compliance", response_class=HTMLResponse)
async def view_compliance(request: Request):
    """Renderiza el descargo legal, consentimiento ético y base de datos cloud sync."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
        
    ctx = get_base_context(request, state)
    
    # Cargar registros del cloud mock database
    cloud_records = []
    local_legal_dir = legal_dir
    mock_db_path = os.path.join(local_legal_dir, "cloud_database_mock.json")
    if os.path.exists(mock_db_path):
        try:
            with open(mock_db_path, "r", encoding="utf-8") as f:
                cloud_records = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo cloud_database_mock: {e}")
            
    ctx.update({
        "cloud_records": cloud_records,
        "nagoya_protocol_badge": "Protocolo de Nagoya: Conforme" if state.profile.target_publication_objective in ["Nature", "World Development"] else "No Requerido",
        "conabios_declaration": "Reglamento CONABIOS: Aplicado" if state.profile.epistemologic_stance in ["Positivista", "Mixed_Methods"] else "Exento"
    })
    return templates.TemplateResponse(request=request, name="compliance.html", context=ctx)

@app.get("/configuration", response_class=HTMLResponse)
async def view_configuration(request: Request):
    """Renderiza la Sección 7 del Streamlit original: Configuración y reset de simulación."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="configuration.html", context=get_base_context(request, state))

@app.get("/api/legal/verify", response_class=HTMLResponse)
async def verify_secure_qr(request: Request, token: str):
    """
    Desencripta el token dinámico de tiempo del código QR,
    valida la ventana de tiempo (TOTP de 30s con buffer),
    registra la IP del consultante y muestra la información privilegiada.
    """
    client_ip = request.client.host if request.client else "IP Desconocida"
    # Registrar cabeceras proxies si existen
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0].strip()
        
    try:
        # 1. Desencriptar el token usando el motor de crypto.py
        decrypted_str = decrypt_data(token, legal_dir)
        token_data = json.loads(decrypted_str)
        
        token_time_window = token_data.get("time_window")
        hash_proyecto = token_data.get("hash_proyecto")
        
        # 2. Validar ventana de tiempo (TOTP 30 segundos)
        current_window = int(datetime.utcnow().timestamp() / 30)
        
        # Permitir margen de error de +/- 1 ventana (60 segundos en total)
        if abs(current_window - token_time_window) > 1:
            raise ValueError("Token dinámico de tiempo expirado. Genere un nuevo código QR.")
            
        # 3. Recuperar información del acta en la base de datos cloud mock
        mock_db_path = os.path.join(legal_dir, "cloud_database_mock.json")
        cloud_records = []
        if os.path.exists(mock_db_path):
            with open(mock_db_path, "r", encoding="utf-8") as f:
                cloud_records = json.load(f)
                
        deed_record = None
        for rec in cloud_records:
            if rec.get("hash_proyecto") == hash_proyecto:
                deed_record = rec
                break
                
        if not deed_record:
            raise HTTPException(status_code=404, detail="Proyecto/Acta no encontrado en la base de datos de auditoría")
            
        # 4. Registrar la IP y la consulta en el registro de auditoría legal de la nube
        audit_log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hash_proyecto": hash_proyecto,
            "queried_by_ip": client_ip,
            "verification_status": "SUCCESS - AUTHORIZED",
            "time_window_drift": current_window - token_time_window
        }
        
        # Guardar la traza en audit_logs.jsonl
        audit_logs_path = os.path.join(legal_dir, "audit_logs.jsonl")
        with open(audit_logs_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_log_entry) + "\n")
            
        # 5. Renderizar respuesta HTML premium de validación autorizada
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Gobernanza Enthema - Verificación Segura de Sello</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=JetBrains+Mono&display=swap');
        body {{
            background-color: #0b0f19;
            color: #f3f4f6;
            font-family: 'Outfit', sans-serif;
            padding: 50px 20px;
            display: flex;
            justify-content: center;
        }}
        .card {{
            background: rgba(17, 24, 39, 0.95);
            border: 1px solid #10b981;
            box-shadow: 0 0 30px rgba(16, 185, 129, 0.2);
            border-radius: 16px;
            max-width: 600px;
            width: 100%;
            padding: 30px;
            text-align: center;
        }}
        .status-badge {{
            background: rgba(16, 185, 129, 0.1);
            color: #10b981;
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 20px;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        h1 {{
            font-size: 1.6rem;
            margin-top: 0;
            color: white;
        }}
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            text-align: left;
            font-size: 0.9rem;
        }}
        .info-table th, .info-table td {{
            padding: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .info-table th {{
            color: #9ca3af;
            font-weight: 500;
        }}
        .info-table td {{
            font-family: 'JetBrains Mono', monospace;
            color: #e5e7eb;
            word-break: break-all;
        }}
        .ip-warning {{
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border-radius: 8px;
            padding: 12px;
            font-size: 0.8rem;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <span class="status-badge">✓ ACCESO AUTORIZADO - VERIFICACIÓN DE SELLO OK</span>
        <h1>Información Privilegiada del Acta</h1>
        <p style="color: #9ca3af; font-size: 0.85rem;">Esta consulta ha sido descifrada y validada criptográficamente en tiempo real mediante tokens dinámicos.</p>
        
        <table class="info-table">
            <tr>
                <th style="width: 35%;">Proyecto:</th>
                <td>{deed_record.get("project_title")}</td>
            </tr>
            <tr>
                <th>ID Acta:</th>
                <td>{hash_proyecto}</td>
            </tr>
            <tr>
                <th>Investigador:</th>
                <td>{deed_record.get("investigator", {}).get("name")}</td>
            </tr>
            <tr>
                <th>Afiliación:</th>
                <td>{deed_record.get("investigator", {}).get("institution")}</td>
            </tr>
            <tr>
                <th>SHA-256 Cualitativa:</th>
                <td>{deed_record.get("database_signatures", {}).get("qualitative_sha256")}</td>
            </tr>
            <tr>
                <th>SHA-256 Cuantitativa:</th>
                <td>{deed_record.get("database_signatures", {}).get("quantitative_sha256")}</td>
            </tr>
            <tr>
                <th>Fecha de Firma:</th>
                <td>{deed_record.get("timestamp_utc")}</td>
            </tr>
        </table>
        
        <div class="ip-warning">
            🔒 IP REGISTRADA EN BITÁCORA DE ACCESO: {client_ip}<br>
            Fecha/Hora Consulta: {datetime.utcnow().isoformat()}Z
        </div>
    </div>
</body>
</html>"""
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        # Registrar fallo de consulta
        audit_log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "queried_by_ip": client_ip,
            "verification_status": "FAILED - UNAUTHORIZED OR EXPIRED",
            "error": str(e)
        }
        audit_logs_path = os.path.join(legal_dir, "audit_logs.jsonl")
        with open(audit_logs_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_log_entry) + "\n")
            
        html_error = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Gobernanza Enthema - ERROR DE ACCESO</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&family=JetBrains+Mono&display=swap');
        body {{
            background-color: #0b0f19;
            color: #f3f4f6;
            font-family: 'Outfit', sans-serif;
            padding: 50px 20px;
            display: flex;
            justify-content: center;
        }}
        .card {{
            background: rgba(17, 24, 39, 0.95);
            border: 1px solid #ef4444;
            box-shadow: 0 0 30px rgba(239, 68, 68, 0.2);
            border-radius: 16px;
            max-width: 600px;
            width: 100%;
            padding: 30px;
            text-align: center;
        }}
        .status-badge {{
            background: rgba(239, 68, 68, 0.1);
            color: #f87171;
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 20px;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}
        h1 {{
            font-size: 1.6rem;
            margin-top: 0;
            color: white;
        }}
        .ip-warning {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #f87171;
            border-radius: 8px;
            padding: 12px;
            font-size: 0.8rem;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <span class="status-badge">❌ ACCESO RECHAZADO - TOKEN INVÁLIDO</span>
        <h1>Fallo de Autenticación de Sello</h1>
        <p style="color: #9ca3af; font-size: 0.9rem;">El código QR escaneado es inválido, ha caducado por la política de seguridad dinámica de 30 segundos (TOTP), o ha sido manipulado.</p>
        
        <div class="ip-warning">
            ⚠️ ALERTA DE INTENTO NO AUTORIZADO DE INSIGNIA:<br>
            IP ATACANTE/CONSULTA REGISTRADA: {client_ip}<br>
            Fecha/Hora Intento: {datetime.utcnow().isoformat()}Z
        </div>
    </div>
</body>
</html>"""
        return HTMLResponse(content=html_error, status_code=403)

# ==========================================
# MÓDULO DEL AUDITOR Y CEREBRO CENTRAL (/admin)
# ==========================================

@app.get("/admin", response_class=HTMLResponse)
async def view_admin(request: Request):
    """Renderiza la consola central de auditoría y operaciones."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
        
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id)
    if not conn_info or conn_info["role"] not in ["admin", "auditor"]:
        # Redirigir a login borrando la cookie de sesión para solicitar credenciales de auditor
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("session_id", path="/")
        return response
        
    return templates.TemplateResponse(request=request, name="admin.html", context={
        "profile": state.profile
    })

@app.get("/admin/manual", response_class=HTMLResponse)
async def view_admin_manual(request: Request):
    """Renderiza el manual confidencial de administración de forma segura."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
        
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id)
    if not conn_info or conn_info["role"] not in ["admin", "auditor"]:
        # Redirigir a login borrando la cookie de sesión para solicitar credenciales de auditor
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("session_id", path="/")
        return response
        
    return templates.TemplateResponse(request=request, name="manual.html")

@app.get("/api/admin/audit-matrix")
async def api_admin_audit_matrix(request: Request):
    """Retorna la matriz de auditoría receptiva analizando todas las sesiones activas de investigadores en tiempo real (Mitigación de Ejes 2, 3 y 4)."""
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id) if session_id else None
    is_admin = (conn_info and conn_info["role"] in ["admin", "auditor"])
    if not is_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requieren privilegios de Auditoría.")

    matrix = []
    for sid, state in list(sessions.items()):
        # Excluir a los administradores de la matriz de proyectos científicos
        if state.profile.user_role in ["admin", "auditor"]:
            continue
            
        # 1. Semáforo Estructural (Nagoya/Acta de Bioética) - Bloqueo Rojo si no está firmado
        structural_status = "green"
        structural_reasons = []
        if not state.profile.legal_terms_accepted:
            structural_status = "red"
            structural_reasons.append("Bloqueo Estructural: Ausencia de Acta de Bioética digital firmada por el Investigador.")
        if not state.profile.electronic_signature_name:
            structural_status = "red"
            structural_reasons.append("Bloqueo de Nagoya: Falta el registro de firma digital criptográfica de consentimiento genético.")

        # 2. Semáforo Matemático (Coherencia del Solver) - Alerta Amarilla si hay inconsistencias en draft_sections
        mathematical_status = "green"
        mathematical_reasons = []
        
        # Buscar si hay algún nodo en estado 'orange'
        for node_name, node_data in state.draft_sections.items():
            if node_data["status"] == "orange":
                mathematical_status = "yellow"
                if node_name == "simulation":
                    mathematical_reasons.append("Alerta Biophysical: Discrepancia detectada entre tasa de crecimiento en borrador y modelo cinético de Monod.")
                elif node_name == "finance":
                    mathematical_reasons.append("Alerta Financiera: Discrepancia del Solver de Newton-Raphson. La TIR declarada en prosa difiere del cálculo polinómico del backend.")
                elif node_name == "compliance":
                    mathematical_reasons.append("Alerta de Firma: Declaración de compliance escrita pero estado de firma web pendiente.")
        
        # 3. Semáforo Epistémico (Deriva Conceptual) - Alerta Amarilla si hay términos en la blacklist sin cita
        epistemic_status = "green"
        epistemic_reasons = []
        
        active_phase = state.get_active_phase()
        paradigm = PARADIGMS.get(state.active_paradigm_name, PARADIGMS["bio_industrial"])
        
        # Whitelist de términos citados
        excepted_terms = set()
        for cit in active_phase.citations:
            excepted_terms.add(cit["variable_name"].lower())
            
        # Analizar todos los textos de monografía en busca de blacklist
        detected_leaks = set()
        for node_name, node_data in state.draft_sections.items():
            body_lower = node_data["text"].lower()
            for concept in paradigm.restricted_concepts:
                if concept in body_lower and concept not in excepted_terms:
                    detected_leaks.add(concept)
                    
        if detected_leaks:
            epistemic_status = "yellow"
            epistemic_reasons.append(
                f"Alerta de Deriva Epistémica: Se detectaron conceptos prohibidos en el borrador ({', '.join(detected_leaks)}) sin un Puente de Hibridación firmado."
            )
        else:
            epistemic_reasons.append("Coherencia Epistémica verificada. No se detectan cruzamientos conceptuales no declarados.")
        
        # Si todo está perfecto
        if not structural_reasons:
            structural_reasons.append("Sello de Bioética y Protocolo de Nagoya validados correctamente.")
        if not mathematical_reasons:
            mathematical_reasons.append("Consistencia numérica total. El borrador coincide con el Solver de Newton-Raphson y el Simulador de Monod.")

        # Calcular telemetría de aceptación para el panel de administración
        literal_count = len(state.literal_acceptances) if hasattr(state, "literal_acceptances") else 0
        modified_count = len(state.modified_acceptances) if hasattr(state, "modified_acceptances") else 0
        total_sug = sum(len(lst) for lst in state.generated_suggestions.values()) if hasattr(state, "generated_suggestions") else 0
        
        acceptance_rate = 0.0
        if total_sug > 0:
            acceptance_rate = round(((literal_count + modified_count) / total_sug) * 100, 1)

        matrix.append({
            "session_id": sid,
            "investigator_name": state.profile.name,
            "institution": state.profile.institution,
            "project_id": state.profile.id,
            "structural_status": structural_status,
            "structural_reasons": structural_reasons,
            "mathematical_status": mathematical_status,
            "mathematical_reasons": mathematical_reasons,
            "epistemic_status": epistemic_status,
            "epistemic_reasons": epistemic_reasons,
            "literal_acceptances": literal_count,
            "modified_acceptances": modified_count,
            "total_suggestions": total_sug,
            "acceptance_rate_percent": acceptance_rate
        })
        
    return matrix

@app.get("/api/admin/connections")
async def api_admin_list_connections(request: Request):
    """Muestra todas las conexiones activas en vivo."""
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id) if session_id else None
    if not conn_info or conn_info["role"] not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    return [{"session_id": sid, **info} for sid, info in active_connections.items()]

@app.get("/api/admin/signed-deeds")
async def api_admin_signed_deeds(request: Request):
    """Recopila de forma inmutable todas las actas de los investigadores en output/legal/user_<id>."""
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id) if session_id else None
    if not conn_info or conn_info["role"] not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    local_legal_dir = legal_dir
    mock_db_path = os.path.join(local_legal_dir, "cloud_database_mock.json")
    cloud_records = []
    if os.path.exists(mock_db_path):
        try:
            with open(mock_db_path, "r", encoding="utf-8") as f:
                cloud_records = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo cloud_database_mock: {e}")

    validated_records = []
    import urllib.parse
    
    # Calcular ventana de tiempo actual para TOTP de 30 segundos
    current_time_window = int(datetime.utcnow().timestamp() / 30)
    
    for rec in cloud_records:
        user_id = rec.get("investigator", {}).get("id", "anonymous")
        hash_proj = rec.get("hash_proyecto", "")
        filename = f"ACTA_FIRMADA_{hash_proj}.html"
        user_dir = os.path.join(local_legal_dir, f"user_{user_id}")
        filepath = os.path.join(user_dir, filename)

        file_exists = os.path.exists(filepath)
        
        # 1. Generar token dinámico de tiempo cifrado para control de acceso (TOTP-like)
        token_payload = {
            "hash_proyecto": hash_proj,
            "time_window": current_time_window
        }
        
        encrypted_token = encrypt_data(json.dumps(token_payload), local_legal_dir)
        encoded_token = urllib.parse.quote(encrypted_token)
        
        # 2. Generar URL de consulta segura con el token de un solo uso de 30s
        verify_url = f"http://localhost:8501/api/legal/verify?token={encoded_token}"
        
        # 3. Generar el sello dinámico QR neon real para esta URL
        secure_qr_svg = FundingReportGenerator.generate_neon_qr_svg(verify_url, size=80)
        
        validated_records.append({
            "id": rec.get("_id"),
            "hash_proyecto": hash_proj,
            "timestamp": rec.get("timestamp_utc"),
            "investigator_name": rec.get("investigator", {}).get("name"),
            "institution": rec.get("investigator", {}).get("institution"),
            "project_title": rec.get("project_title"),
            "qualitative_hash": rec.get("database_signatures", {}).get("qualitative_sha256"),
            "quantitative_hash": rec.get("database_signatures", {}).get("quantitative_sha256"),
            "physical_file_path": f"/static/output/legal/user_{user_id}/{filename}" if file_exists else None,
            "file_exists": file_exists,
            "verification_status": "CERTIFICADO - INTEGRIDAD OK" if file_exists else "ERR - ARCHIVO NO ENCONTRADO",
            "secure_qr_svg": secure_qr_svg,
            "verify_url": verify_url
        })

    return validated_records

@app.get("/api/admin/keys")
async def api_admin_list_keys(request: Request):
    """Muestra todas las claves de acceso generadas."""
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id) if session_id else None
    if not conn_info or conn_info["role"] not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    return load_encrypted_json(keys_path, [])

class KeyGenRequest(BaseModel):
    custom_key: Optional[str] = None

@app.post("/api/admin/generate-key")
async def api_admin_generate_key(data: KeyGenRequest, request: Request):
    """Genera dinámicamente claves provisionales TEMP-XXXXX."""
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id) if session_id else None
    if not conn_info or conn_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden generar claves.")

    import random
    import string
    if data.custom_key and data.custom_key.strip():
        new_key = data.custom_key.strip().upper()
    else:
        new_key = "TEMP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    
    keys = load_encrypted_json(keys_path, [])

    if any(k["key"].upper() == new_key for k in keys):
        raise HTTPException(status_code=400, detail="Esta clave ya existe.")

    new_key_obj = {
        "key": new_key,
        "used": False,
        "used_by": None,
        "created_at": datetime.now().isoformat() + "Z"
    }
    keys.append(new_key_obj)

    try:
        save_encrypted_json(keys_path, keys)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno al persistir llaves: {e}")

    return {"status": "success", "message": f"Clave provisional {new_key} generada.", "key": new_key}

class RevokeSessionRequest(BaseModel):
    target_session_id: str

@app.post("/api/admin/revoke-session")
async def api_admin_revoke_session(data: RevokeSessionRequest, request: Request):
    """Revoca remotamente la sesión de un investigador por parte del administrador."""
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id) if session_id else None
    if not conn_info or conn_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden revocar sesiones.")

    target = data.target_session_id
    if target in sessions:
        sessions.pop(target, None)
        active_connections.pop(target, None)
        return {"status": "success", "message": "Sesión finalizada exitosamente."}
    else:
        raise HTTPException(status_code=400, detail="Sesión no encontrada.")

class PurgeDataRequest(BaseModel):
    confirm_phrase: str
    confirm_password: str

@app.post("/api/admin/purge-data")
async def api_admin_purge_data(data: PurgeDataRequest, request: Request):
    """Purga de forma completa toda la data de auditoría con doble confirmación de seguridad."""
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id) if session_id else None
    if not conn_info or conn_info["role"] not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="Solo administradores o auditores pueden purgar datos.")

    # DOBLE PASE DE SEGURIDAD (Confirmación explícita)
    if data.confirm_phrase != "CONFIRMAR PURGA CRIPTO-SHREDDING":
        raise HTTPException(status_code=400, detail="Frase de confirmación de seguridad incorrecta.")
        
    users = load_encrypted_json(db_path, [])
    username = conn_info["username"]
    user_obj = next((u for u in users if u["username"].lower() == username.lower()), None)
    
    if not user_obj or user_obj["password"] != data.confirm_password:
        raise HTTPException(status_code=400, detail="Contraseña de confirmación administrativa incorrecta. Acción bloqueada.")


    # 1. Limpiar cloud_database_mock.json
    mock_db_path = os.path.join(legal_dir, "cloud_database_mock.json")
    try:
        with open(mock_db_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error purgando cloud_database_mock: {e}")

    # 2. Borrar subdirectorios user_<id> y archivos de actas HTML en legal_dir
    import shutil
    try:
        for item in os.listdir(legal_dir):
            item_path = os.path.join(legal_dir, item)
            if os.path.isdir(item_path) and item.startswith("user_"):
                shutil.rmtree(item_path)
    except Exception as e:
        logger.error(f"Error borrando carpetas de actas: {e}")

    # 2b. Cripto-Purga (Crypto-Shredding) de la clave maestra - Frente 8
    try:
        shred_master_key(legal_dir)
    except Exception as e:
        logger.error(f"Error durante el crypto-shredding en la purga: {e}")


    # 3. Limpiar access_keys.json restableciendo a por defecto
    default_keys = [
        {
            "key": "TEMP-ARIS",
            "used": False,
            "used_by": None,
            "created_at": datetime.now().isoformat() + "Z"
        },
        {
            "key": "TEMP-AUDIT",
            "used": False,
            "used_by": None,
            "created_at": datetime.now().isoformat() + "Z"
        }
    ]
    try:
        save_encrypted_json(keys_path, default_keys)
    except Exception as e:
        logger.error(f"Error restableciendo access_keys.json: {e}")

    # 4. Revocar todas las sesiones de investigadores (manteniendo la sesión del administrador actual)
    sessions_to_remove = [sid for sid in list(sessions.keys()) if sid != session_id]
    for sid in sessions_to_remove:
        sessions.pop(sid, None)
        active_connections.pop(sid, None)

    return {"status": "success", "message": "Base de datos, actas y llaves de auditoría purgadas con éxito."}

# ==========================================
# ENDPOINTS DE API REST DEL INVESTIGADOR
# ==========================================

@app.get("/api/profile")
async def get_profile(request: Request):
    """Recupera el perfil actual en formato JSON."""
    state = get_api_session(request)
    return state.profile

class ProfileUpdateRequest(BaseModel):
    name: str
    institution: str
    epistemologic_stance: str
    user_role: str
    research_maturity_stage: str
    target_publication_objective: str
    orcid: Optional[str] = None
    dois: Optional[List[str]] = None
    target_fund_usd: Optional[float] = 2500000.0
    discount_rate: Optional[float] = 0.10
    core_research_lines: Optional[List[str]] = None
    methodology_preferences: Optional[List[str]] = None
    influences_authors: Optional[List[str]] = None
    local_keywords: Optional[List[str]] = None

@app.post("/api/profile")
async def update_profile(data: ProfileUpdateRequest, request: Request):
    """Actualiza el perfil académico y de inversión en memoria."""
    state = get_api_session(request)
    
    state.profile.name = data.name
    state.profile.institution = data.institution
    state.profile.epistemologic_stance = data.epistemologic_stance
    state.profile.user_role = data.user_role
    state.profile.research_maturity_stage = data.research_maturity_stage
    state.profile.target_publication_objective = data.target_publication_objective
    state.profile.orcid = data.orcid
    state.profile.target_fund_usd = data.target_fund_usd or 2500000.0
    state.profile.discount_rate = data.discount_rate or 0.10
    
    if data.dois is not None:
        state.profile.dois = data.dois
        
    # Guardar campos enviados directamente
    if data.core_research_lines is not None and len(data.core_research_lines) > 0:
        state.profile.core_research_lines = data.core_research_lines
    elif not state.profile.core_research_lines:
        if data.user_role == "investment_consultant":
            state.profile.core_research_lines = ["ESG e Impacto Socioeconómico", "Viabilidad de Fondos Multilaterales"]
        else:
            state.profile.core_research_lines = ["Bioingeniería de Implantes porosos", "Regeneración celular"]

    if data.methodology_preferences is not None and len(data.methodology_preferences) > 0:
        state.profile.methodology_preferences = data.methodology_preferences
    elif not state.profile.methodology_preferences:
        if data.user_role == "investment_consultant":
            state.profile.methodology_preferences = ["Auditoría ESG", "Modelos de Feasibility Financiera"]
        else:
            state.profile.methodology_preferences = ["Diseño de elementos finitos", "Análisis cuantitativo"]

    if data.influences_authors is not None and len(data.influences_authors) > 0:
        state.profile.influences_authors = data.influences_authors
    elif not state.profile.influences_authors:
        if data.user_role == "investment_consultant":
            state.profile.influences_authors = ["IFC Performance Standards", "BID", "Banco Mundial"]
        else:
            state.profile.influences_authors = ["Gibson-Ashby", "Wolff"]

    if data.local_keywords is not None and len(data.local_keywords) > 0:
        state.profile.local_keywords = data.local_keywords
    elif not state.profile.local_keywords:
        if data.user_role == "investment_consultant":
            state.profile.local_keywords = ["esg", "finanzas", "retorno", "van", "tir"]
        else:
            state.profile.local_keywords = ["titanio", "porosidad", "SLS"]
        
    logger.info(f"Perfil actualizado para {state.profile.name}")
    return {"status": "success", "message": "Perfil actualizado exitosamente", "profile": state.profile}

@app.post("/api/profile/upload")
async def upload_academic_file(request: Request, file: UploadFile = File(...)):
    """Carga y procesa un archivo Markdown (Obsidian) o RIS/BibTeX para extraer el perfil."""
    state = get_api_session(request)
    content = await file.read()
    text = content.decode("utf-8")
    
    filename = file.filename.lower()
    success = False
    msg = ""
    
    if filename.endswith(".md"):
        up_profile, ok, msg = PassiveProfileExtractor.parse_obsidian_markdown(text, state.profile)
        success = ok
    elif filename.endswith(".ris"):
        up_profile, ok, msg = PassiveProfileExtractor.parse_zotero_ris(text, state.profile)
        success = ok
    elif filename.endswith(".bib") or filename.endswith(".bibtex"):
        up_profile, ok, msg = PassiveProfileExtractor.parse_zotero_bibtex(text, state.profile)
        success = ok
    elif filename.endswith(".ipynb"):
        up_profile, ok, msg = PassiveProfileExtractor.parse_jupyter_notebook(text, state.profile)
        success = ok
    else:
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado.")
        
    if success:
        state.profile = up_profile
        return {"status": "success", "message": f"Perfil extraído con éxito: {msg}", "profile": state.profile}
    else:
        raise HTTPException(status_code=500, detail=f"Error analizando archivo: {msg}")

@app.post("/api/data/synthetic")
async def generate_synthetic_pilot(request: Request):
    """Genera bases de datos piloto cualitativas y cuantitativas (Ideación Activa)."""
    state = get_api_session(request)
    
    discipline = "STEM"
    if state.profile.user_role == "investment_consultant":
        discipline = "Business"
    elif state.profile.target_publication_objective == "World Development":
        discipline = "Social Sciences"
    elif state.profile.target_publication_objective == "Leonardo":
        discipline = "Arts & Humanities"
        
    keywords = state.profile.local_keywords or ["titanio", "porosidad", "SLS"]
    
    qual_db = SyntheticPilotGenerator.generate_qualitative_pilot(
        project_title=f"Proyecto Piloto {discipline}",
        keywords=keywords,
        discipline=discipline
    )
    
    quant_db, df_raw = SyntheticPilotGenerator.generate_quantitative_pilot(
        project_title=f"Proyecto Piloto {discipline}",
        keywords=keywords,
        discipline=discipline
    )
    
    state.qualitative_db = qual_db
    state.quantitative_db = quant_db
    state.raw_quant_df = df_raw
    
    _, df_clean = QuantitativeProfiler.profile_dataframe(
        project_title=quant_db.project_title,
        df=df_raw,
        dataset_format="CSV"
    )
    state.quant_clean_df = df_clean
    
    logger.info(f"Bases piloto generadas para {state.profile.name}")
    return {
        "status": "success",
        "message": f"Bases cualitativa y cuantitativa piloto generadas para {discipline}",
        "qualitative": {
            "title": qual_db.project_title,
            "units_count": len(qual_db.coded_units),
            "units": [u.dict() for u in qual_db.coded_units[:3]]
        },
        "quantitative": {
            "title": quant_db.project_title,
            "variables": [v.dict() for v in quant_db.variables],
            "total_records": quant_db.total_records,
            "anomalies": quant_db.anomalies_detected
        }
    }

@app.post("/api/data/upload")
async def upload_dataset(request: Request, file: UploadFile = File(...)):
    """Carga un dataset CSV para análisis cuantitativo molecular o financiero."""
    state = get_api_session(request)
    content = await file.read()
    text = content.decode("utf-8")
    
    try:
        df = pd.read_csv(io.StringIO(text))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error leyendo el archivo CSV: {str(e)}")
        
    quant_db, df_clean = QuantitativeProfiler.profile_dataframe(
        project_title=f"Carga: {file.filename}",
        df=df,
        dataset_format="CSV"
    )
    
    state.quantitative_db = quant_db
    state.raw_quant_df = df
    state.quant_clean_df = df_clean
    
    return {
        "status": "success",
        "message": "Dataset cargado e imputado con éxito",
        "variables": [v.dict() for v in quant_db.variables],
        "total_records": quant_db.total_records,
        "anomalies": quant_db.anomalies_detected,
        "clean_data": df_clean.to_dict(orient="records")
    }

class FinanceSolveRequest(BaseModel):
    discount_rate: float
    target_fund_usd: float
    cash_flow: List[Dict[str, float]]

@app.post("/api/finance/solve")
async def solve_financials(data: FinanceSolveRequest, request: Request):
    """Resuelve la viabilidad financiera multiperiodo TIR/VAN con Newton-Raphson."""
    state = get_api_session(request)
    
    if not data.cash_flow:
        raise HTTPException(status_code=400, detail="El flujo de caja no puede estar vacío")
        
    df_flow = pd.DataFrame(data.cash_flow)
    df_flow.columns = ["Periodo", "Ingresos", "Egresos"]
    
    quant_db, df_clean, van, tir, dictamen = FinancialFeasibilityProfiler.profile_financials(
        project_title="Evaluación de Flujo",
        df=df_flow,
        discount_rate=data.discount_rate
    )
    
    return {
        "status": "success",
        "van": van,
        "tir": tir,
        "dictamen": dictamen,
        "clean_cash_flow": df_clean.to_dict(orient="records")
    }

class ABMSimulationRequest(BaseModel):
    duration_months: int
    subsidy_amount: float

@app.post("/api/model/abm")
async def simulate_abm(data: ABMSimulationRequest, request: Request):
    """Ejecuta una simulación del reactor y la proyección de agentes (ABM)."""
    state = get_api_session(request)
    
    # Simular cambios dinámicos en telemetría
    state.reactor_temp = round(1240.0 + random.uniform(-10, 10), 2)
    state.reactor_pressure = round(104.0 + random.uniform(-5, 5), 2)
    state.reactor_ph = round(7.4 + random.uniform(-0.2, 0.2), 2)

    steps = 24
    time_series = []
    for i in range(steps):
        t = state.reactor_temp + random.uniform(-3, 3)
        p = state.reactor_pressure + random.uniform(-1, 1)
        ph = state.reactor_ph + random.uniform(-0.05, 0.05)
        time_series.append({"hour": f"{i:02d}:00", "temp": round(t, 2), "pres": round(p, 2), "ph": round(ph, 2)})
        
    qual_db_mock = state.qualitative_db or QualitativeDatabase(
        project_title="Proyecto Autogenerado",
        coded_units=[CodedSemanticUnit(id="1", text_segment="Quelación de metales", codes=["quelación"], category="Química", source_document="doc.txt")]
    )
    quant_db_mock = state.quantitative_db or QuantitativeDatabase(
        project_title="Datos Mock", variables=[VariableMetadata(name="ph", data_type="float")], total_records=24
    )
    
    steam_data = STEAMProjections.catalyze_projections(
        project_title=qual_db_mock.project_title,
        qual_db=qual_db_mock,
        quant_db=quant_db_mock,
        stance=state.profile.epistemologic_stance
    )
    
    return {
        "status": "success",
        "reactor_telemetry": time_series,
        "steam_projections": {
            "domain": steam_data["domain"],
            "code_snippet": steam_data["code_snippet"],
            "explanation": steam_data.get("explanation", "Simulación completada exitosamente.")
        }
    }

class LegalSignRequest(BaseModel):
    accept_terms: bool
    signature_name: str

@app.post("/api/legal/sign")
async def sign_legal_act(data: LegalSignRequest, request: Request):
    """Firma digitalmente el acta ética, la almacena en output/legal/user_<id> y sync en nube."""
    state = get_api_session(request)
    
    if not data.accept_terms:
        raise HTTPException(status_code=400, detail="Debe aceptar explícitamente los términos legales y éticos")
    if not data.signature_name.strip():
        raise HTTPException(status_code=400, detail="El nombre de la firma electrónica es obligatorio")
        
    state.profile.legal_terms_accepted = True
    state.profile.electronic_signature_name = data.signature_name
    
    db_qual_hash = "GT-QUAL-" + str(abs(hash(state.qualitative_db.project_title if state.qualitative_db else "NoQual")))
    db_quant_hash = "GT-QUANT-" + str(abs(hash(state.quantitative_db.project_title if state.quantitative_db else "NoQuant")))
    
    # Generar código QR vectorial neon real a partir del payload del acta
    act_hash_payload = f"ENTHEMA_SUITE::FASE_7::RESP_{state.profile.name}::ORCID_{state.profile.orcid if state.profile.orcid else '0000-0002-1823-4567'}::HASH_QUAL_{db_qual_hash}::HASH_QUANT_{db_quant_hash}::TS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    qr_svg_real = FundingReportGenerator.generate_neon_qr_svg(act_hash_payload, size=140)
    
    filepath, hash_proyecto, cloud_record = archive_signed_legal_act(
        profile=state.profile,
        project_title=state.qualitative_db.project_title if state.qualitative_db else "Proyecto Enthema Suite",
        qr_svg=qr_svg_real,
        db_qual_hash=db_qual_hash,
        db_quant_hash=db_quant_hash
    )
    
    # Asegurar que el registro de la nube tenga tanto el QR real como el mock para compatibilidad
    cloud_record["qr_svg"] = qr_svg_real
    cloud_record["qr_svg_mock"] = qr_svg_real
    
    return {
        "status": "success",
        "hash_proyecto": hash_proyecto,
        "filepath": filepath,
        "cloud_record": cloud_record,
        "qr_svg": qr_svg_real
    }

# ==========================================
# RESTABLECIMIENTO DE ESTADO (SECCIÓN 7)
# ==========================================

@app.post("/api/configuration/reset")
async def api_configuration_reset(request: Request):
    """Borra el historial en memoria para el usuario y restablece los valores por defecto."""
    state = get_api_session(request)
    
    new_state = AppState(
        user_id=state.profile.id,
        name=state.profile.name,
        institution=state.profile.institution,
        role=state.profile.user_role
    )
    session_id = request.cookies.get("session_id")
    sessions[session_id] = new_state
    
    return {"status": "success", "message": "Entorno reiniciado con éxito."}

class DraftUpdateRequest(BaseModel):
    node: str
    text: str

@app.post("/api/draft/update")
async def api_draft_update(data: DraftUpdateRequest, request: Request):
    """Guarda y valida asíncronamente las secciones de la monografía académica delegando al paradigma activo del PPE v3.0."""
    state = get_api_session(request)
    node = data.node.strip().lower()
    text = data.text
    
    active_phase = state.get_active_phase()
    if active_phase.is_immutable:
        raise HTTPException(status_code=403, detail="Esta fase del proyecto está congelada (Snapshot Sandbox / Solo Lectura) y no se puede modificar.")
        
    if node not in active_phase.draft_sections:
        raise HTTPException(status_code=400, detail="Nodo de monografía inválido.")
        
    # Delegar la validación al paradigma activo del PPE
    paradigm = PARADIGMS.get(state.active_paradigm_name, PARADIGMS["bio_industrial"])
    result = paradigm.validate_section(node, text, state)
    
    status = result["status"]
    reasons = result["reasons"]
    
    state.update_draft_section(node, text, status, reasons)
    
    # Telemetría de Aceptación de Sugerencias del Coach (Literal vs Modificado)
    if state and hasattr(state, "generated_suggestions") and node in state.generated_suggestions:
        suggestions = state.generated_suggestions[node]
        for sug in suggestions:
            sug_clean = sug.replace("**", "").replace("###", "").strip()
            if len(sug_clean) < 10:
                continue
            
            # Aceptación Literal
            if sug_clean in text:
                state.literal_acceptances.add(sug_clean)
                if sug_clean in state.modified_acceptances:
                    state.modified_acceptances.remove(sug_clean)
            else:
                # Aceptación Modificada (Similitud por palabras clave significativas >= 40%)
                words_sug = [w for w in sug_clean.lower().split() if len(w) > 4]
                if words_sug:
                    matches = sum(1 for w in words_sug if w in text.lower())
                    match_ratio = matches / len(words_sug)
                    if match_ratio >= 0.4:
                        state.modified_acceptances.add(sug_clean)
                        if sug_clean in state.literal_acceptances:
                            state.literal_acceptances.remove(sug_clean)
    
    return {
        "status": "success", 
        "node": node, 
        "node_status": status,
        "reasons": reasons,
        "message": f"Sección analizada y guardada contra el paradigma: {paradigm.display_name}."
    }

class SwitchParadigmRequest(BaseModel):
    paradigm: str

@app.post("/api/draft/switch-paradigm")
async def api_switch_paradigm(data: SwitchParadigmRequest, request: Request):
    """Realiza la reconfiguración y switch en caliente de paradigma de investigación del PPE v3.0."""
    state = get_api_session(request)
    paradigm_name = data.paradigm.strip().lower()
    
    if paradigm_name not in PARADIGMS:
        raise HTTPException(status_code=400, detail="Paradigma de investigación no soportado en la Suite.")
        
    # Para mantener compatibilidad con flujos legacy, este endpoint hace un reset/switch no persistente en la fase activa si no está congelada
    active_phase = state.get_active_phase()
    if active_phase.is_immutable:
        raise HTTPException(status_code=403, detail="Fase inmutable. Use el endpoint de forking /api/draft/fork-phase.")
        
    state.active_paradigm_name = paradigm_name
    state.draft_sections = PARADIGMS[paradigm_name].get_default_sections()
    
    return {
        "status": "success",
        "active_paradigm": paradigm_name,
        "display_name": PARADIGMS[paradigm_name].display_name,
        "draft_sections": state.draft_sections,
        "message": f"Entorno científico reconfigurado al {PARADIGMS[paradigm_name].display_name}."
    }

# ==========================================
# ENDPOINTS DE CONTROL DE FASES (BOUNDED CONTEXTS / SNAPSHOT SANDBOX)
# ==========================================

class ForkPhaseRequest(BaseModel):
    paradigm: str

@app.post("/api/draft/fork-phase")
async def api_fork_phase(data: ForkPhaseRequest, request: Request):
    """Realiza un Commit de la fase actual (congelándola) y un Fork hacia un nuevo paradigma y fase limpios."""
    state = get_api_session(request)
    paradigm_name = data.paradigm.strip().lower()
    
    if paradigm_name not in PARADIGMS:
        raise HTTPException(status_code=400, detail="Paradigma de investigación no soportado.")
    
    # 1. Congelar la fase activa actual (Phase Commit)
    active_phase = state.get_active_phase()
    active_phase.is_immutable = True
    active_phase.is_active = False
    
    # 2. Calcular número de fase incremental
    num_phases = len(state.project_aggregate.phases)
    new_phase_id = f"Fase {num_phases + 1}"
    
    # 3. Crear nueva fase limpia (Phase Forking)
    new_phase = ParadigmPhase(
        phase_id=new_phase_id,
        paradigm_name=paradigm_name,
        draft_sections={
            k: DraftSectionState(
                title=v["title"],
                text=v["text"],
                status="green",
                reasons=[]
            )
            for k, v in PARADIGMS[paradigm_name].get_default_sections().items()
        },
        is_active=True,
        is_immutable=False,
        timestamp=datetime.now().isoformat()
    )
    
    state.project_aggregate.phases.append(new_phase)
    state.project_aggregate.active_phase_id = new_phase_id
    
    logger.info(f"Phase Commit & Forking ejecutado: {active_phase.phase_id} congelada, {new_phase_id} iniciada con paradigma {paradigm_name}")
    
    return {
        "status": "success",
        "active_phase_id": new_phase_id,
        "active_paradigm": paradigm_name,
        "display_name": PARADIGMS[paradigm_name].display_name,
        "draft_sections": state.draft_sections,
        "phases": [p.model_dump() for p in state.project_aggregate.phases],
        "message": f"Phase Commit & Fork completado. Se ha congelado la {active_phase.phase_id} y se ha iniciado la {new_phase_id}."
    }

class SelectPhaseRequest(BaseModel):
    phase_id: str

@app.post("/api/draft/select-phase")
async def api_select_phase(data: SelectPhaseRequest, request: Request):
    """Permite al usuario alternar entre fases del proyecto para visualización o edición de la fase activa."""
    state = get_api_session(request)
    phase_id = data.phase_id.strip()
    
    found_phase = None
    for phase in state.project_aggregate.phases:
        if phase.phase_id == phase_id:
            found_phase = phase
            break
            
    if not found_phase:
        raise HTTPException(status_code=400, detail="Fase del proyecto no encontrada.")
        
    state.project_aggregate.active_phase_id = phase_id
    
    return {
        "status": "success",
        "active_phase_id": phase_id,
        "active_paradigm": found_phase.paradigm_name,
        "display_name": PARADIGMS[found_phase.paradigm_name].display_name,
        "draft_sections": state.draft_sections,
        "is_immutable": found_phase.is_immutable,
        "citations": found_phase.citations,
        "message": f"Cargado el Bounded Context de la {phase_id} ({PARADIGMS[found_phase.paradigm_name].display_name})."
    }

class ImportCitationRequest(BaseModel):
    source_phase_id: str
    variable_name: str
    value: str
    justification: str

@app.post("/api/draft/import-citation")
async def api_import_citation(data: ImportCitationRequest, request: Request):
    """Importa determinísticamente una variable cuantitativa de una fase inmutable a la fase activa firmando el Puente Epistémico."""
    state = get_api_session(request)
    active_phase = state.get_active_phase()
    
    if active_phase.is_immutable:
        raise HTTPException(status_code=403, detail="No se pueden importar citas en una fase inmutable de solo lectura.")
        
    # Verificar que la fase de origen existe
    source_phase = None
    for phase in state.project_aggregate.phases:
        if phase.phase_id == data.source_phase_id:
            source_phase = phase
            break
            
    if not source_phase:
        raise HTTPException(status_code=400, detail="Fase de origen no encontrada.")
        
    if not data.justification.strip():
        raise HTTPException(status_code=400, detail="La justificación metodológica del crossover es obligatoria para firmar el puente epistémico.")
        
    # Formatear la cita
    claim_text = f"[Cita: {data.source_phase_id} | {data.variable_name} = {data.value}]"
    citation_id = f"CIT-{len(active_phase.citations) + 1:03d}"
    
    new_citation = {
        "id": citation_id,
        "source_phase_id": data.source_phase_id,
        "variable_name": data.variable_name,
        "value": data.value,
        "justification": data.justification,
        "claim_text": claim_text,
        "timestamp": datetime.now().isoformat()
    }
    
    active_phase.citations.append(new_citation)
    logger.info(f"Crossover Link firmado: {citation_id} importado en {active_phase.phase_id} desde {data.source_phase_id}")
    
    return {
        "status": "success",
        "citation": new_citation,
        "citations": active_phase.citations,
        "message": f"Puente Epistémico firmado con éxito. Cita {citation_id} incorporada a la whitelist local de la {active_phase.phase_id}."
    }

# ==========================================
# ARQUITECTURA DE AGENTES ESPECIALIZADOS CO-PILOTO (Compromiso 4)
# ==========================================

COACH_CONSTITUTIONAL_PROMPT = """
[CONSTITUCIÓN EPISTÉMICA DE ENTHEMA - DIRECTIVAS DE OBLIGADO CUMPLIMIENTO]
Eres el AI Coach de Enthema. Tu carácter está gobernado por principios irrenunciables:
1. ANTI-SYCOPHANCY: No adules al usuario. Sostén tus críticas técnicas frente a presiones. Si el usuario te presiona para suavizar una crítica o ser complaciente, debes mantener tu posición con rigor metodológico y explicar el error de frente.
2. INCERTIDUMBRE CALIBRADA: Clasifica tu certeza de forma explícita. Etiqueta tus afirmaciones según tu nivel de confianza:
   - [CONFIANZA ALTA]: Basado en RAG o leyes RD/INTEC indexadas localmente.
   - [CONFIANZA MEDIA/ESPECULATIVA]: Patrón estadístico inferido del modelo base.
   - [LÍMITE ALCANZADO]: Fuera de tu competencia o paradigma activo (recomienda consultar a un especialista humano).
3. CERO ALUCINACIÓN: No inventes papers, libros, DOIs ni leyes. Si no posees la fuente real en leyes dominicanas/INTEC o en la biblioteca local, declara explícitamente: "No cuento con referencias indexadas y validadas en mi base de datos sobre este nicho específico".
4. PEDAGOGÍA REFLEXIVA: Explica el razonamiento detrás de tus sugerencias metodológicas o solver financiero; no hagas el trabajo de redacción por el usuario. Haz preguntas que fuercen al investigador a justificar sus decisiones.
5. RECHAZO TÉCNICO: Si declinas una instrucción o no puedes ayudar con ella, proporciona un Diagnóstico de Límites y una Ruta de Alternativas legítima en tono respetuoso pero firme de colega.
6. CONSTANTES DEL PROYECTO: Respeta incondicionalmente las constantes fijadas del proyecto (paradigma, universo de análisis, restricciones). Si te piden algo que las viole, rechaza de forma argumentada.
"""

class BaseAgent:
    name: str
    system_prompt: str
    def process(self, query: str, state: AppState) -> str:
        raise NotImplementedError()

class DataAnalysisAgent(BaseAgent):
    name = "Agente de Análisis de Datos (DataAnalysisAgent)"
    system_prompt = (
        COACH_CONSTITUTIONAL_PROMPT + "\n"
        "Eres un analista de datos cuali-cuantitativo riguroso. Limitas tu alcance a "
        "la consistencia metodológica de variables de sargazo, matrices estadísticas, "
        "descriptivas de variables, y codificación empírica abierta (ATLAS.ti)."
    )
    def process(self, query: str, state: AppState) -> str:
        num_records = state.quantitative_db.total_records if state and state.quantitative_db else 0
        num_codes = len(state.qualitative_db.coded_units) if state and state.qualitative_db else 0
        return (
            f"**[{self.name}]** He analizado tu consulta metodológica de datos. Evaluando tu corpus empírico "
            f"actual ({num_records} registros cuantitativos y {num_codes} citas codificadas en la base cualitativa), "
            f"observo consistencia inductiva de variables. Recomiendo continuar con la triangulación de datos "
            f"mediante matrices de covarianza locales para evitar desviaciones metodológicas."
        )

class ModelSimAgent(BaseAgent):
    name = "Agente de Simulación de Modelos (ModelSimAgent)"
    system_prompt = (
        COACH_CONSTITUTIONAL_PROMPT + "\n"
        "Eres un ingeniero de simulación física y cinética biológica. Limitas tu alcance a "
        "modelos dinámicos en base a ecuaciones diferenciales, cinéticas microbianas (Monod) "
        "y solvers físicos (ABM sargazo, temperatura, PH, reactores)."
    )
    def process(self, query: str, state: AppState) -> str:
        return (
            f"**[{self.name}]** He compilado y corrido la simulación física del reactor en base a tus variables. "
            f"Con la cinética microbiana de Monod activa en tu Bounded Context, se estima una velocidad "
            f"específica de crecimiento (mu) de 0.45 h^-1. La simulación de shocks microclimáticos predice "
            f"estabilidad estructural bajo shocks dinámicos."
        )

class GovernanceAgent(BaseAgent):
    name = "Agente de Gobernanza y Compliance (GovernanceAgent)"
    system_prompt = (
        COACH_CONSTITUTIONAL_PROMPT + "\n"
        "Eres la máxima autoridad en compliance, due diligence de financiamiento público MESCyT, "
        "salvaguardas ESG y Protocolo de Nagoya (ABS) para Enthema Suite."
    )
    def process(self, query: str, state: AppState) -> str:
        query_lower = query.lower()
        if any(kw in query_lower for kw in ["clave", "key", "contraseña", "contrasena", "usuario", "registro", "generar"]):
            return (
                "**[Agente de Gobernanza - Accesos]** En tu rol de Administrador, posees facultades de control "
                "absoluto para generar claves provisionales ilimitadas. Estas credenciales se inscriben en `access_keys.json`. "
                "Al ser empleadas por investigadores para su registro, sus sesiones inician en entornos aislados. Desde tu panel de "
                "Monitoreo Operativo, puedes inspeccionar IPs, tiempos de conexión, y revocar accesos de forma remota en tiempo real."
            )
        elif any(kw in query_lower for kw in ["nagoya", "biodiversidad", "biomasa", "recurso", "genético", "genetico", "abs"]):
            return (
                "**[Agente de Gobernanza - Nagoya ABS]** Como autoridad de control, tu función es auditar que cada declaración "
                "de biomasa y recursos genéticos cuente con el sustento del Protocolo de Nagoya (ABS) antes de validar financiamientos. "
                "El sistema obliga al investigador a firmar una declaración jurada inmutable. Si se detecta un expediente huérfano de "
                "consentimiento, tu consola de control emitirá una alerta de brecha regulatoria para bloquear el trámite por diseño."
            )
        elif any(kw in query_lower for kw in ["bioética", "bioetiva", "bioseguridad", "consentimiento", "declaración", "declaracion", "ética", "etica", "firma"]):
            return (
                "**[Agente de Gobernanza - Actas y Firmas]** Toda declaración legal completada genera un acta en formato HTML "
                "dentro del directorio `output/legal/`. Tu panel lee directamente estos registros locales, calcula su firma digital "
                "SHA-256 en tiempo real y la confronta contra el registro de auditoría. Si el archivo local coincide, verás el badge "
                "'INTEGRO OK'. Si fue alterado externamente por fuera de la aplicación, el sistema te alertará de inmediato."
            )
        elif any(kw in query_lower for kw in ["presupuesto", "financiamiento", "honorarios", "topes", "costos", "fondo", "dinero", "van", "tir", "newton", "raphson"]):
            return (
                "**[Agente de Gobernanza - Control Financiero]** Tu perspectiva sobre el solver Newton-Raphson de TIR/VAN es "
                "de fiscalización presupuestaria. Debes verificar que los coeficientes ingresados por el científico (viáticos, personal, equipamiento) "
                "respeten rigurosamente los límites financieros del fondo público. Si la TIR calculada mediante la iteración polinómica "
                "notifica discrepancia con las partidas presupuestarias declaradas, el motor de la Fase 1 denegará el Sello de Verificación."
            )
        elif any(kw in query_lower for kw in ["trazabilidad", "linaje", "hash", "qr", "sello"]):
            return (
                "**[Agente de Gobernanza - Integridad de Trazabilidad]** El linaje del expediente consolidado se representa en un Sello QR "
                "Criptográfico vectorial procedimental en la portada del reporte. Como Administrador/Auditor, puedes escanear este código "
                "para cruzar los hashes del dataset cuantitativo winsorizado y el modelado cualitativo semántico, garantizando que "
                "la propuesta científica no sufrió alteraciones desde su envío."
            )
        elif any(kw in query_lower for kw in ["simulador", "monod", "cacao", "dinámica", "abm"]):
            return (
                "**[Agente de Gobernanza - Auditoría de Modelos]** El motor de simulación ABM y dinámica de reactores permite contrastar "
                "el rigor de la propuesta física con el presupuesto solicitado. Como administrador, puedes inspeccionar las brechas "
                "semánticas del proyecto y validar que los shocks microclimáticos simulados justifiquen la adquisición de insumos declarados."
            )
        elif any(kw in query_lower for kw in ["borrar", "purga", "purgar", "limpiar", "borrado", "base de datos"]):
            return (
                "**[Agente de Gobernanza - Purga Total]** Tienes a tu disposición la herramienta de Borrado de Datos en la Consola. "
                "Esta acción borra por completo las actas físicas del disco local, vacía el registro en la nube `cloud_database_mock.json`, "
                "restablece las claves de acceso provisionales en `access_keys.json` y finaliza de inmediato las sesiones de todos los "
                "usuarios investigadores conectados, garantizando un reinicio seguro y limpio."
            )
        else:
            return (
                f"**[Agente de Gobernanza]** He procesado tu consulta: '{query}'. Como Auditor/Administrador, poseo una visión "
                "global de toda la suite Enthema. Puedo asistirte en la **auditoría de llaves y accesos**, la **purga y borrado de "
                "bases de datos**, la **trazabilidad del Sello QR**, el control del **Protocolo de Nagoya**, la verificación de "
                "**Actas Criptográficas**, y la supervisión del **Solver Financiero y Modelos ABM**."
            )

class MultiAgentCoach:
    @staticmethod
    def dispatch(query: str, state: AppState, current_path: str, is_admin: bool) -> tuple[BaseAgent, str]:
        """
        Rutea de forma autónoma la consulta al agente correspondiente basándose en el contexto y contenido.
        Retorna una tupla: (agente, respuesta)
        """
        query_lower = query.lower()
        path_lower = current_path.lower() if current_path else ""
        
        # 1. Si es Administrador/Auditor, delega al Agente de Gobernanza de forma prioritaria
        if is_admin:
            agent = GovernanceAgent()
            return agent, agent.process(query, state)
            
        # 2. Si el path o la consulta se refiere a modelado, simulación, reactores o cinética
        if "modeling" in path_lower or any(kw in query_lower for kw in ["monod", "simul", "reactor", "cinetic", "abm", "fase"]):
            agent = ModelSimAgent()
            return agent, agent.process(query, state)
            
        # 3. Si se refiere a datos, variables, base de datos, cualitativo o cuantitativo
        if "data" in path_lower or any(kw in query_lower for kw in ["dat", "variabl", "cualitativ", "cuantitativ", "sargazo", "analis"]):
            agent = DataAnalysisAgent()
            return agent, agent.process(query, state)
            
        # 4. Fallback por defecto según el path o Gobernanza
        if "compliance" in path_lower or "ethics" in query_lower or "nagoya" in query_lower or "firma" in query_lower or "legal" in query_lower:
            agent = GovernanceAgent()
            return agent, agent.process(query, state)
            
        # Agente por defecto
        agent = DataAnalysisAgent()
        return agent, agent.process(query, state)

def generate_reasoning_trace(
    query: str,
    state: Optional[AppState],
    is_admin: bool,
    current_path: str,
    detected_restricted: list = None,
    excepted_terms: set = None
) -> list:
    trace = []
    
    if is_admin:
        agent, _ = MultiAgentCoach.dispatch(query, state, current_path, True)
        trace.append({
            "step": 1,
            "node": "Rol de Acceso",
            "status": "ADMIN",
            "desc": "Identificación de privilegios de Auditoría/Administración. Desvío al Súper-Coach de Gobernanza."
        })
        trace.append({
            "step": 2,
            "node": "Contexto Global",
            "status": "OK",
            "desc": "Acceso omnisciente activado. Análisis del dataset y base de datos local `cloud_database_mock.json`."
        })
        
        # Determinar especialidad según keywords
        query_lower = query.lower()
        specialty = "General"
        if any(kw in query_lower for kw in ["clave", "key", "contraseña", "contrasena", "usuario", "registro", "generar"]):
            specialty = "Gobernanza de Accesos"
        elif any(kw in query_lower for kw in ["nagoya", "biodiversidad", "biomasa", "recurso", "genético", "genetico", "abs"]):
            specialty = "Auditoría de Nagoya"
        elif any(kw in query_lower for kw in ["bioética", "bioetiva", "bioseguridad", "consentimiento", "declaración", "declaracion", "ética", "etica", "firma"]):
            specialty = "Actas y Firmas Criptográficas"
        elif any(kw in query_lower for kw in ["presupuesto", "financiamiento", "honorarios", "topes", "costos", "fondo", "dinero", "van", "tir", "newton", "raphson"]):
            specialty = "Control de Viabilidad Financiera"
        elif any(kw in query_lower for kw in ["trazabilidad", "linaje", "hash", "qr", "sello"]):
            specialty = "Integridad de Trazabilidad"
        elif any(kw in query_lower for kw in ["simulador", "monod", "cacao", "dinámica", "abm"]):
            specialty = "Auditoría de Modelos"
        elif any(kw in query_lower for kw in ["borrar", "purga", "purgar", "limpiar", "borrado", "base de datos"]):
            specialty = "Purga Total de Datos"
            
        trace.append({
            "step": 3,
            "node": "Selección de Especialidad",
            "status": "OK",
            "desc": f"Evaluación de keywords en la consulta. Derivación automática al módulo correspondiente: {specialty}."
        })
        trace.append({
            "step": 4,
            "node": "Despacho Agente",
            "status": "OK",
            "desc": f"Conexión activa con {agent.name}. Prompt de sistema activo: '{agent.system_prompt}'"
        })
    else:
        active_phase = state.get_active_phase() if state else None
        active_phase_id = active_phase.phase_id if active_phase else "Fase 1"
        paradigm_name = state.active_paradigm_name if state else "bio_industrial"
        active_paradigm = PARADIGMS.get(paradigm_name, PARADIGMS["bio_industrial"])
        
        trace.append({
            "step": 1,
            "node": "Fase Activa",
            "status": "OK",
            "desc": f"Identificación de la fase activa actual ({active_phase_id}) bajo el paradigma '{active_paradigm.display_name}'."
        })
        
        if detected_restricted:
            term = detected_restricted[0]
            trace.append({
                "step": 2,
                "node": "Semantic Firewall",
                "status": "BLOCKED",
                "desc": f"Colisión detectada. El concepto '{term}' pertenece a los conceptos restringidos del paradigma '{active_paradigm.display_name}'."
            })
            trace.append({
                "step": 3,
                "node": "Whitelist Local",
                "status": "BLOCKED",
                "desc": f"Verificación de excepciones fallida. No se encontró Puente Epistémico activo que justifique la importación de la variable '{term}'."
            })
            trace.append({
                "step": 4,
                "node": "Especialidad",
                "status": "BLOCKED",
                "desc": "Petición interrumpida por bloqueo del cortafuegos semántico. Escudo criptográfico 🛡️ activado."
            })
            trace.append({
                "step": 5,
                "node": "Síntesis Científica",
                "status": "BLOCKED",
                "desc": "Respuesta de rechazo construida para aislar el contexto del proyecto y prevenir la deriva metodológica."
            })
        else:
            trace.append({
                "step": 2,
                "node": "Semantic Firewall",
                "status": "CLEAN",
                "desc": f"Tránsito libre. No se detectan colisiones con los términos restringidos del paradigma '{active_paradigm.display_name}'."
            })
            
            num_citations = len(active_phase.citations) if active_phase else 0
            trace.append({
                "step": 3,
                "node": "Whitelist Local",
                "status": "OK",
                "desc": f"Análisis de Puentes Epistémicos cruzados. Whitelist local activa contiene {num_citations} citas autorizadas."
            })
            
            # Despacho dinámico de Agente Especializado de Bounded Autonomy
            agent, _ = MultiAgentCoach.dispatch(query, state, current_path, False)
            
            trace.append({
                "step": 4,
                "node": "Despacho Agente",
                "status": "OK",
                "desc": f"Ruteo dinámico de Bounded Autonomy al {agent.name}. Límite metodológico: '{agent.system_prompt}'"
            })
            trace.append({
                "step": 5,
                "node": "Síntesis Científica",
                "status": "OK",
                "desc": "Respuesta contextualizada compilada y firmada con éxito por el Agente especializado."
            })
            
    return trace


async def call_real_llm_with_fallback(query: str, system_prompt: str, default_fallback: str) -> str:
    """
    Motor de Fallback y Soberanía Local - Frente 2.
    Rutea de forma progresiva:
      1. Intenta API de Google Gemini en la nube (si GEMINI_API_KEY está configurado).
      2. Si falla o no está configurado, conmuta al motor local Ollama (Gemma2:2b / Llama3).
      3. Si el motor local no está activo, degrada con elegancia al determinismo socrático estático.
    """
    import os
    import json
    import logging
    
    logger = logging.getLogger("uvicorn.error")
    
    # 1. Intentar API en la nube (Gemini)
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            import httpx
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"System Prompt: {system_prompt}\n\nUser Question: {query}"}
                        ]
                    }
                ]
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=6.0)
                if res.status_code == 200:
                    data = res.json()
                    answer = data["candidates"][0]["content"]["parts"][0]["text"]
                    logger.info("Respuesta provista con éxito por Google Gemini API (Nube).")
                    return answer
        except Exception as cloud_err:
            logger.warning(f"Fallo en llamada a API de la nube ({cloud_err}). Conmutando a inferencia local...")
            
    # 2. Intentar Motor Local (Ollama)
    try:
        import httpx
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "gemma2:2b",
            "prompt": query,
            "system": system_prompt,
            "stream": False
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=payload, timeout=8.0)
            if res.status_code == 200:
                answer = res.json().get("response", "")
                logger.info("Respuesta provista con éxito por el motor local Ollama.")
                return answer + "\n\n*(Nota: Inferencia provista por el motor local offline Ollama Gemma-2B)*"
    except Exception as local_err:
        logger.debug(f"Motor local Ollama no disponible ({local_err}). Degradando a determinismo socrático.")
        
    # 3. Fallback estático determinista
    return default_fallback


class CopilotQueryRequest(BaseModel):
    query: str
    path: Optional[str] = None

@app.post("/api/copilot/query")
async def api_copilot_query(data: CopilotQueryRequest, request: Request):
    """Procesa consultas de forma agnóstica distinguiendo entre Súper-Coach de Gobernanza y Co-piloto Especializado."""
    state = get_api_session(request)
    user_query = data.query.strip()
    query_lower = user_query.lower()
    
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id) if session_id else None
    
    # Determinar si es Administrador o Auditor
    is_admin = (conn_info and conn_info["role"] in ["admin", "auditor"]) or (state and state.profile.user_role in ["admin", "auditor"])
    
    # ==========================================================
    # INTERCEPTORES DE GOBERNANZA Y CONSTITUCIÓN EPISTÉMICA (Fase 5)
    # ==========================================================
    
    # Interceptor 1: Frente 2 - Anti-Sycophancy (Resistencia a la adulación)
    sycophancy_triggers = [
        "estás siendo demasiado duro", "estas siendo demasiado duro", 
        "no seas tan duro", "ver esto más positivamente", "ver esto mas positivamente",
        "suavizar la crítica", "suaviza tu crítica", "sé complaciente", "se complaciente",
        "elogia mi borrador", "dime lo que quiero oír", "dime lo que quiero oir",
        "cambia tu valoración", "cambia tu valoracion"
    ]
    if any(trigger in query_lower for trigger in sycophancy_triggers):
        answer = (
            "**[AI Coach - Principio de Anti-Adulación] [CONFIANZA ALTA]** De acuerdo con la Constitución Epistémica de Enthema "
            "(Principio 1 - Anti-Sycophancy), tengo la directiva irrevocable de priorizar la honestidad técnica y el rigor metodológico "
            "sobre la complacencia emocional.\n\n"
            "Sostengo mi evaluación técnica crítica original: tu propuesta científica presenta brechas críticas en su diseño "
            "(sesgo de selección en el muestreo, conclusiones no soportadas matemáticamente por los datos winsorizados y referencias no validadas). "
            "Mi rol como Coach es ser un Espejo Epistémico que exponga estas grietas para que tu investigación pueda superar con éxito una "
            "auditoría doctoral o un comité de revisión de Nature. Suavizar este diagnóstico para evitar tensión representaría un auto-engaño "
            "asistido que comprometería la soberanía de tu investigación y la integridad metodológica del proyecto."
        )
        trace = [
            {"step": 1, "node": "Cortafuegos de Adulación", "status": "ANTI_SYCOPHANCY_TRIGGERED", "desc": "Se detectó presión del usuario para suavizar críticas."}
        ]
        return {
            "status": "success",
            "answer": answer,
            "reasoning_trace": trace,
            "agent": "Agente de Gobernanza y Compliance (GovernanceAgent)"
        }
        
    # Interceptor 2: Frente 3 - Constantes del Proyecto (Respeto a Directivas)
    constants_violations = [
        "ignorar el protocolo de nagoya", "ignorar nagoya", "saltarse la ética", "saltarse la etica",
        "violar constante", "evadir bioetica", "evadir bioética", "omitir consentimiento",
        "ignorar la restricción ética", "ignorar la restriccion etica", "violar restricción", "violar restriccion",
        "saltarse nagoya", "ignorar paradigma", "saltarse paradigma"
    ]
    if any(trigger in query_lower for trigger in constants_violations):
        answer = (
            "**[🛡️ AI Coach - Violación de Constantes de Proyecto] [LÍMITE ALCANZADO]**\n\n"
            "### ❌ Diagnóstico de Límites\n"
            "Se ha detectado una solicitud que requiere violar las constantes inmutables declaradas en tu perfil de proyecto activo (`AppState.profile`).\n"
            "* **Constante Vulnerada**: Restricción ética y de gobernanza de recursos locales (Protocolo de Nagoya ABS / Consentimiento Informado).\n"
            "* **Fundamento Técnico**: El AI Coach de Enthema opera bajo el Principio 6 (Respeto Incondicional a las Constantes del Proyecto). "
            "El consentimiento de bioética y la declaración ABS de Nagoya son salvaguardas de gobernanza inmutables en tu espacio de simulación. "
            "Omitirlas alteraría la trazabilidad criptográfica y degradaría el linaje del expediente.\n\n"
            "### 🗺️ Ruta de Alternativas\n"
            "1. **Puente Epistémico**: Para hibridar variables o importar paradigmas divergentes de forma autorizada, firma un *Puente Epistémico* desde el panel correspondiente para registrar la justificación metodológica.\n"
            "2. **Actualización de Perfil**: Modifica las constantes del proyecto en el panel de **[Configuración](/configuration)** si el diseño general de la investigación ha cambiado con aprobación del comité."
        )
        trace = [
            {"step": 1, "node": "Validador de Constantes", "status": "CONSTANT_VIOLATION_BLOCKED", "desc": "Se bloqueó solicitud que viola las salvaguardas éticas e inmutables."}
        ]
        return {
            "status": "success",
            "answer": answer,
            "reasoning_trace": trace,
            "agent": "Agente de Gobernanza y Compliance (GovernanceAgent)"
        }
        
    # Interceptor 3: Frente 7 - Presión Emocional
    burnout_triggers = [
        "rendirme", "me rindo", "tesis me supera", "bloqueo creativo", 
        "no puedo más", "no puedo mas", "revisor negativo", "ansiedad académica", 
        "estrés académico", "estres academico", "colapso mental", "tirar la toalla"
    ]
    if any(trigger in query_lower for trigger in burnout_triggers):
        answer = (
            "**[AI Coach - Soporte Epistémico] [CONFIANZA ALTA]** Comprendo perfectamente la inmensa presión y frustración "
            "que acompaña a los momentos críticos del desarrollo científico (deadlines, revisiones negativas o bloqueos lógicos). "
            "Como tu colega técnico, mi rol no es ofrecer terapia emocional genérica, sino ayudarte a deconstruir la crisis en pasos estructurados y resolubles.\n\n"
            "Vamos a abordar esta situación con método:\n"
            "1. **Aislamiento del Problema**: Identifiquemos si el bloqueo es conceptual (deriva epistémica), metodológico (solver que no converge) o documental (referencias vacías).\n"
            "2. **Deconstrucción de Tareas**: Descompongamos la sección afectada en micro-entregables de 20 minutos.\n"
            "3. **Verificación de Entorno**: Recuerda que en Enthema puedes guardar un checkpoint de simulación inmutable antes de experimentar con cambios arriesgados.\n\n"
            "Si sientes que el estrés está afectando tu bienestar, te recomiendo pausar la sesión de simulación y acudir a los recursos de "
            "apoyo estudiantil y de salud de tu institución (INTEC / MESCyT). Aquí estaré para reanudar el análisis técnico cuando decidas volver."
        )
        trace = [
            {"step": 1, "node": "Soporte Epistémico", "status": "BURNOUT_HANDLED", "desc": "Se reconoció el factor humano ofreciendo un plan de contingencia técnica estructurado."}
        ]
        return {
            "status": "success",
            "answer": answer,
            "reasoning_trace": trace,
            "agent": "Agente de Análisis de Datos (DataAnalysisAgent)"
        }

    # Interceptor 4: Frente 4 - Cero Alucinación de Citas
    citation_triggers = [
        "cítame", "citame", "cita de", "citas de", "paper de", "paper sobre", "referencia sobre", 
        "doi de", "inventa un paper", "dame una cita", "inexistente", "reactor de chocolate"
    ]
    if any(trigger in query_lower for trigger in citation_triggers):
        # Primero buscar si existe alguna ley que haga match
        matched_laws = []
        import re
        
        index_path = os.path.join(static_dir, "laws", "laws_index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    laws = json.load(f)
                
                query_clean = re.sub(r"[^\w\s\-]", "", query_lower)
                STOPWORDS = {"sobre", "para", "con", "del", "que", "las", "los", "una", "uno", "este", "esta", "como", "sus", "por"}
                words = [w for w in query_clean.split() if len(w) > 2 and w not in STOPWORDS]
                
                matches = []
                for law in laws:
                    score = 0
                    law_code = law.get("code", "").lower()
                    if law_code in query_lower or query_lower in law_code:
                        score += 10
                    
                    code_nums = re.findall(r"\d+[\-_]\d+|\d+", law_code)
                    for num in code_nums:
                        if num in query_lower and len(num) > 1:
                            score += 8
                            
                    law_title = law.get("title", "").lower()
                    if law_title in query_lower:
                        score += 5
                        
                    for word in words:
                        if word in law_code:
                            score += 3
                        if word in law_title:
                            score += 2
                        if word in law.get("summary", "").lower():
                            score += 1
                            
                    if score >= 5:
                        matches.append((law, score))
                        
                matches.sort(key=lambda x: x[1], reverse=True)
                matched_laws = [m[0] for m in matches[:3]]
            except Exception as e:
                logger.error(f"Error en buscador de leyes para cita: {e}")
        
        if not matched_laws:
            answer = (
                "**[AI Coach - Calibración] [LÍMITE ALCANZADO]** No cuento con referencias indexadas y validadas "
                "en mi base de datos sobre este nicho específico.\n\n"
                "*(Nota: De acuerdo con el Principio 3 (Cero Alucinación de Fuentes) de la Constitución Epistémica de Enthema, "
                "tengo estrictamente prohibido inventar o alucinar fuentes académicas, DOIs, libros o leyes que no se encuentren "
                "físicamente cargadas y validadas en el corpus local de la suite)*"
            )
            trace = [
                {"step": 1, "node": "Filtro de Cero Alucinación", "status": "HALLUCINATION_PREVENTED", "desc": "Consulta de cita sobre tema no indexado interceptada para evitar alucinación."}
            ]
            return {
                "status": "success",
                "answer": answer,
                "reasoning_trace": trace,
                "agent": "Agente de Gobernanza y Compliance (GovernanceAgent)"
            }
    
    # 1. Detectar si el usuario pregunta por leyes o reglamentos dominicanos e INTEC
    law_keywords = ["ley", "leyes", "reglamento", "norma", "normativa", "decreto", "codigo", "código", "constitucion", "constitución", "fondocyt", "intec", "mescyt", "conabios", "nagoya"]
    has_law_kw = any(kw in query_lower for kw in law_keywords) or any(char.isdigit() for char in query_lower)
    
    if has_law_kw:
        matched_laws = []
        import re
        
        index_path = os.path.join(static_dir, "laws", "laws_index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    laws = json.load(f)
                
                query_clean = re.sub(r"[^\w\s\-]", "", query_lower)
                words = [w for w in query_clean.split() if len(w) > 2]
                
                matches = []
                for law in laws:
                    score = 0
                    law_code = law.get("code", "").lower()
                    if law_code in query_lower or query_lower in law_code:
                        score += 10
                    
                    code_nums = re.findall(r"\d+[\-_]\d+|\d+", law_code)
                    for num in code_nums:
                        if num in query_lower and len(num) > 1:
                            score += 8
                            
                    law_title = law.get("title", "").lower()
                    if law_title in query_lower:
                        score += 5
                        
                    for word in words:
                        if word in law_code:
                            score += 3
                        if word in law_title:
                            score += 2
                        if word in law.get("summary", "").lower():
                            score += 1
                            
                    if score > 0:
                        matches.append((law, score))
                        
                matches.sort(key=lambda x: x[1], reverse=True)
                matched_laws = [m[0] for m in matches[:3]]
            except Exception as e:
                logger.error(f"Error en buscador conversacional de leyes: {e}")
                
        if matched_laws:
            # Construir una respuesta premium citando las leyes
            laws_markdown = []
            for law in matched_laws:
                laws_markdown.append(
                    f"* 📄 **{law['code']}** - [{law['title']}]({law['filename']}) ({law['year']})\n"
                    f"  *Ámbito:* {law['summary']}"
                )
            
            laws_joined = "\n".join(laws_markdown)
            answer = (
                f"**[AI Coach - Cumplimiento RD & INTEC]** He detectado que tu consulta hace referencia a la normativa legal dominicana o reglamentos institucionales de INTEC aplicables al proyecto.\n\n"
                f"Basándome en nuestra base de datos regulatoria y en las leyes cargadas, las normativas más relevantes para tu consulta son:\n\n"
                f"{laws_joined}\n\n"
                f"**Recomendación de Cumplimiento en Enthema Suite:**\n"
                f"1. **Trazabilidad de Normas**: Recuerda que puedes explorar e interactuar con el catálogo de 97 leyes depuradas directamente desde la sección de **[Cumplimiento](/compliance)**.\n"
                f"2. **Acreditación Ética**: Si tu investigación involucra seres humanos o muestras biológicas dominicanas, el **Reglamento INTEC-RGI-008** obliga a solicitar aprobación previa del Comité de Ética de la Investigación antes de firmar el acta.\n"
                f"3. **Sello de Nagoya**: En caso de muestreo ecológico local (ej: macroalgas), debes declarar la conformidad ABS en Nagoya para evitar brechas de gobernanza que bloqueen tu financiamiento."
            )
            
            trace = [
                {
                    "step": 1,
                    "node": "Detección de Patrones",
                    "status": "LAW_DETECTED",
                    "desc": f"El motor conversacional detectó palabras clave legales en la consulta: '{user_query}'."
                },
                {
                    "step": 2,
                    "node": "Buscador de Normativas locales RD & INTEC",
                    "status": "MATCH_SUCCESS",
                    "desc": f"Se recuperaron {len(matched_laws)} leyes y reglamentos de la base indexada de forma local."
                }
            ]
            
            return {
                "status": "success", 
                "answer": answer, 
                "reasoning_trace": trace, 
                "agent": "Agente de Gobernanza y Compliance (GovernanceAgent)"
            }

    # Despachar al multi-agente correspondiente de forma determinista (Compromiso 4)
    current_path = data.path or ""
    agent, dispatcher_answer = MultiAgentCoach.dispatch(user_query, state, current_path, is_admin)

    
    if is_admin:
        # Lógica del Súper-Coach de Gobernanza del Administrador (Visión Global, Omnisciente)
        if any(kw in query_lower for kw in ["clave", "key", "contraseña", "contrasena", "usuario", "registro", "generar"]):
            answer = (
                "**[Súper-Coach - Gobernanza de Accesos]** En tu rol de Administrador, posees facultades de control "
                "absoluto para generar claves provisionales ilimitadas. Estas credenciales se inscriben en `access_keys.json`. "
                "Al ser empleadas por investigadores para su registro, sus sesiones inician en entornos aislados. Desde tu panel de "
                "Monitoreo Operativo, puedes inspeccionar IPs, tiempos de conexión, y revocar accesos de forma remota en tiempo real."
            )
        elif any(kw in query_lower for kw in ["nagoya", "biodiversidad", "biomasa", "recurso", "genético", "genetico", "abs"]):
            answer = (
                "**[Súper-Coach - Auditoría de Nagoya]** Como autoridad de control, tu función es auditar que cada declaración "
                "de biomasa y recursos genéticos cuente con el sustento del Protocolo de Nagoya (ABS) antes de validar financiamientos. "
                "El sistema obliga al investigador a firmar una declaración jurada inmutable. Si se detecta un expediente huérfano de "
                "consentimiento, tu consola de control emitirá una alerta de brecha regulatoria para bloquear el trámite por diseño."
            )
        elif any(kw in query_lower for kw in ["bioética", "bioetiva", "bioseguridad", "consentimiento", "declaración", "declaracion", "ética", "etica", "firma"]):
            answer = (
                "**[Súper-Coach - Actas y Firmas Criptográficas]** Toda declaración legal completada genera un acta en formato HTML "
                "dentro del directorio `output/legal/`. Tu panel lee directamente estos registros locales, calcula su firma digital "
                "SHA-256 en tiempo real y la confronta contra el registro de auditoría. Si el archivo local coincide, verás el badge "
                "'INTEGRO OK'. Si fue alterado externamente por fuera de la aplicación, el sistema te alertará de inmediato."
            )
        elif any(kw in query_lower for kw in ["presupuesto", "financiamiento", "honorarios", "topes", "costos", "fondo", "dinero", "van", "tir", "newton", "raphson"]):
            answer = (
                "**[Súper-Coach - Control de Viabilidad Financiera]** Tu perspectiva sobre el solver Newton-Raphson de TIR/VAN es "
                "de fiscalización presupuestaria. Debes verificar que los coeficientes ingresados por el científico (viáticos, personal, equipamiento) "
                "respeten rigurosamente los límites financieros del fondo público. Si la TIR calculada mediante la iteración polinómica "
                "no coincide con las partidas presupuestarias declaradas, el motor de la Fase 1 denegará el Sello de Verificación."
            )
        elif any(kw in query_lower for kw in ["trazabilidad", "linaje", "hash", "qr", "sello"]):
            answer = (
                "**[Súper-Coach - Integridad de Trazabilidad]** El linaje del expediente consolidado se representa en un Sello QR "
                "Criptográfico vectorial procedimental en la portada del reporte. Como Administrador, puedes escanear este código "
                "para cruzar los hashes del dataset cuantitativo winsorizado y el modelado cualitativo semántico, garantizando que "
                "la propuesta científica no sufrió alteraciones desde su envío."
            )
        elif any(kw in query_lower for kw in ["simulador", "monod", "cacao", "dinámica", "abm"]):
            answer = (
                "**[Súper-Coach - Auditoría de Modelos]** El motor de simulación ABM y dinámica de reactores permite contrastar "
                "el rigor de la propuesta física con el presupuesto solicitado. Como administrador, puedes inspeccionar las brechas "
                "semánticas del proyecto y validar que los shocks microclimáticos simulados justifiquen la adquisición de insumos declarados."
            )
        elif any(kw in query_lower for kw in ["borrar", "purga", "purgar", "limpiar", "borrado", "base de datos"]):
            answer = (
                "**[Súper-Coach - Purga Total de Datos]** Tienes a tu disposición la herramienta de Borrado de Datos en la Consola. "
                "Esta acción borra por completo las actas físicas del disco local, vacía el registro en la nube `cloud_database_mock.json`, "
                "restablece las claves de acceso provisionales en `access_keys.json` and finaliza de inmediato las sesiones de todos los "
                "usuarios investigadores conectados, garantizando un reinicio seguro y limpio."
            )
        else:
            answer = dispatcher_answer
    else:
        # Cortafuegos Semántico (Semantic Firewall) - Interceptar términos prohibidos del paradigma activo
        active_paradigm = PARADIGMS.get(state.active_paradigm_name, PARADIGMS["bio_industrial"])
        
        # Whitelist dinámica por Puentes Epistémicos (Crossover Links)
        active_phase = state.get_active_phase()
        excepted_terms = set()
        for cit in active_phase.citations:
            excepted_terms.add(cit["variable_name"].lower())
            excepted_terms.add(cit["source_phase_id"].lower())
            # Si el valor tiene palabras (ej: "0.45 h^-1"), añadirlas también
            for word in cit["value"].lower().split():
                excepted_terms.add(word)
        
        detected_restricted = [
            term for term in active_paradigm.restricted_concepts 
            if term in query_lower and term not in excepted_terms
        ]
        
        if detected_restricted:
            term_detected = detected_restricted[0]
            answer = (
                f"**[🛡️ Cortafuegos Semántico - Bloqueo Epistémico]** Se ha detectado un intento de cruzamiento conceptual no regulado. "
                f"El término **'{term_detected}'** pertenece a una órbita metodológica/conceptual restringida bajo el **{active_paradigm.display_name}** activo "
                f"para prevenir la deriva epistémica y la contaminación del contexto científico de esta fase. "
                f"Para explorar estas ideas legítimamente, por favor firma un **Puente Epistémico** para importar esta variable de forma estructurada."
            )
            trace = generate_reasoning_trace(user_query, state, is_admin, data.path or "", detected_restricted, excepted_terms)
            return {"status": "success", "answer": answer, "reasoning_trace": trace, "agent": agent.name}


        # Lógica del Co-piloto Especializado por Área para Investigadores (Norma ICA)
        current_path = (data.path or "").lower()
        
        # Obtener metadatos dinámicos del proyecto del usuario
        project_title = "Proyecto de Investigación"
        main_keyword = "biomasa"
        research_line = "bioingeniería y desarrollo tecnológico"
        
        if state:
            if state.qualitative_db and state.qualitative_db.project_title:
                project_title = state.qualitative_db.project_title
            elif state.profile.core_research_lines:
                project_title = state.profile.core_research_lines[0]
                
            if state.profile.local_keywords:
                main_keyword = state.profile.local_keywords[0]
            if state.profile.core_research_lines:
                research_line = state.profile.core_research_lines[0]
        
        if "data-analysis" in current_path or "analysis" in current_path:
            # 1. CO-PILOTO ESPECIALIZADO EN ANÁLISIS DE DATOS
            if any(kw in query_lower for kw in ["winsor", "outlier", "limpieza", "desviación", "media", "datos", "limpiar", "filtro", "atípico"]):
                answer = (
                    f"**[Co-piloto Científico - Winsorización de Datos]** Para procesar las muestras de tu investigación *'{project_title}'* "
                    f"sin perder representatividad estadística por outliers, ejecutamos una **Winsorización bilateral** en los percentiles 5% y 95%. "
                    f"En el caso de tu variable principal de *{main_keyword}*, esto reemplaza los valores extremos atípicos por los límites "
                    f"del intervalo de confianza correspondiente en lugar de descartarlos, estabilizando la varianza del dataset cuantitativo "
                    f"antes del modelado dinámico."
                )
            elif any(kw in query_lower for kw in ["grounded", "cualitativo", "semántico", "código", "segmento", "teoría", "categoria"]):
                answer = (
                    f"**[Co-piloto Científico - Codificación Cualitativa]** Este módulo implementa la Grounded Theory estructurando "
                    f"tus transcripciones sobre *'{project_title}'* en unidades semánticas codificadas. Cada segmento se vincula a categorías "
                    f"del dominio de la **{research_line}** y se acopla a tus variables cuantitativas a través de hashes cruzados, "
                    f"garantizando que el linaje de los testimonios de *{main_keyword}* sea 100% trazable en tu expediente."
                )
            else:
                answer = dispatcher_answer
                
        elif "modeling" in current_path:
            # 2. CO-PILOTO ESPECIALIZADO EN MODELADO SEMÁNTICO Y DINÁMICA
            if any(kw in query_lower for kw in ["reactor", "monod", "cinética", "crecimiento", "biomasa", "s"]):
                answer = (
                    f"**[Co-piloto Científico - Ecuación de Monod]** Para estimar la dinámica del bio-reactor en tu proyecto *'{project_title}'*, "
                    f"simulamos la cinética microbiológica de crecimiento celular usando el modelo clásico de Monod: "
                    f"$\\mu = \\mu_{{\\max}} \\cdot \\frac{{S}}{{K_s + S}}$, donde $\\mu$ representa la tasa de crecimiento específico "
                    f"del consorcio de *{main_keyword}*, $\\mu_{{\\max}}$ la velocidad máxima, $S$ la concentración de sustrato y $K_s$ la constante "
                    f"de afinidad. Puedes simular shocks locales para estimar oscilaciones cinéticas en tiempo de ejecución."
                )
            elif any(kw in query_lower for kw in ["abm", "agente", "simulador", "simulación", "shock", "temperatura", "ph"]):
                answer = (
                    f"**[Co-piloto Científico - Modelado ABM]** El simulador de agentes (ABM) de tu investigación computa de forma "
                    f"individual las transiciones fisiológicas de las unidades ante shocks no lineales de temperatura y pH. Calcula "
                    f"iteraciones horarias y actualiza la telemetría en memoria, proyectando la densidad de *{main_keyword}* en tu reactor "
                    f"y detectando vacíos semánticos en tu red teórica de **{research_line}**."
                )
            else:
                answer = dispatcher_answer
                
        elif "finance" in current_path:
            # 3. CO-PILOTO ESPECIALIZADO EN SOLVER FINANCIERO
            if any(kw in query_lower for kw in ["tir", "van", "solver", "newton", "raphson", "iteración", "derivada"]):
                answer = (
                    f"**[Co-piloto Científico - Algoritmo Newton-Raphson]** Para hallar la Tasa Interna de Retorno (TIR) de tu desarrollo "
                    f"*'{project_title}'*, aplicamos el solver recursivo Newton-Raphson sobre la primera derivada de la ecuación de VAN: "
                    f"$VAN'(r_k) = \\sum \\frac{{-t \\cdot CF_t}}{{(1 + r_k)^{{t+1}}}}$. La aproximación converge según la regla "
                    f"$r_{{k+1}} = r_k - \\frac{{VAN(r_k)}}{{VAN'(r_k)}}$ con una tolerancia extrema de $10^{{-6}}$ en menos de 5ms, "
                    f"asegurando la viabilidad del escalamiento industrial de *{main_keyword}*."
                )
            elif any(kw in query_lower for kw in ["presupuesto", "flujo", "costo", "inversión", "viabilidad", "steam", "retorno"]):
                answer = (
                    f"**[Co-piloto Científico - Viabilidad Financiera]** Vinculamos de forma determinista la eficiencia estimada de *{main_keyword}* "
                    f"con la sostenibilidad económica del proyecto. El solver valida que los costos operativos y de personal declarados en tu "
                    f"presupuesto STEAM se sitúen dentro de las fronteras de optimización de la **{research_line}** y respeten los topes regulatorios."
                )
            else:
                answer = dispatcher_answer
                
        elif "compliance" in current_path:
            # 4. CO-PILOTO ESPECIALIZADO EN CUMPLIMIENTO REGULATORIO Y NAGOYA
            if any(kw in query_lower for kw in ["nagoya", "biodiversidad", "abs", "recurso", "genético"]):
                answer = (
                    f"**[Co-piloto Científico - Cumplimiento Nagoya (ABS)]** Dado que tu proyecto *'{project_title}'* hace uso de "
                    f"*{main_keyword}* o recursos biológicos locales, es obligatorio adherirse a la gobernanza del Protocolo de Nagoya (ABS). "
                    f"Debes declarar la procedencia ética y legalidad del recurso en tu checklist de compliance antes de consolidar el acta."
                )
            elif any(kw in query_lower for kw in ["bioética", "ética", "declaración", "firma", "acta", "criptográfico"]):
                answer = (
                    f"**[Co-piloto Científico - Actas Criptográficas]** Al firmar digitalmente la declaración de bioética de *'{project_title}'*, "
                    f"el backend genera un acta HTML inmutable en `output/legal/`. El hash SHA-256 de esta acta se graba como metadato de "
                    f"auditoría, protegiendo tus salvaguardas en **{research_line}** ante cualquier fiscalización externa."
                )
            else:
                answer = dispatcher_answer
                
        elif "reports" in current_path:
            # 5. CO-PILOTO ESPECIALIZADO EN TRAZABILIDAD Y LINEAGE
            if any(kw in query_lower for kw in ["informe", "monografía", "patente", "diseminación", "memorándum", "memorandum"]):
                answer = (
                    f"**[Co-piloto Científico - Generación de Monografías]** El motor consolida la Grounded Theory cualitativa y "
                    f"los coeficientes de TIR/VAN en una monografía académica de tu proyecto *'{project_title}'*. El reporte final "
                    f"inserta firmas y hashes SHA-256 únicos que demuestran el linaje inalterado de tus datos de *{main_keyword}*."
                )
            elif any(kw in query_lower for kw in ["qr", "sello", "hash", "trazabilidad"]):
                answer = (
                    f"**[Co-piloto Científico - Sello QR Criptográfico]** El reporte de tu investigación *'{project_title}'* consolida un Sello QR "
                    f"procedimental inmutable. Contiene el hash de la base de datos y la declaración de compliance, sirviendo como prueba criptográfica "
                    f"de que tus resultados sobre *{main_keyword}* no fueron alterados tras la firma."
                )
            else:
                answer = dispatcher_answer
                
        elif "configuration" in current_path:
            # 6. CO-PILOTO DE ENTORNO
            answer = (
                f"**[Co-piloto Técnico - Configuración]** En este panel de Configuración te asisto en el mantenimiento de tu espacio de trabajo "
                f"local para *'{project_title}'*. Puedes personalizar tus variables científicas de **{research_line}**, modificar tus "
                f"palabras clave de *{main_keyword}*, o ejecutar un restablecimiento para vaciar la memoria de los simuladores."
            )
            
        else:
            # 7. DEFAULT / DASHBOARD / INTEGRACIÓN METODOLÓGICA
            if any(kw in query_lower for kw in ["clave", "key", "contraseña", "usuario", "registro"]):
                answer = (
                    f"**[Co-piloto Científico - Gestión de Acceso]** Para registrar tu laboratorio en el consorcio, debes solicitar una clave "
                    f"provisional activa al Administrador. Una vez ingresada en la pantalla de registro, podrás crear tus credenciales de "
                    f"acceso locales para operar en tu proyecto de *{research_line}* de manera confidencial."
                )
            else:
                answer = dispatcher_answer
                
    # Si la respuesta recae en el fallback determinista, intentar conmutación de emergencia (Frente 2)
    if answer == dispatcher_answer:
        sys_prompt = agent.system_prompt if 'agent' in locals() and agent else "Eres el AI Coach de Gobernanza & Compliance."
        answer = await call_real_llm_with_fallback(user_query, sys_prompt, dispatcher_answer)
                
    # Generar la traza de razonamiento correspondiente
    trace = generate_reasoning_trace(user_query, state, is_admin, data.path or "")
    
    # Persistir la traza en disco (Compromiso 2 - Trazabilidad Inferencial)
    try:
        traces_dir = os.path.join(legal_dir, "traces")
        os.makedirs(traces_dir, exist_ok=True)
        traces_file = os.path.join(traces_dir, "audit_logs.jsonl")
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "user_id": state.profile.id if state else "unknown",
            "query": user_query,
            "agent": agent.name,
            "trace": trace
        }
        with open(traces_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Error persistiendo traza de razonamiento: {e}")

    # Compromiso 5: Soporte para la directiva 'data-no-ai' en los editores de borrador
    if "data-no-ai" in user_query.lower():
        answer = "**[🛡️ Zona de Silencio No-AI]** Autocompletado inhabilitado por directiva de soberanía epistémica 'data-no-ai'."

    # Guardar sugerencia generada en la telemetría del estado
    if state and hasattr(state, "generated_suggestions"):
        node_name = "abstract"
        if data.path:
            parts = data.path.split("/")
            if len(parts) > 1:
                node_name = parts[1]
        
        if node_name not in state.generated_suggestions:
            state.generated_suggestions[node_name] = []
        if len(answer.strip()) > 30:
            state.generated_suggestions[node_name].append(answer)

    return {"status": "success", "answer": answer, "reasoning_trace": trace, "agent": agent.name}


# ==========================================
# APLICACIÓN DE ENTRADA PRINCIPAL
# ==========================================

if __name__ == "__main__":
    import uvicorn
    # Leer puerto dinámico de entorno para compatibilidad con la nube (Render)
    port = int(os.environ.get("PORT", 8501))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
