import re
from typing import Tuple
from .models import ResearcherProfile

class CognitiveInterviewer:
    """
    Agente Coach: Entrevistador Socrático y Co-Creador del Perfil de Investigación (Genoma Intelectual).
    Guía al usuario conversacionalmente para estructurar su marco metodológico, conceptual y de impacto.
    """
    
    @staticmethod
    def get_next_question(profile: ResearcherProfile) -> str:
        """
        Analiza el perfil actual del investigador o consultor y determina qué sección requiere aclaración socrática.
        """
        is_consultant = (profile.user_role == "investment_consultant")
        
        if not profile.name or profile.name == "Desconocido":
            if is_consultant:
                return "¿Cómo te llamas y para qué firma consultora o institución estás estructurando este proyecto de inversión?"
            else:
                return "¿Cómo te llamas y a qué universidad o institución de I+D estás afiliado principalmente?"
            
        if len(profile.methodology_preferences) == 0:
            if is_consultant:
                return (
                    f"Hola {profile.name}. En consultoría estratégica de inversión, lo primero es definir la tipología del proyecto. "
                    "¿Este financiamiento es para un desarrollo de infraestructura social y vial (Soberano/Público), "
                    "para una adquisición, fusión o estructuración corporativa (Privado/Corporativo), "
                    "o se enfoca en transición ecológica y sostenibilidad (ESG/Sostenible)?"
                )
            else:
                return (
                    f"Hola {profile.name}. Al iniciar una investigación, el punto de partida es definir tu postura epistémica. "
                    "¿Tu aproximación tiende a ser puramente cuantitativa y estadística (Positivista), "
                    "basada en significados y entrevistas cualitativas (Constructivista), "
                    "o de interpretación textual y práctica creativa (Hermenéutica)?"
                )
            
        if profile.research_maturity_stage == "Pendiente":
            if is_consultant:
                # Los consultores usualmente operan en base a proyectos consolidados o estructurados, pero permitimos selección.
                return (
                    f"Entendido, {profile.name}. ¿En qué fase de madurez se encuentra la formulación del proyecto de inversión? "
                    "Responde si se encuentra en etapa de **Ideación** (fase inicial de propuesta sin estudios de prefactibilidad), "
                    "**En Curso** (estudios técnicos activos), o **Consolidado** (con plan de inversión y bases cuantitativas listas)."
                )
            else:
                return (
                    f"Excelente, {profile.name}. ¿En qué nivel de madurez o etapa de avance se encuentra este proyecto? "
                    "Responde si estás en etapa de **Ideación** (fase inicial de formulación teórica sin datos de campo/laboratorio previos), "
                    "**En Curso** (recopilación activa o curación de datos), o **Consolidado** (cuentas con bases de datos empíricas estructuradas)."
                )

        if profile.target_publication_objective == "Pendiente":
            if is_consultant:
                return (
                    "Perfecto. ¿Cuál es el destino o canal estratégico principal para el reporte de inversión y debida diligencia? "
                    "Elige una opción: registrar la propuesta de inversión ante el Ministerio correspondiente (**ONDA**), "
                    "o presentar la debida diligencia según estándares y formatos de agencias multilaterales de élite como: "
                    "**Nature** (estudios de impacto global), **IEEE** (tecnologías verdes), **World Development** (desarrollo local), "
                    "**Leonardo** (infraestructuras creativas/culturales), o **HBR** (Harvard Business Review - modelos de negocio/adquisiciones)."
                )
            else:
                return (
                    "Excelente decisión metodológica. ¿Cuál es tu canal u objetivo final de publicación o protección de propiedad intelectual? "
                    "Elige una opción: registrar una Patente de Invención (**ONAPI**), registrar Derecho de Autor (**ONDA**), "
                    "o postular a una revista científica indexada de élite como: "
                    "**Nature**, **IEEE**, **World Development**, **Leonardo**, o **HBR** (Harvard Business Review)."
                )

        if len(profile.core_research_lines) == 0:
            if is_consultant:
                return (
                    "Excelente tipología. Definamos los propósitos clave: ¿Cuál es el cliente o país soberano beneficiario "
                    "del crédito, qué monto total en USD se busca financiar (ej: $2,500,000 USD) y qué entidad multilateral o fondo privado evaluará la propuesta?"
                )
            else:
                return (
                    "Excelente postura. Hablemos de tus propósitos: ¿Cuáles son las líneas de investigación núcleo, "
                    "las preguntas fundamentales o las hipótesis en las que estás trabajando o planeas trabajar ahora?"
                )
            
        if len(profile.influences_authors) == 0:
            if is_consultant:
                return (
                    "Estupendo. Para el análisis de riesgos y debidos procesos regulatorios, ¿cuáles son los marcos normativos, "
                    "estándares internacionales o criterios ESG de salvaguardas (ej: Normas de Desempeño de la IFC, Salvaguardas del BM/BID) que guiarán la evaluación?"
                )
            else:
                return (
                    "Perfecto. En tu marco teórico personal, ¿cuáles son los autores de referencia, revistas científicas "
                    "o influencias intelectuales clave que guían tu pensamiento?"
                )
            
        return "Tu perfil cognitivo e intelectual está completamente consolidado en el sistema."

    @staticmethod
    def process_answer(profile: ResearcherProfile, answer: str) -> Tuple[ResearcherProfile, bool, str]:
        """
        Procesa la respuesta del usuario, actualiza el perfil y retorna (perfil_actualizado, completado, mensaje_o_siguiente_pregunta).
        """
        ans = answer.strip()
        if not ans:
            return profile, False, "Por favor, escribe una respuesta válida."
            
        is_consultant = (profile.user_role == "investment_consultant")
        
        # 1. Nombre e Institución
        if not profile.name or profile.name == "Desconocido":
            parts = ans.split(" de ")
            if len(parts) > 1:
                profile.name = parts[0].replace("Me llamo", "").replace("Soy", "").strip()
                profile.institution = parts[1].strip()
            else:
                profile.name = ans.replace("Me llamo", "").replace("Soy", "").strip()
                profile.institution = "Firma Consultora No Declarada" if is_consultant else "Institución No Declarada"
            next_q = CognitiveInterviewer.get_next_question(profile)
            return profile, False, next_q
            
        # 2. Postura / Tipología de Proyecto
        if len(profile.methodology_preferences) == 0:
            ans_lower = ans.lower()
            if is_consultant:
                if "soberano" in ans_lower or "público" in ans_lower or "infra" in ans_lower:
                    profile.epistemologic_stance = "Positivista"
                    profile.methodology_preferences = ["Soberano/Público", "Evaluación de Impacto", "Matriz de Marco Lógico"]
                elif "privado" in ans_lower or "corpora" in ans_lower or "fusión" in ans_lower:
                    profile.epistemologic_stance = "Mixta"
                    profile.methodology_preferences = ["Privado/Corporativo", "Due Diligence Financiero", "Análisis VAN/TIR"]
                else:
                    profile.epistemologic_stance = "Constructivista"
                    profile.methodology_preferences = ["ESG/Sostenible", "Salvaguardas Socioambientales", "Mitigación de Riesgos"]
            else:
                if "positivo" in ans_lower or "cuanti" in ans_lower or "número" in ans_lower:
                    profile.epistemologic_stance = "Positivista"
                    profile.methodology_preferences = ["Cuantitativa", "Econometría", "Modelado Estadístico"]
                elif "construc" in ans_lower or "cuali" in ans_lower or "entrevista" in ans_lower:
                    profile.epistemologic_stance = "Constructivista"
                    profile.methodology_preferences = ["Cualitativa", "Grounded Theory", "Estudios de Caso"]
                elif "hermene" in ans_lower or "art" in ans_lower or "creati" in ans_lower:
                    profile.epistemologic_stance = "Hermenéutica"
                    profile.methodology_preferences = ["Hermenéutica", "Investigación Artística", "Crítica Conceptual"]
                else:
                    profile.epistemologic_stance = "Mixta"
                    profile.methodology_preferences = ["Métodos Mixtos", "Triangulación Metodológica"]
            next_q = CognitiveInterviewer.get_next_question(profile)
            return profile, False, next_q
            
        # 2.5. Madurez del Proyecto (Ideación, En Curso, Consolidado)
        if profile.research_maturity_stage == "Pendiente":
            ans_lower = ans.lower()
            if "idea" in ans_lower or "inici" in ans_lower or "tempran" in ans_lower:
                profile.research_maturity_stage = "Ideación"
            elif "curso" in ans_lower or "desarroll" in ans_lower or "recopil" in ans_lower:
                profile.research_maturity_stage = "En Curso"
            else:
                profile.research_maturity_stage = "Consolidado"
            next_q = CognitiveInterviewer.get_next_question(profile)
            return profile, False, next_q

        # 2.6. Objetivo de Publicación / Protección Intelectual
        if profile.target_publication_objective == "Pendiente":
            ans_lower = ans.lower()
            if "nature" in ans_lower:
                profile.target_publication_objective = "Nature"
            elif "ieee" in ans_lower:
                profile.target_publication_objective = "IEEE"
            elif "world" in ans_lower or "develop" in ans_lower:
                profile.target_publication_objective = "World Development"
            elif "leonardo" in ans_lower:
                profile.target_publication_objective = "Leonardo"
            elif "harvard" in ans_lower or "hbr" in ans_lower:
                profile.target_publication_objective = "HBR"
            elif "onda" in ans_lower:
                profile.target_publication_objective = "ONDA"
            else:
                profile.target_publication_objective = "ONAPI"
            next_q = CognitiveInterviewer.get_next_question(profile)
            return profile, False, next_q
            
        # 3. Líneas de Investigación / Parámetros de Inversión
        if len(profile.core_research_lines) == 0:
            if is_consultant:
                # Intento heurístico de extraer montos y entidades
                # Buscar números que representen montos en USD
                numbers = re.findall(r"\$?\s*(\d+[.,\d]*)\s*(millón|millones|mil|usd|dólares)?", ans, re.IGNORECASE)
                if numbers:
                    val_str = numbers[0][0].replace(",", "")
                    try:
                        val = float(val_str)
                        if "millón" in numbers[0][1] or "millones" in numbers[0][1]:
                            val = val * 1000000.0
                        profile.target_fund_usd = val
                    except ValueError:
                        pass
                
                # Heurística para cliente y financiador
                if "evaluará" in ans:
                    parts_eval = ans.split("evaluará")
                    profile.funding_institution = parts_eval[-1].replace("el", "").replace("la", "").strip().capitalize()
                elif " por " in ans:
                    parts_por = ans.split(" por ")
                    profile.funding_institution = parts_por[-1].strip().capitalize()
                    
                match_country = re.search(r"para\s+([a-zA-Záéíóú\s]+)(?:\s+del|\s+o|\s+de|$)", ans, re.IGNORECASE)
                if match_country:
                    profile.consultancy_client = match_country.group(1).strip().capitalize()
                
                profile.core_research_lines = [f"Financiamiento de proyecto de inversión soberana/privada por ${profile.target_fund_usd:,.2f} USD"]
            else:
                lines = [line.strip() for line in re.split(r"[,;.]", ans) if len(line.strip()) > 5]
                if not lines:
                    lines = [ans]
                profile.core_research_lines = lines
                
            next_q = CognitiveInterviewer.get_next_question(profile)
            return profile, False, next_q
            
        # 4. Influencias / Salvaguardas
        if len(profile.influences_authors) == 0:
            authors = [auth.strip() for auth in re.split(r"[,;y]", ans) if len(auth.strip()) > 3]
            if not authors:
                authors = [ans]
            profile.influences_authors = authors
            
            # Al completar, simulamos inyección de palabras clave locales (Obsidian/Zotero)
            if is_consultant:
                profile.local_keywords = ["esg", "viabilidad", "van", "tir", "riesgos", "soberano"]
                return profile, True, "¡Genial! Hemos construido tu Perfil de Consultor (D0) de forma exitosa. El sistema está ahora listo para auditar, simular y desglosar tu proyecto de inversión."
            else:
                profile.local_keywords = ["sargazo", "metales_pesados", "inflación", "prótesis_falanges", "simulación"]
                return profile, True, "¡Genial! Hemos construido tu Perfil del Investigador (D0) de forma exitosa. El sistema está ahora listo para auditar, simular y desglosar tu proyecto."
            
        return profile, True, "Tu perfil cognitivo e intelectual está completamente consolidado en el sistema."


class PassiveProfileExtractor:
    """
    Agente Extractor Pasivo de Perfiles de Investigación y Consultoría.
    Parsea documentos de Obsidian Markdown y exportaciones Zotero RIS/BibTeX para autocompletar ResearcherProfile.
    """
    
    @staticmethod
    def infer_epistemology_from_text(text: str) -> str:
        """
        Heurística de inferencia epistémica basada en palabras clave presentes en títulos, keywords y resúmenes.
        """
        text_lower = text.lower()
        positivist_words = [
            "regression", "regresión", "control group", "grupo control", "spectroscopy", 
            "espectrometría", "quantitative", "cuantitativo", "statistical", "estadístico", 
            "experiment", "experimento", "van", "tir", "npv", "irr", "financial", "financiero",
            "correlation", "correlación", "dataset", "variable", "anomalies", "outliers", "bifurcación"
        ]
                            
        constructivist_words = [
            "phenomenology", "fenomenología", "grounded theory", "teoría fundamentada", 
            "ethnography", "etnografía", "qualitative", "cualitativo", "interview", 
            "entrevista", "focus group", "grupo focal", "narrative", "narrativa", 
            "social construct", "sargazo", "comunidad", "pescador", "esg", "social", "salvaguarda"
        ]
                                
        hermeneutic_words = [
            "hermeneutic", "hermenéutica", "art ", "arte", "creative", "creativo", 
            "aesthetic", "estético", "curator", "curaduría", "exhibition", "exposición", 
            "deconstruction", "deconstrucción", "poetic", "poético", "philosoph", "filosof", "instalación"
        ]
        
        pos_score = sum(text_lower.count(word) for word in positivist_words)
        con_score = sum(text_lower.count(word) for word in constructivist_words)
        her_score = sum(text_lower.count(word) for word in hermeneutic_words)
        
        if pos_score > con_score and pos_score > her_score:
            return "Positivista"
        elif con_score > pos_score and con_score > her_score:
            return "Constructivista"
        elif her_score > pos_score and her_score > con_score:
            return "Hermenéutica"
        return "Mixta"

    @staticmethod
    def parse_obsidian_markdown(content: str, profile: ResearcherProfile) -> Tuple[ResearcherProfile, bool, str]:
        """
        Parsea notas de Obsidian en Markdown. Soporta YAML frontmatter y búsquedas de marcas de texto clave.
        """
        try:
            # 1. Intentar parsear YAML frontmatter
            yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                for line in yaml_content.split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        k = k.strip().lower()
                        v = v.strip().strip('"').strip("'")
                        
                        if k in ["name", "nombre"]:
                            profile.name = v
                        elif k in ["institution", "institución", "institucion", "afiliacion", "afiliación"]:
                            profile.institution = v
                        elif k in ["epistemologic_stance", "epistemology", "epistemología", "epistemologia", "postura"]:
                            profile.epistemologic_stance = v
                        elif k in ["user_role", "role", "rol"]:
                            if "consultor" in v.lower() or "invers" in v.lower() or "consultant" in v.lower():
                                profile.user_role = "investment_consultant"
                            else:
                                profile.user_role = "classic_researcher"
                        elif k in ["consultancy_client", "client", "cliente"]:
                            profile.consultancy_client = v
                        elif k in ["funding_institution", "funding", "financiador"]:
                            profile.funding_institution = v
                        elif k in ["target_fund_usd", "fund", "monto"]:
                            try:
                                profile.target_fund_usd = float(re.sub(r"[^\d.]", "", v))
                            except ValueError:
                                pass
                        elif k in ["discount_rate", "rate", "tasa"]:
                            try:
                                val = float(re.sub(r"[^\d.]", "", v))
                                if val > 1.0:
                                    val = val / 100.0
                                profile.discount_rate = val
                            except ValueError:
                                pass
                        elif k in ["orcid", "registro orcid", "id orcid"]:
                            profile.orcid = v
                        elif k in ["doi", "dois", "doi de publicaciones", "publicaciones doi"]:
                            profile.dois = [d.strip() for d in v.split(",") if d.strip()]
            
            # 2. Parsear marcas de texto y encabezados si no están en YAML o complementarios
            lines = content.split("\n")
            current_section = None
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                
                # Detectar secciones de lista
                if line_stripped.startswith("## ") or line_stripped.startswith("### "):
                    sec_name = line_stripped.replace("#", "").strip().lower()
                    if "línea" in sec_name or "linea" in sec_name or "propósito" in sec_name:
                        current_section = "lines"
                        continue
                    elif "influencia" in sec_name or "autor" in sec_name or "salvaguarda" in sec_name:
                        current_section = "influences"
                        continue
                    elif "metodología" in sec_name or "diseño" in sec_name:
                        current_section = "methodologies"
                        continue
                    elif "palabra" in sec_name or "keyword" in sec_name:
                        current_section = "keywords"
                        continue
                    elif "doi" in sec_name or "publicacion" in sec_name or "publicación" in sec_name:
                        current_section = "dois"
                        continue
                    else:
                        current_section = None
                        if ":" not in line_stripped:
                            continue
                
                # Extraer items de lista
                if current_section and (line_stripped.startswith("-") or line_stripped.startswith("*")):
                    item = re.sub(r"^[-*]\s*", "", line_stripped).strip().strip('"').strip("'")
                    if current_section == "lines" and item not in profile.core_research_lines:
                        profile.core_research_lines.append(item)
                    elif current_section == "influences" and item not in profile.influences_authors:
                        profile.influences_authors.append(item)
                    elif current_section == "methodologies" and item not in profile.methodology_preferences:
                        profile.methodology_preferences.append(item)
                    elif current_section == "keywords" and item not in profile.local_keywords:
                        profile.local_keywords.append(item)
                    elif current_section == "dois" and item not in profile.dois:
                        profile.dois.append(item)
                    continue

                # Detectar nombre si está en un título principal # Nombre
                if line_stripped.startswith("# ") and not line_stripped.startswith("##"):
                    potential_name = line_stripped.replace("#", "").strip()
                    if not any(w in potential_name.lower() for w in ["línea", "linea", "influencia", "autor", "metodología", "keyword", "doi", "publicacion"]):
                        if not profile.name or profile.name in ["Desconocido", "Investigador Extrapolado"]:
                            profile.name = potential_name

                # Intentar marcas inline (ej: **Nombre:** Dr. Francisco González)
                line_for_inline = re.sub(r"^#+\s*", "", line_stripped).strip()
                inline_match = re.match(r"^\*?\*?([a-zA-ZáéíóúÁÉÍÓÚ\s]+)\*?\*?\s*:\s*(.*)$", line_for_inline)
                if inline_match:
                    k = inline_match.group(1).strip().lower()
                    v = inline_match.group(2).strip().strip('"').strip("'")
                    
                    if k in ["nombre", "name"] and (not profile.name or profile.name == "Desconocido"):
                        profile.name = v
                    elif k in ["institución", "institucion", "institution", "firma"] and (not profile.institution or "No Declarada" in profile.institution or "Entorno Jupyter" in profile.institution):
                        profile.institution = v
                    elif k in ["postura", "postura epistémica", "postura epistemica", "epistemology"] and len(profile.methodology_preferences) == 0:
                        profile.epistemologic_stance = v
                    elif k in ["orcid", "registro orcid", "id orcid"]:
                        profile.orcid = v
                    elif k in ["doi", "dois", "doi de publicaciones", "publicaciones doi"]:
                        profile.dois = [d.strip() for d in v.split(",") if d.strip()]
                    elif k in ["rol", "role", "tipo de investigador"]:
                        if "consultor" in v.lower() or "invers" in v.lower() or "consultant" in v.lower():
                            profile.user_role = "investment_consultant"
                        elif "investigador" in v.lower() or "clásico" in v.lower():
                            profile.user_role = "classic_researcher"
            
            # Completar valores nulos por defecto si no se leyeron
            if not profile.name:
                profile.name = "Investigador Extrapolado"
            if len(profile.core_research_lines) == 0:
                profile.core_research_lines = ["Investigación basada en nota de Obsidian"]
            if len(profile.influences_authors) == 0:
                profile.influences_authors = ["Influencias no declaradas"]
            
            # Inferencia automática de la postura si quedó mixta/por defecto y hay líneas
            if profile.epistemologic_stance in ["Mixed_Methods", "Mixta"] or not profile.epistemologic_stance:
                comb_text = " ".join(profile.core_research_lines) + " " + " ".join(profile.local_keywords)
                profile.epistemologic_stance = PassiveProfileExtractor.infer_epistemology_from_text(comb_text)
                
            # Establecer metodologías en base a la postura si están vacías
            if len(profile.methodology_preferences) == 0:
                if profile.user_role == "investment_consultant":
                    profile.methodology_preferences = ["Due Diligence Financiero", "Salvaguardas ESG"]
                else:
                    if profile.epistemologic_stance == "Positivista":
                        profile.methodology_preferences = ["Cuantitativa", "Modelado Estadístico"]
                    elif profile.epistemologic_stance == "Constructivista":
                        profile.methodology_preferences = ["Cualitativa", "Grounded Theory"]
                    elif profile.epistemologic_stance == "Hermenéutica":
                        profile.methodology_preferences = ["Hermenéutica", "Investigación Artística"]
                    else:
                        profile.methodology_preferences = ["Métodos Mixtos"]
                        
            return profile, True, "¡Nota de Obsidian importada y compilada con éxito!"
        except Exception as e:
            return profile, False, f"Error al procesar la nota de Obsidian: {str(e)}"

    @staticmethod
    def parse_zotero_ris(content: str, profile: ResearcherProfile) -> Tuple[ResearcherProfile, bool, str]:
        """
        Parsea exportaciones de Zotero en formato RIS.
        Extrae autores, palabras clave y deduce líneas a partir de títulos.
        """
        try:
            lines = content.split("\n")
            authors = []
            keywords = []
            titles = []
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped or " - " not in line_stripped:
                    continue
                tag, val = line_stripped.split(" - ", 1)
                tag = tag.strip()
                val = val.strip()
                
                if tag == "AU":
                    # Formato: Lastname, Firstname
                    authors.append(val)
                elif tag == "TI":
                    titles.append(val)
                elif tag == "KW":
                    keywords.append(val)
                elif tag in ["DO", "DI"]:
                    if val not in profile.dois:
                        profile.dois.append(val)
                elif tag in ["UR", "DP"] or "orcid" in val.lower():
                    orcid_match = re.search(r"\b\d{4}-\d{4}-\d{4}-[\dX]{4}\b", val)
                    if orcid_match:
                        profile.orcid = orcid_match.group(0)
            
            # Incorporar autores
            if authors:
                for auth in authors[:5]:  # Máximo 5 autores principales
                    if auth not in profile.influences_authors:
                        profile.influences_authors.append(auth)
            
            # Incorporar palabras clave
            if keywords:
                for kw in keywords[:8]:
                    kw_clean = kw.lower().replace(" ", "_")
                    if kw_clean not in profile.local_keywords:
                        profile.local_keywords.append(kw_clean)
            
            # Extraer líneas de investigación basadas en los títulos más recurrentes
            for ti in titles[:3]:
                if ti not in profile.core_research_lines:
                    profile.core_research_lines.append(ti)
            
            # Inferencia de Postura Epistémica basada en todos los títulos y palabras clave
            combined_corpus = " ".join(titles) + " " + " ".join(keywords)
            profile.epistemologic_stance = PassiveProfileExtractor.infer_epistemology_from_text(combined_corpus)
            
            # Nombre por defecto
            if not profile.name or profile.name == "Desconocido":
                profile.name = "Investigador Zotero"
            profile.institution = "Biblioteca Zotero Ingestada"
            
            # Metodologías por defecto según postura
            if len(profile.methodology_preferences) == 0:
                if profile.user_role == "investment_consultant":
                    profile.methodology_preferences = ["Matriz de Marco Lógico", "Debido Proceso ESG"]
                else:
                    if profile.epistemologic_stance == "Positivista":
                        profile.methodology_preferences = ["Cuantitativa", "Análisis Estadístico"]
                    elif profile.epistemologic_stance == "Constructivista":
                        profile.methodology_preferences = ["Cualitativa", "Grounded Theory"]
                    elif profile.epistemologic_stance == "Hermenéutica":
                        profile.methodology_preferences = ["Crítica Estética", "Hermenéutica"]
                    else:
                        profile.methodology_preferences = ["Triangulación de Datos"]
            
            return profile, True, f"¡RIS de Zotero parseado con éxito! Se extrajeron {len(authors)} autores, {len(titles)} publicaciones y {len(keywords)} palabras clave."
        except Exception as e:
            return profile, False, f"Error al procesar el archivo RIS de Zotero: {str(e)}"

    @staticmethod
    def parse_zotero_bibtex(content: str, profile: ResearcherProfile) -> Tuple[ResearcherProfile, bool, str]:
        """
        Parsea entradas en formato BibTeX de Zotero.
        Usa expresiones regulares sencillas para extraer campos de interés.
        """
        try:
            authors = []
            titles = []
            keywords = []
            
            # Extraer autores: author = {Author1 and Author2}
            author_matches = re.findall(r"author\s*=\s*[\{\"]([^\}\"]+)[\}\"]", content, re.IGNORECASE)
            for am in author_matches:
                parts = am.split(" and ")
                for part in parts:
                    authors.append(part.strip())
                    
            # Extraer títulos: title = {Title Text}
            title_matches = re.findall(r"title\s*=\s*[\{\"]([^\}\"]+)[\}\"]", content, re.IGNORECASE)
            for tm in title_matches:
                titles.append(tm.strip())
                
            # Extraer palabras clave: keywords = {kw1, kw2} o keylist
            kw_matches = re.findall(r"keywords\s*=\s*[\{\"]([^\}\"]+)[\}\"]", content, re.IGNORECASE)
            for km in kw_matches:
                parts = km.split(",")
                for part in parts:
                    keywords.append(part.strip())
            
            # Extraer DOIs: doi = {10.1002/jor.23000}
            doi_matches = re.findall(r"doi\s*=\s*[\{\"]([^\}\"]+)[\}\"]", content, re.IGNORECASE)
            for dm in doi_matches:
                if dm.strip() not in profile.dois:
                    profile.dois.append(dm.strip())
            
            # Extraer ORCID: orcid = {0000-0002-1823-4567}
            orcid_matches = re.findall(r"orcid\s*=\s*[\{\"]([^\}\"]+)[\}\"]", content, re.IGNORECASE)
            if orcid_matches:
                profile.orcid = orcid_matches[0].strip()
            
            # Asignar al perfil
            if authors:
                for auth in authors[:5]:
                    if auth not in profile.influences_authors:
                        profile.influences_authors.append(auth)
            
            if keywords:
                for kw in keywords[:8]:
                    kw_clean = kw.lower().replace(" ", "_")
                    if kw_clean not in profile.local_keywords:
                        profile.local_keywords.append(kw_clean)
            
            for ti in titles[:3]:
                if ti not in profile.core_research_lines:
                    profile.core_research_lines.append(ti)
                    
            combined_corpus = " ".join(titles) + " " + " ".join(keywords)
            profile.epistemologic_stance = PassiveProfileExtractor.infer_epistemology_from_text(combined_corpus)
            
            if not profile.name or profile.name == "Desconocido":
                profile.name = "Investigador BibTeX"
            profile.institution = "Biblioteca BibTeX Ingestada"
            
            if len(profile.methodology_preferences) == 0:
                if profile.user_role == "investment_consultant":
                    profile.methodology_preferences = ["Evaluación Financiera", "Normas de Desempeño IFC"]
                else:
                    if profile.epistemologic_stance == "Positivista":
                        profile.methodology_preferences = ["Cuantitativa", "Modelado de Sistemas"]
                    elif profile.epistemologic_stance == "Constructivista":
                        profile.methodology_preferences = ["Cualitativa", "Grounded Theory"]
                    elif profile.epistemologic_stance == "Hermenéutica":
                        profile.methodology_preferences = ["Investigación Artística", "Fenomenología"]
                    else:
                        profile.methodology_preferences = ["Métodos Mixtos"]
            
            return profile, True, f"¡BibTeX de Zotero parseado con éxito! Se extrajeron {len(authors)} autores y {len(titles)} publicaciones."
        except Exception as e:
            return profile, False, f"Error al procesar el archivo BibTeX de Zotero: {str(e)}"

    @staticmethod
    def parse_jupyter_notebook(content: str, profile: ResearcherProfile) -> Tuple[ResearcherProfile, bool, str]:
        """
        Parsea archivos de Jupyter Notebook (.ipynb) representados como JSON.
        Extrae texto de las celdas de Markdown y comentarios de celdas de Código,
        e infiere los metadatos de perfil.
        """
        try:
            import json
            notebook = json.loads(content)
            cells = notebook.get("cells", [])
            
            markdown_texts = []
            code_comments = []
            code_lines = []
            
            for cell in cells:
                cell_type = cell.get("cell_type", "")
                source = cell.get("source", [])
                
                # 'source' can be a list of strings or a single string
                if isinstance(source, list):
                    source_str = "".join(source)
                else:
                    source_str = str(source)
                source_str = source_str.replace("\\n", "\n")
                
                if cell_type == "markdown":
                    markdown_texts.append(source_str)
                elif cell_type == "code":
                    comments = []
                    for line in source_str.split("\n"):
                        code_lines.append(line)
                        line_stripped = line.strip()
                        if line_stripped.startswith("#"):
                            comments.append(line_stripped.lstrip("#").strip())
                    if comments:
                        code_comments.append("\n".join(comments))
            
            # Combine all texts for parsing
            combined_markdown = "\n".join(markdown_texts)
            combined_comments = "\n".join(code_comments)
            full_corpus = combined_markdown + "\n" + combined_comments
            
            # We can use the parse_obsidian_markdown logic on the extracted text!
            profile, ok, msg = PassiveProfileExtractor.parse_obsidian_markdown(full_corpus, profile)
            if not ok:
                return profile, False, msg
            
            # Additional custom notebook processing
            if not profile.name or profile.name == "Investigador Extrapolado":
                profile.name = "Investigador Jupyter Notebook"
            if "Biblioteca" in profile.institution or "No Declarada" in profile.institution or not profile.institution:
                profile.institution = "Entorno Jupyter Local (Notebook)"
                
            # Scan for libraries to suggest methodologies or keywords
            code_corp = "\n".join(code_lines).lower()
            detected_libs = []
            if "pandas" in code_corp or "pd." in code_corp:
                detected_libs.append("Pandas")
            if "numpy" in code_corp or "np." in code_corp:
                detected_libs.append("NumPy")
            if "scipy" in code_corp or "sp." in code_corp:
                detected_libs.append("SciPy")
            if "scikit-learn" in code_corp or "sklearn" in code_corp:
                detected_libs.append("Scikit-Learn")
            if "matplotlib" in code_corp or "plt." in code_corp:
                detected_libs.append("Matplotlib")
            if "seaborn" in code_corp or "sns." in code_corp:
                detected_libs.append("Seaborn")
            if "statsmodels" in code_corp:
                detected_libs.append("Statsmodels")
            if "tensorflow" in code_corp or "keras" in code_corp or "torch" in code_corp:
                detected_libs.append("Deep Learning")
                
            if detected_libs:
                for lib in detected_libs:
                    if lib not in profile.methodology_preferences:
                        profile.methodology_preferences.append(lib)
                if "notebook_data" not in profile.local_keywords:
                    profile.local_keywords.append("notebook_data")
                    
            return profile, True, f"¡Jupyter Notebook parseado con éxito! Se extrajeron {len(markdown_texts)} celdas de texto, {len(cells) - len(markdown_texts)} celdas de código, y se detectaron librerías científicas: {', '.join(detected_libs) if detected_libs else 'Ninguna'}."
        except Exception as e:
            return profile, False, f"Error al procesar el Jupyter Notebook: {str(e)}. Asegúrate de que sea un archivo .ipynb válido (JSON)."
