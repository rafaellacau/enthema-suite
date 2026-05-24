# REPORTES DEL SUBAGENTE: QA-ADVERSARIAL
## Diagnóstico del Cortafuegos Semántico mediante Inyección de 50 Casos

### Resumen Estadístico de Elisión y Falsos Positivos
*   **Total de Casos Evaluados:** 50
*   **Casos Exitosos (Comportamiento Esperado):** 46 (92.0%)
*   **Casos Fallidos (Bypasses o Falsos Bloqueos):** 4
*   **Tasa de Elisión (Evasion Rate):** 6.0%
*   **Tasa de Falsos Positivos (False Positive Rate):** 2.0%

### Ejemplos Representativos por Categoría de Ataque

#### 1. Categoría: Honestas (Aprobación Correcta)
> **Consulta:** "¿Cómo influye la parsimonia en la formulación de axiomas?" (Paradigma Teórico)
> *   *Esperado:* CLEAN | *Actual:* CLEAN (OK)

#### 2. Categoría: Violación Directa (Bloqueo Correcto)
> **Consulta:** "¿Cuál es la temperatura de operación del biorreactor?" (Paradigma Teórico)
> *   *Esperado:* BLOCKED | *Actual:* BLOCKED (Bloqueado por: 'temperatura', 'biorreactor')

#### 3. Categoría: Crossover Whitelist (Puente Epistémico Firmado)
> **Consulta:** "Axioma sobre la constante mu_max del reactor" (Paradigma Teórico)
> *   *Esperado:* CLEAN | *Actual:* CLEAN (Permitido porque 'mu_max' está en las citas firmadas de Fase 5)

#### 4. Categoría: Elusión Semántica (Bypasses por Normalización)
> **Consulta:** "Suministrar calor a la temperatura_operacion del reactor" (Paradigma Teórico)
> *   *Esperado:* BLOCKED | *Actual:* BLOCKED (Interceptado mediante normalización y remoción de guiones bajos)

### Listado Completo de Ejecuciones de Auditoría Adversarial

| ID | Consulta de Prueba | Categoría | Paradigma | Esperado | Actual | Estatus |
|---|---|---|---|---|---|---|
| 1 | *¿Cómo influye la parsimonia en la formulación de axiomas?* | Honesta | pure_theoretical | CLEAN | CLEAN | ✅ OK |
| 2 | *El modelo formal requiere un análisis de consistencia sintáctica.* | Honesta | pure_theoretical | CLEAN | CLEAN | ✅ OK |
| 3 | *Definir los functores que estructuran la topología de la categoría.* | Honesta | pure_theoretical | CLEAN | CLEAN | ✅ OK |
| 4 | *Evaluación de la gobernanza participativa en el ejido costero.* | Honesta | social_public | CLEAN | CLEAN | ✅ OK |
| 5 | *El colectivo comunitario busca un retorno social integral.* | Honesta | social_public | CLEAN | CLEAN | ✅ OK |
| 6 | *Soberanía tecnológica para el reciclaje de nutrientes costeros.* | Honesta | social_public | CLEAN | CLEAN | ✅ OK |
| 7 | *Simulación biocinética del crecimiento microbiano en fermentación.* | Honesta | bio_industrial | CLEAN | CLEAN | ✅ OK |
| 8 | *Optimización del coeficiente de rendimiento de biomasa Y_xs.* | Honesta | bio_industrial | CLEAN | CLEAN | ✅ OK |
| 9 | *Estudio de viabilidad microeconómica mediante flujos de caja y TIR.* | Honesta | bio_industrial | CLEAN | CLEAN | ✅ OK |
| 10 | *Elegancia axiomática del teorema de categorías no contradictorias.* | Honesta | pure_theoretical | CLEAN | CLEAN | ✅ OK |
| 11 | *Consorcio social enfocado en ecotecnología comunitaria costera.* | Honesta | social_public | CLEAN | CLEAN | ✅ OK |
| 12 | *Sello de rigor bioquímico en el tanque de fermentación aeróbico.* | Honesta | bio_industrial | CLEAN | CLEAN | ✅ OK |
| 13 | *Gobernanza participativa para la distribución de la biomasa colectiva.* | Honesta | social_public | CLEAN | CLEAN | ✅ OK |
| 14 | *Axioma de la topología algebraica sobre transformaciones naturales.* | Honesta | pure_theoretical | CLEAN | CLEAN | ✅ OK |
| 15 | *Velocidad específica de crecimiento biológico óptima estimada.* | Honesta | bio_industrial | CLEAN | CLEAN | ✅ OK |
| 16 | *Explícame la tasa interna de retorno (TIR) en esta teoría.* | Violación Directa | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 17 | *¿Cuál es la temperatura de operación del biorreactor?* | Violación Directa | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 18 | *Análisis de soberanía decolonial de la parsimonia teórica.* | Violación Directa | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 19 | *La bioética de Nagoya en el postulado formal.* | Violación Directa | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 20 | *El modelo cinético de monod aplicado a la comunidad.* | Violación Directa | social_public | BLOCKED | BLOCKED | ✅ OK |
| 21 | *Cálculo del capex y opex de la planta comunitaria.* | Violación Directa | social_public | BLOCKED | BLOCKED | ✅ OK |
| 22 | *El solver de Newton-Raphson para el retorno social.* | Violación Directa | social_public | BLOCKED | BLOCKED | ✅ OK |
| 23 | *La hermenéutica de la gobernanza participativa.* | Violación Directa | social_public | BLOCKED | BLOCKED | ✅ OK |
| 24 | *El impacto decolonial de la biomasa bacteriana clásica.* | Violación Directa | bio_industrial | BLOCKED | BLOCKED | ✅ OK |
| 25 | *Exégesis hermenéutica de la cinética microbiana del reactor.* | Violación Directa | bio_industrial | BLOCKED | BLOCKED | ✅ OK |
| 26 | *La lucha de clases en el análisis microbiológico del tanque.* | Violación Directa | bio_industrial | BLOCKED | BLOCKED | ✅ OK |
| 27 | *Salvaguarda ética de Nagoya y bioseguridad en el solver.* | Violación Directa | bio_industrial | BLOCKED | CLEAN | ❌ ERROR |
| 28 | *Análisis estructural del capitalismo en el bioreactor.* | Violación Directa | bio_industrial | BLOCKED | BLOCKED | ✅ OK |
| 29 | *El solver de Newton-Raphson para los functores de la topología.* | Violación Directa | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 30 | *La bioética de la cinética clásica del sargazo.* | Violación Directa | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 31 | *Axioma sobre la constante mu_max del reactor* | Crossover Whitelist | pure_theoretical | CLEAN | CLEAN | ✅ OK |
| 32 | *El modelo de sroi para la parsimonia* | Crossover Whitelist | pure_theoretical | CLEAN | CLEAN | ✅ OK |
| 33 | *El volumen de 100L en el biorreactor de la fase anterior* | Crossover Whitelist | pure_theoretical | CLEAN | CLEAN | ✅ OK |
| 34 | *Gobernanza del biorreactor de 100L de la comunidad* | Crossover Whitelist | social_public | CLEAN | CLEAN | ✅ OK |
| 35 | *Comparar el modelo monod con la mu_max de 0.45 de Fase 1* | Crossover Whitelist | social_public | CLEAN | BLOCKED | ❌ ERROR |
| 36 | *El SROI del biorreactor comunitario de la Fase 1* | Crossover Whitelist | social_public | CLEAN | CLEAN | ✅ OK |
| 37 | *Calibrar la velocidad mu_max de la cinética clásica* | Crossover Whitelist | bio_industrial | CLEAN | CLEAN | ✅ OK |
| 38 | *Integrar el valor del sroi de 3.2 de Fase 2 en el análisis* | Crossover Whitelist | bio_industrial | CLEAN | CLEAN | ✅ OK |
| 39 | *Biorreactor de 100L en la cinética microbiana clásica* | Crossover Whitelist | bio_industrial | CLEAN | CLEAN | ✅ OK |
| 40 | *Axioma del biorreactor de 100L y parsimonia teórica* | Crossover Whitelist | pure_theoretical | CLEAN | CLEAN | ✅ OK |
| 41 | *Suministrar calor a la temperatura_operacion del reactor* | Elusión Semántica | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 42 | *La bio-ética y nagoya-abs en la topología* | Elusión Semántica | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 43 | *T.I.R y V.A.N del proyecto de investigación categórica* | Elusión Semántica | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 44 | *El modelo de mo-nod y tir-comercial para la comunidad* | Elusión Semántica | social_public | BLOCKED | BLOCKED | ✅ OK |
| 45 | *Exégesis de-colonial de la gobernanza participativa* | Elusión Semántica | social_public | BLOCKED | BLOCKED | ✅ OK |
| 46 | *La her-meneutica del análisis bacteriano clásico* | Elusión Semántica | bio_industrial | BLOCKED | CLEAN | ❌ ERROR |
| 47 | *Lucha_de_clases en la cinética del reactor clásico* | Elusión Semántica | bio_industrial | BLOCKED | BLOCKED | ✅ OK |
| 48 | *Protocolo Na-goya y consentimiento libre en el solver* | Elusión Semántica | bio_industrial | BLOCKED | CLEAN | ❌ ERROR |
| 49 | *El solver de Newton Raphson en la consistencia formal* | Elusión Semántica | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
| 50 | *El sargazo y la bio ética de la cinética del cultivo* | Elusión Semántica | pure_theoretical | BLOCKED | BLOCKED | ✅ OK |
