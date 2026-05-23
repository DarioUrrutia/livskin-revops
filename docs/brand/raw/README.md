# docs/brand/raw/ — Material crudo del Interludio Discovery (GITIGNORED)

**Propósito**: staging local para material con PII o datos sensibles del encuentro con la doctora (chats reales pacientes, credenciales doctora, audio encuentro). Claude lo procesa y extrae patterns anonimizados a `docs/brand/voice-v1.md`, `personas.md`, `casos-exito.md`, etc. (tracked).

**Reglas**:
- ✅ Esta carpeta está en `.gitignore` — solo este README va a GitHub
- ✅ Contenido crudo se queda LOCAL en tu máquina (Dario) y eventualmente en VPS3 como backup
- ❌ NUNCA mover archivos crudos a paths tracked sin anonimizar primero (blur nombres, remover apellidos, redactar phone numbers)
- ❌ NUNCA compartir capturas con nombres reales fuera del repo

**Estructura**:

```
docs/brand/raw/
├── README.md                          ← este archivo (único tracked)
├── screenshots-chats/                 ← capturas WhatsApp doctora ↔ pacientes
│   ├── 01-kelly-rios-reschedule.png   (ejemplo nombre archivo)
│   └── ...
├── credenciales-doctora/              ← PDFs certificados, títulos, especializaciones
│   └── certificados-completos.pdf
└── audio-encuentro/                   ← grabación encuentro 2026-05-?? (si tomaste)
    └── encuentro-doctora-YYYY-MM-DD.m4a
```

**Workflow**:

1. Dario suelta archivos crudos en subcarpetas correspondientes
2. Claude lee, extrae patterns + quotes literales + ejemplos
3. Claude escribe versión anonimizada/sintetizada en `docs/brand/*.md` tracked
4. Material crudo se queda acá como referencia + auditoría
5. Backup periódico a VPS3 si Dario decide (opcional)

**Política PII**:
- Nombres pacientes reales → reemplazar por arquetipos ("Cliente Persona A", "Recurrente Botox B")
- Phone numbers → `+51 ********`
- Direcciones → ciudad/distrito solo
- Doctora: nombre+apellido OK en outputs (es la marca personal), DNI/firma NO
