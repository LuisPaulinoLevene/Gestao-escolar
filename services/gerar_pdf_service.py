import os
from playwright.sync_api import sync_playwright


def gerar_pdf(html: str) -> bytes:

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        pagina = browser.new_page()

        pagina.set_content(
            html,
            wait_until="networkidle"
        )

        pdf = pagina.pdf(
            format="A4",
            print_background=True,
            margin={
                "top": "10mm",
                "bottom": "10mm",
                "left": "10mm",
                "right": "10mm"
            }
        )

        browser.close()

        return pdf
