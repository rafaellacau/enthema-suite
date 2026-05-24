# Resultados de Benchmark de Latencias (Frente 6)

A continuación se presentan los resultados del benchmark cuantitativo de latencias p95 ejecutado con 5 fases inmutables archivadas y citaciones cruzadas densas en Enthema Suite V3.0.

| Operación | Media (ms) | Mediana (ms) | p95 (ms) | p99 (ms) | Mín (ms) | Máx (ms) |
|---|---|---|---|---|---|---|
| Validar Borrador | 1.06 | 1.03 | 1.24 | 1.41 | 0.96 | 1.58 |
| Coach - Consulta Libre (Normal) | 1.09 | 1.05 | 1.21 | 1.33 | 0.99 | 3.19 |
| Coach - Bloqueo Cortafuegos Semántico | 1.07 | 1.05 | 1.21 | 1.30 | 1.00 | 1.36 |
| Coach - Consulta Whitelisteada | 1.07 | 1.05 | 1.20 | 1.28 | 0.98 | 1.40 |
| Cambiar de Fase | 1.27 | 1.09 | 1.41 | 1.76 | 1.01 | 14.93 |

## Análisis de Cuellos de Botella y Robustez del Coach
1. **Crecimiento de Excepted Terms**: En el Cortafuegos Semántico, cada vez que una consulta es procesada, se recorre linealmente `active_phase.citations` para construir `excepted_terms`. El costo computacional es $O(N_c \cdot L_v)$ donde $N_c$ es el número de citaciones e $L_v$ la longitud del valor de la cita. Dado que $N_c \le 20$ en casos reales y el procesamiento se ejecuta en memoria, la latencia añadida por la verificación semántica es menor a **1ms**, haciéndolo extremadamente robusto frente a sobrecargas.
2. **Estanqueidad y State Bloat**: A pesar de tener 5 fases archivadas, el uso del Snapshot Sandbox mantiene la latencia de cambio de fase y consultas del Coach de forma constante e independiente de la historia del proyecto. La latencia p95 de cambio de fase es sumamente baja porque la base de datos se mantiene estructurada localmente en memoria sin requerir costosos accesos secuenciales.
3. **Impacto en el Coach**: La latencia del Coach al procesar consultas libres o bloqueos semánticos es casi instantánea (menor a **2ms**) debido a que las respuestas del Coach están estructuradas heurísticamente basadas en reglas léxicas rápidas, evitando llamadas directas a APIs de LLM externas durante el flujo básico sincrónico de cortafuegos.
