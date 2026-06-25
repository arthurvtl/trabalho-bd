"""
repository.py
=============
Camada de repositorio: e aqui que cada entidade ganha suas operacoes de CRUD
(Create, Read, Update, Delete).

Separar o repositorio das classes de modelo (models.py) e uma boa pratica de
orientacao a objetos: o modelo guarda os dados e o repositorio sabe como
ler e gravar esses dados no banco. Assim, se um dia trocarmos o SQLite por
outro banco, so mexemos aqui.

Cada metodo usa consultas parametrizadas (com "?"), o que evita SQL Injection
e cuida do escape de aspas automaticamente.
"""

from models import Esporte, Aluno


class EsporteRepository:
    """CRUD completo da tabela Esporte (a tabela escolhida para o CRUD principal)."""

    def __init__(self, db):
        self.db = db

    # ---- CREATE ----
    def criar(self, esporte):
        """Insere um novo esporte. O id e gerado como MAX(id) + 1."""
        proximo_id = self._proximo_id()
        self.db.executar(
            "INSERT INTO Esporte (id, nome, descricao, eh_coletivo) VALUES (?, ?, ?, ?)",
            (proximo_id, esporte.nome, esporte.descricao, 1 if esporte.eh_coletivo else 0),
        )
        esporte.id = proximo_id
        return esporte

    # ---- READ ----
    def listar(self):
        """Devolve todos os esportes como uma lista de objetos Esporte."""
        linhas = self.db.consultar("SELECT * FROM Esporte ORDER BY id")
        return [self._para_objeto(linha) for linha in linhas]

    def buscar_por_id(self, id):
        """Devolve um Esporte pelo id, ou None se nao existir."""
        linha = self.db.consultar_um("SELECT * FROM Esporte WHERE id = ?", (id,))
        return self._para_objeto(linha) if linha else None

    # ---- UPDATE ----
    def atualizar(self, esporte):
        """Atualiza nome, descricao e tipo de um esporte existente."""
        cursor = self.db.executar(
            "UPDATE Esporte SET nome = ?, descricao = ?, eh_coletivo = ? WHERE id = ?",
            (esporte.nome, esporte.descricao, 1 if esporte.eh_coletivo else 0, esporte.id),
        )
        # rowcount = 0 significa que nenhum id correspondeu (esporte inexistente).
        return cursor.rowcount > 0

    # ---- DELETE ----
    def excluir(self, id):
        """
        Remove um esporte pelo id. Atencao: se houver uma Turma usando este
        esporte, a regra ON DELETE RESTRICT do banco impede a exclusao e uma
        excecao sqlite3.IntegrityError sera levantada (tratada no menu).
        """
        cursor = self.db.executar("DELETE FROM Esporte WHERE id = ?", (id,))
        return cursor.rowcount > 0

    # ---- auxiliares internos ----
    def _proximo_id(self):
        linha = self.db.consultar_um("SELECT COALESCE(MAX(id), 0) + 1 AS prox FROM Esporte")
        return linha["prox"]

    def _para_objeto(self, linha):
        """Converte uma linha do banco (sqlite3.Row) em um objeto Esporte."""
        return Esporte(
            id=linha["id"],
            nome=linha["nome"],
            descricao=linha["descricao"],
            eh_coletivo=bool(linha["eh_coletivo"]),
        )


class AlunoRepository:
    """
    CRUD da entidade Aluno. Como Aluno e uma especializacao de Pessoa, cada
    operacao mexe nas DUAS tabelas (Pessoa e Aluno) de forma coordenada.
    """

    def __init__(self, db):
        self.db = db

    # ---- CREATE ----
    def criar(self, aluno):
        """
        Cria um aluno em dois passos, dentro da mesma transacao:
          1. insere a Pessoa (dados comuns);
          2. insere o Aluno apontando para essa Pessoa.
        """
        proximo_id = self._proximo_id_pessoa()
        self.db.conexao.execute(
            "INSERT INTO Pessoa (id, nome, cpf, email, data_nasc, "
            "fk_telefone_telefone_PK, fk_endereco_endereco_PK) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (proximo_id, aluno.nome, aluno.cpf, aluno.email, aluno.data_nasc,
             aluno.fk_telefone, aluno.fk_endereco),
        )
        self.db.conexao.execute(
            "INSERT INTO Aluno (fk_Pessoa_id, data_matricula, condicao_saude) "
            "VALUES (?, ?, ?)",
            (proximo_id, aluno.data_matricula, aluno.condicao_saude),
        )
        self.db.conexao.commit()
        aluno.id = proximo_id
        return aluno

    # ---- READ ----
    def listar(self):
        """Lista todos os alunos juntando os dados de Pessoa e Aluno."""
        linhas = self.db.consultar(
            "SELECT p.id, p.nome, p.cpf, p.email, p.data_nasc, "
            "       p.fk_telefone_telefone_PK, p.fk_endereco_endereco_PK, "
            "       a.data_matricula, a.condicao_saude "
            "FROM Aluno a "
            "JOIN Pessoa p ON a.fk_Pessoa_id = p.id "
            "ORDER BY p.id"
        )
        return [self._para_objeto(linha) for linha in linhas]

    def buscar_por_id(self, id):
        """Busca um aluno (Pessoa + Aluno) pelo id da pessoa."""
        linha = self.db.consultar_um(
            "SELECT p.id, p.nome, p.cpf, p.email, p.data_nasc, "
            "       p.fk_telefone_telefone_PK, p.fk_endereco_endereco_PK, "
            "       a.data_matricula, a.condicao_saude "
            "FROM Aluno a "
            "JOIN Pessoa p ON a.fk_Pessoa_id = p.id "
            "WHERE p.id = ?",
            (id,),
        )
        return self._para_objeto(linha) if linha else None

    # ---- UPDATE ----
    def atualizar(self, aluno):
        """Atualiza os dados da Pessoa e do Aluno na mesma transacao."""
        self.db.conexao.execute(
            "UPDATE Pessoa SET nome = ?, cpf = ?, email = ?, data_nasc = ? WHERE id = ?",
            (aluno.nome, aluno.cpf, aluno.email, aluno.data_nasc, aluno.id),
        )
        cursor = self.db.conexao.execute(
            "UPDATE Aluno SET data_matricula = ?, condicao_saude = ? WHERE fk_Pessoa_id = ?",
            (aluno.data_matricula, aluno.condicao_saude, aluno.id),
        )
        self.db.conexao.commit()
        return cursor.rowcount > 0

    # ---- DELETE ----
    def excluir(self, id):
        """
        Exclui o aluno removendo a Pessoa correspondente. Como Aluno tem
        ON DELETE CASCADE em relacao a Pessoa, apagar a Pessoa apaga tambem o
        Aluno e suas matriculas automaticamente.
        """
        cursor = self.db.executar("DELETE FROM Pessoa WHERE id = ?", (id,))
        return cursor.rowcount > 0

    # ---- auxiliares internos ----
    def _proximo_id_pessoa(self):
        linha = self.db.consultar_um("SELECT COALESCE(MAX(id), 0) + 1 AS prox FROM Pessoa")
        return linha["prox"]

    def _para_objeto(self, linha):
        return Aluno(
            id=linha["id"],
            nome=linha["nome"],
            cpf=linha["cpf"],
            email=linha["email"],
            data_nasc=linha["data_nasc"],
            fk_telefone=linha["fk_telefone_telefone_PK"],
            fk_endereco=linha["fk_endereco_endereco_PK"],
            data_matricula=linha["data_matricula"],
            condicao_saude=linha["condicao_saude"],
        )
