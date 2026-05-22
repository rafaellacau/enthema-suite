from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class DueDiligenceIssue(BaseModel):
    """
    Representa un riesgo o alerta en el espectro ESG (Environmental, Social, Governance)
    detectado en el informe cualitativo del proyecto de consultoría.
    """
    id: str = Field(..., description="ID único de la alerta de due diligence")
    category: str = Field(..., description="Dimensión ESG: Ambiental, Social, Gobernanza")
    description: str = Field(..., description="Descripción detallada del riesgo o brecha detectada")
    severity: str = Field("Media", description="Severidad del riesgo: Alta, Media, Baja")
    text_segment: str = Field(..., description="Cita o fragmento de texto donde se infiere el riesgo")

class ResearcherProfile(BaseModel):
    """
    Representa el ADN o Genoma Intelectual del investigador o consultor.
    Se alimenta de Obsidian, Zotero, informes o del onboarding cognitivo.
    """
    id: str = Field(..., description="ID único (ej. iniciales o cédula)")
    name: str = Field(..., description="Nombre completo")
    institution: str = Field(..., description="Institución o firma consultora")
    epistemologic_stance: str = Field(
        "Mixed_Methods", 
        description="Postura epistémica predominante: Positivista, Constructivista, Hermenéutica, Mixta"
    )
    user_role: str = Field(
        "classic_researcher",
        description="Rol de operación en la suite: classic_researcher o investment_consultant"
    )
    research_maturity_stage: str = Field(
        "Pendiente",
        description="Grado de madurez de la investigación: Ideación (early-stage sin datos), En Curso, Consolidado (con datos)"
    )
    target_publication_objective: str = Field(
        "Pendiente",
        description="Canal u objetivo final del entregable: Nature, IEEE, World Development, Leonardo, HBR, ONAPI, ONDA"
    )
    legal_terms_accepted: bool = Field(
        False,
        description="Indica si el usuario aceptó explícitamente los descargos éticos y de responsabilidad civil de Enthema"
    )
    electronic_signature_name: str = Field(
        "",
        description="Firma digitalizada de consentimiento y descargo del usuario"
    )
    # Parámetros específicos de consultoría
    consultancy_client: Optional[str] = Field("República Dominicana", description="País o cliente objetivo del financiamiento")
    funding_institution: Optional[str] = Field("Organismo Multilateral", description="Entidad evaluadora (ej. Banco Mundial, BID, Fondo Privado)")
    discount_rate: float = Field(0.10, description="Tasa de descuento de referencia para el cálculo de VAN/TIR")
    target_fund_usd: float = Field(2500000.0, description="Monto de préstamo o financiamiento objetivo en USD")
    orcid: Optional[str] = Field(None, description="ORCID o identificador científico del investigador")
    dois: List[str] = Field(default_factory=list, description="Lista de DOIs de publicaciones relevantes asociadas al investigador")
    
    core_research_lines: List[str] = Field(
        default_factory=list, 
        description="Líneas de investigación o propósitos de inversión núcleo"
    )
    methodology_preferences: List[str] = Field(
        default_factory=list, 
        description="Preferencias metodológicas o marcos de diseño de proyectos"
    )
    influences_authors: List[str] = Field(
        default_factory=list, 
        description="Autores de referencia, marcos teóricos o salvaguardas regulatorias"
    )
    local_keywords: List[str] = Field(
        default_factory=list, 
        description="Palabras clave locales del perfil"
    )

class ConsortiumProfile(BaseModel):
    """
    Representa el genoma intelectual conjunto del consorcio o equipo multidisciplinar.
    Combina los grafos de múltiples investigadores e inyecta la planificación de producción.
    """
    project_title: str = Field(..., description="Título de la propuesta o proyecto de investigación")
    funding_agency: str = Field(
        "FONDOCYT", 
        description="Organismo financiador objetivo (FONDOCYT, Horizonte Europa, ERC, etc.)"
    )
    lead_researcher_id: str = Field(..., description="ID del investigador principal (Líder)")
    members: List[ResearcherProfile] = Field(
        default_factory=list, 
        description="Lista de investigadores que componen el consorcio multidisciplinario"
    )
    synergy_nodes: List[str] = Field(
        default_factory=list, 
        description="Conceptos e intersecciones donde los grafos semánticos de los miembros se cruzan"
    )
    detected_gaps: List[str] = Field(
        default_factory=list, 
        description="Agujeros estructurales y vacíos metodológicos colectivos identificados en el equipo"
    )
    total_budget_usd: float = Field(0.0, description="Presupuesto total calculado por el formulador presupuestario")
    duration_months: int = Field(12, description="Duración total del proyecto en meses")

class CodedSemanticUnit(BaseModel):
    """
    Unidad atómica de análisis cualitativo (estilo ATLAS.ti agéntico).
    Representa una cita empírica directa con sus códigos y categorías asociadas.
    """
    id: str = Field(..., description="ID único de la unidad de texto codificada")
    text_segment: str = Field(..., description="Cita directa o fragmento de texto extraído de la fuente cruda")
    codes: List[str] = Field(..., description="Códigos temáticos asignados a este fragmento (Grounded Theory)")
    category: str = Field(..., description="Categoría conceptual integradora (axial coding)")
    source_document: str = Field(..., description="Nombre del archivo, audio o nota de origen")

class QualitativeDatabase(BaseModel):
    """
    Corpus empírico cualitativo estructurado de la investigación o consultoría.
    """
    project_title: str = Field(..., description="Título del proyecto asociado")
    coded_units: List[CodedSemanticUnit] = Field(
        default_factory=list, 
        description="Lista de citas y fragmentos codificados"
    )
    theme_network: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Mapa relacional que conecta Categorías -> Códigos asociados"
    )
    esg_issues: List[DueDiligenceIssue] = Field(
        default_factory=list,
        description="Alertas de salvaguardas y riesgos ESG detectados en consultoría de inversión"
    )

class VariableMetadata(BaseModel):
    """
    Estructura de metadatos para una variable en el dataset cuantitativo (Diccionario de Variables).
    """
    name: str = Field(..., description="Nombre exacto de la columna o variable")
    data_type: str = Field(..., description="Tipo de dato (float, int, category, datetime)")
    description: Optional[str] = Field(None, description="Descripción semántica de lo que mide la variable")
    valid_range: Optional[str] = Field(None, description="Rango de valores lógicos esperados (ej: '0-100', 'datetime')")
    missing_count: int = Field(0, description="Cantidad de valores nulos o vacíos detectados")

class QuantitativeDatabase(BaseModel):
    """
    Corpus empírico cuantitativo curado de la investigación.
    """
    project_title: str = Field(..., description="Título del proyecto asociado")
    variables: List[VariableMetadata] = Field(
        default_factory=list, 
        description="Diccionario de variables estructurado y estandarizado"
    )
    total_records: int = Field(..., description="Cantidad total de registros / filas en el dataset curado")
    anomalies_detected: List[str] = Field(
        default_factory=list, 
        description="Lista de advertencias estadísticas, valores atípicos o sesgos de muestreo detectados"
    )
    dataset_format: str = Field("CSV", description="Formato del archivo estructurado limpio (CSV, Parquet, etc.)")
