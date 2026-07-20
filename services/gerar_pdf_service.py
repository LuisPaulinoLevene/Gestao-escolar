from services import playwright_service

playwright = None
browser = None
async def gerar_pdf(html: str) -> bytes:

    page = await playwright_service.browser.new_page(
        viewport={
            "width": 900,
            "height": 1200
        }
    )

    try:
        await page.set_content(
            html,
            wait_until="load"
        )

        await page.emulate_media(
            media="print"
        )

        pdf = await page.pdf(
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={
                "top": "10mm",
                "bottom": "10mm",
                "left": "10mm",
                "right": "10mm"
            }
        )

        return pdf

    finally:
        await page.close()