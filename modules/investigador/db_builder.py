import pandas as pd
import numpy as np
import uuid
import re
from typing import List, Dict, Tuple
from .models import QualitativeDatabase, CodedSemanticUnit, QuantitativeDatabase, VariableMetadata, DueDiligenceIssue

class QualitativeEncoder:
    """
    Motor Cualitativo de Codificación Temática (Estilo ATLAS.ti / Grounded Theory).
    Analiza transcripciones y notas de campo crudas para estructurar el corpus cualitativo del proyecto.
    """
    
    @staticmethod
    def encode_text(project_title: str, document_name: str, raw_text: str) -> QualitativeDatabase:
        """
        Analiza un bloque de texto crudo y simula una codificación inductiva
        de categorías semánticas y citas directas.
        """
        # Limpieza inicial del texto
        paragraphs = [p.strip() for p in raw_text.split("\n") if len(p.strip()) > 15]
        
        coded_units = []
        theme_network = {}
        
        # Diccionario heurístico de códigos y categorías según el dominio semántico
        heuristics = {
            # Dominio Sargazo / Biofertilizantes
            r"(sargazo|alga|costa|playa)": {
                "codes": ["#SargazoInvasivo", "#ImpactoCostero"],
                "category": "Materia Prima y Entorno"
            },
            r"(metal|plomo|arsénico|cadmio|toxic|contamina)": {
                "codes": ["#MetalesPesados", "#ToxicidadSuelo"],
                "category": "Riesgo Bioquímico"
            },
            r"(fertilizante|compost|abono|cultivo|tomate|tierra)": {
                "codes": ["#Biofertilizante", "#RendimientoAgricola"],
                "category": "Aplicación Agrónoma"
            },
            # Dominio Macroeconomía / PYMEs / Inflación
            r"(inflación|precios|costos|encarece)": {
                "codes": ["#InflaciónCostos", "#ErosiónMárgenes"],
                "category": "Presión Macroeconómica"
            },
            r"(crédito|banco|interés|financiamiento|préstamo)": {
                "codes": ["#AccesoCrédito", "#TasaInterésElevada"],
                "category": "Gobernanza Financiera"
            },
            r"(pyme|negocio|comercio|empresa|empleado)": {
                "codes": ["#SupervivenciaPYME", "#LiquidezOperativa"],
                "category": "Impacto Sectorial"
            },
            # Dominio Prótesis / Biomecánica / Falanges
            r"(prótesis|falange|dedo|mano|quirúrgico)": {
                "codes": ["#DiseñoPrótesis", "#BiomecánicaMano"],
                "category": "Ingeniería Médica"
            },
            r"(densidad|hueso|fricción|articulación)": {
                "codes": ["#DensidadÓsea", "#FísicaCinemática"],
                "category": "Parámetros Biomecánicos"
            }
        }
        
        for idx, paragraph in enumerate(paragraphs):
            assigned_codes = []
            assigned_category = "General"
            
            # Evaluar heurísticas semánticas
            for pattern, meta in heuristics.items():
                if re.search(pattern, paragraph, re.IGNORECASE):
                    assigned_codes.extend(meta["codes"])
                    assigned_category = meta["category"]
            
            # Si no hace match, asignamos códigos genéricos
            if not assigned_codes:
                assigned_codes = ["#ConceptoGeneral"]
                assigned_category = "Conceptualización Inicial"
            
            # Eliminar duplicados
            assigned_codes = list(set(assigned_codes))
            
            # Crear unidad codificada
            unit_id = f"QUAL-{uuid.uuid4().hex[:6].upper()}"
            unit = CodedSemanticUnit(
                id=unit_id,
                text_segment=paragraph,
                codes=assigned_codes,
                category=assigned_category,
                source_document=document_name
            )
            coded_units.append(unit)
            
            # Registrar en la red de categorías y códigos
            if assigned_category not in theme_network:
                theme_network[assigned_category] = []
            for code in assigned_codes:
                if code not in theme_network[assigned_category]:
                    theme_network[assigned_category].append(code)
                    
        return QualitativeDatabase(
            project_title=project_title,
            coded_units=coded_units,
            theme_network=theme_network
        )


class QuantitativeProfiler:
    """
    Motor Cuantitativo de Curaduría y Perfilado de Datasets Experimentales.
    Limpia, perfila, detecta anomalías y estandariza diccionarios de variables.
    """
    
    @staticmethod
    def profile_dataframe(project_title: str, df: pd.DataFrame, file_format: str = "CSV") -> Tuple[QuantitativeDatabase, pd.DataFrame]:
        """
        Analiza un DataFrame de Pandas, realiza limpieza de nulos y atípicos, 
        y genera la metadata estructurada del dataset.
        Retorna una tupla (QuantitativeDatabase, DataFrame_Limpio).
        """
        df_clean = df.copy()
        variables_meta = []
        anomalies = []
        
        # 1. Limpieza e Imputación de Datos
        for col in df_clean.columns:
            missing_count = int(df_clean[col].isnull().sum())
            total_count = len(df_clean)
            
            # Inferir tipo de dato
            col_type = str(df_clean[col].dtype)
            inferred_type = "category"
            
            if "int" in col_type:
                inferred_type = "int"
                # Imputar nulos con la mediana
                if missing_count > 0:
                    median_val = df_clean[col].median()
                    df_clean[col] = df_clean[col].fillna(median_val)
                    anomalies.append(f"Variable '{col}': Imputados {missing_count} nulos con la mediana ({median_val}).")
            elif "float" in col_type:
                inferred_type = "float"
                # Imputar nulos con la media
                if missing_count > 0:
                    mean_val = round(float(df_clean[col].mean()), 4)
                    df_clean[col] = df_clean[col].fillna(mean_val)
                    anomalies.append(f"Variable '{col}': Imputados {missing_count} nulos con la media ({mean_val}).")
            elif "datetime" in col_type or df_clean[col].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}").any():
                inferred_type = "datetime"
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                # Imputar fechas con método forward-fill
                if missing_count > 0:
                    df_clean[col] = df_clean[col].fillna(method='ffill')
                    anomalies.append(f"Variable '{col}': Imputados {missing_count} nulos de tiempo usando forward-fill.")
            else:
                # Categórica o Texto
                inferred_type = "category"
                if missing_count > 0:
                    mode_series = df_clean[col].mode()
                    mode_val = str(mode_series[0]) if not mode_series.empty else "Desconocido"
                    df_clean[col] = df_clean[col].fillna(mode_val)
                    anomalies.append(f"Variable '{col}': Imputados {missing_count} nulos de categoría con la moda ('{mode_val}').")
            
            # Determinar rangos válidos lógicos
            valid_range = None
            if inferred_type in ["int", "float"]:
                # 1. Corrección de anomalías físicas (valores negativos en concentraciones o medidas físicas)
                if any(x in col.lower() for x in ["ppm", "densidad", "concentracion", "longitud", "peso", "canal"]):
                    negatives = df_clean[df_clean[col] < 0]
                    if len(negatives) > 0:
                        df_clean[col] = df_clean[col].clip(lower=0.0)
                        anomalies.append(f"Variable '{col}': Corregidas {len(negatives)} anomalías físicas de valores negativos (clipeados a 0).")
                
                min_val = df_clean[col].min()
                max_val = df_clean[col].max()
                valid_range = f"{min_val} a {max_val}"
                
                # 2. Detección y tratamiento de atípicos via Winsorization (IQR heurístico)
                if total_count >= 5:
                    q1 = df_clean[col].quantile(0.25)
                    q3 = df_clean[col].quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = df_clean[(df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)]
                    if len(outliers) > 0:
                        # Aplicar Winsorización (clipear a los límites IQR)
                        df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
                        anomalies.append(f"Variable '{col}': Detectados {len(outliers)} atípicos. Se aplicó Winsorización robusta en rango [{round(lower_bound, 2)}, {round(upper_bound, 2)}].")
            
            elif inferred_type == "datetime":
                min_date = df_clean[col].min()
                max_date = df_clean[col].max()
                valid_range = f"{min_date.strftime('%Y-%m-%d')} a {max_date.strftime('%Y-%m-%d')}" if pd.notnull(min_date) else "N/A"
            else:
                unique_vals = list(df_clean[col].unique())[:5]
                valid_range = f"Categorías: {', '.join(map(str, unique_vals))}"
                if len(df_clean[col].unique()) > 20:
                    valid_range += " (y más...)"
            
            # Crear metadato de variable
            meta = VariableMetadata(
                name=col,
                data_type=inferred_type,
                description=f"Variable autogenerada que representa mediciones de {col}.",
                valid_range=valid_range,
                missing_count=missing_count
            )
            variables_meta.append(meta)
            
        # Detectar sesgo de tamaño muestral general
        if len(df_clean) < 10:
            anomalies.append("Alerta de Sesgo Muestral: El dataset es extremadamente pequeño (menos de 10 registros), lo que limita severamente la potencia estadística de los análisis.")

        db = QuantitativeDatabase(
            project_title=project_title,
            variables=variables_meta,
            total_records=len(df_clean),
            anomalies_detected=anomalies,
            dataset_format=file_format
        )
        
        return db, df_clean


class DueDiligenceEncoder:
    """
    Motor Cualitativo de Due Diligence y Análisis de Riesgos ESG (Environmental, Social, Governance).
    Ingiere informes técnicos o minutas para levantar alertas críticas en el diseño de proyectos de inversión.
    """
    
    @staticmethod
    def encode_consultancy_text(project_title: str, document_name: str, raw_text: str) -> QualitativeDatabase:
        """
        Codifica un informe técnico detectando impactos temáticos de ESG y estructurando
        alertas de salvaguardas (DueDiligenceIssue).
        """
        paragraphs = [p.strip() for p in raw_text.split("\n") if len(p.strip()) > 15]
        
        coded_units = []
        theme_network = {
            "Ambiental (E)": [],
            "Social (S)": [],
            "Gobernanza (G)": []
        }
        esg_issues = []
        
        # Heurísticas de riesgos ESG
        esg_heuristics = [
            {
                "pattern": r"(deforestación|tala|bosque|árbol|fauna|flora|ecológico|agua|río|cauce|biodiversidad)",
                "category": "Ambiental (E)",
                "code": "#ImpactoAmbiental",
                "severity": "Alta",
                "desc": "Alerta de alteración ecológica: Se detectan actividades que interfieren con hábitats naturales críticos o recursos hídricos locales."
            },
            {
                "pattern": r"(desplazamiento|reubicación|vivienda|familia|comunidad|indígena|expropiación|consulta|social)",
                "category": "Social (S)",
                "code": "#ImpactoSocial",
                "severity": "Alta",
                "desc": "Alerta de reasentamiento o conflicto comunitario: Se menciona el desplazamiento de familias o la alteración de comunidades locales sin registro de consulta previa."
            },
            {
                "pattern": r"(licencia|permiso|contrato|soborno|corrupción|transparencia|regulación|ministerio)",
                "category": "Gobernanza (G)",
                "code": "#RiesgoGobernanza",
                "severity": "Media",
                "desc": "Brecha de cumplimiento institucional: Pendiente de validación de permisos regulatorios o contratos de concesión por parte de ministerios locales."
            }
        ]
        
        for paragraph in paragraphs:
            assigned_codes = []
            paragraph_category = "General"
            
            for h in esg_heuristics:
                if re.search(h["pattern"], paragraph, re.IGNORECASE):
                    assigned_codes.append(h["code"])
                    paragraph_category = h["category"]
                    
                    # Generar una alerta formal de Due Diligence
                    issue_id = f"ESG-{uuid.uuid4().hex[:6].upper()}"
                    issue = DueDiligenceIssue(
                        id=issue_id,
                        category=h["category"],
                        description=h["desc"],
                        severity=h["severity"],
                        text_segment=paragraph
                    )
                    esg_issues.append(issue)
                    
                    if h["code"] not in theme_network[h["category"]]:
                        theme_network[h["category"]].append(h["code"])
            
            if not assigned_codes:
                assigned_codes = ["#OperaciónEstándar"]
                paragraph_category = "Gobernanza (G)"
                if "#OperaciónEstándar" not in theme_network["Gobernanza (G)"]:
                    theme_network["Gobernanza (G)"].append("#OperaciónEstándar")
                    
            unit_id = f"CONS-{uuid.uuid4().hex[:6].upper()}"
            unit = CodedSemanticUnit(
                id=unit_id,
                text_segment=paragraph,
                codes=assigned_codes,
                category=paragraph_category,
                source_document=document_name
            )
            coded_units.append(unit)
            
        return QualitativeDatabase(
            project_title=project_title,
            coded_units=coded_units,
            theme_network=theme_network,
            esg_issues=esg_issues
        )


class FinancialFeasibilityProfiler:
    """
    Motor Cuantitativo de Viabilidad Financiera y Costo-Beneficio.
    Calcula de manera exacta indicadores financieros clave (VAN, TIR) a partir
    de flujos de caja proyectados para la toma de decisiones soberanas o corporativas.
    """
    
    @staticmethod
    def calcular_tir(flujos: List[float], max_iter: int = 100, tol: float = 1e-6) -> float:
        """
        Solver numérico de Newton-Raphson para calcular la Tasa Interna de Retorno (TIR).
        Evita dependencias obsoletas y garantiza estabilidad en flujos normales.
        """
        if all(f >= 0 for f in flujos) or all(f <= 0 for f in flujos):
            return 0.0 # Requiere al menos un cambio de signo (inversión inicial negativa)
            
        r = 0.10 # Estimación inicial de tasa del 10%
        for _ in range(max_iter):
            van = sum(f / (1 + r)**t for t, f in enumerate(flujos))
            d_van = sum(-t * f / (1 + r)**(t + 1) for t, f in enumerate(flujos))
            if d_van == 0:
                break
            r_next = r - van / d_van
            if abs(r_next - r) < tol:
                return r_next
            r = r_next
        return r

    @staticmethod
    def profile_financials(
        project_title: str, 
        df: pd.DataFrame, 
        discount_rate: float
    ) -> Tuple[QuantitativeDatabase, pd.DataFrame, float, float, str]:
        """
        Analiza un conjunto de datos financieros con flujos de caja plurianuales,
        imputa nulos, y calcula reactivamente el VAN, la TIR y emite el dictamen de viabilidad.
        """
        df_clean = df.copy()
        
        # 1. Estandarizar columnas de flujos
        # Espera columnas: Año/Periodo, Ingresos, Egresos. Si no, calcula flujo.
        if "Ingresos" in df_clean.columns and "Egresos" in df_clean.columns:
            df_clean["Ingresos"] = df_clean["Ingresos"].fillna(df_clean["Ingresos"].mean())
            df_clean["Egresos"] = df_clean["Egresos"].fillna(df_clean["Egresos"].mean())
            df_clean["Flujo_Caja"] = df_clean["Ingresos"] - df_clean["Egresos"]
        elif "Flujo_Caja" not in df_clean.columns:
            # Si solo tiene una columna numérica, asumimos que es el flujo de caja
            num_cols = df_clean.select_dtypes(include=[np.number]).columns
            if len(num_cols) > 0:
                df_clean["Flujo_Caja"] = df_clean[num_cols[0]].fillna(0.0)
            else:
                df_clean["Flujo_Caja"] = 0.0
                
        # 2. Calcular VAN e TIR
        flujos = df_clean["Flujo_Caja"].tolist()
        
        van = sum(f / (1 + discount_rate)**t for t, f in enumerate(flujos))
        tir = FinancialFeasibilityProfiler.calcular_tir(flujos)
        
        # 3. Dictamen de Viabilidad
        if tir >= discount_rate and van > 0:
            dictamen = "VIABLE (La rentabilidad del proyecto supera la tasa de descuento exigida)"
        elif tir > 0 and van < 0:
            dictamen = "NO VIABLE / RETORNO INSUFICIENTE (La TIR es positiva pero inferior a la tasa de corte)"
        else:
            dictamen = "NO VIABLE / RIESGO EXTREMO (El proyecto destruye valor o tiene flujos negativos acumulados)"
            
        # 4. Crear metadata cuantitativa
        variables_meta = []
        for col in df_clean.columns:
            meta = VariableMetadata(
                name=col,
                data_type=str(df_clean[col].dtype),
                description=f"Columna financiera del proyecto: {col}",
                valid_range=f"{df_clean[col].min()} a {df_clean[col].max()}",
                missing_count=0
            )
            variables_meta.append(meta)
            
        anomalies = [
            f"Análisis Financiero: Tasa de Descuento aplicada: {discount_rate*100:.1f}%.",
            f"Tasa Interna de Retorno (TIR) calculada: {tir*100:.2f}%.",
            f"Valor Actual Neto (VAN) acumulado: ${van:,.2f} USD."
        ]
        
        if tir < 0.05:
            anomalies.append("Alerta Financiera: La rentabilidad (TIR) es críticamente baja, menor al 5%.")
            
        db = QuantitativeDatabase(
            project_title=project_title,
            variables=variables_meta,
            total_records=len(df_clean),
            anomalies_detected=anomalies,
            dataset_format="Excel/Finanzas"
        )
        
        return db, df_clean, van, tir, dictamen


class SyntheticPilotGenerator:
    """
    Generador Procedural de Datos Científicos Piloto (Bootstrapper de Datos Sintéticos).
    Diseñado para investigadores en etapa de 'Ideación' que requieren un corpus experimental inicial
    coherente a su disciplina y palabras clave para validar el flujo completo de Enthema.
    """
    
    @staticmethod
    def generate_qualitative_pilot(profile, project_title: str) -> Tuple[QualitativeDatabase, str]:
        """
        Genera un corpus de bitácora y transcripción cualitativa realista basada en la disciplina,
        postura epistémica y palabras clave del perfil.
        Retorna la base de datos cualitativa codificada y el texto crudo simulado.
        """
        stance = profile.epistemologic_stance
        keywords = ", ".join(profile.local_keywords) if profile.local_keywords else "conceptos núcleo"
        name = profile.name if profile.name else "Investigador"
        inst = profile.institution if profile.institution else "Centro de Investigación"
        
        # 1. Determinar el dominio semántico
        if profile.user_role == "investment_consultant" or "esg" in keywords.lower() or "finanzas" in keywords.lower():
            domain = "social"
        elif "prótesis" in keywords.lower() or "falange" in keywords.lower() or "biomec" in keywords.lower():
            domain = "stem"
        elif "cine" in keywords.lower() or "pintura" in keywords.lower() or "arte" in keywords.lower() or "vanguardia" in keywords.lower() or stance == "Hermenéutica":
            domain = "art"
        else:
            domain = "environment"
            
        # 2. Generar textos procedimentales ricos
        if domain == "stem":
            raw_text = f"""[Sesión de Grupo Focal - Biomecánica y Prótesis de Falanges]
Investigador Principal: Dr. {name} ({inst})
Fecha del Registro: 2026-05-22
Filiación y Postura: Metodología con enfoque en biomecánica clínica.

Registro Clínico Quirúrgico - Cirujano 1:
"En las hemiartroplastias de mano, uno de los grandes problemas clínicos que vemos en los hospitales dominicanos es el stress shielding o apantallamiento de tensiones. El titanio macizo tiene un módulo elástico de unos 110 GPa, mientras que el hueso cortical de la falange proximal solo tiene 18 GPa. Esta enorme diferencia de rigidez hace que el hueso receptor deje de recibir carga fisiológica, atrofiándose progresivamente y provocando un aflojamiento aséptico de la prótesis."

Comentario del Diseñador Ortopédico - Cirujano 2:
"Para mitigar este problema biomecánico, es imperativo que diseñemos vástagos con gradiente de porosidad elástica. Utilizar Titanio Grado 5 biomédico e imprimirlo mediante sinterizado láser selectivo (SLS) nos permite fabricar una microestructura porosa calibrada. Al regular la porosidad en base a la densidad ósea Hounsfield (HU) promedio medida en las tomografías computarizadas de los pacientes dominicanos, podemos disminuir el módulo de Young del implante a unos 20 GPa, adaptándolo casi a la perfección al hueso cortical receptor."

Discusión de Protocolo Ético:
"Declaramos solemnemente que antes de realizar cualquier ensayo biomecánico destructivo in vitro o preclínico in vivo, debemos depositar el expediente ante el Comité Nacional de Bioética (CONABIOS) y respetar los reglamentos del Ministerio de Salud Pública de la República Dominicana, asegurando el consentimiento informado en todas las fases del desarrollo tecnológico."
"""
        elif domain == "social":
            raw_text = f"""[Entrevistas Cualitativas de Campo - Viabilidad de PYMEs y Microcréditos]
Investigador Principal: Dr/Ing. {name} ({inst})
Fecha del Registro: 2026-05-22
Filiación y Postura: Enfoque de resiliencia sectorial y salvaguardas sociales.

Transcripción de Microempresaria Dominicana (Samaná):
"Tengo una pequeña pyme de alimentos en la costa y la situación con los precios está muy dura. La inflación de costos ha erosionado completamente nuestros márgenes operativos. Cuando vamos a un banco comercial, nos exigen requisitos imposibles de cumplir para una pequeña empresa de pueblo, lo que limita gravemente nuestro acceso al crédito y la liquidez operativa. Terminas en manos de prestamistas informales con tasas de interés sumamente elevadas, del 10% o 15% mensual, lo que destruye cualquier posibilidad de supervivencia y viabilidad a largo plazo."

Declaración de Consultor de Desarrollo Social:
"Para estructurar este financiamiento con organismos multilaterales (BID / Banco Mundial), debemos alinear el proyecto bajo las Normas de Desempeño sobre Sostenibilidad de la IFC. La inclusión de un fondo de microcrédito rotatorio debe contar con salvaguardas sociales estrictas para evitar el sobreendeudamiento familiar, garantizando mecanismos de consulta pública previa, libre e informada en las comunidades vulnerables."
"""
        elif domain == "art":
            raw_text = f"""[Bitácora de Crítica Conceptual - Vanguardias Artísticas y Layouts Fílmicos]
Investigador Principal: Lic. {name} ({inst})
Fecha del Registro: 2026-05-22
Filiación y Postura: Enfoque interpretativo y hermenéutico del arte.

Análisis Curatorial - Manifiesto Estético:
"La composición formal en la pintura vanguardista caribeña de mediados de siglo representa una ruptura cromática sin precedentes. Los artistas rompieron la paleta neoclásica impuesta por las academias para incorporar colores saturados y contrastes de luminosidad extremos, respondiendo a la intensidad lumínica de la geografía insular. No se trata simplemente de un cambio técnico, sino de una manifestación de la identidad y la resistencia cultural del Caribe dominicano."

Anotación de Director de Arte y Estética Cinematográfica:
"En la composición de layouts fílmicos actuales, observamos una reutilización de esta ruptura cromática. Analizando los fotogramas, vemos que la composición áurea define los encuadres de mayor tensión dramática, regulando la frecuencia cromática en base a un contraste hermenéutico profundo. Esta interacción de encuadres y colores genera un diálogo estético que desafía la percepción tradicional del espectador y establece una nueva gramática de narrativa audiovisual."
"""
        else:
            raw_text = f"""[Bitácora Transoperatoria y Muestreo Clínico de Campo - Sargazo en Costas]
Investigador Principal: Dr/Dra. {name} ({inst})
Fecha del Registro: 2026-05-22
Filiación y Postura: Enfoque de sostenibilidad ambiental y bioreactores.

Declaración del Líder Cooperativa de Pescadores (Barahona):
"El sargazo invasivo llega en oleadas gigantescas a nuestras playas dominicanas. Esto paraliza por completo nuestra pesca artesanal, ya que las redes se enredan y los motores de las lanchas se dañan por el sobrecalentamiento. Además de arruinar el turismo costero, cuando el sargazo se descompone en la costa genera gases tóxicos y lixiviados ácidos. Necesitamos con urgencia un plan para retirar esta biomasa y darle un uso productivo, como abono agrícola o biocombustibles, para mitigar este impacto social y ambiental severo."

Comentario de Bioquímico de Laboratorio:
"Para transformar el sargazo en un biofertilizante de alto rendimiento para el cultivo de tomate, primero debemos analizar el riesgo bioquímico de toxicidad de suelo. El sargazo absorbe una gran cantidad de metales pesados en su tránsito oceánico, detectándose concentraciones de plomo, cadmio y arsénico que superan los límites permitidos. Es indispensable diseñar un proceso químico de quelación y lavado con ácidos orgánicos ligeros para extraer y precipitar los metales antes de que la biomasa entre al compostaje, garantizando la inocuidad alimentaria de los cultivos receptores."
"""
        
        qual_db = QualitativeEncoder.encode_text(project_title, "bitacora_piloto_ideacion.txt", raw_text)
        return qual_db, raw_text

    @staticmethod
    def generate_quantitative_pilot(profile, project_title: str) -> pd.DataFrame:
        """
        Genera un DataFrame de Pandas procedural con datos científicos crudos realistas,
        incluyendo nulos, valores fuera de rango y atípicos, para ser procesados
        por el curador cuantitativo.
        """
        keywords = ", ".join(profile.local_keywords) if profile.local_keywords else "conceptos núcleo"
        stance = profile.epistemologic_stance
        
        # 1. Determinar el dominio semántico
        if profile.user_role == "investment_consultant" or "esg" in keywords.lower() or "finanzas" in keywords.lower():
            domain = "social"
        elif "prótesis" in keywords.lower() or "falange" in keywords.lower() or "biomec" in keywords.lower():
            domain = "stem"
        elif "cine" in keywords.lower() or "pintura" in keywords.lower() or "arte" in keywords.lower() or "vanguardia" in keywords.lower() or stance == "Hermenéutica":
            domain = "art"
        else:
            domain = "environment"
            
        np.random.seed(42)
        n_records = 15
        
        if domain == "stem":
            data = {
                "Paciente_ID": [f"PAC-{i:03d}" for i in range(1, n_records + 1)],
                "Módulo_Young_GPa": [round(np.random.normal(110.0, 5.0), 2) for _ in range(n_records)],
                "Densidad_Hounsfield": [float(np.random.randint(850, 1150)) for _ in range(n_records)],
                "Porosidad_Diseño": [round(np.random.uniform(0.4, 0.8), 3) for _ in range(n_records)],
                "Fricción_Articular": [round(np.random.uniform(0.1, 0.3), 3) for _ in range(n_records)]
            }
            data["Módulo_Young_GPa"][3] = -12.5
            data["Módulo_Young_GPa"][8] = 230.0
            data["Densidad_Hounsfield"][6] = np.nan
            data["Densidad_Hounsfield"][11] = np.nan
            
        elif domain == "social":
            data = {
                "PYME_ID": [f"PYME-{i:03d}" for i in range(1, n_records + 1)],
                "Tasa_Interes_Anual": [round(np.random.uniform(0.18, 0.45), 3) for _ in range(n_records)],
                "Ingreso_Mensual_DOP": [float(np.random.randint(45000, 120000)) for _ in range(n_records)],
                "Empleados": [int(np.random.randint(1, 10)) for _ in range(n_records)],
                "Gasto_Inflacion_DOP": [float(np.random.randint(5000, 25000)) for _ in range(n_records)]
            }
            data["Tasa_Interes_Anual"][2] = -0.05
            data["Tasa_Interes_Anual"][9] = 1.95
            data["Ingreso_Mensual_DOP"][4] = np.nan
            data["Ingreso_Mensual_DOP"][12] = np.nan
            data["Empleados"][7] = -3
            
        elif domain == "art":
            data = {
                "Obra_ID": [f"OBRA-{i:03d}" for i in range(1, n_records + 1)],
                "Composición_Aurea": [round(np.random.uniform(0.5, 0.95), 3) for _ in range(n_records)],
                "Frecuencia_Cromática_Hz": [float(np.random.randint(400, 750)) for _ in range(n_records)],
                "Contraste_Luminosidad": [round(np.random.uniform(0.3, 0.8), 3) for _ in range(n_records)],
                "Valoración_Hermenéutica_Score": [round(np.random.uniform(5.0, 10.0), 1) for _ in range(n_records)]
            }
            data["Composición_Aurea"][3] = -0.15
            data["Composición_Aurea"][10] = 2.45
            data["Frecuencia_Cromática_Hz"][5] = np.nan
            data["Valoración_Hermenéutica_Score"][8] = -1.0
            
        else:
            data = {
                "Muestra_ID": [f"M-{i:03d}" for i in range(1, n_records + 1)],
                "Plomo_ppm": [round(np.random.normal(1.3, 0.2), 2) for _ in range(n_records)],
                "Cadmio_ppm": [round(np.random.normal(0.45, 0.08), 3) for _ in range(n_records)],
                "Rendimiento_Abono_kg": [round(np.random.uniform(15.0, 50.0), 2) for _ in range(n_records)],
                "Ph_Suelo": [round(np.random.uniform(5.5, 7.8), 2) for _ in range(n_records)]
            }
            data["Plomo_ppm"][2] = -0.8
            data["Plomo_ppm"][11] = 24.5
            data["Cadmio_ppm"][5] = np.nan
            data["Ph_Suelo"][8] = -1.2
            
        return pd.DataFrame(data)

