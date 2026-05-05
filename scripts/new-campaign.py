#!/usr/bin/env python3
"""
new-campaign.py — Inicializa una nueva campaña a partir de docs/campaigns/_template/

Forza al operador a declarar MODO CAMPAÑA + propósito + hipótesis ANTES de generar archivos.
Esto preserva la disciplina del principio operativo #12 (modo declarado proyecto/campaña).

Uso:
    python scripts/new-campaign.py

NO acepta argumentos CLI por diseño — los prompts interactivos son OBLIGATORIOS.
"""

from __future__ import annotations

import datetime
import re
import shutil
import sys
from pathlib import Path

# Windows: stdout/stderr default a cp1252, romple con emojis. Forzar UTF-8.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "docs" / "campaigns" / "_template"
CAMPAIGNS_DIR = REPO_ROOT / "docs" / "campaigns"

DEFAULT_AD_ACCOUNT = "2885433191763149"
DEFAULT_PIXEL_ID = "4410809639201712"
DEFAULT_WA_PHONE = "+51980727888"


def banner() -> None:
    print()
    print("=" * 70)
    print("  Inicializar nueva campaña — Livskin")
    print("=" * 70)
    print()
    print("  ⚠️  Antes de proceder, leé `CLAUDE.md` § principio #12 (modo declarado).")
    print("      Una campaña sin propósito declarado se desvía.")
    print()
    print("  El script va a forzarte a articular el contexto antes de crear archivos.")
    print("  Si no estás listo para declarar MODO CAMPAÑA, salí con Ctrl+C.")
    print()
    print("=" * 70)
    print()


def ask(prompt: str, *, default: str = "", required: bool = True, multiline: bool = False) -> str:
    while True:
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "

        if multiline:
            print(full_prompt + " (vacío + Enter para terminar)")
            lines: list[str] = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            value = "\n  ".join(lines).strip()
        else:
            value = input(full_prompt).strip()

        if not value and default:
            value = default
        if not value and required:
            print("  ❌ Este campo es obligatorio.")
            continue
        return value


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} (yes/no): ").strip().lower()
        if answer in ("yes", "y", "si", "sí"):
            return True
        if answer in ("no", "n"):
            return False
        print("  Respondé 'yes' o 'no'.")


def validate_slug(slug: str) -> str:
    if not re.match(r"^\d{4}-\d{2}-[a-z0-9-]+$", slug):
        print(
            "  ❌ Formato inválido. Debe ser YYYY-MM-slug-kebab-case "
            "(ej: 2026-08-fiestas-patrias)."
        )
        sys.exit(1)
    return slug


def validate_date(date_str: str) -> str:
    try:
        datetime.date.fromisoformat(date_str)
    except ValueError:
        print(f"  ❌ Fecha inválida: {date_str}. Formato YYYY-MM-DD.")
        sys.exit(1)
    return date_str


def collect_inputs() -> dict[str, str]:
    print()
    print("  PASO 1 — Declaración de modo")
    print("  " + "-" * 60)
    if not ask_yes_no("  ¿Confirmás que estás declarando MODO CAMPAÑA?"):
        print()
        print("  ❌ MODO CAMPAÑA no declarado. Saliendo sin crear nada.")
        print("     Si querés trabajar en proyecto durable, no usés este script.")
        sys.exit(0)

    print()
    print("  PASO 2 — Identidad de la campaña")
    print("  " + "-" * 60)
    slug = validate_slug(
        ask("  Slug de la campaña (YYYY-MM-tema)", default="").lower()
    )
    target_dir = CAMPAIGNS_DIR / slug
    if target_dir.exists():
        print(f"  ❌ Ya existe `docs/campaigns/{slug}/`. Cancelando.")
        sys.exit(1)

    name = ask("  Nombre completo (humano)")
    treatment = ask("  Tratamiento canónico (ej: Armonización Facial)")

    print()
    print("  PASO 3 — Propósito + hipótesis (ESENCIAL — esto se embebe en el brief)")
    print("  " + "-" * 60)
    print()
    print("  Propósito (1-2 líneas — qué problema resuelve esta campaña):")
    purpose = ask("  ", multiline=True)

    print()
    print("  Hipótesis principal a validar (testable, falsificable):")
    hypothesis = ask("  ", multiline=True)

    print()
    print("  PASO 4 — Parámetros operativos")
    print("  " + "-" * 60)
    budget = ask("  Budget en PEN (solo número, sin S/)")
    start = validate_date(ask("  Fecha inicio (YYYY-MM-DD)"))
    end = validate_date(ask("  Fecha fin (YYYY-MM-DD)"))
    shortcode = ask(
        "  Shortcode prefix (ej: ARM-AGO-FB)", default=""
    ).upper()

    print()
    print("  PASO 5 — IDs de Meta (defaults Livskin Perú — Enter para aceptar)")
    print("  " + "-" * 60)
    ad_account = ask("  Ad Account ID", default=DEFAULT_AD_ACCOUNT)
    pixel_id = ask("  Pixel ID", default=DEFAULT_PIXEL_ID)
    wa_phone = ask("  WhatsApp E.164", default=DEFAULT_WA_PHONE)

    declared_by = ask("  Operador (tu nombre o 'Brand Orchestrator')", default="Dario")

    return {
        "CAMPAIGN_SLUG": slug,
        "CAMPAIGN_NAME": name,
        "TREATMENT": treatment,
        "PURPOSE": purpose,
        "HYPOTHESIS": hypothesis,
        "BUDGET_PEN": budget,
        "START_DATE": start,
        "END_DATE": end,
        "SHORTCODE_PREFIX": shortcode,
        "AD_ACCOUNT": ad_account,
        "PIXEL_ID": pixel_id,
        "WA_PHONE_E164": wa_phone,
        "DECLARED_BY": declared_by,
        "DECLARED_AT": datetime.date.today().isoformat(),
    }


def render(content: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    return content


def clone_template(values: dict[str, str]) -> Path:
    target_dir = CAMPAIGNS_DIR / values["CAMPAIGN_SLUG"]
    target_dir.mkdir(parents=True, exist_ok=False)

    for source in TEMPLATE_DIR.iterdir():
        if source.name in ("README.md",):
            # README del template no se copia — pertenece al template, no a la campaña.
            continue
        if source.is_dir():
            shutil.copytree(source, target_dir / source.name)
            continue
        rendered = render(source.read_text(encoding="utf-8"), values)
        (target_dir / source.name).write_text(rendered, encoding="utf-8")

    return target_dir


def summary(target_dir: Path, values: dict[str, str]) -> None:
    print()
    print("=" * 70)
    print(f"  ✅ Campaña creada: {target_dir.relative_to(REPO_ROOT)}")
    print("=" * 70)
    print()
    print("  Modo CAMPAÑA activo. Archivos generados:")
    print()
    for path in sorted(target_dir.iterdir()):
        print(f"    - {path.relative_to(target_dir)}")
    print()
    print("  Próximos pasos:")
    print(f"    1. Revisá `{target_dir.relative_to(REPO_ROOT)}/brief.md` — la declaración está embebida")
    print("    2. Marcá el brief como `approved` cuando esté listo")
    print(f"    3. Continuá con `plan.md` y `campaign-config-final.md`")
    print(f"    4. Cuando arranque la corrida, seguí `ads-manager-checklist.md`")
    print()
    print("  Recordatorio: NO toques doctrina (`docs/brand/`) durante la campaña.")
    print("  Todo aprendizaje durante producción → `_doctrine-feedback.md`.")
    print()


def main() -> None:
    if not TEMPLATE_DIR.is_dir():
        print(f"❌ No existe template en {TEMPLATE_DIR}")
        sys.exit(1)

    banner()
    values = collect_inputs()
    target_dir = clone_template(values)
    summary(target_dir, values)


if __name__ == "__main__":
    main()
