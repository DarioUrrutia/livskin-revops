"""Smoke test de la UI Agenda con Playwright (HEADED, mobile viewport).

Login automatico + navega a la pestana Agenda + valida que las cards se
renderizan correctamente en mobile sin botones cortados.

Uso:
    py scripts/agenda_ui_test.py

Requiere:
    pip install playwright
    py -m playwright install chromium

Credentials: lee de keys/.env.integrations o pide en consola.
"""
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ERP_URL = "https://erp.livskin.site"


def get_credentials() -> tuple[str, str]:
    """Lee credentials de env o pide al usuario."""
    env_file = Path("keys/.env.integrations")
    user, pwd = None, None
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("ERP_TEST_USERNAME="):
                user = line.split("=", 1)[1].strip()
            elif line.startswith("ERP_TEST_PASSWORD="):
                pwd = line.split("=", 1)[1].strip()
    if not user:
        user = os.environ.get("ERP_TEST_USERNAME") or input("ERP username: ").strip()
    if not pwd:
        pwd = os.environ.get("ERP_TEST_PASSWORD") or input("ERP password: ").strip()
    return user, pwd


def main():
    user, pwd = get_credentials()
    if not user or not pwd:
        print("ERROR: necesito ERP credentials")
        sys.exit(1)

    with sync_playwright() as p:
        # Mobile viewport (iPhone 13 Pro)
        iphone = p.devices["iPhone 13 Pro"]
        browser = p.chromium.launch(headless=False, slow_mo=400)
        context = browser.new_context(**iphone)
        page = context.new_page()

        print(f"\n[1] Navegando a {ERP_URL}/login ...")
        page.goto(f"{ERP_URL}/login")
        page.fill("input[name='username']", user)
        page.fill("input[name='password']", pwd)
        page.click("button[type='submit']")
        page.wait_for_url(f"{ERP_URL}/", timeout=10000)
        print("    [OK] login exitoso")

        print("\n[2] Verificando que las pestanas existentes responden (regresion check)...")
        for tab in ["venta", "gasto", "pagos", "cliente", "dashboard", "libro"]:
            page.click(f"button[data-tab='{tab}']")
            time.sleep(0.4)
            visible = page.is_visible(f"#tab-{tab}")
            print(f"    [{'OK' if visible else 'FAIL'}] pestaña {tab} visible={visible}")

        print("\n[3] Click en pestana AGENDA...")
        agenda_btn = page.locator("button[data-tab='agenda']")
        if not agenda_btn.is_visible():
            print("    [FAIL] boton Agenda no visible — feature flag puede estar OFF?")
            sys.exit(1)
        agenda_btn.click()
        page.wait_for_selector("#tab-agenda", state="visible", timeout=5000)
        print("    [OK] tab-agenda visible")

        time.sleep(2)  # esperar carga de cards
        cards = page.locator(".agenda-card")
        count = cards.count()
        print(f"\n[4] Cards renderizadas: {count}")
        if count == 0:
            print("    [WARN] no hay cards (smoke data?)")
        else:
            for i in range(min(count, 5)):
                card = cards.nth(i)
                bbox = card.bounding_box()
                print(f"    card {i}: w={bbox['width']:.0f}px x h={bbox['height']:.0f}px")
                # Validar botones dentro de la card no overflow
                btns = card.locator(".agenda-btn")
                for j in range(btns.count()):
                    bb = btns.nth(j).bounding_box()
                    if bb["x"] + bb["width"] > bbox["x"] + bbox["width"] + 5:
                        print(f"        [FAIL] boton {j} overflow horizontal!")

        print("\n[5] Test boton '+ manual' abre modal...")
        page.click("button[onclick='abrirModalNuevaCita()']")
        time.sleep(0.5)
        modal_visible = page.is_visible("#modal-nueva-cita")
        print(f"    [{'OK' if modal_visible else 'FAIL'}] modal visible={modal_visible}")
        if modal_visible:
            # Cerrar modal
            page.click("button[onclick='cerrarModalNuevaCita()']")

        print("\n[6] Screenshot mobile ...")
        Path("docs/audits").mkdir(exist_ok=True)
        page.screenshot(path="docs/audits/agenda-ui-mobile-2026-05-09.png", full_page=True)
        print("    [OK] guardado en docs/audits/agenda-ui-mobile-2026-05-09.png")

        print("\n[DONE] presiona Enter para cerrar el browser...")
        try:
            input()
        except EOFError:
            time.sleep(8)
        browser.close()


if __name__ == "__main__":
    main()
