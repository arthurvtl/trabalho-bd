"""
banco.py
========
Camada de acesso ao banco de dados MySQL (Aiven).

A classe Banco concentra a conexao com o servidor e oferece metodos simples
para consultar e executar comandos. Ela tambem cuida da inicializacao: se o
banco estiver vazio (por exemplo, em uma maquina nova ou caso as tabelas tenham
sido apagadas), ela recria o esquema e recarrega os dados automaticamente, a
partir dos arquivos schema_mysql.sql e seed_mysql.sql.

A conexao usa SSL (exigido pelo Aiven). Usamos SQLAlchemy com o driver PyMySQL,
que e Python puro e facil de instalar.
"""

import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

import config

# Pasta onde este arquivo esta, para localizar os scripts .sql
PASTA = os.path.dirname(os.path.abspath(__file__))


class Banco:
    """Gerencia a conexao e a inicializacao do banco MySQL."""

    def __init__(self):
        senha = quote_plus(config.SENHA)
        url = (
            f"mysql+pymysql://{config.USUARIO}:{senha}"
            f"@{config.HOST}:{config.PORT}/{config.BANCO}"
        )
        # connect_args com ssl liga a conexao TLS exigida pelo Aiven.
        # pool_pre_ping evita usar conexoes que cairam por inatividade.
        self.engine = create_engine(
            url,
            connect_args={"ssl": {"ssl": {}}},
            pool_pre_ping=True,
            pool_recycle=280,
        )
        self.garantir_estrutura()

    # ------------------------------------------------------------------ #
    # Inicializacao automatica (auto recuperacao)
    # ------------------------------------------------------------------ #

    def garantir_estrutura(self):
        """Cria as tabelas e carrega os dados se o banco estiver vazio."""
        if self._pessoa_pronta():
            return
        self._rodar_script("schema_mysql.sql")
        if self._contar("Pessoa") == 0:
            self._rodar_script("seed_mysql.sql")

    def _pessoa_pronta(self):
        """Diz se a tabela Pessoa ja existe e tem dados."""
        try:
            return self._contar("Pessoa") > 0
        except Exception:
            return False

    def _contar(self, tabela):
        with self.engine.connect() as conn:
            return conn.execute(text(f"SELECT COUNT(*) FROM {tabela}")).scalar()

    def _rodar_script(self, nome_arquivo):
        """Le um arquivo .sql e executa cada comando."""
        caminho = os.path.join(PASTA, nome_arquivo)
        with open(caminho, encoding="utf-8") as arquivo:
            comandos = self._dividir(arquivo.read())
        with self.engine.begin() as conn:
            for comando in comandos:
                # exec_driver_sql envia o SQL direto ao driver, sem o SQLAlchemy
                # tentar interpretar os ":" como parametros.
                conn.exec_driver_sql(comando)

    @staticmethod
    def _dividir(texto):
        """Remove comentarios e linhas vazias e separa os comandos pelo ';'."""
        linhas = [
            linha for linha in texto.splitlines()
            if linha.strip() and not linha.strip().startswith("--")
        ]
        junto = "\n".join(linhas)
        return [parte.strip() for parte in junto.split(";") if parte.strip()]

    # ------------------------------------------------------------------ #
    # Operacoes basicas
    # ------------------------------------------------------------------ #

    def consultar(self, sql, parametros=None):
        """Executa um SELECT e devolve uma lista de dicionarios."""
        with self.engine.connect() as conn:
            resultado = conn.execute(text(sql), parametros or {})
            return [dict(linha) for linha in resultado.mappings().all()]

    def executar(self, sql, parametros=None):
        """Executa INSERT, UPDATE ou DELETE dentro de uma transacao."""
        with self.engine.begin() as conn:
            conn.execute(text(sql), parametros or {})

    def proximo_id(self, tabela, coluna="id"):
        """Calcula o proximo id como MAX(coluna) + 1 (para tabelas sem auto incremento)."""
        with self.engine.connect() as conn:
            return conn.execute(
                text(f"SELECT COALESCE(MAX({coluna}), 0) + 1 FROM {tabela}")
            ).scalar()
