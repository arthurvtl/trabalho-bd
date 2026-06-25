-- ============================================================================
-- Sistema de Gestao de Centro de Treinamento (CT)
-- Script de carga inicial de dados - dialeto SQLite
-- ----------------------------------------------------------------------------
-- A PRIMEIRA parte (Secao A) reproduz exatamente os dados do "8 Scripts de
-- Carga Inicial de Dados" do relatorio (.docx). Nenhum valor foi alterado.
--
-- A SEGUNDA parte (Secao B) contem dados complementares para as tabelas que
-- nao foram populadas no relatorio (Horario, Aula, Frequencia, ItemHorario,
-- PlanoAluno, encarregado e Cancelamento_Aula). Eles existem apenas para
-- deixar o banco completo (o Template do trabalho pede ao menos 5 registros
-- por tabela) e nao interferem nas consultas da Secao 9 do relatorio.
--
-- A ordem dos INSERT respeita as chaves estrangeiras (a tabela referenciada e
-- carregada antes da que depende dela).
-- ============================================================================

-- ===========================================================================
-- SECAO A - Dados do relatorio (Secao 8 do .docx)
-- ===========================================================================

-- Tabelas auxiliares de endereco / contato / dominio
INSERT INTO telefone (telefone_PK, telefone) VALUES
    (1, '27999991111'), (2, '27999992222'), (3, '27999993333'),
    (4, '27999994444'), (5, '27999995555');

INSERT INTO endereco (endereco_PK, logradouro, bairro, cidade, complemento) VALUES
    (1, 'Rua A, 123', 'Centro', 'Vitoria', 'Apto 1'),
    (2, 'Rua B, 45', 'Praia da Costa', 'Vila Velha', 'Casa'),
    (3, 'Av C, 900', 'Laranjeiras', 'Serra', 'Bloco B'),
    (4, 'Rua D, 12', 'Campo Grande', 'Cariacica', 'Fundos'),
    (5, 'Av E, 55', 'Jardim da Penha', 'Vitoria', 'Casa 2');

INSERT INTO periodicidade (periodicidade_PK, nome, qnt_dias) VALUES
    (1, 'Mensal', 30), (2, 'Bimestral', 60), (3, 'Trimestral', 90),
    (4, 'Semestral', 180), (5, 'Anual', 365);

INSERT INTO situacao (situacao_PK, nome) VALUES
    (1, 'Paga'), (2, 'Pendente'), (3, 'Atrasada'),
    (4, 'Cancelada'), (5, 'Isenta');

-- Pessoas e papeis
INSERT INTO Pessoa (id, nome, cpf, email, data_nasc, fk_telefone_telefone_PK, fk_endereco_endereco_PK) VALUES
    (1,  'Carlos Silva',  '111.111.111-11', 'carlos@email.com',   '2010-05-10', 1, 1),
    (2,  'Maria Souza',   '222.222.222-22', 'maria@email.com',    '2008-08-20', 2, 2),
    (3,  'Joao Pedro',    '333.333.333-33', 'joao@email.com',     '2012-01-15', 3, 3),
    (4,  'Ana Clara',     '444.444.444-44', 'ana@email.com',      '1995-11-30', 4, 4),
    (5,  'Roberto Gomes', '555.555.555-55', 'roberto@email.com',  '2000-02-25', 5, 5),
    (6,  'Fernanda Lima', '666.666.666-66', 'fernanda@email.com', '1985-07-12', 1, 2),
    (7,  'Lucas Alves',   '777.777.777-77', 'lucas@email.com',    '1990-09-05', 2, 3),
    (8,  'Juliana Costa', '888.888.888-88', 'juliana@email.com',  '1988-12-10', 3, 4),
    (9,  'Marcos Paulo',  '999.999.999-99', 'marcos@email.com',   '1982-03-22', 4, 1),
    (10, 'Aline Barros',  '000.000.000-00', 'aline@email.com',    '1992-06-18', 5, 2);

-- IDs 1 a 5 como Alunos
INSERT INTO Aluno (fk_Pessoa_id, data_matricula, condicao_saude) VALUES
    (1, '2023-01-10', 'Apto'), (2, '2023-02-15', 'Apto'), (3, '2023-03-20', 'Asma leve'),
    (4, '2023-04-05', 'Apto'), (5, '2023-05-12', 'Apto');

-- IDs 6 a 10 como Professores
INSERT INTO Professor (fk_Pessoa_id) VALUES (6), (7), (8), (9), (10);

-- IDs 6 a 10 tambem como Responsaveis (para os alunos menores de idade)
INSERT INTO Responsavel (fk_Pessoa_id) VALUES (6), (7), (8), (9), (10);

-- Dominio esportivo
INSERT INTO Esporte (id, nome, descricao, eh_coletivo) VALUES
    (1, 'Natacao',  'Aulas em piscina aquecida', FALSE),
    (2, 'Futebol',  'Futebol de campo',          TRUE),
    (3, 'Volei',    'Volei de quadra indoor',    TRUE),
    (4, 'Basquete', 'Basquete quadra oficial',   TRUE),
    (5, 'Judo',     'Artes marciais no tatame',  FALSE);

-- Professores e suas especialidades
INSERT INTO especiliazado (fk_Esporte_id, fk_Professor_fk_Pessoa_id) VALUES
    (1, 6), (2, 7), (3, 8), (4, 9), (5, 10);

INSERT INTO HorarioTurma (id, nome) VALUES
    (1, 'Manha - 08:00'), (2, 'Manha - 10:00'), (3, 'Tarde - 14:00'),
    (4, 'Tarde - 16:00'), (5, 'Noite - 19:00');

INSERT INTO Turma (id, nome, vagas_totais, fk_HorarioTurma_id, fk_Esporte_id) VALUES
    (1, 'Nat-Infantil-M',  15, 1, 1), (2, 'Fut-Sub15-T',    22, 4, 2),
    (3, 'Vol-Adulto-N',    14, 5, 3), (4, 'Bas-Iniciante-M', 20, 2, 4),
    (5, 'Jud-Avancado-T',  10, 3, 5);

-- Relacionamentos
INSERT INTO Matricula_turma (fk_Aluno_fk_Pessoa_id, fk_Turma_id) VALUES
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (1, 2), (2, 3);

INSERT INTO ministra (fk_Professor_fk_Pessoa_id, fk_Turma_id) VALUES
    (6, 1), (7, 2), (8, 3), (9, 4), (10, 5);

INSERT INTO PlanoPagamento (id, nome, valor, fk_periodicidade_periodicidade_PK, descricao) VALUES
    (1, 'Plano Basico Mensal',   100.00, 1, 'Acesso a 1 esporte'),
    (2, 'Plano Trimestral',      270.00, 3, 'Acesso a 1 esporte com desconto'),
    (3, 'Plano Semestral Multi', 500.00, 4, 'Acesso a 2 esportes'),
    (4, 'Plano Anual Premium',   900.00, 5, 'Livre acesso'),
    (5, 'Plano Mensal Premium',  150.00, 1, 'Livre acesso mensal');

INSERT INTO Mensalidade (id, valor, data_vencimento, data_pagamento, fk_situacao_situacao_PK, forma_pagamento) VALUES
    (1, 100.00, '2023-10-10', '2023-10-09', 1, 'PIX'),
    (2, 100.00, '2023-11-10', NULL,         2, 'Boleto'),
    (3, 270.00, '2023-10-15', '2023-10-15', 1, 'Cartao de Credito'),
    (4, 150.00, '2023-09-10', NULL,         3, 'PIX'),
    (5, 900.00, '2023-01-10', '2023-01-05', 1, 'Cartao de Credito');

-- ===========================================================================
-- SECAO B - Dados complementares (tabelas nao populadas no relatorio)
-- Adicionados apenas para completar o banco. Podem ser removidos sem afetar
-- as consultas da Secao 9.
-- ===========================================================================

INSERT INTO Horario (id, horario_inicio, horario_fim) VALUES
    (1, '07:00', '08:00'), (2, '08:00', '09:00'), (3, '10:00', '11:00'),
    (4, '18:00', '19:00'), (5, '19:00', '20:00');

-- int_dia_da_semana: 1 = Domingo ... 7 = Sabado
INSERT INTO ItemHorario (int_dia_da_semana, fk_Horario_id, fk_HorarioTurma_id) VALUES
    (2, 1, 1), (3, 2, 1), (4, 3, 2), (5, 4, 3), (6, 5, 4);

INSERT INTO Aula (data_aula, aula_foi_dada, fk_Turma_id) VALUES
    ('2025-05-01', TRUE,  1), ('2025-05-02', TRUE,  2), ('2025-05-03', FALSE, 3),
    ('2025-05-04', TRUE,  4), ('2025-05-05', TRUE,  5);

INSERT INTO Frequencia (presenca) VALUES
    (TRUE), (FALSE), (TRUE), (TRUE), (FALSE);

INSERT INTO PlanoAluno (fk_Aluno_fk_Pessoa_id, fk_PlanoPagamento_id) VALUES
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5);

-- Cada aluno (1 a 5) associado a um responsavel (6 a 10)
INSERT INTO encarregado (fk_Aluno_fk_Pessoa_id, fk_Responsavel_fk_Pessoa_id) VALUES
    (1, 6), (2, 7), (3, 8), (4, 9), (5, 10);

INSERT INTO Cancelamento_Aula (id, justificativa) VALUES
    (1, 'Professor nao compareceu'), (2, 'Dedetizacao'), (3, 'Reforma no CT'),
    (4, 'Muita chuva'), (5, 'Feriado municipal');
