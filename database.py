"""
database.py
===========
Camada de acesso ao banco de dados SQLite.

A classe Database concentra toda a conversa com o arquivo .db:
  - abre a conexao;
  - liga a verificacao de chaves estrangeiras (PRAGMA foreign_keys);
  - na primeira execucao, cria as tabelas (schema.sql) e carrega os dados
    iniciais (seed.sql).

Usamos apenas a biblioteca padrao do Python (sqlite3), entao nao e preciso
instalar nada. O banco fica num unico arquivo (ct.db) criado ao lado deste
script.
"""

import os
import sqlite3

# Caminho absoluto da pasta onde este arquivo esta. Usar isto garante que o
# programa encontra schema.sql, seed.sql e ct.db nao importa de qual pasta o
# professor execute o "python main.py".
PASTA = os.path.dirname(os.path.abspath(__file__))

CAMINHO_BANCO = os.path.join(PASTA, "ct.db")
CAMINHO_SCHEMA = os.path.join(PASTA, "schema.sql")
CAMINHO_SEED = os.path.join(PASTA, "seed.sql")


class Database:
    """Gerencia a conexao e a inicializacao do banco SQLite."""

    def __init__(self, caminho_banco=CAMINHO_BANCO):
        self.caminho_banco = caminho_banco
        # Descobrimos se o banco ja existia ANTES de abrir a conexao, porque
        # abrir a conexao ja cria o arquivo vazio.
        banco_novo = not os.path.exists(self.caminho_banco)

        self.conexao = sqlite3.connect(self.caminho_banco)
        # row_factory = sqlite3.Row permite acessar colunas pelo nome
        # (ex.: linha["nome"]) alem do indice, deixando o codigo mais legivel.
        self.conexao.row_factory = sqlite3.Row
        # Liga a integridade referencial. No SQLite ela vem DESLIGADA por padrao
        # e precisa ser ativada em cada conexao.
        self.conexao.execute("PRAGMA foreign_keys = ON;")

        if banco_novo:
            self.inicializar()

    def inicializar(self):
        """Cria as tabelas e carrega os dados iniciais a partir dos .sql."""
        print("Banco nao encontrado. Criando esquema e carregando dados iniciais...")
        self._executar_script(CAMINHO_SCHEMA)
        self._executar_script(CAMINHO_SEED)
        self.conexao.commit()
        print("Banco criado com sucesso (arquivo ct.db).\n")

    def _executar_script(self, caminho_sql):
        """Le um arquivo .sql inteiro e o executa no banco."""
        with open(caminho_sql, "r", encoding="utf-8") as arquivo:
            script = arquivo.read()
        # executescript roda varios comandos SQL separados por ponto e virgula.
        self.conexao.executescript(script)

    def executar(self, sql, parametros=()):
        """
        Executa um comando de escrita (INSERT, UPDATE, DELETE), confirma a
        transacao e devolve o cursor (util para pegar lastrowid ou rowcount).
        """
        cursor = self.conexao.execute(sql, parametros)
        self.conexao.commit()
        return cursor

    def consultar(self, sql, parametros=()):
        """Executa uma consulta (SELECT) e devolve todas as linhas."""
        cursor = self.conexao.execute(sql, parametros)
        return cursor.fetchall()

    def consultar_um(self, sql, parametros=()):
        """Executa uma consulta e devolve apenas a primeira linha (ou None)."""
        cursor = self.conexao.execute(sql, parametros)
        return cursor.fetchone()

    def fechar(self):
        """Fecha a conexao com o banco."""
        self.conexao.close()
