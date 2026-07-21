from playwright.sync_api import sync_playwright


def gerar_pdf(html: str) -> bytes:

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
                "--disable-setuid-sandbox",
            ],
        )

        page = browser.new_page()

        page.set_content(
            html,
            wait_until="networkidle"
        )

        # Espera todas as imagens carregarem
        page.evaluate("""
            () => Promise.all(
                Array.from(document.images).map(img => {
                    if (img.complete) {
                        return Promise.resolve();
                    }
                    return new Promise(resolve => {
                        img.onload = resolve;
                        img.onerror = resolve;
                    });
                })
            )
        """)

        page.wait_for_timeout(1000)

        pdf = page.pdf(
            format="A4",
            print_background=True,
            margin={
                "top": "10mm",
                "bottom": "10mm",
                "left": "10mm",
                "right": "10mm",
            },
        )

        browser.close()

        return pdf