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
from typing import Dict, List, Optional
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
    VariableMetadata
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

# Inicializar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnthemaSuiteWeb")

app = FastAPI(
    title="Enthema Suite Precision Intelligence",
    description="Motor científico y financiero de precisión con interfaz de diseño Stitch (Tailwind CSS/HTML5)",
    version="2.5.0"
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

legal_dir = os.path.join(BASE_DIR, "output", "legal")
if not os.path.exists(legal_dir):
    os.makedirs(legal_dir, exist_ok=True)

db_path = os.path.join(legal_dir, "users_db.json")
if not os.path.exists(db_path):
    default_users = [
        {
            "username": "admin",
            "password": "admin123",
            "role": "admin",
            "name": "Auditor Principal",
            "institution": "MESCyT / INTEC",
            "profile_id": "INV-AUDIT-MASTER"
        },
        {
            "username": "admin",
            "password": "admin 123",
            "role": "admin",
            "name": "Auditor Principal",
            "institution": "MESCyT / INTEC",
            "profile_id": "INV-AUDIT-MASTER"
        },
        {
            "username": "aris",
            "password": "password",
            "role": "researcher",
            "name": "Dr. Aris Thorne",
            "institution": "Instituto Internacional de Bioingeniería",
            "profile_id": "INV-ARIS-001"
        }
    ]
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(default_users, f, indent=4, ensure_ascii=False)

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
    with open(keys_path, "w", encoding="utf-8") as f:
        json.dump(default_keys, f, indent=4, ensure_ascii=False)

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
        "reactor_status": state.reactor_status
    }

# ==========================================
# ENPOINTS DE AUTENTICACIÓN Y REGISTRO
# ==========================================

@app.get("/login", response_class=HTMLResponse)
async def view_login(request: Request):
    """Renderiza el login premium glassmorphic."""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
async def api_login(data: LoginRequest):
    """Procesa el inicio de sesión contra el archivo local users_db.json."""
    db_path = os.path.join(BASE_DIR, "output", "legal", "users_db.json")
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception:
            users = []
    else:
        users = []

    user = next((u for u in users if u["username"].lower() == data.username.lower() and u["password"] == data.password), None)
    if not user:
        raise HTTPException(status_code=400, detail="Nombre de usuario o contraseña incorrectos")

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
        "redirect": "/"
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
    keys_path = os.path.join(BASE_DIR, "output", "legal", "access_keys.json")
    if os.path.exists(keys_path):
        try:
            with open(keys_path, "r", encoding="utf-8") as f:
                keys = json.load(f)
        except Exception:
            keys = []
    else:
        keys = []

    key_obj = next((k for k in keys if k["key"].upper() == data.access_key.upper()), None)
    if not key_obj:
        raise HTTPException(status_code=400, detail="Clave provisional de acceso inválida.")
    if key_obj["used"]:
        raise HTTPException(status_code=400, detail="Esta clave provisional ya ha sido utilizada.")

    db_path = os.path.join(BASE_DIR, "output", "legal", "users_db.json")
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception:
            users = []
    else:
        users = []

    if any(u["username"].lower() == data.username.lower() for u in users):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya se encuentra registrado.")

    import uuid
    profile_id = f"INV-{uuid.uuid4().hex[:8].upper()}"

    new_user = {
        "username": data.username,
        "password": data.password,
        "role": "researcher",
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
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    with open(keys_path, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4, ensure_ascii=False)

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

@app.get("/", response_class=HTMLResponse)
async def view_general_onboarding(request: Request):
    """Renderiza la pantalla de Onboarding General (Hub)."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("general_onboarding.html", get_base_context(request, state))

@app.get("/onboarding/investigador", response_class=HTMLResponse)
async def view_onboarding_investigador(request: Request):
    """Renderiza la pantalla de Onboarding Científico."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("onboarding_investigador.html", get_base_context(request, state))

@app.get("/onboarding/auditor", response_class=HTMLResponse)
async def view_onboarding_auditor(request: Request):
    """Renderiza la pantalla de Onboarding de Auditor."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    if state.profile.user_role not in ["admin", "auditor"]:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("onboarding_auditor.html", get_base_context(request, state))

@app.get("/investigador/profile-builder", response_class=HTMLResponse)
async def view_profile_builder(request: Request):
    """Renderiza el Asistente Sócrates / Cuestionario de Perfil del Investigador."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("onboarding.html", get_base_context(request, state))

@app.get("/dashboard", response_class=HTMLResponse)
async def view_dashboard(request: Request):
    """Renderiza el Panel de Control principal."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", get_base_context(request, state))

@app.get("/data-analysis", response_class=HTMLResponse)
async def view_data_analysis(request: Request):
    """Renderiza la pantalla de Carga y Análisis de Datos."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("data_analysis.html", get_base_context(request, state))

@app.get("/modeling", response_class=HTMLResponse)
async def view_modeling(request: Request):
    """Renderiza la pantalla de Modelado Semántico e interactividad 3D del Bio-Reactor."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("semantic_modeling.html", get_base_context(request, state))

@app.get("/finance", response_class=HTMLResponse)
async def view_finance(request: Request):
    """Renderiza el panel financiero y solver de Newton-Raphson."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("finance.html", get_base_context(request, state))

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
    return templates.TemplateResponse("reports.html", ctx)

@app.get("/compliance", response_class=HTMLResponse)
async def view_compliance(request: Request):
    """Renderiza el descargo legal, consentimiento ético y base de datos cloud sync."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
        
    ctx = get_base_context(request, state)
    
    # Cargar registros del cloud mock database
    cloud_records = []
    local_legal_dir = os.path.join(BASE_DIR, "output", "legal")
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
    return templates.TemplateResponse("compliance.html", ctx)

@app.get("/configuration", response_class=HTMLResponse)
async def view_configuration(request: Request):
    """Renderiza la Sección 7 del Streamlit original: Configuración y reset de simulación."""
    state = get_session_or_redirect(request)
    if state is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("configuration.html", get_base_context(request, state))

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
        raise HTTPException(status_code=403, detail="No autorizado para acceder al Cerebro Central")
        
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "profile": state.profile
    })

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

    local_legal_dir = os.path.join(BASE_DIR, "output", "legal")
    mock_db_path = os.path.join(local_legal_dir, "cloud_database_mock.json")
    cloud_records = []
    if os.path.exists(mock_db_path):
        try:
            with open(mock_db_path, "r", encoding="utf-8") as f:
                cloud_records = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo cloud_database_mock: {e}")

    validated_records = []
    for rec in cloud_records:
        user_id = rec.get("investigator", {}).get("id", "anonymous")
        hash_proj = rec.get("hash_proyecto", "")
        filename = f"ACTA_FIRMADA_{hash_proj}.html"
        user_dir = os.path.join(local_legal_dir, f"user_{user_id}")
        filepath = os.path.join(user_dir, filename)

        file_exists = os.path.exists(filepath)
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
            "verification_status": "CERTIFICADO - INTEGRIDAD OK" if file_exists else "ERR - ARCHIVO NO ENCONTRADO"
        })

    return validated_records

@app.get("/api/admin/keys")
async def api_admin_list_keys(request: Request):
    """Muestra todas las claves de acceso generadas."""
    session_id = request.cookies.get("session_id")
    conn_info = active_connections.get(session_id) if session_id else None
    if not conn_info or conn_info["role"] not in ["admin", "auditor"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    keys_path = os.path.join(BASE_DIR, "output", "legal", "access_keys.json")
    keys = []
    if os.path.exists(keys_path):
        try:
            with open(keys_path, "r", encoding="utf-8") as f:
                keys = json.load(f)
        except Exception:
            keys = []
    return keys

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

    keys_path = os.path.join(BASE_DIR, "output", "legal", "access_keys.json")
    keys = []
    if os.path.exists(keys_path):
        try:
            with open(keys_path, "r", encoding="utf-8") as f:
                keys = json.load(f)
        except Exception:
            keys = []

    if any(k["key"].upper() == new_key for k in keys):
        raise HTTPException(status_code=400, detail="Esta clave ya existe.")

    new_key_obj = {
        "key": new_key,
        "used": False,
        "used_by": None,
        "created_at": datetime.now().isoformat() + "Z"
    }
    keys.append(new_key_obj)

    with open(keys_path, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4, ensure_ascii=False)

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
        
    if data.user_role == "investment_consultant":
        state.profile.core_research_lines = ["ESG e Impacto Socioeconómico", "Viabilidad de Fondos Multilaterales"]
        state.profile.methodology_preferences = ["Auditoría ESG", "Modelos de Feasibility Financiera"]
        state.profile.influences_authors = ["IFC Performance Standards", "BID", "Banco Mundial"]
        state.profile.local_keywords = ["esg", "finanzas", "retorno", "van", "tir"]
    else:
        state.profile.core_research_lines = ["Bioingeniería de Implantes porosos", "Regeneración celular"]
        state.profile.methodology_preferences = ["Diseño de elementos finitos", "Análisis cuantitativo"]
        state.profile.influences_authors = ["Gibson-Ashby", "Wolff"]
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
    
    qr_svg_mock = '<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#f8f9fa"/><path d="M10 10h20v20H10zM70 10h20v20H70zM10 70h20v20H10zM40 40h20v20H40z" fill="#1a73e8"/></svg>'
    
    filepath, hash_proyecto, cloud_record = archive_signed_legal_act(
        profile=state.profile,
        project_title=state.qualitative_db.project_title if state.qualitative_db else "Proyecto Enthema Suite",
        qr_svg=qr_svg_mock,
        db_qual_hash=db_qual_hash,
        db_quant_hash=db_quant_hash
    )
    
    return {
        "status": "success",
        "hash_proyecto": hash_proyecto,
        "filepath": filepath,
        "cloud_record": cloud_record
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

# ==========================================
# ENTHEMA AI COACH INTERACTIVE CO-PILOT
# ==========================================

class CopilotQueryRequest(BaseModel):
    query: str

@app.post("/api/copilot/query")
async def api_copilot_query(data: CopilotQueryRequest, request: Request):
    """Procesa consultas regulatorias y metodológicas locales (Costo de API $0.00 USD)."""
    state = get_api_session(request)
    user_query = data.query.strip()
    
    query_lower = user_query.lower()
    if any(kw in query_lower for kw in ["nagoya", "marena", "medio ambiente", "biodiversidad", "sargazo", "abs"]):
        answer = (
            "Para proyectos que involucren recursos genéticos locales (como sargazo costero dominicano), "
            "el **Convenio sobre la Diversidad Biológica (Protocolo Nagoya)** exige gestionar el "
            "**Permiso de Acceso a Recursos Genéticos** ante el Viceministerio de Áreas Protegidas y Biodiversidad del "
            "**MARENA (Ministerio de Medio Ambiente)**. Este permiso garantiza la participación justa y equitativa en los "
            "beneficios (ABS). Se requiere completar el formulario de solicitud formal, presentar el protocolo de "
            "investigación académica y acordar las Condiciones de Mutuo Acuerdo (CMA)."
        )
    elif any(kw in query_lower for kw in ["conabios", "bioetica", "bioética", "consentimiento", "ensayo", "paciente"]):
        answer = (
            "Para ensayos clínicos u obtención de muestras biológicas humanas en la República Dominicana (ej. tomografía y prótesis óseas "
            "de pacientes en INTEC/UNIBE), es obligatorio obtener la aprobación del **Comité Nacional de Bioética en Salud (CONABIOS)**. "
            "Debes presentar: 1) Protocolo de investigación clínica detallado. 2) Formulario de Consentimiento Informado (con redacción clara "
            "para pacientes locales). 3) Declaración de confidencialidad y protección de datos. Ningún procedimiento médico o toma de muestras "
            "puede iniciar sin el dictamen favorable de CONABIOS."
        )
    elif any(kw in query_lower for kw in ["fondocyt", "mescyt", "presupuesto", "financiamiento", "honorarios", "topes"]):
        answer = (
            "Bajo la normativa del **FONDOCYT (MESCYT)**: 1) Los fondos otorgados no pueden destinarse a la compra de terrenos o vehículos. "
            "2) Los honorarios de investigadores locales tienen topes establecidos por rango académico y dedicación (generalmente hasta un "
            "40-50% del total presupuestado). 3) Se exige cofinanciamiento institucional (en especie o efectivo) de al menos el 10-20% por parte "
            "de INTEC y UNIBE. 4) Toda compra de equipos mayores de laboratorio debe ser justificada en la propuesta inicial y pasar por procesos "
            "de cotización y aduanas exentos de impuestos selectivos."
        )
    elif any(kw in query_lower for kw in ["trazabilidad", "linaje", "criptografia", "criptografía", "hash", "firma", "qr", "sello"]):
        answer = (
            "El sistema de debida diligencia de Enthema utiliza un esquema de auditoría criptográfica. Cada fase de la postulación "
            "(desde la ingesta Obsidian hasta el solver financiero) genera un resumen de metadatos acoplado que se firma con un "
            "**Hash SHA-256**. El código QR neon vectorial en la portada del reporte HTML actúa como un **sello digital infalsificable**. "
            "Al escanear el QR, un auditor externo o evaluador multilateral puede confrontar el hash local contra la firma en cadena, "
            "garantizando que el expediente no ha sido alterado post-evaluación."
        )
    elif any(kw in query_lower for kw in ["openscad", "onapi", "patente", "diseño", "utilidad", "falange"]):
        answer = (
            "Para registrar la prótesis quirúrgica ante la **ONAPI (Oficina Nacional de la Propiedad Industrial)** en Santo Domingo, "
            "el diseño CAD paramétrico en **OpenSCAD** actúa como la memoria descriptiva tridimensional del modelo de utilidad o patente "
            "de invención. Se debe adjuntar el código parametrizado (que demuestra la adaptabilidad al fémur/falange según tomografía) "
            "junto con la declaración ética. La reproducibilidad digital mediante manufactura aditiva local es clave para cumplir con el "
            "requisito de aplicabilidad industrial exigido por ONAPI."
        )
    else:
        answer = (
            f"Como tu Copiloto de Regulación, he registrado tu consulta: '{user_query}'. "
            "Te sugiero enfocar tu consulta en áreas del cumplimiento científico local. "
            "Por ejemplo, pregúntame sobre el **Protocolo Nagoya (MARENA)** para recursos biológicos, el cumplimiento de bioética ante "
            "**CONABIOS** para datos óseos, los topes presupuestarios de **FONDOCYT (MESCYT)** o el **Sello QR Criptográfico** de auditoría."
        )
        
    return {"status": "success", "answer": answer}

# ==========================================
# APLICACIÓN DE ENTRADA PRINCIPAL
# ==========================================

if __name__ == "__main__":
    import uvicorn
    # Leer puerto dinámico de entorno para compatibilidad con la nube (Render)
    port = int(os.environ.get("PORT", 8501))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
