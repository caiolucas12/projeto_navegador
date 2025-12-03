# ---- CLASSE DA PAGINA ----
class Pagina:
    def __init__(self, url, link_interno = None):
        self.url = url
        self.link_interno = link_interno or []

    def mostrar_links(self):
        '''mostra os links internos disponiveis'''
        if not self.link_interno:
            print('nenhum link disponivel')
            return
        else:
            print('Links disponíveis:')
            for i, link in enumerate(self.link_interno, 1):
                print(f"  [{i}] {link}")

    def tem_link(self, caminho):
        '''normaliza removendo espaços e a / inicial para comparação'''
        caminho_limpo = caminho.strip().lstrip('/')
        for link in self.link_interno:
            '''compara o link que ja existe com o digitado'''
            if link.strip().lstrip('/') == caminho_limpo:
                return True
        return False
