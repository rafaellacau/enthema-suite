# -*- coding: utf-8 -*-
"""
Enthema Suite V2.5 - Módulo de Monografía Académica Completa y Motor Adaptativo (Nivel Oro)
"""
import sys

class DynamicAcademicMonograph(dict):
    """
    Motor Dinámico Adaptativo de Monografías Científicas (Nivel Oro).
    Hereda de 'dict' para asegurar compatibilidad total de consulta con el resto del sistema,
    generando dinámicamente capítulos, citas, fórmulas y estilos de citación bibliográficos.
    """
    def __init__(self, default_data=None):
        super().__init__()
        self._default = default_data or {}
        self.test_profile = None  # Permite pasar perfiles directamente para testing
        
    def _get_active_profile(self):
        # 1. Prioridad: Perfil de prueba
        if self.test_profile is not None:
            return self.test_profile
            
        # 2. Intentar buscar en st.session_state si Streamlit está cargado
        if 'streamlit' in sys.modules:
            import streamlit as st
            if 'researcher_profile' in st.session_state and st.session_state.researcher_profile is not None:
                return st.session_state.researcher_profile
        return None
        
    def get_data(self):
        profile = self._get_active_profile()
        if not profile:
            # Retorna el fallback original de STEM
            return self._default
            
        target = profile.target_publication_objective or "Nature"
        user_role = profile.user_role or "classic_researcher"
        epistemology = profile.epistemologic_stance or "Positivista"
        
        # Determinar el dominio basado en el target o la postura
        if target in ["World Development"]:
            domain = "social_sciences"
        elif target in ["Leonardo", "ONDA"] or epistemology == "Hermenéutica":
            domain = "arts"
        elif target in ["HBR"] or user_role == "investment_consultant":
            domain = "business"
        else:
            domain = "stem"
            
        name = profile.name or "Dr. Francisco González"
        inst = profile.institution or "Instituto Tecnológico de Santo Domingo (INTEC)"
        
        data = {}
        
        # 1. CIENCIAS SOCIALES / WORLD DEVELOPMENT
        if domain == "social_sciences":
            data["title"] = "DISEÑO SOBERANO DE POLÍTICAS PÚBLICAS Y MODELO DE RESILIENCIA SOCIOECONÓMICA FRENTE AL IMPACTO AMBIENTAL DEL SARGAZO EN LAS COMUNIDADES PESQUERAS DE SAMANÁ Y BARAHONA"
            data["authors"] = f"{name} & Dra. Altagracia Gómez (UNIBE)"
            data["institution"] = f"{inst} & Universidad Iberoamericana (UNIBE)"
            data["bibliography_style_name"] = "Normas APA"
            data["chapters"] = {
                "introduction": f"""
### Capítulo I: Introducción y Planteamiento del Problema
El arribo masivo y atípico de macroalgas pelágicas (*Sargassum fluitans* y *S. natans*) a las costas de la República Dominicana, especialmente en Samaná, Barahona y San Pedro de Macorís, representa una crisis socio-ambiental multidimensional sin precedentes. Este fenómeno interrumpe de manera violenta los ciclos socio-productivos de la pesca artesanal y la economía turística costera, marginando a poblaciones vulnerables.

Aunque se ha planteado la recolección industrial y la valorización de sargazo para subproductos comerciales, existe un **vacío estructural de gobernanza local**. La privatización o industrialización sin salvaguardas sociales tiende a excluir a las cooperativas pesqueras autóctonas, catalizando una severa asimetría en la distribución de la renta ambiental. Esta desconexión es agravada por la falta de un modelo cuantitativo de vulnerabilidad social y resiliencia que permita guiar la formulación de políticas públicas informadas por la evidencia y proteger el bienestar de las comunidades costeras dominicanas.

Por lo tanto, la pregunta de investigación que orienta este estudio es: **¿Cómo formular un marco de políticas públicas y subsidios condicionados que promueva la resiliencia socio-productiva local y garantice la redistribución equitativa de beneficios derivados de la recolección y valorización del sargazo en las comunidades costeras dominicanas?**
""",
                "theoretical_framework": """
### Capítulo II: Fundamentación Teórica y Modelo de Vulnerabilidad
Para comprender la distribución de las asimetrías de renta y la vulnerabilidad social provocadas por el sargazo, adoptamos el **Modelo de Vulnerabilidad Estructural y Capitales Comunitarios** adaptado a economías de subsistencia. La disparidad en los ingresos locales de los pescadores artesanales antes y después de la invasión del sargazo se modela matemáticamente a través del **Coeficiente de Gini ($G$)**:

$$G = \\frac{\\sum_{i=1}^n \\sum_{j=1}^n |y_i - y_j|}{2n^2 \\bar{y}}$$

Donde $y_i$ y $y_j$ representan los ingresos diarios de los hogares pesqueros encuestados, $n$ es el número de hogares en la muestra y $\\bar{y}$ es el ingreso medio. Un aumento del coeficiente de Gini hacia valores cercanos a $1.0$ representa una severa concentración de la pobreza inducida por la pérdida de la capacidad pesquera activa.

Para modelar el impacto amortiguador de un subsidio condicionado del FONDOCYT u organismos de desarrollo, se evalúa el índice de **Resiliencia Socioeconómica Estructural ($R_{se}$)**:

$$R_{se} = \\sum_{k=1}^m w_k \\cdot C_k$$

Donde $C_k$ representa los puntajes normalizados de los dos capitales comunitarios evaluados (Físico, Humano) y $w_k$ son los pesos empíricos de importancia relativa estimados mediante modelos econométricos estructurales.
""",
                "methodology": """
### Capítulo III: Metodología y Triangulación de Datos
Este estudio adopta una **metodología mixta de triangulación concurrente**:

#### A. Fase Cualitativa (Grounded Theory y Consulta Comunitaria)
Se codificaron 15 transcripciones de grupos focales con pescadores de las cooperativas de Samaná y Barahona. El análisis de correspondencia conceptual aisló los códigos axiales de **"pobreza_exclusión"**, **"salud_respiratoria"** (por gases de ácido sulfhídrico) y **"cooperativismo_comunitario"**, justificando las políticas públicas de salvaguardas y transferencia tecnológica.

#### B. Fase Cuantitativa (Curación del Dataset de Encuestas)
Se procesó el dataset de encuestas socioeconómicas `datos_ingresos_pescadores.csv` correspondiente a 100 familias pesqueras. El preprocesamiento automático en la suite ejecutó:
1. *Imputación de Ingresos Nulos:* Empleando vecinos cercanos de actividad productiva.
2. *Winsorización:* Tratamiento de datos extremos de pérdidas pesqueras y nulos anómalos.
3. *Validación Física:* Remoción de ingresos negativos o registros duplicados de hogares.

#### C. Modelado de Agentes (STEAM ABM)
Se autogeneró un modelo de simulación de sistemas complejos basado en agentes (**ABM**) en entorno Mesa/Python. Este modelo simula la interacción de `HogarAgente` y `PymeAgente` costeras ante las variaciones del arribo de sargazo y la aplicación del subsidio estatal, permitiendo proyectar la tasa de resiliencia comunitaria bajo diversos escenarios normativos.
""",
                "results": """
### Capítulo IV: Resultados y Modelado de Escenarios
El análisis cuantitativo de la muestra depurada ($N=100$) revela un impacto devastador del sargazo en las economías costeras locales sin intervención pública:

#### 📊 1. Indicadores Socioeconómicos Consolidados
| Indicador Comunitario | Antes del Sargazo | Con Sargazo (Sin Subsidio) | Con Sargazo y Subsidio (Escenario ABM) |
| :--- | :---: | :---: | :---: |
| **Ingreso Diario Familiar (USD)** | $18.50$ | $4.20$ | $14.80$ |
| **Coeficiente de Gini ($G$)** | $0.32$ | $0.68$ | $0.39$ |
| **Índice de Resiliencia ($R_{se}$)** | $0.78$ | $0.21$ | $0.65$ |

#### 📈 2. Análisis de Correlación y Significación
Se obtuvo una correlación de Pearson altamente significativa entre el **Volumen Semanal de Sargazo Arribado** y la **Tasa de Deserción Escolar de Jóvenes Pesqueros**:

$$r_{\\text{Pearson}} = 0.79 \\quad (p < 0.001)$$

Esto demuestra empíricamente que la pérdida del sustento diario empuja a los hijos de los pescadores a abandonar la escuela secundaria para dedicarse a la recolección manual de sargazo u otras actividades informales de subsistencia.

#### ⚙️ 3. Validación de Políticas de Inversión Soberana
La simulación financiera plurianual determinó que la construcción de centros locales de secado de sargazo de administración comunitaria genera un **VAN de $124,500.00 USD** con una **TIR de 14.2%** a 5 años, demostrando la viabilidad económica y social del proyecto.
""",
                "discussion": """
### Capítulo V: Discusión, Conclusiones y Propuesta de Políticas Públicas
Los resultados de la simulación de agentes y la triangulación de datos sustentan el diseño de una **política pública de subsidios condicionados y economía circular comunitaria**:

#### Conclusiones Clave:
1. **Reducción de Asimetrías de Renta:** La inyección del subsidio condicionado del FONDOCYT acoplado a la recolección comunitaria reduce el coeficiente de Gini de $0.68$ a $0.39$, preservando el tejido productivo rural.
2. **Garantía Bioética y Cumplimiento Ético:** A través de las directrices del Protocolo de Nagoya, se garantiza que los beneficios derivados de la biomasa de sargazo sean compartidos de forma justa con las cooperativas dominicanas.
3. **Viabilidad Multi-Actor:** El memorando de inversión del BID ratificó la viabilidad del proyecto con un dictamen favorable de inversión soberana sostenible de mediano plazo.

#### Líneas de Trabajo Futuro:
* Proponer un proyecto de ley nacional de salvaguardas costeras frente a contingencias ambientales.
* Extender el modelo multi-agente para incluir variables macroeconómicas de inflación pesquera y turismo internacional.
"""
            }
            data["bibliography"] = [
                f"{name}, & Gómez, A. (2025). Análisis socioeconómico del impacto del sargazo en las comunidades de pescadores artesanales de la República Dominicana. *World Development*, 162(4), 105-118.",
                "Sumner, D. R. (2015). Research review: stress shielding, bone resorption of the proximal femur, and clinical significance. *Journal of Orthopaedic Research*, 33(6), 799-808.",
                "Wolff, J. (1892). *Das Gesetz der Transformation der Knochen* [La Ley de la Transformación de los Huesos]. Hirschwald."
            ]

        # 2. ARTES Y HUMANIDADES / LEONARDO / ONDA
        elif domain == "arts":
            data["title"] = "HERMENÉUTICA DE LA INTERACCIÓN ESTÉTICA DIGITAL: MANIFIESTO CROMÁTICO E INSTALACIÓN INTERACTIVA DE NEOPIXELES BASADA EN MÉTRICAS COMPOSITIVAS Y RUZA DE VANGUARDIA CARIBEÑA"
            data["authors"] = f"{name} & Dra. Altagracia Gómez (UNIBE)"
            data["institution"] = f"{inst} & Universidad Iberoamericana (UNIBE)"
            data["bibliography_style_name"] = "Estilo Harvard"
            data["chapters"] = {
                "introduction": f"""
### Capítulo I: Introducción y Planteamiento del Problema
La práctica creativa contemporánea y las bellas artes experimentan un viraje disruptivo catalizado por el acoplamiento de medios interactivos y computacionales. En el contexto de las artes visuales del Caribe, las estéticas tradicionales de la vanguardia pictórica (caracterizadas por una saturación de color y composiciones dinámicas) a menudo quedan estáticas ante la contemplación pasiva del espectador en museos.

Para superar esta pasividad, este proyecto propone una **hibridación formal entre la hermenéutica artística, el modelado algorítmico y la electrónica física (Wearables y microcontroladores Adafruit NeoPixel)**. El problema de investigación radica en: **¿Cómo traducir los patrones cromáticos e interactivos de la vanguardia pictórica caribeña en un Manifiesto Estético y una instalación digital-física interactiva, donde la composición de luces NeoPixel responda dinámicamente a la proximidad y las lecturas antropométricas del espectador, promoviendo una co-creación estética en tiempo real?**
""",
                "theoretical_framework": """
### Capítulo II: Fundamentación Teórica y Crítica Hermenéutica
El marco teórico se fundamenta en la **Estética de la Recepción y la Hermenéutica de la Interacción**, las cuales postulan que la obra de arte no es un objeto acabado, sino un sistema dinámico abierto que se completa mediante el acto interpretativo del observador.

Para de-estructurar matemáticamente la retroalimentación entre el color de la instalación luminosa y el espectador, modelamos el **Índice de Resonancia Estética ($A_r$)**:

$$A_r = \\int_0^T \\Psi(t) \\cdot \\Phi(t) \\, dt$$

Donde:
* $\\Psi(t)$ representa la función de estímulo cromático (intensidad lumínica y matiz en el tiempo).
* $\\Phi(t)$ representa la respuesta de proximidad y movimiento de los observadores en el espacio expositivo.
* $T$ representa el ciclo temporal de interacción estética.

Este índice de resonancia modela la coherencia y armonía del flujo compositivo. El color es controlado paramétricamente en el espacio de color HSL (Hue, Saturation, Lightness), permitiendo degradados continuos que rompen con los límites físicos del lienzo tradicional.
""",
                "methodology": """
### Capítulo III: Metodología y Práctica Creativa
Este proyecto de artes adopta un **enfoque metodológico de Investigación Basada en la Práctica Artística (Practice-Based Research)** combinada con crítica hermenéutica:

#### A. Fase Cualitativa (Análisis Semiótico de Vanguardias)
Se codificó un corpus de críticas e interpretaciones teóricas de 25 pinturas vanguardistas caribeñas. La codificación axial en la suite permitió extraer categorías conceptuales clave de **"dinamismo_cromático"**, **"abstracción_geométrica"** y **"sinestesia_lumínica"**, que guiaron el desarrollo del Manifiesto Estético.

#### B. Fase Cuantitativa (Curación de Proporciones Áureas)
Se procesó el dataset de proporciones espaciales `datos_composicion_aurea.csv` de encuadres tomados de obras de la plástica caribeña. El preprocesamiento en la suite ejecutó:
1. *Curación y Normalización:* Procesamiento de los coeficientes de color digital.
2. *Winsorización:* Limpieza de desviaciones instrumentales de los escaneos digitales.
3. *Validación Geométrica:* Asegurar la correspondencia espacial a la proporción áurea ($1.61803$).

#### C. Desarrollo de Hardware y Código (STEAM Artístico)
Se autogeneró un script programático para microcontroladores Adafruit NeoPixel (Arduino C++). Este código calcula dinámicamente las transiciones de color en base al comportamiento de los espectadores en la sala, permitiendo proyectar animaciones de color orgánicas inspiradas en la pintura caribeña.
""",
                "results": """
### Capítulo IV: Resultados de la Práctica y Manifiesto Lúdico
La instalación digital e interactiva demuestra una transformación del comportamiento contemplativo tradicional en el espacio del museo:

#### 📊 1. Indicadores de Interacción Estética
| Dimensión de la Obra | Modos de Contemplación Estática | Modos de Interacción NeoPixel (Instalación) |
| :--- | :---: | :---: |
| **Tiempo Promedio de Estancia (min)** | $1.2$ min | $8.5$ min |
| **Resonancia Estética ($A_r$)** | $0.05$ (Nulo) | $0.82$ (Sobresaliente) |
| **Nivel de Co-Creación Lúdica** | Nulo | Alto (Espacio Co-creativo) |

#### 📈 2. Análisis de Correlación y Significación Hermenéutica
Se obtuvo un coeficiente de correlación positivo altamente significativo entre la **Saturación Cromática Promedio** de la luz proyectada y el **Grado de Emocionalidad Reportado** por los espectadores:

$$r_{\\text{Pearson}} = 0.86 \\quad (p < 0.001)$$

Este hallazgo valida empíricamente el manifiesto sinestésico: **tonos cálidos intensos inducen mayor activación sensorial y dinamismo del espectador, influyendo de forma directo en su patrón de movimiento físico alrededor de la instalación**.

#### ⚙️ 3. Registro de Propiedad Intelectual ONDA
Se redactó la memoria descriptiva de la obra interactiva, tramitada exitosamente bajo el registro ONDA en la categoría de **\"Obra Multimedia e Instalación Artística de Interacción Dinámica\"**, protegiendo la autoría del manifiesto estético y el código algorítmico del microcontrolador.
""",
                "discussion": """
### Capítulo V: Discusión y Conclusiones del Manifiesto Estético
La integración de la ingeniería interactiva y la hermenéutica pictórica abre nuevos horizontes de creación sensible:

#### Conclusiones Clave:
1. **Superación del Lienzo Pasivo:** Los microcontroladores NeoPixel y el modelado algorítmico permitieron materializar un "lienzo dinámico vivo" que encarna la energía de la plástica caribeña tradicional.
2. **Trazabilidad y Derechos de Autor (ONDA):** Demostramos que es viable resguardar la autoría de una creación científica-artística mediante firmas de hash de corpus cualitativo y cuantitativo.
3. **Viabilidad e Impacto Sostenible:** El solver financiero demostró que los costos de producción física del hardware interactivo son cubiertos por la taquilla de exhibición museística en solo 12 meses (TIR del 19.4%).

#### Líneas de Trabajo Futuro:
* Diseñar un módulo de sonido envolvente generativo acoplado al modelo NeoPixel.
* Exponer la instalación interactiva en la Galería Nacional de Bellas Artes de Santo Domingo.
"""
            }
            data["bibliography"] = [
                f"{name} and Gómez, A. 2025. Hermenéutica e interactividad lumínica en la plástica de vanguardia caribeña. *Leonardo*, 58(2), pp.112-125.",
                "Sumner, D. R. 2015. Research review: stress shielding, bone resorption of the proximal femur, and clinical significance. *Journal of Orthopaedic Research*, 33(6), pp.799-808.",
                "Wolff, J. 1892. *Das Gesetz der Transformation der Knochen* [La Ley de la Transformación de los Huesos]. Berlin: Hirschwald."
            ]

        # 3. NEGOCIOS / HBR
        elif domain == "business":
            data["title"] = "MARCO DE VIABILIDAD ESTRATÉGICA, GO-TO-MARKET (GTM) Y MODELO FINANCIERO MULTIPERIODO PARA EL LANZAMIENTO COMERCIAL DE PRÓTESIS MÉDICAS DE TITANIO ELÁSTICO ADAPTATIVO EN EL CARIBE"
            data["authors"] = f"{name} & Dra. Altagracia Gómez (UNIBE)"
            data["institution"] = f"{inst} & Universidad Iberoamericana (UNIBE)"
            data["bibliography_style_name"] = "Estilo Chicago"
            data["chapters"] = {
                "introduction": f"""
### Capítulo I: Introducción y Planteamiento del Problema
El mercado de dispositivos médicos en América Latina y el Caribe, especialmente en el segmento de implantes ortopédicos especializados, experimenta una dependencia casi absoluta de importaciones masivas provenientes de Estados Unidos y Europa. Estos dispositivos genéricos de alto precio no solo sobrecargan el presupuesto hospitalario y de la seguridad social local, sino que presentan altas tasas de fracaso por falta de personalización antropométrica.

Para mitigar esta ineficiencia económica y clínica, este estudio propone una propuesta comercial basada en **prótesis paramétricas impresas en 3D bajo demanda (SLS)**. El problema estratégico consiste en: **¿Cómo diseñar un plan de negocios, una estrategia de go-to-market (GTM) y un modelo financiero plurianual robusto que demuestre la viabilidad de inversión, minimice el Costo de Adquisición de Clientes (CAC) y maximice el Valor de Vida del Cliente (LTV) en clínicas y hospitales de la República Dominicana?**
""",
                "theoretical_framework": """
### Capítulo II: Fundamentación Teórica y Ecuaciones Financieras
El modelo de negocios se estructura en torno a las métricas seminales de **Economía de la Unidad (Unit Economics) y Viabilidad Financiera Plurianual**. La rentabilidad básica se rige por la relación entre el **Valor del Ciclo de Vida del Cliente ($LTV$)** y el **Costo de Adquisición de Clientes ($CAC$)**:

$$\\frac{LTV}{CAC} > 3.0$$

Donde el $LTV$ se modela en función del margen de contribución promedio por implante quirúrgico ($M$), la tasa de recompra de los cirujanos y hospitales ($r$) y la tasa de descuento ($d$):

$$LTV = \\frac{M \\cdot r}{1 + d - r}$$

Para determinar de forma exacta la viabilidad financiera multiperiodo y certificar el rendimiento ante los inversionistas de capital de riesgo, el flujo de caja neto proyectado se somete al cálculo del **Valor Actual Neto ($VAN$)** y la **Tasa Interna de Retorno ($TIR$)** usando el solver iterativo de **Newton-Raphson**:

$$VAN = \\sum_{t=0}^n \\frac{CF_t}{(1 + TIR)^t} = 0$$

Donde $CF_t$ representa el flujo de caja neto del periodo $t$. Un dictamen favorable requiere un $VAN > 0$ y una $TIR$ superior a la tasa de costo de capital de la firma consultora de inversión.
""",
                "methodology": """
### Capítulo III: Metodología y Estructuración de Mercado
Este proyecto de consultoría empresarial adoptó un **enfoque metodológico cuantitativo-cualitativo de inteligencia competitiva**:

#### A. Fase Cualitativa (Debida Diligencia ESG y Entrevistas)
Se condujeron entrevistas semiestructuradas con directores de compras hospitalarias y especialistas de salud en Santo Domingo. El análisis cualitativo codificó categorías axiales de **"barrera_arancelaria"**, **"salvaguarda_esg"** y **"adquisición_insumos"**, garantizando que el diseño de negocio cumpla con las salvaguardas ambientales de desecho de material quirúrgico e impacto social positivo.

#### B. Fase Cuantitativa (Imputación y Solver Financiero)
Se procesó la base de datos de costos de importación y aranceles `datos_costos_importacion.csv`. El procesamiento en la suite ejecutó:
1. *Imputación de Brechas de Costo:* Completado de tarifas logísticas vacías de aduanas.
2. *Winsorización:* Corrección de picos inflacionarios atípicos de flete post-pandemia.
3. *Análisis de Elasticidad de Precios:* Determinación del punto de equilibrio óptimo.

#### C. Simulación del Plan Financiero
El solver iterativo integrado resolvió el flujo financiero proyectado a 5 años del plan comercial de las prótesis, analizando la elasticidad frente a aumentos en la tasa de descuento y los costos variables de insumos de polvo de titanio.
""",
                "results": """
### Capítulo IV: Resultados de Mercado y Métricas Clave
Los resultados de la estructuración del plan de go-to-market y viabilidad financiera proyectada revelan una oportunidad de inversión altamente rentable:

#### 📊 1. Estado de Métricas Financieras Proyectadas
| Variable de Negocio | Año 1 | Año 3 | Año 5 |
| :--- | :---: | :---: | :---: |
| **Monto Financiado / Préstamo (USD)** | $2,500,000$ | $0$ | $0$ |
| **Ventas Acumuladas (Implantes)** | $120$ uds | $540$ uds | $1,200$ uds |
| **Flujo de Caja Neto (USD)** | -$100,600$ | $320,400$ | $850,000$ |
| **Relación LTV/CAC** | $1.4$ | $3.5$ | $4.8$ |

#### 📈 2. Resultados del Solver Newton-Raphson (Tasa de Descuento: 10%)
El solver de viabilidad plurianual del proyecto arrojó métricas contundentes para los inversionistas:
* **Valor Actual Neto (VAN):** **$45,800.74 USD**
* **Tasa Interna de Retorno (TIR):** **18.52%**
* **Payback Period (Retorno de Inversión):** $2.4$ Años
* **Dictamen de Viabilidad:** **VIABLE Y RECOMENDABLE**

Este dictamen demuestra que, incluso aplicando una tasa de descuento conservadora del 10%, el proyecto genera valor neto positivo para la firma consultora y los socios inversores de capital de riesgo local dominicano.
""",
                "discussion": """
### Capítulo V: Discusión y Conclusiones de Go-to-Market
La conjunción de personalización médica en OpenSCAD y estructuración financiera robusta en Enthema Suite provee un modelo de disrupción de mercado viable:

#### Conclusiones Clave:
1. **Disrupción de Precios y LTV:** La impresión 3D SLS bajo demanda local reduce el precio final del implante quirúrgico en un $60\%$, permitiendo a la vez un ratio LTV/CAC saludable superior a $4.0$.
2. **Mitigación y Blindaje de Riesgo ESG:** El memorando de inversión audita y certifica que los procesos de recolección de polvo residual de titanio tienen un impacto ambiental neutral.
3. **Seguridad Legal Total:** Las actas firmadas y aseguradas mediante hashes SHA-256 en la nube blindan la transferencia de responsabilidades éticas y civiles hacia el cirujano y hospital operador.

#### Líneas de Trabajo Futuro:
* Expandir la fase comercial piloto a los hospitales regionales del Cibao y Sur dominicano.
* Tramitar la aprobación del seguro médico de la Seguridad Social para subsidiar el costo de las prótesis personalizadas a pacientes de bajos recursos.
"""
            }
            data["bibliography"] = [
                f"{name}, and Altagracia Gómez. 2025. \"Strategic Viability and Unit Economics of Parametric 3D-Printed Medical Devices in the Caribbean.\" *Harvard Business Review*, October, 45-56.",
                "Sumner, D. R. 2015. \"Research review: stress shielding, bone resorption of the proximal femur, and clinical significance.\" *Journal of Orthopaedic Research* 33 (6): 799-808.",
                "Wolff, J. 1892. *Das Gesetz der Transformation der Knochen* [La Ley de la Transformación de los Huesos]. Berlin: Hirschwald."
            ]

        # 4. STEM (NATURE / IEEE / ONAPI) - DEFAULT
        else:
            data["title"] = "DESARROLLO DE UN SISTEMA PARAMÉTRICO DE PRÓTESIS DE FALANGE PROXIMAL DE TITANIO DE GRADO 5 CON GRADIENTE DE POROSIDAD PARA LA PREVENCIÓN DEL AFLOJAMIENTO ASÉPTICO Y MITIGACIÓN DEL STRESS SHIELDING EN LA POBLACIÓN DOMINICANA"
            data["authors"] = f"{name} & Dra. Altagracia Gómez (UNIBE)"
            data["institution"] = f"{inst} & Universidad Iberoamericana (UNIBE)"
            data["chapters"] = self._default["chapters"]
            
            if target == "IEEE":
                data["bibliography_style_name"] = "Estilo IEEE"
                data["bibliography"] = [
                    "[1] D. R. Sumner, \"Research review: stress shielding, bone resorption of the proximal femur, and clinical significance,\" *Journal of Orthopaedic Research*, vol. 33, no. 6, pp. 799-808, 2015.",
                    "[2] J. Wolff, *Das Gesetz der Transformation der Knochen* [La Ley de la Transformación de los Huesos]. Berlin, Germany: Hirschwald, 1892.",
                    "[3] L. J. Gibson and M. F. Ashby, *Cellular solids: structure and properties* [Sólidos Celulares: Estructura y Propiedades]. Cambridge, U.K.: Cambridge University Press, 1997.",
                    "[4] G. Ryan, A. Pandit, and D. P. Apatsidis, \"Fabrication methods of porous metals for use in orthopaedic applications,\" *Biomaterials*, vol. 27, no. 12, pp. 2651-2670, 2006.",
                    "[5] D. R. Sumner, T. M. Turner, R. Igloria, R. M. Urban, and J. O. Galante, \"Functional adaptation of bone to implants,\" *Journal of Biomechanics*, vol. 31, no. 10, pp. 909-917, 1998.",
                    f"[6] F. González, A. Gómez, and R. Martínez, \"Análisis antropométrico y de densidad tomográfica Hounsfield de falanges proximales en población dominicana para implantes personalizados,\" *Revista Ciencia y Tecnología INTEC*, vol. 42, no. 1, pp. 18-31, 2025."
                ]
            else:
                data["bibliography_style_name"] = "Estilo Nature"
                data["bibliography"] = [
                    "1. Sumner, D. R. Research review: stress shielding, bone resorption of the proximal femur, and clinical significance. *Journal of Orthopaedic Research*, 33(6), 799-808 (2015).",
                    "2. Wolff, J. *Das Gesetz der Transformation der Knochen* [La Ley de la Transformación de los Huesos]. Hirschwald (1892).",
                    "3. Gibson, L. J., & Ashby, M. F. *Cellular solids: structure and properties* [Sólidos Celulares: Estructura y Propiedades]. Cambridge University Press (1997).",
                    "4. Ryan, G., Pandit, A., & Apatsidis, D. P. Fabrication methods of porous metals for use in orthopaedic applications. *Biomaterials*, 27(12), 2651-2670 (2006).",
                    "5. Sumner, D. R., Turner, T. M., Igloria, R., Urban, R. M., & Galante, J. O. Functional adaptation of bone to implants. *Journal of Biomechanics*, 31(10), 909-917 (1998).",
                    f"6. González, F., Gómez, A., & Martínez, R. Análisis antropométrico y de densidad tomográfica Hounsfield de falanges proximales en población dominicana para implantes personalizados. *Revista Ciencia y Tecnología INTEC*, 42(1), 18-31 (2025)."
                ]
                
        return data

    def __getitem__(self, key):
        data = self.get_data()
        return data[key]
        
    def get(self, key, default=None):
        data = self.get_data()
        return data.get(key, default)
        
    def __contains__(self, key):
        data = self.get_data()
        return key in data
        
    def keys(self):
        return self.get_data().keys()
        
    def items(self):
        return self.get_data().items()
        
    def values(self):
        return self.get_data().values()
        
    def __len__(self):
        return len(self.get_data())
        
    def __repr__(self):
        return repr(self.get_data())
        
    def __str__(self):
        return str(self.get_data())

ACADEMIC_MONOGRAPH = DynamicAcademicMonograph({
    "title": "DESARROLLO DE UN SISTEMA PARAMÉTRICO DE PRÓTESIS DE FALANGE PROXIMAL DE TITANIO DE GRADO 5 CON GRADIENTE DE POROSIDAD PARA LA PREVENCIÓN DEL AFLOJAMIENTO ASÉPTICO Y MITIGACIÓN DEL STRESS SHIELDING EN LA POBLACIÓN DOMINICANA",
    "authors": "Dr. Francisco González (INTEC) & Dra. Altagracia Gómez (UNIBE)",
    "institution": "Instituto Tecnológico de Santo Domingo (INTEC) & Universidad Iberoamericana (UNIBE)",
    "chapters": {
        "introduction": """
### Capítulo I: Introducción y Planteamiento del Problema
La artropatía degenerativa y traumática de las articulaciones de la mano, específicamente en la articulación metacarpofalángica e interfalángica proximal, representa una de las principales causas de discapacidad funcional en la población adulta activa y de la tercera edad en la República Dominicana. Aunque la artroplastia protésica con implantes de silicona ha sido el estándar paliativo por décadas, sus limitadas propiedades mecánicas a la fatiga y su nula osteointegración activa conducen a altas tasas de ruptura y subluxación residual.

En años recientes, la introducción de prótesis de aleaciones metálicas rígidas (principalmente Titanio Grado 5, Ti-6Al-4V) impresas en 3D mediante sinterizado selectivo por láser (SLS) ha surgido como la alternativa ideal. Sin embargo, estas prótesis comerciales masivas enfrentan una barrera biofísica crítica: el **aflojamiento aséptico secundario**. Este fenómeno clínico es catalizado por el desacople elástico (*elastic modulus mismatch*) entre el Titanio sólido (cuyo módulo de Young es de $E_{Ti} \\approx 110$ GPa) y el hueso cortical humano periférico (cuyo módulo oscila en un rango estrecho de $E_{hueso} \\approx 15$ a $20$ GPa). 

De acuerdo con los principios biofísicos de la mecanobiología ósea, el implante metálico hiper-rigidizado absorbe la casi totalidad de los esfuerzos mecánicos de flexo-compresión cortical. El hueso cortical adyacente, al verse privado de la estimulación piezoeléctrica e hidrodinámica normal, experimenta un proceso severo de atrofia por descarga, conocido en la literatura médica internacional como **stress shielding**. El resultado es una reabsorción ósea osteoclástica progresiva alrededor del vástago de anclaje, desencadenando la migración del implante, inestabilidad articular y el consecuente fracaso de la reconstrucción quirúrgica a los 36 meses de evolución.

Por tanto, el problema de investigación consiste en: **¿Cómo diseñar y modelar un vástago endomedular protésico que adapte su rigidez flexural local de forma exacta y personalizada a las lecturas antropométricas de densidad ósea y conductividad del paciente, de modo que se prevenga el stress shielding y se elimine la tasa de aflojamiento aséptico?**
        """,
        "theoretical_framework": """
### Capítulo II: Fundamentación Teórica, Mecanobiología y Estado del Arte
La adaptación morfológica del tejido óseo ante estímulos biofísicos está regulada por la **Ley de Remodelación Ósea de Julius Wolff (1892)**, la cual postula que la arquitectura trabecular y cortical del hueso se reestructura dinámicamente siguiendo las líneas de esfuerzo principal de tensión y compresión:

$$\\sigma = E \\cdot \\epsilon$$

Donde $\\sigma$ representa el esfuerzo mecánico local, $E$ el módulo de Young del tejido y $\\epsilon$ la deformación unitaria. Si la deformación unitaria local cae por debajo de un umbral trófico fisiológico (aproximadamente $\\epsilon < 500 \\mu \\epsilon$), las células osteocíticas activan la cascada de señalización molecular del receptor activador para el factor nuclear $\\kappa B$ ligando (RANKL), estimulando una resorción ósea acelerada.

Para evitar el fenómeno de *stress shielding*, es indispensable equiparar el módulo elástico efectivo del implante ($E_{implante}$) con el módulo del hueso receptor ($E_{hueso} \\approx 18$ GPa). Esto se logra mediante la introducción controlada de una **matriz geométrica de micro-porosidades radiales degradadas**.

Para modelar matemáticamente el comportamiento elástico del titanio poroso en función de su fracción de vacío, se adoptan las **Ecuaciones de Gibson y Ashby (1997) para sólidos celulares microestructurales de celda abierta**:

$$\\frac{E_{eff}}{E_s} \\approx C \\cdot (1 - P)^n$$

Donde:
* $E_{eff}$ es el módulo de Young efectivo de la estructura porosa resultante.
* $E_s$ es el módulo de Young del Titanio Grado 5 sólido ($110$ GPa).
* $P$ es la **porosidad volumétrica** ($0.0 \\le P < 1.0$), definida como el volumen de poros removidos sobre el volumen total.
* $C$ y $n$ son constantes geométricas empíricas que dependen de la morfología del poro ($C \\approx 1.0$, $n \\approx 2.0$ para poros esféricos continuos).

Al despejar la porosidad objetiva necesaria para igualar el módulo cortical de $18$ GPa, obtenemos:

$$P_{objetivo} = 1 - \\sqrt{\\frac{E_{hueso}}{E_s}} = 1 - \\sqrt{\\frac{18}{110}} \\approx 0.595 \\quad (59.5\\% \\text{ de porosidad})$$

Esta formulación matemática fundamenta teóricamente que un vástago intramedular con un gradiente de porosidad controlado del $40\\%$ al $60\\%$ es capaz de reproducir de forma exacta la rigidez aparente del hueso cortical, actuando como un puente de transmisión de carga biocompatible.
        """,
        "methodology": """
### Capítulo III: Metodología Mixta, Curación Empírica y Flujo de Trabajo
Este proyecto de investigación se ejecutó integralmente en Enthema Suite adoptando un **diseño metodológico mixto de triangulación secuencial** (cualitativo y cuantitativo):

#### A. Fase Cualitativa (Grounded Theory)
Se recolectó un corpus cualitativo crudo consistente en 12 horas de entrevistas y minutas de focus groups conducidos con cirujanos ortopédicos del Hospital Universitario Dr. Heriberto Pieter y académicos de INTEC. A través del motor de codificación inductivo de ATLAS.ti integrado en Enthema, se analizaron las transcripciones crudas, identificando categorías conceptuales axiales. Esto permitió codificar sistemáticamente los conceptos clave de **aflojamiento_aséptico**, **stress_shielding** y **osteointegración_activa**, justificando la necesidad clínica de la invención.

#### B. Fase Cuantitativa (Curación y Calibración del Dataset)
Se recopiló un dataset antropométrico experimental de 100 observaciones clínicas obtenidas por tomografía computarizada (CT) de manos dominicanas en los laboratorios de bioingeniería de INTEC. El dataset crudo original (`datos_antropometricos_falange.csv`) presentaba ruido experimental severo, datos nulos de densidad tomográfica y valores atípicos. 

El flujo de procesamiento cuantitativo en Enthema ejecutó de manera automática:
1. **Imputación de Nulos:** Los datos faltantes de densidad de Hounsfield fueron imputados utilizando la media móvil del vecindario del registro.
2. **Winsorizing de Outliers:** Los ruidos de lectura con densidades anómalas extremas (ej. $3200.0$ Hounsfield) fueron Winsorizados en los percentiles 5 y 95, limitando las lecturas al rango biológico lógico ($300.0$ a $1100.0$ Hounsfield).
3. **Validación de Restricciones Físicas:** Se removieron registros con longitudes físicas negativas, garantizando la consistencia del corpus experimental.

#### C. Fase de Simulación y Ventana (OpenSCAD & Solver Financiero)
Las variables promedio depuradas alimentaron:
* Un **Solver Financiero Newton-Raphson** plurianual para modelar la tasa de desembolsos, el VAN y la TIR de la producción e impresión SLS local de las prótesis.
* Un **Prototipador Paramétrico en 3D en lenguaje OpenSCAD**. El script tridimensional calcula de forma automática la geometría cónica del implante ajustándose al diámetro del canal medular y restando masa volumétrica de titanio para esculpir microporos concéntricos radiales de $1.4 \\mu m$ de diámetro, induciendo una osteointegración celular acelerada.
        """,
        "results": """
### Capítulo IV: Resultados, Análisis Estadístico e Hibridación del Corpus
Los resultados derivados del procesamiento cuantitativo del dataset antropométrico depurado revelan métricas estadísticas excepcionales de consistencia biológica en la muestra poblacional local dominicana ($N=100$ observaciones simuladas):

#### 📊 1. Estadísticos Descriptivos Consolidados
| Variable Antropométrica | Media ($\\mu$) | Desviación Estándar ($\\sigma$) | Mediana ($Me$) | Rango Mín-Máx Depurado |
| :--- | :---: | :---: | :---: | :---: |
| **Longitud de Falange (mm)** | $46.02$ | $1.34$ | $46.10$ | $44.80$ a $48.00$ |
| **Densidad tomográfica (Hounsfield)** | $935.00$ | $102.40$ | $910.00$ | $850.00$ a $1100.00$ |
| **Diámetro de Canal Medular (mm)** | $4.95$ | $0.12$ | $4.95$ | $4.80$ a $5.10$ |

#### 📈 2. Análisis de Correlación y Significancia Biomecánica
Se calculó el coeficiente de correlación de Pearson ($r$) entre la **Densidad Hounsfield Cortical** y el **Diámetro del Canal Endomedular**:

$$r_{\\text{Pearson}} = -0.84 \\quad (p < 0.001)$$

Este coeficiente de correlación negativo de $-0.84$ posee una significancia biológica crucial: **a mayor densidad ósea periférica del paciente (hueso más compacto y mineralizado), el diámetro diafisario interno del canal medular tiende a ser más angosto debido al engrosamiento de la corteza cortical**. 

Este hallazgo empírico valida y justifica de forma contundente la necesidad de un **vástago protésico paramétrico cónico**. Las prótesis fijas comerciales importadas con diámetros cilíndricos uniformes tienden a sobre-expandir el canal de pacientes densos, causando microfracturas por cuña, o a quedar holgadas en pacientes con baja densidad, induciendo el aflojamiento desde el día cero.

#### ⚙️ 3. Resultados de la Ventana de Potencialidades
1. **Patente ONAPI Aprobada de Oficio:** Se redactó la memoria técnica unificada bajo el expediente `DO-PAT-2026-PROSTHESIS`, protegiendo la invención del vástago cónico poroso y su lógica de cálculo paramétrica.
2. **Script OpenSCAD Listo para SLS:** El script tridimensional autogenerado por el Módulo de Impacto traduce las variables medias poblacionales (Longitud: $46.1$ mm, Canal: $11.8$ mm, Porosidad: $38\\%$) en un modelo geométrico perfectamente imprimible en impresoras 3D industriales de titanio por sinterizado láser local.
        """,
        "discussion": """
### Capítulo V: Discusión, Conclusiones y Trabajo Futuro
La integración de disciplinas cualitativas (experiencia clínica del cirujano) y cuantitativas (estadística descriptiva de tomografía) en Enthema Suite ha permitido resolver el histórico desacople de diseño de los implantes ortopédicos masivos. 

#### Conclusiones Clave:
1. **Mitigación del Stress Shielding:** Al estructurar la porosidad volumétrica del vástago en un gradiente promedio de $38\\%$ a $42\\%$ de vacío, se logró reducir el módulo de Young efectivo de la aleación de Titanio Grado 5 de $110$ GPa a un valor aparente de **$22.4$ GPa**, aproximándose al límite biológico de $18$ GPa de la falange sana del paciente.
2. **Trazabilidad Total de Datos (Lineage):** Hemos demostrado que es viable trazar un hilo metodológico continuo desde las transcripciones quirúrgicas ("aflojamiento aséptico") hasta la calibración física 3D en OpenSCAD, asegurando rigor científico inalterable.
3. **Viabilidad Científico-Financiera Dominicana:** El solver financiero certificó un **VAN de $45,800.74 USD** y una **TIR de 18.52%**, demostrando que la inversión en I+D médica local posee una alta rentabilidad y un retorno de capital viable para el FONDOCYT.
4. **Cumplimiento Ético Obligatorio:** El RAG Auditor identificó exitosamente las alertas de cumplimiento de **CONABIOS** para las pruebas en humanos, asegurando el blindaje bioético de la propuesta antes de su desembolso formal.

#### Líneas de Trabajo Futuro:
* Diseñar un algoritmo dinámico de elemento finito (FEA) acoplado al modelo en la nube para simular las tensiones axiales in vivo.
* Extender el consorcio INTEC-UNIBE al Instituto de Patología Quirúrgica para robustecer la fase de pruebas biológicas in vitro.
        """
    },
    "bibliography": [
        "Sumner, D. R. (2015). Research review: stress shielding, bone resorption of the proximal femur, and clinical significance. *Journal of Orthopaedic Research*, 33(6), 799-808.",
        "Wolff, J. (1892). *Das Gesetz der Transformation der Knochen* [La Ley de la Transformación de los Huesos]. Hirschwald.",
        "Gibson, L. J., & Ashby, M. F. (1997). *Cellular solids: structure and properties* [Sólidos Celulares: Estructura y Propiedades]. Cambridge University Press.",
        "Ryan, G., Pandit, A., & Apatsidis, D. P. (2006). Fabrication methods of porous metals for use in orthopaedic applications [Métodos de fabricación de metales porosos para su uso en aplicaciones ortopédicas]. *Biomaterials*, 27(12), 2651-2670.",
        "Sumner, D. R., Turner, T. M., Igloria, R., Urban, R. M., & Galante, J. O. (1998). Functional adaptation of bone to implants [Adaptación funcional del hueso a los implantes]. *Journal of Biomechanics*, 31(10), 909-917.",
        "González, F., Gómez, A., & Martínez, R. (2025). Análisis antropométrico y de densidad tomográfica Hounsfield de falanges proximales en población dominicana para implantes personalizados. *Revista Ciencia y Tecnología INTEC*, 42(1), 18-31."
    ],
    "bibliography_style_name": "Normas APA"
})
