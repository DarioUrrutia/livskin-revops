# Runbook: Setup de Obsidian como vault del proyecto

**Cuándo ejecutar:** primera vez que quieres usar Obsidian en una máquina (laptop personal o del trabajo).  
**Tiempo estimado:** 10 minutos.  
**Pre-requisitos:** tener el repo clonado localmente.

---

## 1. Instalar Obsidian

Descargar desde https://obsidian.md (gratis, disponible para Windows, Mac, Linux).

Instalar y abrir.

## 2. Abrir el repo como vault

1. En la pantalla de bienvenida de Obsidian, click **"Open folder as vault"**
2. Navega a: `C:\Users\daizu\Claude Code\Union VPS - Maestro - Livskin\`
3. Click **"Open"**
4. Obsidian te preguntará si confías en esta ubicación → **"Trust author and enable plugins"**

Obsidian lee automáticamente todos los `.md` del repo.

## 3. Configuración recomendada

### Settings → Files and Links

- **Default editing mode:** "Source mode" (ve el markdown tal cual; "Live preview" es alternativa aceptable)
- **Automatically update internal links:** ✅ ON
- **New link format:** "Relative path to file"
- **Detect all file extensions:** ✅ ON (opcional, para ver archivos no-md en sidebar)
- **Excluded files:** agrega `keys/`, `erp/`, `backups/`, `notes/privado/` **(si quieres privacy total)**

### Settings → Appearance

- **Theme:** cualquiera que te guste (Minimal, Things, o default)
- **Reading mode font:** Inter, SF Pro o cualquier legible
- **Text font:** idem

### Settings → Hotkeys

Atajos útiles:
- `Ctrl+O` — Quick switcher (abre cualquier archivo por nombre)
- `Ctrl+Shift+F` — Search in files (full-text)
- `Ctrl+G` — Graph view
- `Ctrl+Shift+O` — Outgoing links del archivo actual
- `Ctrl+Shift+I` — Incoming links (backlinks)

## 4. Plugins recomendados (todos gratis)

Settings → Community plugins → Browse.

### Esenciales

- **Dataview** — queries SQL-like sobre frontmatter YAML. Muy útil para generar tablas vivas (ej: "todos los ADRs aprobados en fase 2").
- **Templater** — plantillas con atajos de teclado. Útil para crear ADRs nuevos rápido.

### Recomendados

- **Calendar** — muestra sesiones/audits por fecha
- **Kanban** — tableros para workflows (ej: backlog visual)
- **Mind Map** — vista alternativa del grafo
- **Better PDF Plugin** — para ver PDFs dentro del vault (ej: blueprint.docx si lo conviertes)

## 5. Uso del grafo

- **Graph view (Ctrl+G):** ve cómo están conectados TODOS los documentos
- **Local graph** (click derecho en un archivo → "Open local graph"): ve solo lo conectado al archivo actual
- **Filters:** ocultar `.gitkeep`, `README.md` si quieres vista más limpia

Notas que aparecen en el grafo:
- Cada ADR es un nodo
- Session logs son nodos conectados a los ADRs que mencionan
- Cuando uno linkeas un ADR en un session log, aparece línea en el grafo

## 6. Cómo crear notas nuevas

### Nota personal privada

1. Navega a `notes/privado/` en el sidebar
2. Click derecho → "New note"
3. Nombre como quieras
4. Escribe libremente

**Esta nota NO se versiona en git.** Es tuya y queda en tu laptop.

### Nota compartida (colaborativa con Claude Code)

1. Navega a `notes/compartido/`
2. Click derecho → "New note"
3. Usa la plantilla de `notes/README.md`
4. Al hacer commit + push, la nota llega a GitHub y a mí

### ADR nuevo (decisión estructural)

**Mejor no crearlo manual** — pídele a Claude Code: "escribe ADR para decidir X". Yo uso la plantilla `docs/decisiones/_template.md`, completo contexto y opciones, lo pongo en review.

## 7. Sincronización entre máquinas

**No usamos Obsidian Sync** (es pago). Usamos git:

1. En máquina A: tomas notas, commit + push
2. En máquina B: `git pull` → las notas compartidas aparecen
3. Notas en `notes/privado/` son locales — cada máquina tiene las suyas

Si alguna vez quieres sincronizar notas privadas entre tus máquinas, una opción gratis es:
- Guardarlas en tu Google Drive o Dropbox
- Hacer symlink desde `notes/privado/` a esa carpeta sincronizada

## 8. Integración con el segundo cerebro

- `notes/compartido/` se indexa automáticamente en Layer 2 del cerebro (cuando Fase 1 esté lista)
- Desde Claude Code puedo buscar semánticamente en tus notas compartidas
- `notes/privado/` nunca se indexa (privacy by design)

## 9. Troubleshooting

### "Obsidian abre lento"

El plugin `Dataview` puede indexar al abrir. Primera vez lenta, después rápida. No agregar plugins pesados si tienes laptop modesta.

### "No veo los backlinks"

Verifica en Settings → Files and Links que "Use [[Wikilinks]]" esté en el formato correcto. Los ADRs usan `[link](path.md)` (markdown estándar), Obsidian los detecta de ambas maneras.

### "Accidentalmente moví un archivo y se rompieron links"

Obsidian por default **actualiza links automáticamente** cuando mueves un archivo dentro del vault. Verifica "Automatically update internal links" en settings.

Si ya se rompió: usa `git checkout <archivo>` para revertir.

### "Quiero subir .obsidian/ al git para compartir configuración"

Por default está en `.gitignore` porque contiene workspace personal (qué archivos tenías abiertos, qué plugins activos, preferencias). Si quieres compartir **solo** las configuraciones base (plugins instalados), puedes editar `.gitignore` para incluir partes específicas:

```
.obsidian/plugins/
.obsidian/themes/
!.obsidian/community-plugins.json
```

Pero mejor dejarlo como está — cada usuario con sus preferencias.

---

## Referencias

- Obsidian docs: https://help.obsidian.md/
- Dataview docs: https://blacksmithgu.github.io/obsidian-dataview/
- Templater docs: https://silentvoid13.github.io/Templater/
- [ADR-0001 § 9.2](../decisiones/0001-segundo-cerebro-filosofia-y-alcance.md) — Obsidian como capa humana del segundo cerebro
