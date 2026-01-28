import sys
"""Serve para encerrar o programa quando o user quiser sair"""
import os
"""Usado para limpar a tela quando o usuário muda de pagina ou quiser sair"""

from Banco_de_dados import GerenciadorBD
from Pagina import Pagina
from Historico import Historico

# CLASSE PARA O NAVEGADOR
class Navegador:
    def __init__(self, user_info=None):
        self.user_info = user_info or {'login': 'guest', 'nome': 'Visitante', 'is_admin': False}
        self.bd = GerenciadorBD() #a lista self.paginas vai pegar todas as paginas cadastradas que aparecerá futuramente
        self.paginas = {}
        self.historico = Historico() #cria um historico para o navegador
        self.home = None
        self._carregar_paginas_do_bd()

    def normalizar_url(self, base, caminho):
        if caminho.startswith('/'):
            caminho = caminho.lstrip('/')
        return f"{base.rstrip('/')}/{caminho}"


    def _carregar_paginas_do_bd(self):
        """Lê tabelas paginas e links_internos e preenche self.paginas."""
        cur = self.bd.conn.execute("SELECT url FROM paginas")
        rows = cur.fetchall()
        for r in rows:
            url = r["url"]
            # cria Pagina com lista vazia pra ser preenchida
            self.paginas[url] = Pagina(url, link_interno=[])

        # agora vai ler links e anexar
        cur2 = self.bd.conn.execute("SELECT url_principal, link FROM links_internos ORDER BY id")
        for r in cur2.fetchall():
            pai = r["url_principal"]
            link = r["link"]
            if pai in self.paginas:
                self.paginas[pai].link_interno.append(link)
            else:
                # inconsistência: criar a página pai com o link
                self.paginas[pai] = Pagina(pai, link_interno=[link])

    def _limpar_tela(self):
        """Limpa a tela do terminal de forma compatível com Windows/Linux/Mac."""
        os.system('cls' if os.name == 'nt' else 'clear')



    #gerar a interface do jeito que o professor pediu
    def interface(self):
        print(f'Historico de visitas: {self.historico.formatar()}')

        if self.home:
            '''mostra o conteuco da pag'''
            print(f'Home: {self.home}')

            if self.home in self.paginas:
                '''se a pag existe no dict mostra os links dela'''
                self.paginas[self.home].mostrar_links()

            else:
                print('Conteúdo não carregado.')

        else:
            print('Home: [Pagina inicial / Vazio] ')
        print('Comandos: URL | número (atalho link) | /caminho (link relativo) |')
        print('#add url | #addlink url_principal link | #back | #list | #showhist | #help | #sair')
        print()

    '''é boa pratica colocar os metodos de alto nível antes dos de baixo nivel, por isso verão muitas funcionalidades que só aparecerão mais tarde no codigo '''
    def acessar(self, entrada): # esse metodo vai ler o primeiro caractere que o usuario digitar, veja abaixo:
        entrada = entrada.strip()
        if not entrada:
            return

        if entrada.startswith('#'): #começar com '#' significa que o usuario quer usar alguma funcionalidade, como #back
            self.executar_comando(entrada) #terá um metodo somente para executar o comando
            return

        if entrada.startswith('/'):
            self.acessar_url_interno(entrada)
            return
        if entrada.isdigit():
            self.acessar_por_indice(entrada)
            return
        else:
            self.acessar_url(entrada)


    def executar_comando(self, comando):

        partes = comando.split()
        cmd = partes[0].lower()
        comandos_admin = {'#add', '#addlink'}
        cmd_base = partes[0].lower()

        if not self.user_info.get('is_admin', False) and cmd_base in comandos_admin:
            print("Você não tem permissão para usar este comando. Somente administradores podem usar isso.")
            input("ENTER para continuar...")
            return


        if cmd == '#back':
            anterior = self.historico.voltar()
            if anterior:
                self.home = anterior
                print(f"Voltando para {self.home}.... ")
            else:
                print('Nada para voltar no histórico.')
                input('ENTER para continuar...')

        elif cmd == '#add':
            if len(partes)<2:
                print("Uso: #add (url)")
                input('ENTER....')
                return

            url = partes[1]
            ok = self.bd.adicionar_pagina(url)

            if ok:
                self.paginas[url] = Pagina(url, link_interno=[])
                print(f"Pagina '{url}' adicionada com sucesso")
            else:
                print(f"A página '{url}' já existe")
            input('ENTER para continuar...')

        elif cmd == '#addlink': # adicionar link interno
            if len(partes) < 3:
                print('Uso: #addlink (url_principal) (link)')
                input('ENTER....')
                return

            url_principal = partes[1]
            link = self.normalizar_url(url_principal, partes[2])
            if not self.bd.existe_pagina(url_principal):
                print('A página principal não existe.')
                input('ENTER....')
                return
            if link == url_principal:
                print('Uma página não pode apontar para ela mesma.')
                input('ENTER...')
                return
            self.bd.adicionar_link(url_principal, link)
            self.paginas[url_principal].link_interno.append(link)
            print(f'Link "{link}" adicionado à página "{url_principal}".')
            input('ENTER para continuar...')

        elif cmd == '#list':    #lista as paginas cadastradas
            if not self.paginas:
                print('Nenhuma pagina cadastrada')
            else:
              print('Paginas cadastradas:')
              for url in self.paginas:
                  print(f' - {url}')
            input('ENTER para continuar...')

        elif cmd == '#showhist':  #mostra o histórico
            if not self.historico.paginas:
                print('Histórico vazio.')
            else:
                print('Histórico de visitas: ')
                print(self.historico.formatar())
            input('ENTER para continuar...')

        elif cmd == '#help':
            print('Comandos disponíveis:\n')

            print('  URL        - Abre uma página pelo endereço informado')
            print('    Ex: site.com\n')

            print('  número     - Abre um link interno pelo número exibido')
            print('    Ex: 1\n')

            print('  /caminho   - Abre um link relativo à página atual')
            print('    Ex: /contato\n')

            print('  #add url   - (Admin) Cadastra uma nova página')
            print('    Ex: #add site.com\n')

            print('  #addlink url_principal link - (Admin) Adiciona um link interno a uma página')
            print('    Ex: #addlink site.com/home menu\n')

            print('  #back      - Volta para a página anterior\n')

            print('  #list      - Lista todas as páginas cadastradas\n')

            print('  #showhist  - Mostra o histórico de navegação\n')

            print('  #sair      - Encerra o navegador\n')

            input('ENTER para continuar...')


        elif cmd == '#sair':              #sai do navegador
            print('Saindo do navegador...')
            self.bd.fechar()              #usado para fechar o banco
            sys.exit()                    #usado para saída limpa

        else:
            print('Comando inválido, use #help para ver os comandos disponíveis.')
            input('ENTER para continuar...')

    def acessar_url(self, url):

        if url in self.paginas:

            if self.home:
                self.historico.adicionar(self.home) #vai colocar a home no historico
            self.home = url

        else:
            print('Pagina não encontrada\n')
            input('Pressione ENTER para continuar.....')

    def acessar_url_interno(self, caminho):
        if not self.home:
            print('Abra uma página primeiro.')
            input("ENTER...")
            return

        nova_url = self.normalizar_url(self.home, caminho)

        pagina_atual = self.paginas[self.home]

        # evita duplicação
        if nova_url not in pagina_atual.link_interno:
            pagina_atual.link_interno.append(nova_url)
            self.bd.adicionar_link(self.home, nova_url)

        if nova_url not in self.paginas:
            self.bd.adicionar_pagina(nova_url)
            self.paginas[nova_url] = Pagina(nova_url, [])

        self.historico.adicionar(self.home)
        self.home = nova_url



    def acessar_por_indice(self, escolha_usuario):
        if not self.home:
            print('Abra uma página primeiro.')
            return

        pagina_atual = self.paginas[self.home]

        try:
            indice = int(escolha_usuario) - 1
        except ValueError:
            return

        if indice < 0 or indice >= len(pagina_atual.link_interno):
            return

        proxima_url = pagina_atual.link_interno[indice]

        if proxima_url not in self.paginas:
            self.bd.adicionar_pagina(proxima_url)
            self.paginas[proxima_url] = Pagina(proxima_url, [])

        self.historico.adicionar(self.home)
        self.home = proxima_url



    def loop(self):
        """é o loop do navegador, que vai fazer aparecer a interface na tela e ler as entradas"""
        try:
            while True:
                self._limpar_tela()
                self.interface()
                entrada = input('URL / comando: ').strip()
                if not entrada:
                    continue
                self.acessar(entrada)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            """garante q o banco seja fechado no final"""
            self.bd.fechar()