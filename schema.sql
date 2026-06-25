-- ============================================================================
-- Sistema de Gestao de Centro de Treinamento (CT)
-- Script de criacao do esquema do banco - dialeto SQLite
-- ----------------------------------------------------------------------------
-- Este script e a versao SQLite do "7 Scripts de Criacao do Esquema do Banco"
-- do relatorio (.docx). O conteudo logico e identico. As unicas adaptacoes de
-- sintaxe necessarias para o SQLite sao:
--
--   1. O SQLite nao suporta "ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY".
--      Por isso, as chaves estrangeiras que no relatorio aparecem como ALTER
--      TABLE foram declaradas aqui de forma inline (REFERENCES dentro do
--      proprio CREATE TABLE).
--   2. Como as FKs sao inline, as tabelas sao criadas em ordem topologica
--      (a tabela referenciada e criada antes da que a referencia).
--   3. Os tipos VARCHAR, DATE, TIME, FLOAT e BOOLEAN sao mantidos: o SQLite os
--      aceita por afinidade de tipo. BOOLEAN guarda 0 (FALSE) ou 1 (TRUE).
--
-- A integridade referencial so e aplicada se "PRAGMA foreign_keys = ON" estiver
-- ativo na conexao (o programa Python ativa isso automaticamente).
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- Tabelas independentes (sem chaves estrangeiras)
-- ----------------------------------------------------------------------------

CREATE TABLE telefone (
    telefone_PK INT NOT NULL PRIMARY KEY,
    telefone    VARCHAR
);

CREATE TABLE endereco (
    endereco_PK INT NOT NULL PRIMARY KEY,
    logradouro  VARCHAR,
    bairro      VARCHAR,
    cidade      VARCHAR,
    complemento VARCHAR
);

CREATE TABLE periodicidade (
    periodicidade_PK INT NOT NULL PRIMARY KEY,
    nome             VARCHAR,
    qnt_dias         INT
);

CREATE TABLE situacao (
    situacao_PK INT NOT NULL PRIMARY KEY,
    nome        VARCHAR
);

CREATE TABLE Esporte (
    id          INT PRIMARY KEY,
    nome        VARCHAR,
    descricao   VARCHAR,
    eh_coletivo BOOLEAN
);

CREATE TABLE HorarioTurma (
    id   INT PRIMARY KEY,
    nome VARCHAR
);

CREATE TABLE Horario (
    id             INT PRIMARY KEY,
    horario_inicio TIME,
    horario_fim    TIME
);

-- ----------------------------------------------------------------------------
-- Pessoa e suas especializacoes (Aluno, Professor, Responsavel)
-- ----------------------------------------------------------------------------

CREATE TABLE Pessoa (
    id                      INT PRIMARY KEY,
    nome                    VARCHAR,
    cpf                     VARCHAR,
    email                   VARCHAR,
    data_nasc               DATE,
    fk_telefone_telefone_PK INT,
    fk_endereco_endereco_PK INT,
    CONSTRAINT FK_Pessoa_2 FOREIGN KEY (fk_telefone_telefone_PK)
        REFERENCES telefone (telefone_PK) ON DELETE NO ACTION,
    CONSTRAINT FK_Pessoa_3 FOREIGN KEY (fk_endereco_endereco_PK)
        REFERENCES endereco (endereco_PK) ON DELETE SET NULL
);

CREATE TABLE Responsavel (
    fk_Pessoa_id INT PRIMARY KEY,
    CONSTRAINT FK_Responsavel_2 FOREIGN KEY (fk_Pessoa_id)
        REFERENCES Pessoa (id) ON DELETE CASCADE
);

CREATE TABLE Professor (
    fk_Pessoa_id INT PRIMARY KEY,
    CONSTRAINT FK_Professor_2 FOREIGN KEY (fk_Pessoa_id)
        REFERENCES Pessoa (id) ON DELETE CASCADE
);

CREATE TABLE Aluno (
    data_matricula DATE,
    condicao_saude VARCHAR,
    fk_Pessoa_id   INT PRIMARY KEY,
    CONSTRAINT FK_Aluno_2 FOREIGN KEY (fk_Pessoa_id)
        REFERENCES Pessoa (id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- Turma e estruturas dependentes
-- ----------------------------------------------------------------------------

CREATE TABLE Turma (
    id                 INT PRIMARY KEY,
    nome               VARCHAR,
    vagas_totais       INT,
    fk_HorarioTurma_id INT,
    fk_Esporte_id      INT,
    CONSTRAINT FK_Turma_2 FOREIGN KEY (fk_HorarioTurma_id)
        REFERENCES HorarioTurma (id) ON DELETE RESTRICT,
    CONSTRAINT FK_Turma_3 FOREIGN KEY (fk_Esporte_id)
        REFERENCES Esporte (id) ON DELETE RESTRICT
);

CREATE TABLE Aula (
    data_aula     DATE,
    aula_foi_dada BOOLEAN,
    fk_Turma_id   INT,
    CONSTRAINT FK_Aula_1 FOREIGN KEY (fk_Turma_id)
        REFERENCES Turma (id) ON DELETE CASCADE
);

CREATE TABLE Matricula_turma (
    fk_Aluno_fk_Pessoa_id INT,
    fk_Turma_id           INT,
    CONSTRAINT FK_Matricula_turma_1 FOREIGN KEY (fk_Aluno_fk_Pessoa_id)
        REFERENCES Aluno (fk_Pessoa_id) ON DELETE CASCADE,
    CONSTRAINT FK_Matricula_turma_2 FOREIGN KEY (fk_Turma_id)
        REFERENCES Turma (id) ON DELETE CASCADE
);

-- Conforme o relatorio, a tabela Frequencia foi modelada apenas com o atributo
-- "presenca". Mantida fiel ao documento.
CREATE TABLE Frequencia (
    presenca BOOLEAN
);

-- ----------------------------------------------------------------------------
-- Financeiro: planos e mensalidades
-- ----------------------------------------------------------------------------

CREATE TABLE PlanoPagamento (
    id                                INT PRIMARY KEY,
    nome                              VARCHAR,
    valor                             FLOAT,
    fk_periodicidade_periodicidade_PK INT,
    descricao                         VARCHAR,
    CONSTRAINT FK_PlanoPagamento_2 FOREIGN KEY (fk_periodicidade_periodicidade_PK)
        REFERENCES periodicidade (periodicidade_PK) ON DELETE SET NULL
);

CREATE TABLE Mensalidade (
    valor                   FLOAT,
    data_vencimento         DATE,
    data_pagamento          DATE,
    fk_situacao_situacao_PK INT,
    forma_pagamento         VARCHAR,
    id                      INT PRIMARY KEY,
    CONSTRAINT FK_Mensalidade_2 FOREIGN KEY (fk_situacao_situacao_PK)
        REFERENCES situacao (situacao_PK) ON DELETE SET NULL
);

-- ----------------------------------------------------------------------------
-- Horarios das turmas e associacoes
-- ----------------------------------------------------------------------------

CREATE TABLE ItemHorario (
    int_dia_da_semana  INT,
    fk_Horario_id      INT,
    fk_HorarioTurma_id INT,
    CONSTRAINT FK_ItemHorario_1 FOREIGN KEY (fk_Horario_id)
        REFERENCES Horario (id) ON DELETE CASCADE,
    CONSTRAINT FK_ItemHorario_2 FOREIGN KEY (fk_HorarioTurma_id)
        REFERENCES HorarioTurma (id) ON DELETE CASCADE
);

CREATE TABLE PlanoAluno (
    fk_Aluno_fk_Pessoa_id INT,
    fk_PlanoPagamento_id  INT,
    CONSTRAINT FK_PlanoAluno_1 FOREIGN KEY (fk_Aluno_fk_Pessoa_id)
        REFERENCES Aluno (fk_Pessoa_id) ON DELETE CASCADE,
    CONSTRAINT FK_PlanoAluno_2 FOREIGN KEY (fk_PlanoPagamento_id)
        REFERENCES PlanoPagamento (id) ON DELETE CASCADE
);

CREATE TABLE Cancelamento_Aula (
    id            INT PRIMARY KEY,
    justificativa VARCHAR
);

-- ----------------------------------------------------------------------------
-- Tabelas associativas (relacionamentos N para N)
-- ----------------------------------------------------------------------------

CREATE TABLE encarregado (
    fk_Aluno_fk_Pessoa_id       INT,
    fk_Responsavel_fk_Pessoa_id INT,
    CONSTRAINT FK_encarregado_1 FOREIGN KEY (fk_Aluno_fk_Pessoa_id)
        REFERENCES Aluno (fk_Pessoa_id) ON DELETE CASCADE,
    CONSTRAINT FK_encarregado_2 FOREIGN KEY (fk_Responsavel_fk_Pessoa_id)
        REFERENCES Responsavel (fk_Pessoa_id) ON DELETE CASCADE
);

CREATE TABLE ministra (
    fk_Professor_fk_Pessoa_id INT,
    fk_Turma_id               INT,
    CONSTRAINT FK_ministra_1 FOREIGN KEY (fk_Professor_fk_Pessoa_id)
        REFERENCES Professor (fk_Pessoa_id) ON DELETE CASCADE,
    CONSTRAINT FK_ministra_2 FOREIGN KEY (fk_Turma_id)
        REFERENCES Turma (id) ON DELETE CASCADE
);

-- Nome "especiliazado" mantido exatamente como no relatorio para que os
-- scripts de carga e de consulta continuem compativeis.
CREATE TABLE especiliazado (
    fk_Esporte_id             INT,
    fk_Professor_fk_Pessoa_id INT,
    CONSTRAINT FK_especiliazado_1 FOREIGN KEY (fk_Esporte_id)
        REFERENCES Esporte (id) ON DELETE CASCADE,
    CONSTRAINT FK_especiliazado_2 FOREIGN KEY (fk_Professor_fk_Pessoa_id)
        REFERENCES Professor (fk_Pessoa_id) ON DELETE CASCADE
);
