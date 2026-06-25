"""
models.py
=========
Classes que representam as entidades do dominio do Centro de Treinamento.

Aqui aplicamos orientacao a objetos para espelhar o Modelo Conceitual do
relatorio. A entidade Pessoa e uma superclasse e Aluno e uma especializacao
(herda de Pessoa), exatamente como aparece no diagrama Entidade-Relacionamento
(Secao 5.1 e 5.2 do .docx).

Estas classes sao apenas "objetos de dados": elas guardam os atributos e sabem
se descrever. Quem conversa com o banco sao as classes de repositorio
(ver repository.py).
"""


class Esporte:
    """Modalidade esportiva oferecida pelo CT (tabela Esporte)."""

    def __init__(self, id=None, nome="", descricao="", eh_coletivo=False):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        # Guardamos sempre como booleano de Python; a conversao para 0/1 do
        # SQLite acontece na camada de repositorio.
        self.eh_coletivo = bool(eh_coletivo)

    @property
    def tipo(self):
        """Texto amigavel para exibir o tipo do esporte."""
        return "Coletivo" if self.eh_coletivo else "Individual"

    def __str__(self):
        return f"[{self.id}] {self.nome} ({self.tipo}) - {self.descricao}"


class Pessoa:
    """
    Superclasse que centraliza os dados comuns a Alunos, Professores e
    Responsaveis (tabela Pessoa). Evita redundancia, como descrito na
    Secao 5.1 do relatorio.
    """

    def __init__(self, id=None, nome="", cpf="", email="", data_nasc="",
                 fk_telefone=None, fk_endereco=None):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.data_nasc = data_nasc
        self.fk_telefone = fk_telefone
        self.fk_endereco = fk_endereco

    def __str__(self):
        return f"[{self.id}] {self.nome} - CPF {self.cpf} - {self.email}"


class Aluno(Pessoa):
    """
    Aluno e uma especializacao de Pessoa (herda todos os atributos de Pessoa)
    e acrescenta os campos proprios da tabela Aluno: data de matricula e
    condicao de saude. Veja a Secao 5.2 do relatorio.
    """

    def __init__(self, id=None, nome="", cpf="", email="", data_nasc="",
                 fk_telefone=None, fk_endereco=None,
                 data_matricula="", condicao_saude=""):
        # Reaproveita o construtor da superclasse Pessoa (heranca em acao).
        super().__init__(id, nome, cpf, email, data_nasc, fk_telefone, fk_endereco)
        self.data_matricula = data_matricula
        self.condicao_saude = condicao_saude

    def __str__(self):
        return (f"[{self.id}] {self.nome} - CPF {self.cpf} - "
                f"matricula em {self.data_matricula} - saude: {self.condicao_saude}")
