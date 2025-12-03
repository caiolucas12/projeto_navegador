import sys
"""Serve para encerrar o programa quando o user quiser sair"""
import os
"""Usado para limpar a tela quando o usuário muda de pagina ou quiser sair"""

from Banco_de_dados import GerenciadorBD
from Navegador import Navegador




# o nosso menu
class Sistema:
    def __init__(self):
        self.bd = GerenciadorBD()

    def menu_principal(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Menu Principal')
            print('1. Login Usuário')
            print('2. Criar Usuário')
            print('3. Login Admin')
            print('0. Sair')
            op = input('Escolha: ').strip()

            if op in ('1', 'login'):
                self.login_usuario()
            elif op in ('2', 'criar', 'criar usuario'):
                self.criar_usuario()
            elif op in ('3', 'admin'):
                self.login_admin()
            elif op in ('0', 'sair'):
                print('Saindo...')
                sys.exit()
            else:
                input('Opção inválida. ENTER...')

    def criar_usuario(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        print('--- CRIAR NOVO USUÁRIO ---')
        login = input('Login: ').strip()
        senha = input('Senha: ').strip()
        nome = input('Nome interno: ').strip()

        if not login or not senha or not nome:
            print('Login, senha e nome NÃO podem ser vazios.')
            input('ENTER...')
            return

        ok = self.bd.criar_usuario(login, senha, nome)
        if ok:
            print('Usuário criado com sucesso!')
        else:
            print('Já existe um usuário com esse login.')
        input('ENTER...')

    def login_usuario(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print('--- LOGIN ---')
        login = input('Login: ')
        senha = input('Senha: ')

        user = self.bd.validar_login(login, senha)
        if user:
            user = dict(user)
            if user["login"] == "admin":
                user["is_admin"] = True
            else:
                user["is_admin"] = False
            print(f'Bem-vindo, {user["nome"]}!')
            input('ENTER para continuar...')
            self.menu_usuario(user)
        else:
            print('Login incorreto.')
            input('ENTER...')

    def menu_usuario(self, user):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'=== Área do Usuário ({user["login"]}) ===')
            print('1. Editar Perfil')
            print('2. Abrir Navegador')
            print('0. Sair')
            op = input('Escolha: ')

            if op == '1':
                self.menu_editar_usuario(user)
            elif op == '2':
                self.abrir_navegador(user)
            elif op == '0':
                return

    def menu_editar_usuario(self, user):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'--- Editar Usuário: {user["login"]} ---')
            print('1. Editar seu Nome de Usuário')
            print('2. Editar Seu Nome')
            print('3. Editar sua Senha')
            print('0. Voltar')
            op = input('Escolha: ')

            if op == '1':  # editar login
                novo_login = input('Novo Nome de Usuário: ').strip()
                if not novo_login:
                    print('Login inválido.')
                else:
                    if self.bd.atualizar_login(user['login'], novo_login):
                        user['login'] = novo_login
                        print('Login atualizado!')
                    else:
                        print('Login já em uso.')
                input('ENTER...')

            elif op == '2':  # editar nome
                novo_nome = input('Novo nome: ').strip()
                if novo_nome:
                    self.bd.atualizar_nome(user['login'], novo_nome)
                    user['nome'] = novo_nome
                    print('Nome atualizado!')
                else:
                    print('Nome inválido.')
                input('ENTER...')

            elif op == '3':  # editar senha
                nova_senha = input('Nova senha: ').strip()
                if nova_senha:
                    self.bd.atualizar_senha(user['login'], nova_senha)
                    user['senha'] = nova_senha
                    print('Senha atualizada!')
                else:
                    print('Senha inválida.')
                input('ENTER...')


            elif op == '0':
                return

    def login_admin(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print('--- LOGIN ADMIN ---')
        user = input('User: ')
        senha = input('Senha: ')

        if user == 'admin' and senha == 'admin':
            self.menu_admin()
        else:
            print('Acesso negado.')
            input('ENTER...')

    def abrir_navegador(self, user_info):
        nav = Navegador(user_info)
        nav.loop()

    def menu_admin(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('=== MENU ADMIN ===')
            print('1. Criar Página (#add)')
            print('2. Adicionar Link (#addlink)')
            print('3. Listar Usuários')
            print('4. Excluir Usuário')
            print('5. Abrir Navegador (Admin)')
            print('0. Sair')

            op = input('Escolha: ')

            if op == '1':
                url = input('URL nova: ')
                if self.bd.adicionar_pagina(url):
                    print('Página criada!')
                else:
                    print('Página já existe!')
                input('ENTER...')

            elif op == '2':
                pai = input('URL principal: ')
                link = input('Link interno: ')

                if not self.bd.existe_pagina(pai):
                    print('Essa página não existe!')
                    input('ENTER...')
                else:
                    self.bd.adicionar_link(pai, link)
                    print('Link adicionado!')
                    input('ENTER...')

            elif op == '3':
                lista_usuarios = self.bd.listar_usuarios()
                if not lista_usuarios:
                    print('Nenhum usuário cadastrado.')
                else:
                    print('---# USUÁRIOS CADASTRADOS #---')
                    for u in lista_usuarios:
                        print(f'ID: {u["id"]} - Login: {u["login"]} ({u["nome"]}) | Senha: {u["senha"]}')
                input('ENTER...')

            elif op == '4':
                alvo = input('Login do usuário a excluir: ').strip()
                if alvo == 'admin':
                    print("Você não pode excluir o administrador.")
                    input("ENTER para continuar...")
                    continue

                cursor = self.bd.conn.execute('DELETE FROM usuarios WHERE login = ?', (alvo,))
                self.bd.conn.commit()
                if cursor.rowcount == 0: #  verifica quantas linhas foram alteradas no delete, se forem mais que 0, deletou realmente, se não, provavelmente o nome foi digitado incorretamente e n deletou ngm
                    print('Nenhum usuário encontrado com esse login.')
                else:
                    print('Usuário removido.')
                input('ENTER...')

            elif op == '5': # navegador no modo adm
                admin_info = {'login': 'admin', 'nome': 'Admin', 'is_admin': True}
                self.abrir_navegador(admin_info)

            elif op == '0':
                return