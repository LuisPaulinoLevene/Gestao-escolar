import os
import glob


def gerar_pdf(html: str) -> bytes:

    print("=== LISTANDO PLAYWRIGHT ===")

    for caminho in glob.glob(
        "/opt/render/.cache/ms-playwright/**/*",
        recursive=True
    ):
        if "chrome" in caminho:
            print(caminho)

    raise Exception("Teste de caminho concluído")
