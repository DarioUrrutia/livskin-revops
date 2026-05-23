# docs/brand/discovery-fill/ — Workbook lleno (TRACKED en git)

**Propósito**: outputs del workbook interactivo `docs/brand/interludio-discovery-workbook.html` después del encuentro con la doctora. Este folder SÍ va a git porque el contenido es el insumo formal para construir brand voice + personas + journey + catálogo.

**Archivos esperados acá**:

```
docs/brand/discovery-fill/
├── README.md                          ← este archivo
├── workbook-export.json               ← export JSON del workbook (datos estructurados)
├── workbook-export.md                 ← export Markdown del workbook (legible humano)
├── fotos-antes-despues/               ← fotos extraídas del export JSON (base64 → PNG)
│   ├── caso-01-antes.png
│   ├── caso-01-despues.png
│   └── ...
└── notas-claude.md                    ← mis observaciones + extracciones + decisiones tomadas
```

**Workflow Dario → Claude**:

1. **Dario**: en el workbook abierto en Chrome, click "📥 Exportar como Markdown" → guarda como `workbook-export.md`
2. **Dario**: click "💾 Exportar como JSON" → guarda como `workbook-export.json`
3. **Dario**: ambos archivos en este folder (`docs/brand/discovery-fill/`)
4. **Claude**: lee ambos archivos + procesa fotos del JSON (base64 decoded a `fotos-antes-despues/`)
5. **Claude**: produce 12 outputs digitales en `docs/brand/`:
   - `voice-v1.md`
   - `personas.md`
   - `journey-map.md`
   - `catalogo-tratamientos.md`
   - `precios-strategy.md`
   - `painpoints-responses.md`
   - `diferenciacion.md`
   - `operacion.md`
   - `casos-exito.md`
   - `reengagement.md`
   - `scoring-rules.md`
   - `captacion-global.md`

**Anonimización**:
- Si workbook tiene nombres reales pacientes en sección "Casos de éxito", Claude los reemplaza por arquetipos antes de mover a outputs `casos-exito.md`
- Material crudo con PII vive en `docs/brand/raw/` (gitignored)
