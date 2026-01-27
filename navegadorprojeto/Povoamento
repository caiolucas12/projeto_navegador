from Banco_de_dados import GerenciadorBD

bd = GerenciadorBD()

paginas = [
    "home",
    "home/produtos",
    "home/produtos/pc",
    "home/produtos/notebook",
    "home/produtos/celular",
    "home/servicos",
    "home/servicos/manutencao",
    "home/servicos/consultoria",
    "home/sobre"
]

for url in paginas:
    bd.adicionar_pagina(url)


links_internos = {
    "home": [
        "home/produtos",
        "home/servicos",
        "home/sobre"
    ],
    "home/produtos": [
        "home/produtos/pc",
        "home/produtos/notebook",
        "home/produtos/celular"
    ],
    "home/servicos": [
        "home/servicos/manutencao",
        "home/servicos/consultoria"
    ]
}

for pagina_pai, filhos in links_internos.items():
    for filho in filhos:
        bd.adicionar_link(pagina_pai, filho)


bd.fechar()

print("Banco povoado com sucesso.")