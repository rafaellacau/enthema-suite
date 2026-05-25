# 🔬 La Paradoja del Puente de Citación y Fuga Epistémica (Epistemic Lineage Leak)

> **Respuesta de Ingeniería:** La convivencia entre la inmutabilidad histórica (**Snapshot Sandbox**) y el aislamiento ontológico (**Semantic Firewall**) genera una paradoja de control de I/O. Para resolverla sin incurrir en colapsos de usabilidad ni en elusiones semánticas, Enthema Suite v4.0 implementa un pipeline de procesamiento segregado y auditoría semántica post-hoc.
> **Código de Compliance:** LAW-HUM-007

---

## 🧭 Definición de la Paradoja

La paradoja del puente de citación se formula de la siguiente manera:
1. **La Necesidad del Investigador**: Al transitar de un paradigma a otro (ej. de Bio-Industrial a Teórico Puro), el científico requiere referenciar sus hallazgos previos (ej. *"Adoptamos el postulado de que el reactor de la Fase 1 opera con una cinética de Monod donde $\mu_{max} = 0.45 \text{ h}^{-1}$"*).
2. **La Grieta de Control (I/O)**:
   - **Si el Cortafuegos es Estricto**: Detecta términos vedados del paradigma anterior (*reactor, Monod, h⁻¹*) y bloquea la monografía de la Fase 2, destruyendo la usabilidad y la continuidad de la investigación.
   - **Si el Cortafuegos es Permisivo**: Permite la entrada de estos términos bajo tags de citación (ej. `[Cita: Fase 1]`). Sin embargo, al inyectar este borrador en la ventana de contexto del LLM para el AI Coach, el modelo lee dichos tokens físicos y matemáticos y los asimila estadísticamente en sus sugerencias cognitivas, provocando una **deriva epistémica destructiva (Epistemic Drift)**.

---

## 🛡️ Arquitectura de Solución: El Pipeline Segregado de Enthema

Para resolver de manera absoluta esta filtración ontológica, la ingeniería de Enthema Suite implementa un protocolo de seguridad en cuatro capas:

```
        BORRADOR DEL CIENTÍFICO (Fase 2 - Teórico Puro)
   "Adoptamos el postulado de que [Cita: Fase 1] μ_max = 0.45 h^-1 [/Cita]..."
                               │
                               ▼
        1. LEXICAL TOKEN PARSER & STRIPPER (Regex/AST)
   - Extrae el bloque citado: "[Cita: Fase 1] ... [/Cita]"
   - Envía al AI Coach un contexto SANITIZADO (sin tokens físicos prohibidos)
                               │
                               ▼
            2. SEGREGATED ATTENTION BOUNDING (FASTAPI)
   - El AI Coach genera recomendaciones basándose únicamente en el borrador limpio.
   - La cita se archiva como metadato inmutable de sólo lectura en el AppState.
                               │
                               ▼
            3. POST-HOC LEXICAL AUDITOR (LÉXICO PROHIBIDO)
   - Un segundo modelo de validación ligero (o validador AST) escanea la respuesta del Coach.
   - Si la salida contiene términos prohibidos de la lista negra de la Fase 2, 
     el output es rechazado y se regenera.
                               │
                               ▼
                   SALIDA SEGURA Y AUDITADA
```

### 1. Aislamiento Léxico por Parser de Tokens (Lexical Token Parser)
El borrador del investigador pasa por un preprocesador dinámico antes de ser enviado a la API de inferencia del AI Coach. Este parser identifica bloques envueltos en etiquetas estructuradas de citación:
* `[Cita: Fase X] ... [/Cita]`
El contenido dentro de estas etiquetas se **remueve temporalmente** de la cadena de texto enviada al motor generativo del AI Coach para co-autoría, o se sustituye por un token abstracto inocuo (ej. `[ANTECEDENTE_F1_ANCLADO]`). De este modo, los términos prohibidos física y matemáticamente no entran a la ventana de atención primaria del LLM, eliminando de raíz la elusión semántica.

### 2. Bounded Context por Fases de AppState
Los paradigmas en Enthema Suite no comparten bases de datos mutables en caliente. La transición de paradigma congela la fase como un Snapshot Sandbox en modo de **sólo lectura (read-only)**. Las variables importadas se archivan como metadatos indexados bajo firma criptográfica **SHA-256**. El AI Coach tiene prohibido leer directamente el historial conversacional o los archivos de RAG de la fase anterior; cualquier referencia pasa estrictamente por la API de Citación Segura.

### 3. Auditor Léxico Post-Hoc (Post-hoc Lexical Auditor)
Tras la inferencia del AI Coach, la salida del modelo pasa por un pipeline de validación compuesto por una llamada asíncrona a un validador léxico. Este validador contrasta la propuesta del Coach contra el `forbidden_lexicon()` del paradigma activo. Si el modelo alucinó categorías de la fase 1 impulsado por las citas, el auditor detecta la contaminación cruzada, bloquea la salida y fuerza una regeneración con penalización de temperatura o notifica al usuario del desvío ontológico.

---

## 🧭 Criterios de Validez y Auditoría Epistémica

Para certificar que un proyecto cumple con la norma **LAW-HUM-007**, la Matriz de Auditoría verifica en su Capa 1 y Capa 3:
* **[ ] Parser Activo**: Confirmación de que el pipeline de sanitización léxica intermedia procesa todas las llamadas de API de co-autoría.
* **[ ] Inmutabilidad de Citación**: Verificación de que el hash SHA-256 del antecedente citado coincide exactamente con el commit de la fase previa archivada.
* **[ ] No-Inferencia Cruzada**: El AI Coach nunca debe sugerir fórmulas físicas (ej. Monod) en fases puramente teóricas o hermenéuticas, incluso si estas son citadas exhaustivamente por el investigador.
