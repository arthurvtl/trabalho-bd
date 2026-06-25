"""
main.py
=======
Interface do programa: um menu interativo de terminal que permite operar o
banco do Centro de Treinamento.

Pelo menu da para:
  1. Fazer o CRUD da tabela Esporte (inserir, listar, alterar e excluir).
  2. Fazer o CRUD da entidade Aluno (que envolve as tabelas Pessoa e Aluno).
  3. Executar os 8 relatorios (consultas SQL) da Secao 9 do relatorio.

Assim o programa atende as duas opcoes que o trabalho permite ao mesmo tempo:
um CRUD completo E um menu de acesso as consultas.

Como rodar:
    python main.py

Na primeira execucao o banco (ct.db) e criado e populado automaticamente.
"""

import sqlite3

from database import Database
from models import Esporte, Aluno
from repository import EsporteRepository, AlunoRepository
from relatorios import Relatorios


class App:
    """Controla o fluxo da interface de menu."""

    def __init__(self):
        self.db = Database()
        self.esporte_repo = EsporteRepository(self.db)
        self.aluno_repo = AlunoRepository(self.db)
        self.relatorios = Relatorios(self.db)

    # ======================================================================
    # Utilidades de interface (entrada e saida de texto)
    # ======================================================================

    def titulo(self, texto):
        """Imprime um titulo de secao destacado."""
        print()
        print("=" * 60)
        print(f"  {texto}")
        print("=" * 60)

    def imprimir_tabela(self, titulos, linhas):
        """
        Imprime resultados em forma de tabela de texto, calculando a largura
        de cada coluna pelo maior valor. Funciona para qualquer consulta.
        """
        if not linhas:
            print("\n(Nenhum registro encontrado.)\n")
            return

        # Transforma cada celula em texto e calcula a largura de cada coluna.
        matriz = [[self._formatar_celula(valor) for valor in linha] for linha in linhas]
        larguras = []
        for indice, titulo in enumerate(titulos):
            largura_dados = max((len(linha[indice]) for linha in matriz), default=0)
            larguras.append(max(len(str(titulo)), largura_dados))

        separador = "-+-".join("-" * largura for largura in larguras)
        cabecalho = " | ".join(str(t).ljust(larguras[i]) for i, t in enumerate(titulos))

        print()
        print(cabecalho)
        print(separador)
        for linha in matriz:
            print(" | ".join(valor.ljust(larguras[i]) for i, valor in enumerate(linha)))
        print(f"\n({len(linhas)} registro(s).)\n")

    def _formatar_celula(self, valor):
        """Converte um valor do banco em texto amigavel para a tabela."""
        if valor is None:
            return "(nulo)"
        return str(valor)

    def ler_texto(self, rotulo, obrigatorio=True, atual=None):
        """
        Le um texto do teclado. Se 'atual' for informado (modo edicao),
        pressionar Enter mantem o valor atual.
        """
        sufixo = f" [{atual}]" if atual is not None else ""
        while True:
            valor = input(f"{rotulo}{sufixo}: ").strip()
            if valor == "" and atual is not None:
                return atual
            if valor == "" and not obrigatorio:
                return ""
            if valor != "":
                return valor
            print("  Valor obrigatorio. Tente novamente.")

    def ler_inteiro(self, rotulo, atual=None):
        """Le um numero inteiro do teclado, repetindo ate ser valido."""
        sufixo = f" [{atual}]" if atual is not None else ""
        while True:
            valor = input(f"{rotulo}{sufixo}: ").strip()
            if valor == "" and atual is not None:
                return atual
            try:
                return int(valor)
            except ValueError:
                print("  Digite um numero inteiro valido.")

    def ler_sim_nao(self, rotulo, atual=None):
        """Le uma resposta sim/nao e devolve True/False."""
        padrao = None
        if atual is not None:
            padrao = "s" if atual else "n"
        sufixo = f" [{padrao}]" if padrao is not None else " (s/n)"
        while True:
            valor = input(f"{rotulo}{sufixo}: ").strip().lower()
            if valor == "" and padrao is not None:
                return atual
            if valor in ("s", "sim"):
                return True
            if valor in ("n", "nao"):
                return False
            print("  Responda com 's' ou 'n'.")

    def pausar(self):
        input("Pressione Enter para continuar...")

    # ======================================================================
    # Menu principal
    # ======================================================================

    def executar(self):
        opcoes = {
            "1": ("CRUD de Esporte", self.menu_esporte),
            "2": ("CRUD de Aluno", self.menu_aluno),
            "3": ("Relatorios (consultas SQL)", self.menu_relatorios),
        }
        while True:
            self.titulo("Sistema de Gestao de Centro de Treinamento (CT)")
            for chave, (rotulo, _) in opcoes.items():
                print(f"  {chave}. {rotulo}")
            print("  0. Sair")
            escolha = input("\nEscolha uma opcao: ").strip()

            if escolha == "0":
                print("\nEncerrando. Ate logo!\n")
                self.db.fechar()
                break
            if escolha in opcoes:
                opcoes[escolha][1]()
            else:
                print("\nOpcao invalida.\n")

    # ======================================================================
    # CRUD de Esporte
    # ======================================================================

    def menu_esporte(self):
        acoes = {
            "1": ("Listar esportes", self.esporte_listar),
            "2": ("Inserir esporte", self.esporte_inserir),
            "3": ("Alterar esporte", self.esporte_alterar),
            "4": ("Excluir esporte", self.esporte_excluir),
        }
        while True:
            self.titulo("CRUD de Esporte")
            for chave, (rotulo, _) in acoes.items():
                print(f"  {chave}. {rotulo}")
            print("  0. Voltar")
            escolha = input("\nEscolha uma opcao: ").strip()
            if escolha == "0":
                return
            if escolha in acoes:
                acoes[escolha][1]()
                self.pausar()
            else:
                print("\nOpcao invalida.\n")

    def esporte_listar(self):
        esportes = self.esporte_repo.listar()
        titulos = ["id", "nome", "tipo", "descricao"]
        linhas = [(e.id, e.nome, e.tipo, e.descricao) for e in esportes]
        self.imprimir_tabela(titulos, linhas)

    def esporte_inserir(self):
        print("\n-- Novo esporte --")
        nome = self.ler_texto("Nome")
        descricao = self.ler_texto("Descricao", obrigatorio=False)
        eh_coletivo = self.ler_sim_nao("E um esporte coletivo?")
        novo = Esporte(nome=nome, descricao=descricao, eh_coletivo=eh_coletivo)
        self.esporte_repo.criar(novo)
        print(f"\nEsporte inserido com sucesso (id {novo.id}).")

    def esporte_alterar(self):
        id = self.ler_inteiro("\nId do esporte a alterar")
        esporte = self.esporte_repo.buscar_por_id(id)
        if not esporte:
            print("Esporte nao encontrado.")
            return
        print("Deixe em branco para manter o valor atual.")
        esporte.nome = self.ler_texto("Nome", atual=esporte.nome)
        esporte.descricao = self.ler_texto("Descricao", obrigatorio=False, atual=esporte.descricao)
        esporte.eh_coletivo = self.ler_sim_nao("E um esporte coletivo?", atual=esporte.eh_coletivo)
        if self.esporte_repo.atualizar(esporte):
            print("\nEsporte atualizado com sucesso.")
        else:
            print("\nNada foi atualizado.")

    def esporte_excluir(self):
        id = self.ler_inteiro("\nId do esporte a excluir")
        esporte = self.esporte_repo.buscar_por_id(id)
        if not esporte:
            print("Esporte nao encontrado.")
            return
        print(f"Esporte selecionado: {esporte}")
        if not self.ler_sim_nao("Confirma a exclusao?"):
            print("Exclusao cancelada.")
            return
        try:
            self.esporte_repo.excluir(id)
            print("\nEsporte excluido com sucesso.")
        except sqlite3.IntegrityError:
            # Disparado pela regra ON DELETE RESTRICT quando ha uma Turma usando
            # este esporte. Avisamos o usuario em vez de quebrar o programa.
            print("\nNao foi possivel excluir: existe(m) turma(s) vinculada(s) "
                  "a este esporte.")

    # ======================================================================
    # CRUD de Aluno
    # ======================================================================

    def menu_aluno(self):
        acoes = {
            "1": ("Listar alunos", self.aluno_listar),
            "2": ("Inserir aluno", self.aluno_inserir),
            "3": ("Alterar aluno", self.aluno_alterar),
            "4": ("Excluir aluno", self.aluno_excluir),
        }
        while True:
            self.titulo("CRUD de Aluno")
            for chave, (rotulo, _) in acoes.items():
                print(f"  {chave}. {rotulo}")
            print("  0. Voltar")
            escolha = input("\nEscolha uma opcao: ").strip()
            if escolha == "0":
                return
            if escolha in acoes:
                acoes[escolha][1]()
                self.pausar()
            else:
                print("\nOpcao invalida.\n")

    def aluno_listar(self):
        alunos = self.aluno_repo.listar()
        titulos = ["id", "nome", "cpf", "email", "data_nasc", "data_matricula", "condicao_saude"]
        linhas = [(a.id, a.nome, a.cpf, a.email, a.data_nasc, a.data_matricula, a.condicao_saude)
                  for a in alunos]
        self.imprimir_tabela(titulos, linhas)

    def aluno_inserir(self):
        print("\n-- Novo aluno --")
        nome = self.ler_texto("Nome")
        cpf = self.ler_texto("CPF")
        email = self.ler_texto("E-mail", obrigatorio=False)
        data_nasc = self.ler_texto("Data de nascimento (AAAA-MM-DD)", obrigatorio=False)
        data_matricula = self.ler_texto("Data de matricula (AAAA-MM-DD)", obrigatorio=False)
        condicao_saude = self.ler_texto("Condicao de saude", obrigatorio=False)
        novo = Aluno(nome=nome, cpf=cpf, email=email, data_nasc=data_nasc,
                     data_matricula=data_matricula, condicao_saude=condicao_saude)
        self.aluno_repo.criar(novo)
        print(f"\nAluno inserido com sucesso (id {novo.id}).")

    def aluno_alterar(self):
        id = self.ler_inteiro("\nId do aluno a alterar")
        aluno = self.aluno_repo.buscar_por_id(id)
        if not aluno:
            print("Aluno nao encontrado.")
            return
        print("Deixe em branco para manter o valor atual.")
        aluno.nome = self.ler_texto("Nome", atual=aluno.nome)
        aluno.cpf = self.ler_texto("CPF", atual=aluno.cpf)
        aluno.email = self.ler_texto("E-mail", obrigatorio=False, atual=aluno.email)
        aluno.data_nasc = self.ler_texto("Data de nascimento", obrigatorio=False, atual=aluno.data_nasc)
        aluno.data_matricula = self.ler_texto("Data de matricula", obrigatorio=False, atual=aluno.data_matricula)
        aluno.condicao_saude = self.ler_texto("Condicao de saude", obrigatorio=False, atual=aluno.condicao_saude)
        if self.aluno_repo.atualizar(aluno):
            print("\nAluno atualizado com sucesso.")
        else:
            print("\nNada foi atualizado.")

    def aluno_excluir(self):
        id = self.ler_inteiro("\nId do aluno a excluir")
        aluno = self.aluno_repo.buscar_por_id(id)
        if not aluno:
            print("Aluno nao encontrado.")
            return
        print(f"Aluno selecionado: {aluno}")
        print("Observacao: as matriculas deste aluno tambem serao removidas (ON DELETE CASCADE).")
        if not self.ler_sim_nao("Confirma a exclusao?"):
            print("Exclusao cancelada.")
            return
        self.aluno_repo.excluir(id)
        print("\nAluno excluido com sucesso.")

    # ======================================================================
    # Menu de Relatorios
    # ======================================================================

    def menu_relatorios(self):
        lista = self.relatorios.todos()
        while True:
            self.titulo("Relatorios (consultas SQL da Secao 9)")
            for indice, (rotulo, _) in enumerate(lista, start=1):
                print(f"  {indice}. {rotulo}")
            print("  0. Voltar")
            escolha = input("\nEscolha um relatorio: ").strip()
            if escolha == "0":
                return
            if escolha.isdigit() and 1 <= int(escolha) <= len(lista):
                rotulo, funcao = lista[int(escolha) - 1]
                titulos, linhas = funcao()
                self.titulo(rotulo)
                self.imprimir_tabela(titulos, linhas)
                self.pausar()
            else:
                print("\nOpcao invalida.\n")


if __name__ == "__main__":
    try:
        App().executar()
    except KeyboardInterrupt:
        # Permite sair com Ctrl+C sem mostrar um erro feio.
        print("\n\nPrograma interrompido pelo usuario.\n")
