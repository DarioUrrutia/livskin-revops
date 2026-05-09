"""Quick screenshot solo de pestana Agenda en iPhone 15 viewport.

No interactua con modales, solo navega y captura.
"""
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
    out = Path(f"docs/audits/agenda-quick-{date.today().isoformat()}")
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        iphone15 = {
            "viewport": {"width": 393, "height": 852},
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
        }
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(**iphone15)
        page = context.new_page()

        page.goto(f"{ERP_URL}/login")
        page.fill("input[name='username']", user)
        page.fill("input[name='password']", pwd)
        page.click("button[type='submit']")
        page.wait_for_url(f"{ERP_URL}/")

        page.click("button[data-tab='agenda']")
        time.sleep(2.5)
        page.screenshot(path=str(out / "agenda-fullpage.png"), full_page=True)
        print(f"[OK] Screenshot guardado en {out / 'agenda-fullpage.png'}")

        time.sleep(2)
        browser.close()


if __name__ == "__main__":
    main()
