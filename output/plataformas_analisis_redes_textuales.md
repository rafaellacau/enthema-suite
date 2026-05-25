# 🔍 InfraNodus y Plataformas de Análisis de Redes Textuales: Funcionamiento y Utilidad en Investigación

> **Alcance:** Explicación conceptual, metodológica y práctica de plataformas como InfraNodus para investigación cualitativa, análisis del discurso y ciencias sociales.  
> **Código de Compliance:** LAW-HUM-005  
> **Nota:** No es un tutorial técnico ni una reseña comercial. Es un marco para comprender su valor epistemológico y operativo en investigación académica y auditoría de IA.

---

## 🧭 ¿Qué es InfraNodus?

**InfraNodus** es una plataforma de análisis textual basada en **teoría de redes** y **grafos de conocimiento** que representa cualquier texto o corpus como una red visual donde:
- **Los nodos** = palabras, concepts o entidades clave (lematizadas).
- **Las aristas** = relaciones de co-ocurrencia en ventanas de contexto (típicamente de 4-gramas, es decir, palabras que aparecen juntas en un rango cercano).

El principio central es que las ideas y discursos no son listas lineales de palabras, sino redes de conceptos interconectados. Al mapear un texto como una red, podemos utilizar las herramientas matemáticas de la **ciencia de redes** (centralidad de intermediación, modularidad, análisis de comunidades de Louvain) para desvelar la estructura subyacente del pensamiento, identificar los temas dominantes y, lo más importante, detectar **brechas cognitivas (semantic/cognitive gaps)**.

---

## 🛠️ Conceptos Clave del Análisis de Redes Textuales

### 1. Co-ocurrencia y Pesos de Arista (Distance-based weights)
En el análisis textual infranodal, las aristas no son binarias; poseen pesos asociados a la cercanía sintáctica de los términos en el texto original:
- **Peso 3 (Adyacencia inmediata):** Las palabras están pegadas una al lado de la otra (0 palabras de separación).
- **Peso 2 (Distancia media):** Hay 1 palabra de separación entre los términos.
- **Peso 1 (Distancia lejana):** Hay 2 palabras de separación entre los términos.

Este gradiente permite al algoritmo ponderar con mayor fuerza las asociaciones explícitas y directas, separándolas de las relaciones incidentales de largo alcance.

### 2. Centralidad de Intermediación (Betweenness Centrality)
Los términos con alta centralidad de intermediación actúan como **nodos broker (puentes articuladores)**. No son necesariamente las palabras más frecuentes, sino aquellas que conectan diferentes comunidades de tópicos. En investigación científica, los brokers suelen representar conceptos interdisciplinares clave que integran distintas dimensiones del estudio (por ejemplo, cómo la *Zeolita Activada* conecta la química del reactor con el brote epidemiológico y la viabilidad financiera).

### 3. Detección de Comunidades (Algoritmo de Louvain)
El sistema agrupa los conceptos en clústeres basados en la densidad de sus conexiones internas en comparación con el resto de la red. Esto identifica de forma automatizada y objetiva los "tópicos de discurso" o comunidades semánticas que coexisten dentro del corpus, eliminando el sesgo heurístico del investigador.

### 4. Brechas Cognitivas (Cognitive Gaps) y Estructura del Discurso
InfraNodus se destaca por su capacidad para identificar **brechas estructurales** (structural holes). Si dos comunidades semánticas densas están completamente desconectadas o tienen muy pocas conexiones entre sí, el sistema detecta un "vacío semántico". Inyectar un concepto que actúe como puente entre estas comunidades (por ejemplo, conectar *Viabilidad Financiera* y *Gastroenteritis* a través de *Retorno Social SROI*) genera nuevas hipótesis de investigación y enriquece la coherencia global del estudio.

---

## 📥 Trazabilidad y Exportación de Redes Semánticas

Para cumplir con los rigores del método científico y la auditoría epistémica, los grafos semánticos deben poder exportarse para su replicación e inmutabilidad:
- **Exportación en CSV:** Genera una lista explícita de aristas con sus pesos de co-ocurrencia y atributos comunitarios para análisis estadísticos en R o Python.
- **Exportación en GEXF (Graph Exchange XML Format):** El estándar de la industria para importar redes en herramientas de visualización avanzadas como Gephi, permitiendo renderizados personalizados y cálculos a gran escala.
- **Exportación en JSON:** El volcado completo del estado de la red (nodos, coordenadas, comunidades y pesos), útil para persistencia y replicación inmutable bajo hashing SHA-256 en la suite de auditoría de Enthema.
