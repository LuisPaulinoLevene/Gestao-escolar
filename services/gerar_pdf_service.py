import os
import glob


def gerar_pdf(html: str) -> bytes:

    print("=== LISTANDO PLAYWRIGHT ===")

    caminhos = []

    base = "/opt/render/.cache/ms-playwright"

    for caminho in glob.glob(
        base + "/**/*",
        recursive=True
    ):

        if (
            "chrome" in caminho.lower()
            or "chromium" in caminho.lower()
        ):
            caminhos.append(caminho)

    print(caminhos)

    raise Exception({
        "cache": os.path.exists(base),
        "quantidade": len(caminhos),
        "caminhos": caminhos
    })
