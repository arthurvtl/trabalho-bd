-- ============================================================================
-- Sistema de Gestao de Centro de Treinamento (CT)
-- Script de criacao do esquema do banco - MySQL (Aiven)
-- ----------------------------------------------------------------------------
-- Esta e a versao MySQL do "7 Scripts de Criacao do Esquema do Banco" do
-- relatorio. Como o relatorio ja foi escrito em dialeto MySQL, o conteudo e
-- praticamente identico. Os ajustes feitos foram:
--
--   1. Em MySQL todo VARCHAR precisa de um tamanho, entao foram definidos
--      tamanhos para cada coluna de texto.
--   2. As chaves estrangeiras foram declaradas dentro do CREATE TABLE (inline)
--      e as tabelas sao criadas em ordem, de modo que o script possa ser
--      executado de uma vez e seja seguro repetir (CREATE TABLE IF NOT EXISTS).
--   3. As regras ON DELETE (CASCADE, RESTRICT, SET NULL) foram mantidas como
--      no relatorio.
--
-- O tipo BOOLEAN do MySQL e armazenado como TINYINT (0 ou 1), e TRUE e FALSE
-- funcionam normalmente.
-- ============================================================================

-- Tabelas independentes (sem chaves estrangeiras)

CREATE TABLE IF NOT EXISTS telefone (
    telefone_PK INT NOT NULL PRIMARY KEY,
    telefone    VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS endereco (
    endereco_PK INT NOT NULL PRIMARY KEY,
    logradouro  VARCHAR(150),
    bairro      VARCHAR(80),
    cidade      VARCHAR(80),
    complemento VARCHAR(80)
);

CREATE TABLE IF NOT EXISTS periodicidade (
    periodicidade_PK INT NOT NULL PRIMARY KEY,
    nome             VARCHAR(40),
    qnt_dias         INT
);

CREATE TABLE IF NOT EXISTS situacao (
    situacao_PK INT NOT NULL PRIMARY KEY,
    nome        VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS Esporte (
    id          INT PRIMARY KEY,
    nome        VARCHAR(60),
    descricao   VARCHAR(255),
    eh_coletivo BOOLEAN
);

CREATE TABLE IF NOT EXISTS HorarioTurma (
    id   INT PRIMARY KEY,
    nome VARCHAR(60)
);

CREATE TABLE IF NOT EXISTS Horario (
    id             INT PRIMARY KEY,
    horario_inicio TIME,
    horario_fim    TIME
);

-- Pessoa e suas especializacoes (Aluno, Professor, Responsavel)

CREATE TABLE IF NOT EXISTS Pessoa (
    id                      INT PRIMARY KEY,
    nome                    VARCHAR(120),
    cpf                     VARCHAR(20),
    email                   VARCHAR(120),
    data_nasc               DATE,
    fk_telefone_telefone_PK INT,
    fk_endereco_endereco_PK INT,
    CONSTRAINT FK_Pessoa_2 FOREIGN KEY (fk_telefone_telefone_PK)
        REFERENCES telefone (telefone_PK) ON DELETE NO ACTION,
    CONSTRAINT FK_Pessoa_3 FOREIGN KEY (fk_endereco_endereco_PK)
        REFERENCES endereco (endereco_PK) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Responsavel (
    fk_Pessoa_id INT PRIMARY KEY,
    CONSTRAINT FK_Responsavel_2 FOREIGN KEY (fk_Pessoa_id)
        REFERENCES Pessoa (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Professor (
    fk_Pessoa_id INT PRIMARY KEY,
    CONSTRAINT FK_Professor_2 FOREIGN KEY (fk_Pessoa_id)
        REFERENCES Pessoa (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Aluno (
    data_matricula DATE,
    condicao_saude VARCHAR(120),
    fk_Pessoa_id   INT PRIMARY KEY,
    CONSTRAINT FK_Aluno_2 FOREIGN KEY (fk_Pessoa_id)
        REFERENCES Pessoa (id) ON DELETE CASCADE
);

-- Turma e estruturas dependentes

CREATE TABLE IF NOT EXISTS Turma (
    id                 INT PRIMARY KEY,
    nome               VARCHAR(80),
    vagas_totais       INT,
    fk_HorarioTurma_id INT,
    fk_Esporte_id      INT,
    CONSTRAINT FK_Turma_2 FOREIGN KEY (fk_HorarioTurma_id)
        REFERENCES HorarioTurma (id) ON DELETE RESTRICT,
    CONSTRAINT FK_Turma_3 FOREIGN KEY (fk_Esporte_id)
        REFERENCES Esporte (id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Aula (
    id            INT PRIMARY KEY AUTO_INCREMENT,
    data_aula     DATE,
    aula_foi_dada BOOLEAN,
    fk_Turma_id   INT,
    CONSTRAINT FK_Aula_1 FOREIGN KEY (fk_Turma_id)
        REFERENCES Turma (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Matricula_turma (
    id                    INT PRIMARY KEY AUTO_INCREMENT,
    fk_Aluno_fk_Pessoa_id INT,
    fk_Turma_id           INT,
    CONSTRAINT FK_Matricula_turma_1 FOREIGN KEY (fk_Aluno_fk_Pessoa_id)
        REFERENCES Aluno (fk_Pessoa_id) ON DELETE CASCADE,
    CONSTRAINT FK_Matricula_turma_2 FOREIGN KEY (fk_Turma_id)
        REFERENCES Turma (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Frequencia (
    id       INT PRIMARY KEY AUTO_INCREMENT,
    presenca BOOLEAN
);

-- Financeiro: planos e mensalidades

CREATE TABLE IF NOT EXISTS PlanoPagamento (
    id                                INT PRIMARY KEY,
    nome                              VARCHAR(80),
    valor                             FLOAT,
    fk_periodicidade_periodicidade_PK INT,
    descricao                         VARCHAR(255),
    CONSTRAINT FK_PlanoPagamento_2 FOREIGN KEY (fk_periodicidade_periodicidade_PK)
        REFERENCES periodicidade (periodicidade_PK) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Mensalidade (
    valor                   FLOAT,
    data_vencimento         DATE,
    data_pagamento          DATE,
    fk_situacao_situacao_PK INT,
    forma_pagamento         VARCHAR(40),
    id                      INT PRIMARY KEY,
    CONSTRAINT FK_Mensalidade_2 FOREIGN KEY (fk_situacao_situacao_PK)
        REFERENCES situacao (situacao_PK) ON DELETE SET NULL
);

-- Horarios das turmas e associacoes

CREATE TABLE IF NOT EXISTS ItemHorario (
    id                 INT PRIMARY KEY AUTO_INCREMENT,
    int_dia_da_semana  INT,
    fk_Horario_id      INT,
    fk_HorarioTurma_id INT,
    CONSTRAINT FK_ItemHorario_1 FOREIGN KEY (fk_Horario_id)
        REFERENCES Horario (id) ON DELETE CASCADE,
    CONSTRAINT FK_ItemHorario_2 FOREIGN KEY (fk_HorarioTurma_id)
        REFERENCES HorarioTurma (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS PlanoAluno (
    fk_Aluno_fk_Pessoa_id INT,
    fk_PlanoPagamento_id  INT,
    PRIMARY KEY (fk_Aluno_fk_Pessoa_id, fk_PlanoPagamento_id),
    CONSTRAINT FK_PlanoAluno_1 FOREIGN KEY (fk_Aluno_fk_Pessoa_id)
        REFERENCES Aluno (fk_Pessoa_id) ON DELETE CASCADE,
    CONSTRAINT FK_PlanoAluno_2 FOREIGN KEY (fk_PlanoPagamento_id)
        REFERENCES PlanoPagamento (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Cancelamento_Aula (
    id            INT PRIMARY KEY,
    justificativa VARCHAR(255)
);

-- Tabelas associativas (relacionamentos N para N)

CREATE TABLE IF NOT EXISTS encarregado (
    fk_Aluno_fk_Pessoa_id       INT,
    fk_Responsavel_fk_Pessoa_id INT,
    PRIMARY KEY (fk_Aluno_fk_Pessoa_id, fk_Responsavel_fk_Pessoa_id),
    CONSTRAINT FK_encarregado_1 FOREIGN KEY (fk_Aluno_fk_Pessoa_id)
        REFERENCES Aluno (fk_Pessoa_id) ON DELETE CASCADE,
    CONSTRAINT FK_encarregado_2 FOREIGN KEY (fk_Responsavel_fk_Pessoa_id)
        REFERENCES Responsavel (fk_Pessoa_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ministra (
    fk_Professor_fk_Pessoa_id INT,
    fk_Turma_id               INT,
    PRIMARY KEY (fk_Professor_fk_Pessoa_id, fk_Turma_id),
    CONSTRAINT FK_ministra_1 FOREIGN KEY (fk_Professor_fk_Pessoa_id)
        REFERENCES Professor (fk_Pessoa_id) ON DELETE CASCADE,
    CONSTRAINT FK_ministra_2 FOREIGN KEY (fk_Turma_id)
        REFERENCES Turma (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS especiliazado (
    fk_Esporte_id             INT,
    fk_Professor_fk_Pessoa_id INT,
    PRIMARY KEY (fk_Esporte_id, fk_Professor_fk_Pessoa_id),
    CONSTRAINT FK_especiliazado_1 FOREIGN KEY (fk_Esporte_id)
        REFERENCES Esporte (id) ON DELETE CASCADE,
    CONSTRAINT FK_especiliazado_2 FOREIGN KEY (fk_Professor_fk_Pessoa_id)
        REFERENCES Professor (fk_Pessoa_id) ON DELETE CASCADE
);
