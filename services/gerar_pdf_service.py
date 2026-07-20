import os

def gerar_pdf(html):

    caminhos = [
        "/opt/render",
        "/opt/render/project",
        "/opt/render/project/src",
        "/opt/render/.cache",
        "/opt/render/project/.cache",
        "/opt/render/project/src/.cache",
    ]

    resultado = {}

    for p in caminhos:
        resultado[p] = os.path.exists(p)

    raise Exception(resultado)
