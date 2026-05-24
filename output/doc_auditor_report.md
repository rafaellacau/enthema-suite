# REPORTES DEL SUBAGENTE: DOC-AUDITOR
## Verificación de Consistencia entre Promesas Escritas y Código Real

> [!WARNING]
> **Dictamen de Auditoría:** El Manifiesto de Enthema Suite v3.0 declara compromisos de honestidad epistémica revolucionarios, pero **el backend de producción no cuenta con las implementaciones correspondientes a cinco de sus siete compromisos constitutivos**, considerándolos 'Promesas de Marketing' sin sustento funcional en la base de código actual.

### Tabla de Promesas Escritas Incumplidas

| Compromiso Prometido | Brecha Encontrada en Código | Gravedad | Archivos Afectados | Esfuerzo de Remediación |
|---|---|---|---|---|
| **Bounded autonomy multi-agente con orquestación visible (Bibliógrafo, Reflexivo, Metodológico, etc.).** | El procesamiento de consultas al AI Coach en el endpoint `/api/copilot/query` (L1902) está hardcodeado en una única función monolítica que evalúa condicionales sobre palabras clave y rutas de pestañas, en lugar de instanciar un framework de agentes (como LangGraph o CrewAI) con memoria compartida. | **Alta** | `app.py (L1902-2050)` | Refactorizar el backend del Coach dividiéndolo en clases de agentes independientes con interfaces bien definidas y un orquestador central que emita los estados de discusión. |

### Recomendación Global de Consistencia
Para evitar publicidad engañosa y violaciones a la integridad del software de investigación, se sugiere: 
1. **Alinear el Manifiesto**: Modificar el README y el manifiesto para aclarar que las capacidades de C2PA, multi-agentes y timecodes multimedia representan el **Roadmap Estratégico a largo plazo** y no características de producción activas en la v3.0.
2. **Establecer Contratos de Validación**: Implementar clases abstractas o interfaces Pydantic rigurosas para que cualquier merge de código nuevo obligue a cumplir las firmas y metadatos declarados.
