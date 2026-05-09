"""ERP full audit con Playwright (HEADED, mobile viewport).

Walkthrough completo del ERP de Livskin:
- Login automatico
- Visita cada pestana (venta, gasto, pagos, cliente, dashboard, libro, agenda)
- Detecta overflow visual, console errors, elementos cortados
- Captura screenshot de cada pestana
- Reporta findings al final

Genera artefactos en docs/audits/erp-ui-audit-<fecha>/

Uso:
    py scripts/erp_full_audit.py

Requiere credentials en keys/.env.integrations:
    ERP_TEST_USERNAME=...
    ERP_TEST_PASSWORD=...
"""
import os
import sys
import time
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

ERP_URL = "https://erp.livskin.site"
TABS = ["venta", "gasto", "pagos", "cliente", "dashboard", "libro", "agenda"]


def get_credentials() -> tuple[str, str]:
    env_file = Path("keys/.env.integrations")
    user, pwd = None, None
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("ERP_TEST_USERNAME="):
                user = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("ERP_TEST_PASSWORD="):
                pwd = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not user:
        user = os.environ.get("ERP_TEST_USERNAME") or input("ERP username: ").strip()
    if not pwd:
        pwd = os.environ.get("ERP_TEST_PASSWORD") or input("ERP password: ").strip()
    return user, pwd


def main():
    user, pwd = get_credentials()
    if not user or not pwd:
        print("ERROR: faltan credentials")
        sys.exit(1)

    today = date.today().isoformat()
    out_dir = Path(f"docs/audits/erp-ui-audit-{today}")
    out_dir.mkdir(parents=True, exist_ok=True)

    console_errors: dict[str, list[str]] = {tab: [] for tab in TABS}
    findings: list[str] = []

    with sync_playwright() as p:
        # Viewport iPhone 15 (393x852) — alineado con devices reales del usuario:
        # iPhone 15/16 + Xiaomi 14T Pro. Memoria: feedback_mobile_targets_layout_rules.
        iphone15 = {
            "viewport": {"width": 393, "height": 852},
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        }
        browser = p.chromium.launch(headless=False, slow_mo=350)
        context = browser.new_context(**iphone15)
        page = context.new_page()

        # Capturar console errors globales
        current_tab = ["login"]
        page.on("pageerror", lambda exc: console_errors.setdefault(current_tab[0], []).append(f"PAGEERROR: {exc}"))
        page.on("console", lambda msg: (
            console_errors.setdefault(current_tab[0], []).append(f"[{msg.type}] {msg.text}")
            if msg.type in ("error", "warning") else None
        ))

        # ── LOGIN ──
        print(f"\n[LOGIN] {ERP_URL}/login")
        page.goto(f"{ERP_URL}/login")
        page.fill("input[name='username']", user)
        page.fill("input[name='password']", pwd)
        page.click("button[type='submit']")
        page.wait_for_url(f"{ERP_URL}/", timeout=10000)
        print("    [OK] login")

        # ── WALKTHROUGH POR PESTANA ──
        for tab in TABS:
            current_tab[0] = tab
            print(f"\n[TAB] {tab}")
            try:
                btn = page.locator(f"button[data-tab='{tab}']")
                if btn.count() == 0 or not btn.first.is_visible():
                    findings.append(f"[{tab}] boton no visible (feature flag OFF?)")
                    print(f"    [SKIP] boton no visible")
                    continue

                btn.first.click()
                time.sleep(0.6)
                content = page.locator(f"#tab-{tab}")
                if not content.is_visible():
                    findings.append(f"[{tab}] contenido no visible despues de click")
                    print(f"    [FAIL] contenido invisible")
                    continue

                # Triggers especificos por pestana
                if tab == "libro":
                    # cargarLibro() se llama en el onclick del boton, esperar que cargue
                    time.sleep(1.5)
                if tab == "agenda":
                    time.sleep(1.5)  # cargarAgenda fetches /api/appointments
                if tab == "dashboard":
                    time.sleep(2.0)  # dashboard carga grafico Chart.js

                # Scroll al final para detectar overflow
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.3)
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(0.3)

                # Screenshot full page
                screenshot_path = out_dir / f"tab-{tab}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"    [OK] screenshot -> {screenshot_path.name}")

                # Detectar elementos overflow horizontal del viewport (390px iPhone 13 Pro).
                # IGNORA elementos dentro de contenedores scrolleables (overflow-x: auto/scroll)
                # porque esos son intencionales — accesibles via swipe horizontal.
                overflowing = page.evaluate("""
                    () => {
                        const vw = window.innerWidth;
                        const overflows = [];
                        const isScrollableContainer = (el) => {
                            const cs = getComputedStyle(el);
                            return cs.overflowX === 'auto' || cs.overflowX === 'scroll';
                        };
                        const hasScrollableAncestor = (el) => {
                            let p = el.parentElement;
                            while (p && p !== document.body) {
                                if (isScrollableContainer(p)) return true;
                                p = p.parentElement;
                            }
                            return false;
                        };
                        document.querySelectorAll('*').forEach(el => {
                            const r = el.getBoundingClientRect();
                            if (r.right > vw + 5 && r.width > 50 && el.offsetParent) {
                                if (hasScrollableAncestor(el)) return;  // intencional
                                const id = el.id || el.className?.toString().slice(0,40) || el.tagName;
                                overflows.push({id, w: Math.round(r.width), right: Math.round(r.right)});
                            }
                        });
                        return overflows.slice(0, 8);
                    }
                """)
                if overflowing:
                    findings.append(f"[{tab}] {len(overflowing)} elem overflow horizontal:")
                    for ov in overflowing[:3]:
                        findings.append(f"     - {ov['id']} w={ov['w']}px right={ov['right']}px")
                    print(f"    [WARN] {len(overflowing)} elementos overflow")
                else:
                    print(f"    [OK] sin overflow horizontal")

            except Exception as e:
                findings.append(f"[{tab}] EXCEPTION: {e}")
                print(f"    [FAIL] {e}")

        # ── PRUEBAS FUNCIONALES MINIMAS ──
        print("\n[FUNC] datalist clientes en pestana Venta")
        try:
            page.click("button[data-tab='venta']")
            time.sleep(0.4)
            datalist = page.locator("#lista-clientes option")
            count = datalist.count()
            print(f"    [{'OK' if count > 0 else 'WARN'}] datalist tiene {count} clientes")
            if count == 0:
                findings.append("[venta] datalist clientes vacio")
        except Exception as e:
            findings.append(f"[venta] datalist clientes EXCEPTION: {e}")

        # ── REPORTE FINAL ──
        print("\n" + "=" * 60)
        print("REPORTE FINAL")
        print("=" * 60)
        if findings:
            print(f"\n[{len(findings)}] FINDINGS:")
            for f in findings:
                print(f"  {f}")
        else:
            print("\n[CLEAN] sin findings — UI sana en mobile")

        print("\nCONSOLE ERRORS POR PESTANA:")
        any_errors = False
        for tab, errs in console_errors.items():
            real_errs = [e for e in errs if "PAGEERROR" in e or "[error]" in e]
            if real_errs:
                any_errors = True
                print(f"  [{tab}] {len(real_errs)} errores:")
                for e in real_errs[:3]:
                    print(f"     - {e[:120]}")
        if not any_errors:
            print("  [CLEAN] sin errores en consola")

        # Guardar reporte markdown
        report_path = out_dir / "REPORT.md"
        with report_path.open("w", encoding="utf-8") as f:
            f.write(f"# ERP UI Audit — {today}\n\n")
            f.write(f"**Viewport:** iPhone 15 (393×852) — alineado con devices reales (iPhone 15/16 + Xiaomi 14T Pro)\n")
            f.write(f"**Pestañas validadas:** {len(TABS)}\n\n")
            f.write("## Findings\n\n")
            if findings:
                for fi in findings:
                    f.write(f"- {fi}\n")
            else:
                f.write("Sin findings — UI sana en mobile.\n")
            f.write("\n## Screenshots\n\n")
            for tab in TABS:
                p_path = out_dir / f"tab-{tab}.png"
                if p_path.exists():
                    f.write(f"- ![{tab}](tab-{tab}.png)\n")
            f.write("\n## Console errors por pestaña\n\n")
            for tab, errs in console_errors.items():
                real = [e for e in errs if "PAGEERROR" in e or "[error]" in e]
                if real:
                    f.write(f"### {tab}\n")
                    for e in real[:5]:
                        f.write(f"- `{e[:200]}`\n")
        print(f"\n[REPORT] {report_path}")

        print("\nPresiona Enter para cerrar el browser...")
        try:
            input()
        except EOFError:
            time.sleep(8)
        browser.close()


if __name__ == "__main__":
    main()
