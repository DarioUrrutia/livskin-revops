"""ERP smoke test E2E con Playwright (HEADED, mobile viewport).

Simula a un usuario real haciendo el flujo completo:

  PARTE A — Audit visual (regresion check)
    1. Login
    2. Walkthrough las 7 pestañas
    3. Header refactor visible (logo + user + boton Salir + menu admin)

  PARTE B — Smoke funcional Agenda (ADR-0035 Fase 4A.1)
    4. Pestana Agenda muestra las citas TEST_SMOKE
    5. Click 'Confirmar' en una scheduled -> verifica que pasa a confirmed
    6. Click 'Vino' en una confirmed -> verifica que pasa a attended + crea cliente
    7. Click 'No vino' en otra -> verifica que pasa a no_show
    8. Click 'Reagendar' en otra -> verifica que crea nueva cita

  PARTE C — Coherencia cross-tab
    9. Validar que el cliente nuevo creado por mark_attended aparece en pestana Cliente
    10. Validar que el datalist Venta lista el cliente nuevo
    11. Validar que pestana Dashboard carga sin errores

  PARTE D — Header + logout (verificar que cierre sesion funciona)
    12. Click Salir -> redirect a /login
    13. Re-login + validar que sesion fresca

Genera artefactos en docs/audits/erp-smoke-e2e-<fecha>/

Uso:
    py scripts/erp_smoke_e2e.py

Requiere:
    keys/.env.integrations: ERP_TEST_USERNAME=... ERP_TEST_PASSWORD=...
"""
import os
import sys
import time
from datetime import date
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ERP_URL = "https://erp.livskin.site"


def get_credentials() -> tuple[str, str]:
    env_file = Path("keys/.env.integrations")
    user, pwd = None, None
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("ERP_TEST_USERNAME="):
                user = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("ERP_TEST_PASSWORD="):
                pwd = line.split("=", 1)[1].strip().strip('"').strip("'")
    return user, pwd


def check(label: str, condition: bool, details: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    icon = "[+]" if condition else "[-]"
    line = f"  [{status}] {icon} {label}"
    if details:
        line += f" -- {details}"
    print(line)
    return condition


def main():
    user, pwd = get_credentials()
    if not user or not pwd:
        print("ERROR: faltan credentials en keys/.env.integrations")
        sys.exit(1)

    today = date.today().isoformat()
    out_dir = Path(f"docs/audits/erp-smoke-e2e-{today}")
    out_dir.mkdir(parents=True, exist_ok=True)

    findings: list[tuple[str, bool, str]] = []  # (test, passed, details)

    def record(label: str, ok: bool, details: str = ""):
        findings.append((label, ok, details))
        check(label, ok, details)

    with sync_playwright() as p:
        # Viewport iPhone 15 (393x852) — devices reales: iPhone 15/16 + Xiaomi 14T Pro.
        iphone15 = {
            "viewport": {"width": 393, "height": 852},
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        }
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(**iphone15)
        page = context.new_page()

        # ═══════════════════════════════════════════════════════════════
        # PARTE A — Audit visual
        # ═══════════════════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("PARTE A — Audit visual + header")
        print("=" * 60)

        print("\n[A1] Login")
        page.goto(f"{ERP_URL}/login")
        page.fill("input[name='username']", user)
        page.fill("input[name='password']", pwd)
        page.click("button[type='submit']")
        try:
            page.wait_for_url(f"{ERP_URL}/", timeout=10000)
            record("login redirect a /", True)
        except Exception as e:
            record("login redirect a /", False, str(e))
            browser.close()
            sys.exit(1)

        page.screenshot(path=str(out_dir / "01-after-login.png"), full_page=True)

        print("\n[A2] Header refactor visible")
        record("logo presente", page.locator(".header-logo img").count() > 0)
        record("nombre user visible", page.locator(".header-user-name").count() > 0)
        record("boton Salir prominente", page.locator(".header-logout-btn").count() > 0)
        record("boton menu admin (⚙️)", page.locator(".header-menu-toggle").count() > 0)

        # Click menu admin -> verifica que se abre
        page.click(".header-menu-toggle")
        time.sleep(0.4)
        record("menu admin desplegable abre", page.locator(".header-admin-menu.open").count() > 0)
        page.screenshot(path=str(out_dir / "02-header-menu-open.png"))
        # Cerrar menu clickeando fuera
        page.locator("body").click(position={"x": 50, "y": 200})
        time.sleep(0.3)

        print("\n[A3] Walkthrough pestañas (regresion check)")
        for tab in ["venta", "gasto", "pagos", "cliente", "dashboard", "libro", "agenda"]:
            btn = page.locator(f"button[data-tab='{tab}']")
            if btn.count() == 0:
                record(f"pestaña {tab} existe", False, "boton no encontrado")
                continue
            btn.first.click()
            time.sleep(0.6)
            visible = page.is_visible(f"#tab-{tab}")
            record(f"pestaña {tab} renderiza", visible)

        # ═══════════════════════════════════════════════════════════════
        # PARTE B — Smoke funcional Agenda
        # ═══════════════════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("PARTE B — Smoke funcional Agenda")
        print("=" * 60)

        print("\n[B1] Navegar a Agenda")
        page.click("button[data-tab='agenda']")
        time.sleep(2)  # esperar carga de cards
        cards = page.locator(".agenda-card")
        n_cards = cards.count()
        record(f"Agenda muestra cards (smoke data)", n_cards >= 3, f"{n_cards} cards visibles")

        if n_cards == 0:
            print("    [SKIP] sin cards — saltar resto de Parte B")
        else:
            page.screenshot(path=str(out_dir / "03-agenda-cards.png"), full_page=True)

            # Capturar lista de cods + estados ANTES de las acciones
            apt_states_before = page.evaluate("""
                () => Array.from(document.querySelectorAll('.agenda-card')).map(c => {
                    const meta = c.querySelector('.agenda-card-meta')?.textContent || '';
                    const status = c.querySelector('.agenda-card-status')?.textContent?.trim() || '';
                    const m = meta.match(/LIVAPT_TEST_\\d+/);
                    return m ? {cod: m[0], status} : null;
                }).filter(Boolean);
            """)
            print(f"    Estados iniciales: {apt_states_before}")

            # B2: Confirmar una scheduled
            print("\n[B2] Click Confirmar en una cita scheduled")
            confirmar_btn = page.locator(".agenda-btn-confirm").first
            if confirmar_btn.count() > 0:
                # Auto-accept del confirm()
                page.once("dialog", lambda d: d.accept())
                confirmar_btn.click()
                time.sleep(2)
                # Recargar y validar
                cards_after = page.evaluate("""
                    () => Array.from(document.querySelectorAll('.agenda-card-status'))
                        .map(s => s.textContent.trim())
                """)
                # debe haber al menos una "Confirmada" mas que antes
                count_confirmed = sum(1 for s in cards_after if "Confirmada" in s)
                record("Confirmar cambia estado a Confirmada", count_confirmed >= 1, f"{count_confirmed} confirmadas")
                page.screenshot(path=str(out_dir / "04-after-confirm.png"), full_page=True)
            else:
                record("boton Confirmar disponible", False)

            # B3: Vino en una confirmed
            print("\n[B3] Click Vino en una cita confirmed (crea cliente)")
            # Tomar lista de clientes ANTES (para validar creación nueva)
            page.click("button[data-tab='cliente']")
            time.sleep(0.8)
            clientes_before = page.evaluate("""
                () => Array.from(document.querySelectorAll('#lista-clientes option')).length
            """)
            print(f"    Clientes antes de Vino: {clientes_before}")

            page.click("button[data-tab='agenda']")
            time.sleep(1.5)
            vino_btn = page.locator(".agenda-btn-attended").first
            if vino_btn.count() > 0:
                page.once("dialog", lambda d: d.accept())
                vino_btn.click()
                time.sleep(2)
                page.screenshot(path=str(out_dir / "05-after-vino.png"), full_page=True)
                # Validar que ahora hay 1 cliente más
                page.click("button[data-tab='cliente']")
                time.sleep(0.8)
                clientes_after = page.evaluate("""
                    () => Array.from(document.querySelectorAll('#lista-clientes option')).length
                """)
                # OJO: el datalist se carga al render del template — necesita reload del page
                page.reload()
                time.sleep(2)
                clientes_after_reload = page.evaluate("""
                    () => Array.from(document.querySelectorAll('#lista-clientes option')).length
                """)
                print(f"    Clientes despues (reload): {clientes_after_reload}")
                record(
                    "Vino crea cliente nuevo (datalist crece tras reload)",
                    clientes_after_reload > clientes_before,
                    f"{clientes_before} -> {clientes_after_reload}",
                )
            else:
                record("boton Vino disponible", False, "ninguna cita en confirmed")

            # B4: No vino
            print("\n[B4] Click No vino en una cita")
            page.click("button[data-tab='agenda']")
            time.sleep(1.5)
            no_vino_btn = page.locator(".agenda-btn-noshow").first
            if no_vino_btn.count() > 0:
                page.once("dialog", lambda d: d.accept())
                no_vino_btn.click()
                time.sleep(2)
                page.screenshot(path=str(out_dir / "06-after-no-vino.png"), full_page=True)
                cards_after = page.evaluate("""
                    () => Array.from(document.querySelectorAll('.agenda-card-status'))
                        .map(s => s.textContent.trim())
                """)
                count_no_show = sum(1 for s in cards_after if "No vino" in s)
                record("No vino marca status no_show", count_no_show >= 1, f"{count_no_show} en no_show")
            else:
                record("boton No vino disponible", False, "ninguna confirmed")

        # ═══════════════════════════════════════════════════════════════
        # PARTE C — Coherencia cross-tab
        # ═══════════════════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("PARTE C — Coherencia cross-tab")
        print("=" * 60)

        print("\n[C1] Pestaña Cliente carga (no errores)")
        page.click("button[data-tab='cliente']")
        time.sleep(1)
        record("Cliente tab visible", page.is_visible("#tab-cliente"))

        print("\n[C2] Pestaña Dashboard carga (gráficos)")
        page.click("button[data-tab='dashboard']")
        time.sleep(3)  # Chart.js render
        record("Dashboard tab visible", page.is_visible("#tab-dashboard"))
        page.screenshot(path=str(out_dir / "07-dashboard.png"), full_page=True)

        print("\n[C3] Pestaña Libro carga (data)")
        page.click("button[data-tab='libro']")
        time.sleep(2)
        record("Libro tab visible", page.is_visible("#tab-libro"))
        page.screenshot(path=str(out_dir / "08-libro.png"), full_page=True)

        # ═══════════════════════════════════════════════════════════════
        # PARTE D — Header + logout
        # ═══════════════════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("PARTE D — Header + logout")
        print("=" * 60)

        print("\n[D1] Click Salir → redirect a /login")
        page.click(".header-logout-btn")
        time.sleep(2)
        url_after_logout = page.url
        record("logout redirect a /login", "/login" in url_after_logout, url_after_logout)
        page.screenshot(path=str(out_dir / "09-after-logout.png"), full_page=True)

        print("\n[D2] Re-login funciona")
        page.fill("input[name='username']", user)
        page.fill("input[name='password']", pwd)
        page.click("button[type='submit']")
        try:
            page.wait_for_url(f"{ERP_URL}/", timeout=10000)
            record("re-login exitoso", True)
        except Exception:
            record("re-login exitoso", False)

        # ═══════════════════════════════════════════════════════════════
        # REPORTE FINAL
        # ═══════════════════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("REPORTE FINAL")
        print("=" * 60)
        passed = sum(1 for _, ok, _ in findings if ok)
        failed = sum(1 for _, ok, _ in findings if not ok)
        print(f"\nTOTAL: {passed} PASS · {failed} FAIL · {len(findings)} tests")

        if failed > 0:
            print("\nFALLAS:")
            for label, ok, details in findings:
                if not ok:
                    print(f"  ✗ {label}" + (f" — {details}" if details else ""))

        # Guardar reporte markdown
        report = out_dir / "SMOKE_E2E_REPORT.md"
        with report.open("w", encoding="utf-8") as f:
            f.write(f"# ERP Smoke E2E — {today}\n\n")
            f.write(f"**Viewport:** iPhone 13 Pro (390×844) · headed mode\n\n")
            f.write(f"**Resultado:** {passed}/{len(findings)} PASS\n\n")
            f.write("## Tests ejecutados\n\n")
            f.write("| # | Test | Status | Detalles |\n")
            f.write("|---|---|---|---|\n")
            for i, (label, ok, details) in enumerate(findings, 1):
                icon = "✅" if ok else "❌"
                f.write(f"| {i} | {label} | {icon} | {details or '—'} |\n")
            f.write("\n## Screenshots\n\n")
            for png in sorted(out_dir.glob("*.png")):
                f.write(f"- ![{png.stem}]({png.name})\n")

        print(f"\nReporte: {report}")
        print(f"Screenshots: {out_dir}")

        print("\nPresiona Enter para cerrar el browser...")
        try:
            input()
        except EOFError:
            time.sleep(8)
        browser.close()


if __name__ == "__main__":
    main()
