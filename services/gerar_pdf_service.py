from playwright.sync_api import sync_playwright


CHROME_PATH = (
    "/opt/render/.cache/ms-playwright/"
    "chromium-1228/chrome-linux64/chrome"
)


def gerar_pdf(html: str) -> bytes:

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        pagina = browser.new_page()

        pagina.set_content(
            html,
            wait_until="networkidle"
        )

        pagina.wait_for_timeout(1000)

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
