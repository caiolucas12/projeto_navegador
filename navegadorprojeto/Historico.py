# ---- CLASSE PARA O HISTORICO ----
class Historico:
    def __init__(self):
        self.paginas = [] #lista com as ultimas paginas web visitadas

    def adicionar(self, url): #adicionar uma pagina ao historico
        self.paginas.append(url)

    # função para ser usada quando o usuario quiser voltar sua pagina
    def voltar(self):
        if not self.paginas:
            return None
        return self.paginas.pop()

    #apenas para formatar da maneira certa
    def formatar(self):
        if not self.paginas:
            return '[]'
        return "["+"][".join(self.paginas) + "]"