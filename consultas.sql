-- ============================================================================
-- Sistema de Gestao de Centro de Treinamento (CT)
-- Scripts de consulta (Secao 9 do relatorio) - dialeto SQLite
-- ----------------------------------------------------------------------------
-- Sao as mesmas 8 consultas do relatorio. A unica diferenca de sintaxe esta na
-- Consulta 8: o relatorio usa "EXTRACT(YEAR FROM data)", que e padrao
-- MySQL/PostgreSQL. No SQLite a funcao equivalente e
-- "strftime('%Y', data)" (que retorna texto, por isso usamos CAST para INT).
-- O programa Python executa exatamente estas consultas.
-- ============================================================================

-- Consulta 1: Quantidade de alunos por turma e esporte
-- Objetivo: ocupacao atual das turmas, cruzando com a capacidade maxima.
SELECT
    t.nome           AS Turma,
    e.nome           AS Esporte,
    t.vagas_totais   AS Capacidade,
    COUNT(m.fk_Aluno_fk_Pessoa_id) AS Alunos_Matriculados
FROM Turma t
JOIN Esporte e ON t.fk_Esporte_id = e.id
LEFT JOIN Matricula_turma m ON t.id = m.fk_Turma_id
GROUP BY t.id, t.nome, e.nome, t.vagas_totais
ORDER BY Alunos_Matriculados DESC;

-- Consulta 2: Projecao de arrecadacao por tipo de periodicidade
-- Objetivo: valor total dos planos agrupados pela periodicidade de cobranca.
SELECT
    per.nome      AS Frequencia_Cobranca,
    COUNT(pp.id)  AS Qtd_Planos_Ofertados,
    SUM(pp.valor) AS Potencial_Arrecadacao
FROM PlanoPagamento pp
JOIN periodicidade per ON pp.fk_periodicidade_periodicidade_PK = per.periodicidade_PK
GROUP BY per.periodicidade_PK, per.nome
ORDER BY Potencial_Arrecadacao DESC;

-- Consulta 3: Carga de turmas por professor
-- Objetivo: em quantas turmas cada professor esta alocado.
SELECT
    p.nome               AS Nome_Professor,
    COUNT(min.fk_Turma_id) AS Qtd_Turmas_Lecionadas
FROM Pessoa p
JOIN Professor prof ON p.id = prof.fk_Pessoa_id
JOIN ministra min ON prof.fk_Pessoa_id = min.fk_Professor_fk_Pessoa_id
GROUP BY p.id, p.nome
ORDER BY Qtd_Turmas_Lecionadas DESC;

-- Consulta 4: Resumo financeiro de mensalidades
-- Objetivo: soma dos valores das mensalidades agrupadas por situacao.
SELECT
    s.nome      AS Status_Mensalidade,
    COUNT(m.id) AS Volume_Boletos,
    SUM(m.valor) AS Valor_Acumulado
FROM Mensalidade m
JOIN situacao s ON m.fk_situacao_situacao_PK = s.situacao_PK
GROUP BY s.situacao_PK, s.nome
ORDER BY Valor_Acumulado DESC;

-- Consulta 5: Vagas ofertadas por categoria de esporte
-- Objetivo: total de vagas separando esportes coletivos e individuais.
SELECT
    CASE WHEN e.eh_coletivo = TRUE THEN 'Coletivo' ELSE 'Individual' END AS Tipo_Esporte,
    SUM(t.vagas_totais) AS Vagas_Totais_Disponiveis
FROM Esporte e
JOIN Turma t ON e.id = t.fk_Esporte_id
GROUP BY e.eh_coletivo
ORDER BY Vagas_Totais_Disponiveis DESC;

-- Consulta 6: Distribuicao demografica dos alunos (bairros)
-- Objetivo: quantidade de alunos agrupados pelo bairro onde residem.
SELECT
    end.bairro AS Bairro,
    COUNT(a.fk_Pessoa_id) AS Quantidade_Alunos
FROM Aluno a
JOIN Pessoa p ON a.fk_Pessoa_id = p.id
JOIN endereco end ON p.fk_endereco_endereco_PK = end.endereco_PK
GROUP BY end.bairro
ORDER BY Quantidade_Alunos DESC;

-- Consulta 7: Especializacoes dos professores
-- Objetivo: quantos professores estao aptos a lecionar cada esporte.
SELECT
    e.nome AS Modalidade_Esportiva,
    COUNT(esp.fk_Professor_fk_Pessoa_id) AS Professores_Especializados
FROM Esporte e
LEFT JOIN especiliazado esp ON e.id = esp.fk_Esporte_id
GROUP BY e.id, e.nome
ORDER BY Professores_Especializados DESC, e.nome ASC;

-- Consulta 8: Concentracao etaria dos alunos (uso de funcao de data)
-- Objetivo: extrair o ano de nascimento dos alunos para ver a concentracao
-- por ano. Versao SQLite de "EXTRACT(YEAR FROM p.data_nasc)".
SELECT
    CAST(strftime('%Y', p.data_nasc) AS INTEGER) AS Ano_Nascimento,
    COUNT(a.fk_Pessoa_id) AS Total_Nascidos
FROM Aluno a
JOIN Pessoa p ON a.fk_Pessoa_id = p.id
GROUP BY Ano_Nascimento
ORDER BY Total_Nascidos DESC;
