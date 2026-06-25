"""
relatorios.py
=============
Reune as 8 consultas da Secao 9 do relatorio (.docx) como metodos de uma
classe. Cada metodo executa um SELECT e devolve duas coisas:
  - a lista de titulos das colunas (para montar o cabecalho da tabela);
  - as linhas com os resultados.

Manter as consultas separadas da interface deixa o codigo organizado: o
main.py so precisa pedir "me da o relatorio X" sem saber o SQL por tras.
"""


class Relatorios:
    """Executa os relatorios gerenciais do sistema (consultas da Secao 9)."""

    def __init__(self, db):
        self.db = db

    def _rodar(self, sql):
        """Executa um SELECT e devolve (titulos_das_colunas, linhas)."""
        cursor = self.db.conexao.execute(sql)
        titulos = [descricao[0] for descricao in cursor.description]
        linhas = cursor.fetchall()
        return titulos, linhas

    # Consulta 1
    def alunos_por_turma(self):
        return self._rodar(
            "SELECT t.nome AS Turma, e.nome AS Esporte, "
            "       t.vagas_totais AS Capacidade, "
            "       COUNT(m.fk_Aluno_fk_Pessoa_id) AS Alunos_Matriculados "
            "FROM Turma t "
            "JOIN Esporte e ON t.fk_Esporte_id = e.id "
            "LEFT JOIN Matricula_turma m ON t.id = m.fk_Turma_id "
            "GROUP BY t.id, t.nome, e.nome, t.vagas_totais "
            "ORDER BY Alunos_Matriculados DESC"
        )

    # Consulta 2
    def arrecadacao_por_periodicidade(self):
        return self._rodar(
            "SELECT per.nome AS Frequencia_Cobranca, "
            "       COUNT(pp.id) AS Qtd_Planos_Ofertados, "
            "       SUM(pp.valor) AS Potencial_Arrecadacao "
            "FROM PlanoPagamento pp "
            "JOIN periodicidade per ON pp.fk_periodicidade_periodicidade_PK = per.periodicidade_PK "
            "GROUP BY per.periodicidade_PK, per.nome "
            "ORDER BY Potencial_Arrecadacao DESC"
        )

    # Consulta 3
    def carga_por_professor(self):
        return self._rodar(
            "SELECT p.nome AS Nome_Professor, "
            "       COUNT(min.fk_Turma_id) AS Qtd_Turmas_Lecionadas "
            "FROM Pessoa p "
            "JOIN Professor prof ON p.id = prof.fk_Pessoa_id "
            "JOIN ministra min ON prof.fk_Pessoa_id = min.fk_Professor_fk_Pessoa_id "
            "GROUP BY p.id, p.nome "
            "ORDER BY Qtd_Turmas_Lecionadas DESC"
        )

    # Consulta 4
    def resumo_financeiro(self):
        return self._rodar(
            "SELECT s.nome AS Status_Mensalidade, "
            "       COUNT(m.id) AS Volume_Boletos, "
            "       SUM(m.valor) AS Valor_Acumulado "
            "FROM Mensalidade m "
            "JOIN situacao s ON m.fk_situacao_situacao_PK = s.situacao_PK "
            "GROUP BY s.situacao_PK, s.nome "
            "ORDER BY Valor_Acumulado DESC"
        )

    # Consulta 5
    def vagas_por_categoria(self):
        return self._rodar(
            "SELECT CASE WHEN e.eh_coletivo = TRUE THEN 'Coletivo' ELSE 'Individual' END "
            "         AS Tipo_Esporte, "
            "       SUM(t.vagas_totais) AS Vagas_Totais_Disponiveis "
            "FROM Esporte e "
            "JOIN Turma t ON e.id = t.fk_Esporte_id "
            "GROUP BY e.eh_coletivo "
            "ORDER BY Vagas_Totais_Disponiveis DESC"
        )

    # Consulta 6
    def alunos_por_bairro(self):
        return self._rodar(
            "SELECT end.bairro AS Bairro, "
            "       COUNT(a.fk_Pessoa_id) AS Quantidade_Alunos "
            "FROM Aluno a "
            "JOIN Pessoa p ON a.fk_Pessoa_id = p.id "
            "JOIN endereco end ON p.fk_endereco_endereco_PK = end.endereco_PK "
            "GROUP BY end.bairro "
            "ORDER BY Quantidade_Alunos DESC"
        )

    # Consulta 7
    def especializacoes(self):
        return self._rodar(
            "SELECT e.nome AS Modalidade_Esportiva, "
            "       COUNT(esp.fk_Professor_fk_Pessoa_id) AS Professores_Especializados "
            "FROM Esporte e "
            "LEFT JOIN especiliazado esp ON e.id = esp.fk_Esporte_id "
            "GROUP BY e.id, e.nome "
            "ORDER BY Professores_Especializados DESC, e.nome ASC"
        )

    # Consulta 8 (versao SQLite de EXTRACT(YEAR FROM ...))
    def concentracao_etaria(self):
        return self._rodar(
            "SELECT CAST(strftime('%Y', p.data_nasc) AS INTEGER) AS Ano_Nascimento, "
            "       COUNT(a.fk_Pessoa_id) AS Total_Nascidos "
            "FROM Aluno a "
            "JOIN Pessoa p ON a.fk_Pessoa_id = p.id "
            "GROUP BY Ano_Nascimento "
            "ORDER BY Total_Nascidos DESC"
        )

    def todos(self):
        """
        Devolve a lista de relatorios disponiveis como pares
        (titulo, funcao). O menu usa isso para montar as opcoes
        automaticamente.
        """
        return [
            ("Quantidade de alunos por turma e esporte", self.alunos_por_turma),
            ("Projecao de arrecadacao por periodicidade", self.arrecadacao_por_periodicidade),
            ("Carga de turmas por professor", self.carga_por_professor),
            ("Resumo financeiro de mensalidades", self.resumo_financeiro),
            ("Vagas ofertadas por categoria de esporte", self.vagas_por_categoria),
            ("Distribuicao de alunos por bairro", self.alunos_por_bairro),
            ("Especializacoes dos professores", self.especializacoes),
            ("Concentracao etaria dos alunos", self.concentracao_etaria),
        ]
