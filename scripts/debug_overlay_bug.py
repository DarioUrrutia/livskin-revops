"""Debug visual del bug overlay form-venta en mobile.

Llena form basico + captura el estado del DOM en el momento del submit
para identificar QUE elemento intercepta el click del boton.
"""
import sys
import time
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

ERP_URL = "https://erp.livskin.site"


def get_creds():
    user, pwd = None, None
    for line in Path("keys/.env.integrations").read_text(encoding="utf-8").splitlines():
        if line.startswith("ERP_TEST_USERNAME="):
            user = line.split("=", 1)[1].strip()
        elif line.startswith("ERP_TEST_PASSWORD="):
            pwd = line.split("=", 1)[1].strip()
    return user, pwd


def main():
    user, pwd = get_creds()
    today = date.today().isoformat()
    out_dir = Path(f"docs/audits/erp-overlay-debug-{today}")
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        iphone = p.devices["iPhone 13 Pro"]
        browser = p.chromium.launch(headless=False, slow_mo=400)
        context = browser.new_context(**iphone)
        page = context.new_page()
        page.on("dialog", lambda d: d.accept())

        # Login
        page.goto(f"{ERP_URL}/login")
        page.fill("input[name='username']", user)
        page.fill("input[name='password']", pwd)
        page.click("button[type='submit']")
        page.wait_for_url(f"{ERP_URL}/")

        # Llenar venta basica
        print("\n[1] Llenar form venta basico...")
        page.fill("#fecha-venta", today)
        page.fill("#input-cliente-venta", "TEST_DEBUG")
        time.sleep(0.5)

        # Item 0
        page.select_option("select[name='tipo_0']", "Tratamiento")
        time.sleep(0.4)
        cat_options = page.evaluate("() => Array.from(document.querySelector('select[name=\"categoria_0\"]').options).map(o => o.value)")
        print(f"    Categorias disponibles: {cat_options[:5]}...")
        if "Botox" in cat_options:
            page.select_option("select[name='categoria_0']", "Botox")
        page.fill("input[name='zona_0']", "Test zona")
        page.fill("input[name='precio_orig_0']", "100")
        time.sleep(0.6)

        # Pago
        page.fill("input[name='efectivo']", "100")
        time.sleep(0.8)

        # Screenshot full page con form lleno
        page.screenshot(path=str(out_dir / "01-form-venta-lleno-fullpage.png"), full_page=True)
        print("[OK] screenshot 01: full page form lleno")

        # Scroll al boton submit
        page.locator("#btn-guardar-venta").scroll_into_view_if_needed()
        time.sleep(0.4)
        page.screenshot(path=str(out_dir / "02-scrolled-to-submit.png"))
        print("[OK] screenshot 02: scroll al btn submit (viewport actual)")

        # Diagnostico: que esta encima del boton submit?
        diag = page.evaluate("""
            () => {
                const btn = document.getElementById('btn-guardar-venta');
                if (!btn) return {error: 'btn no existe'};
                const r = btn.getBoundingClientRect();
                const cx = r.x + r.width / 2;
                const cy = r.y + r.height / 2;

                // Punto exacto del centro del boton
                const elAtPoint = document.elementFromPoint(cx, cy);

                // Stack de elementos en ese punto
                const stack = [];
                let el = elAtPoint;
                while (el && el !== document.body && stack.length < 8) {
                    stack.push({
                        tag: el.tagName,
                        id: el.id || '(no-id)',
                        cls: (el.className?.toString() || '').slice(0, 40),
                        zIndex: getComputedStyle(el).zIndex,
                        pos: getComputedStyle(el).position
                    });
                    el = el.parentElement;
                }

                // Bbox del boton
                return {
                    btnBbox: {x: r.x, y: r.y, w: r.width, h: r.height, bottom: r.bottom, right: r.right},
                    viewport: {w: window.innerWidth, h: window.innerHeight, scrollY: window.scrollY},
                    elementAtCenterPoint: {
                        tag: elAtPoint?.tagName,
                        id: elAtPoint?.id,
                        cls: (elAtPoint?.className?.toString() || '').slice(0, 60),
                        text: (elAtPoint?.textContent || '').trim().slice(0, 80)
                    },
                    stack
                };
            }
        """)
        print("\n[DIAG]")
        print(f"  Btn bbox: {diag['btnBbox']}")
        print(f"  Viewport: {diag['viewport']}")
        print(f"  Element at btn-center point:")
        e = diag["elementAtCenterPoint"]
        print(f"    tag={e['tag']} id={e['id']} cls={e['cls']}")
        print(f"    text='{e['text']}'")
        print("  Element stack (from top):")
        for i, item in enumerate(diag["stack"]):
            print(f"    [{i}] {item['tag']}#{item['id']} (cls={item['cls']}, z={item['zIndex']}, pos={item['pos']})")

        # Probar click forzado para ver si envia
        print("\n[3] Intentar click submit con force=True...")
        try:
            page.locator("#btn-guardar-venta").click(force=True)
            time.sleep(2)
            page.screenshot(path=str(out_dir / "03-after-force-click.png"), full_page=True)
            url_after = page.url
            print(f"    URL despues: {url_after}")
            # Si estamos de vuelta en /  con flash message, success
            if page.locator(".mensaje").count() > 0:
                print("    [OK] flash message detectado — submit envio")
            else:
                print("    [?] no flash — verificar")
        except Exception as e:
            print(f"    [FAIL] {e}")

        print("\nPresiona Enter para cerrar...")
        try:
            input()
        except EOFError:
            time.sleep(8)
        browser.close()


if __name__ == "__main__":
    main()
