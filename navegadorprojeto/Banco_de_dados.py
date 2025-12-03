import sqlite3
"""Nosso banco de dados que vai criar o arquivo navegador.py, permite também comandos para salvar nossas paginas, links e historico, pra persistirem os dados"""

class GerenciadorBD:
    """Gerencia o uso do sqlite, todas as paginas e links internos"""

    def __init__(self, nome_banco="navegador.bd"):
        """inicia o programa e cria as tabelas"""
        self.conn = sqlite3.connect(nome_banco)          #   abre ou cria o banco
        self.conn.row_factory = sqlite3.Row              #   faz com que as consultas retorrnem dict (cada linha vira um dict)
        self._criar_tabelas()                            #   garante que as tabelas existam

    def _criar_tabelas(self):
        """Func que vai criar as tabelas de pag, usuarios e links internos"""
        cursor = self.conn.cursor()                      #   conn conecta com o banco e o cursor executa os comandos dentro do banco

        #   a tabela das nossas pag cadastradas
        sql_paginas = """
            CREATE TABLE IF NOT EXISTS paginas (
                url TEXT PRIMARY KEY
            );
        """

        cursor.execute(sql_paginas)                      #   executa a criação da tabela de pag

        sql_links = """
            CREATE TABLE IF NOT EXISTS links_internos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_principal TEXT NOT NULL,
                link TEXT NOT NULL
            );
        """

        cursor.execute(sql_links)                        #   executa a criação da tablea de links

        sql_usuarios = """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                nome TEXT NOT NULL,
                email TEXT
            );
        """

        cursor.execute(sql_usuarios)                     #   executa a criação da tabela de usuarios

        cursor.execute("INSERT OR IGNORE INTO usuarios (login, senha, nome, email) VALUES ('admin', 'admin', 'Administrador', NULL)")

        self.conn.commit()                               #   salva tudo no bc

    def adicionar_pagina(self, url):
        try:
            self.conn.execute("INSERT INTO paginas (url) VALUES (?)", (url,))          #   o ? garante que o banco receba o valor da url na forma de texto
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:                                                  #   não deixa o codigo quebrar em caso de tentativa de cadastro de duplicatas
            return False

    def adicionar_link(self, url_principal, link):
        self.conn.execute("INSERT INTO links_internos (url_principal, link) VALUES (?, ?)", (url_principal, link))    #   o ? tem a mesma função aqui
        self.conn.commit()                               #    salva no bc

    def existe_pagina(self, url):
        cursor = self.conn.execute("SELECT 1 FROM paginas WHERE url = ?", (url,))      #   SELECT 1  + o fetchone nao traz os dados, so verifica se existe algo, o que deixa o codigo mais leve
        return cursor.fetchone() is not None                                           #   retorna true se existe, false se nao achar nada

    def obter_links(self, url_principal):
        cursor = self.conn.execute("SELECT link FROM links_internos WHERE url_principal = ?", (url_principal,))              #   busca apenas a coluna de link onde a determinada url principal bate com o site atual
        return [r["link"] for r in cursor.fetchall()]                                                                      #   transforma o resultado do banco em uma lista simples, pegando todos os links referidos a essa url



    #   os users do navegador

    def criar_usuario(self, login, senha, nome, email=None):
        try:
            self.conn.execute("INSERT INTO usuarios (login, senha, nome, email) VALUES (?, ?, ?, ?)", (login, senha, nome, email))    #   insere no bc os dados do novo user
            self.conn.commit()                               #   salva no bc
            return True
        except sqlite3.IntegrityError:
            return False                                     #   retorna false se o login ja existir, evitando duplicatas e impedindo que o cod quebre

    def validar_login(self, login, senha):
        cursor = self.conn.execute("SELECT * FROM usuarios WHERE login = ? AND senha = ?", (login, senha))              #   busca a linha de login e senha para validar
        return cursor.fetchone()                                                                                       #   retorna os dados do usuario ou none se o user errou os dados de login

    def listar_usuarios(self):                               #   usado pelo admin para ver quem esta cadastrado
        cursor = self.conn.execute("SELECT id, login, nome, senha FROM usuarios")
        return cursor.fetchall()                             #   retorna as infos de todos os users

    def atualizar_login(self, login_original, novo_login):
        try:
            self.conn.execute(
                "UPDATE usuarios SET login = ? WHERE login = ?",
                (novo_login, login_original)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def atualizar_nome(self, login, novo_nome):
        self.conn.execute(
            "UPDATE usuarios SET nome = ? WHERE login = ?",
            (novo_nome, login)
        )
        self.conn.commit()

    def atualizar_senha(self, login, nova_senha):
        self.conn.execute(
            "UPDATE usuarios SET senha = ? WHERE login = ?",
            (nova_senha, login)
        )
        self.conn.commit()

    def fechar(self) -> None:
        """Fecha a conexão com o banco"""
        try:
           self.conn.close()
        except Exception:
           pass