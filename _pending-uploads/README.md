# `_pending-uploads/` — staging local de fotos para landings

**Carpeta gitignored** (excepto este README). Dario deja aquí fotos para procesar en próxima sesión.

---

## Cómo usar

### Para Dario

1. Cuando tengas fotos para una landing (existente o nueva), arrastrá los archivos directamente a esta carpeta.
2. **Naming sugerido** (no obligatorio — Claude infiere si está vacío):
   ```
   <slug-hint>-<descripcion-corta>.jpg
   ```
   Ejemplos:
   - `dia-madre-hero-doctora-mirando-camara.jpg`
   - `botox-section-resultados-paciente-anonima.jpg`
   - `og-livskin-logo-pink.png`

3. En la próxima sesión modo CAMPAÑA con Claude, decí: *"hay fotos nuevas en pending"*.

### Para Claude

Al inicio de sesión modo CAMPAÑA con la doctrina cargada:

1. Listar `_pending-uploads/` con `ls`
2. Si hay archivos nuevos:
   - Pasar checklist de `docs/brand/image-guidelines.md` § "Checklist pre-upload" para cada uno
   - Preguntar destino a Dario para cada archivo
   - Mover a `infra/landing-pages/<slug>/uploads/<naming-convencional>` con renombre apropiado
   - Editar HTML/JSX para usarla
   - Actualizar la metadata correspondiente en `livskin-config.json` si aplica
   - Commit + push → CF Pages auto-deploy
3. Después del proceso: `_pending-uploads/` queda vacía (excepto README)

---

## Reglas duras

- ❌ NO commitear archivos de esta carpeta (.gitignore lo previene)
- ❌ NO usar fotos de aquí directamente desde el HTML (mover primero a `uploads/` apropiado)
- ❌ NO dejar archivos sin procesar entre sesiones por más de 2 semanas (limpia o procesá)

---

## Alternativa — drag-drop directo en chat

Para 1-3 fotos ad-hoc durante la sesión, **no hace falta esta carpeta**: pegá la foto directamente en el chat con Claude indicando destino. Más rápido para batches chicos.

Esta carpeta es para batches >5 fotos o pre-loading entre sesiones.

---

## Cross-link

- `docs/brand/image-guidelines.md` § "Mecánica de upload (modo bootstrap actual)" — política completa
- `.gitignore` línea de `_pending-uploads/*` — reglas técnicas de exclusión
