"""
app.py
======
Painel do Dono - Sistema de Gestao de Centro de Treinamento (CT).

Aplicacao visual feita com Streamlit. Permite ao dono do centro de treinamento
ver e gerenciar alunos, professores, turmas, esportes e os vinculos entre eles
(matriculas, alocacoes de professores, especializacoes, responsaveis e planos),
alem de acompanhar relatorios gerenciais.

Os dados ficam em um banco MySQL hospedado no Aiven, configurado em config.py.
Na primeira execucao, se o banco estiver vazio, o esquema e os dados sao criados
automaticamente (ver banco.py).

Como rodar:
    streamlit run app.py
"""

from datetime import date

import pandas as pd
import streamlit as st

from banco import Banco

DATA_MIN = date(1900, 1, 1)
DATA_MAX = date(2100, 12, 31)


# ---------------------------------------------------------------------------
# Conexao (criada uma unica vez por sessao)
# ---------------------------------------------------------------------------

@st.cache_resource
def obter_banco():
    return Banco()


# ---------------------------------------------------------------------------
# Funcoes auxiliares
# ---------------------------------------------------------------------------

def mostrar_tabela(linhas):
    """Exibe uma lista de dicionarios como tabela, ou um aviso se estiver vazia."""
    if linhas:
        st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum registro cadastrado ainda.")


def escalar(banco, sql):
    """Devolve o primeiro valor da primeira linha de uma consulta."""
    resultado = banco.consultar(sql)
    if not resultado:
        return 0
    return list(resultado[0].values())[0]


def mapa_opcoes(banco, sql):
    """Monta um dicionario {rotulo: id} a partir de uma consulta com colunas id e rotulo."""
    return {linha["rotulo"]: linha["id"] for linha in banco.consultar(sql)}


SQL_ALUNOS = (
    "SELECT p.id AS id, CONCAT(p.id, ' - ', p.nome) AS rotulo "
    "FROM Aluno a JOIN Pessoa p ON a.fk_Pessoa_id = p.id ORDER BY p.nome"
)
SQL_PROFESSORES = (
    "SELECT p.id AS id, CONCAT(p.id, ' - ', p.nome) AS rotulo "
    "FROM Professor pr JOIN Pessoa p ON pr.fk_Pessoa_id = p.id ORDER BY p.nome"
)
SQL_RESPONSAVEIS = (
    "SELECT p.id AS id, CONCAT(p.id, ' - ', p.nome) AS rotulo "
    "FROM Responsavel r JOIN Pessoa p ON r.fk_Pessoa_id = p.id ORDER BY p.nome"
)
SQL_TURMAS = "SELECT id, CONCAT(id, ' - ', nome) AS rotulo FROM Turma ORDER BY nome"
SQL_ESPORTES = "SELECT id, CONCAT(id, ' - ', nome) AS rotulo FROM Esporte ORDER BY nome"
SQL_PLANOS = "SELECT id, CONCAT(id, ' - ', nome) AS rotulo FROM PlanoPagamento ORDER BY nome"
SQL_HORARIOS_TURMA = "SELECT id, CONCAT(id, ' - ', nome) AS rotulo FROM HorarioTurma ORDER BY nome"


# ---------------------------------------------------------------------------
# Pagina: Visao geral
# ---------------------------------------------------------------------------

def pagina_visao_geral(banco):
    st.header("Visao geral")
    st.caption("Resumo do centro de treinamento e relatorios gerenciais.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alunos", escalar(banco, "SELECT COUNT(*) FROM Aluno"))
    col2.metric("Professores", escalar(banco, "SELECT COUNT(*) FROM Professor"))
    col3.metric("Turmas", escalar(banco, "SELECT COUNT(*) FROM Turma"))
    col4.metric("Esportes", escalar(banco, "SELECT COUNT(*) FROM Esporte"))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Matriculas", escalar(banco, "SELECT COUNT(*) FROM Matricula_turma"))
    col6.metric(
        "Mensalidades em aberto",
        escalar(banco,
                "SELECT COUNT(*) FROM Mensalidade m JOIN situacao s "
                "ON m.fk_situacao_situacao_PK = s.situacao_PK "
                "WHERE s.nome IN ('Pendente', 'Atrasada')"),
    )
    col7.metric("Planos", escalar(banco, "SELECT COUNT(*) FROM PlanoPagamento"))
    col8.metric(
        "Vagas totais",
        escalar(banco, "SELECT COALESCE(SUM(vagas_totais), 0) FROM Turma"),
    )

    st.divider()
    st.subheader("Relatorios")

    # Consulta 1: ocupacao das turmas
    st.markdown("**Ocupacao das turmas**")
    ocupacao = banco.consultar(
        "SELECT t.nome AS Turma, e.nome AS Esporte, t.vagas_totais AS Capacidade, "
        "COUNT(m.fk_Aluno_fk_Pessoa_id) AS Matriculados "
        "FROM Turma t JOIN Esporte e ON t.fk_Esporte_id = e.id "
        "LEFT JOIN Matricula_turma m ON t.id = m.fk_Turma_id "
        "GROUP BY t.id, t.nome, e.nome, t.vagas_totais ORDER BY Matriculados DESC"
    )
    coluna_tabela, coluna_grafico = st.columns(2)
    with coluna_tabela:
        mostrar_tabela(ocupacao)
    with coluna_grafico:
        if ocupacao:
            grafico = pd.DataFrame(ocupacao).set_index("Turma")[["Matriculados"]]
            st.bar_chart(grafico)

    # Consulta 4: resumo financeiro
    st.markdown("**Resumo financeiro das mensalidades**")
    financeiro = banco.consultar(
        "SELECT s.nome AS Situacao, COUNT(m.id) AS Quantidade, SUM(m.valor) AS Total "
        "FROM Mensalidade m JOIN situacao s ON m.fk_situacao_situacao_PK = s.situacao_PK "
        "GROUP BY s.situacao_PK, s.nome ORDER BY Total DESC"
    )
    mostrar_tabela(financeiro)

    # Consulta 2: arrecadacao por periodicidade
    st.markdown("**Arrecadacao potencial por periodicidade dos planos**")
    arrecadacao = banco.consultar(
        "SELECT per.nome AS Periodicidade, COUNT(pp.id) AS Planos, SUM(pp.valor) AS Total "
        "FROM PlanoPagamento pp JOIN periodicidade per "
        "ON pp.fk_periodicidade_periodicidade_PK = per.periodicidade_PK "
        "GROUP BY per.periodicidade_PK, per.nome ORDER BY Total DESC"
    )
    mostrar_tabela(arrecadacao)

    # Consulta 5: vagas por categoria
    st.markdown("**Vagas por categoria de esporte**")
    categorias = banco.consultar(
        "SELECT CASE WHEN e.eh_coletivo = TRUE THEN 'Coletivo' ELSE 'Individual' END AS Tipo, "
        "SUM(t.vagas_totais) AS Vagas "
        "FROM Esporte e JOIN Turma t ON e.id = t.fk_Esporte_id "
        "GROUP BY e.eh_coletivo ORDER BY Vagas DESC"
    )
    mostrar_tabela(categorias)

    # Consulta 3: carga por professor
    st.markdown("**Carga de turmas por professor**")
    carga = banco.consultar(
        "SELECT p.nome AS Professor, COUNT(mi.fk_Turma_id) AS Turmas "
        "FROM Pessoa p JOIN Professor pr ON p.id = pr.fk_Pessoa_id "
        "JOIN ministra mi ON pr.fk_Pessoa_id = mi.fk_Professor_fk_Pessoa_id "
        "GROUP BY p.id, p.nome ORDER BY Turmas DESC"
    )
    mostrar_tabela(carga)


# ---------------------------------------------------------------------------
# Pagina: Alunos
# ---------------------------------------------------------------------------

def pagina_alunos(banco):
    st.header("Alunos")

    linhas = banco.consultar(
        "SELECT p.id AS id, p.nome, p.cpf, p.email, p.data_nasc, "
        "a.data_matricula, a.condicao_saude "
        "FROM Aluno a JOIN Pessoa p ON a.fk_Pessoa_id = p.id ORDER BY p.id"
    )
    mostrar_tabela(linhas)

    aba_add, aba_editar, aba_remover = st.tabs(["Adicionar", "Editar", "Remover"])

    with aba_add:
        with st.form("aluno_add", clear_on_submit=True):
            nome = st.text_input("Nome")
            cpf = st.text_input("CPF")
            email = st.text_input("E-mail")
            nasc = st.date_input("Data de nascimento", value=date(2005, 1, 1),
                                 min_value=DATA_MIN, max_value=DATA_MAX)
            matricula = st.date_input("Data de matricula", value=date.today(),
                                      min_value=DATA_MIN, max_value=DATA_MAX)
            saude = st.text_input("Condicao de saude", value="Apto")
            if st.form_submit_button("Cadastrar aluno"):
                if not nome.strip():
                    st.error("O nome e obrigatorio.")
                else:
                    novo_id = banco.proximo_id("Pessoa")
                    banco.executar(
                        "INSERT INTO Pessoa (id, nome, cpf, email, data_nasc) "
                        "VALUES (:id, :nome, :cpf, :email, :nasc)",
                        {"id": novo_id, "nome": nome, "cpf": cpf, "email": email, "nasc": nasc},
                    )
                    banco.executar(
                        "INSERT INTO Aluno (fk_Pessoa_id, data_matricula, condicao_saude) "
                        "VALUES (:id, :matricula, :saude)",
                        {"id": novo_id, "matricula": matricula, "saude": saude},
                    )
                    st.success(f"Aluno cadastrado com o id {novo_id}.")
                    st.rerun()

    with aba_editar:
        opcoes = mapa_opcoes(banco, SQL_ALUNOS)
        if not opcoes:
            st.info("Nenhum aluno para editar.")
        else:
            escolhido = st.selectbox("Aluno", list(opcoes.keys()), key="aluno_edit_sel")
            ident = opcoes[escolhido]
            atual = banco.consultar(
                "SELECT p.nome, p.cpf, p.email, p.data_nasc, a.data_matricula, a.condicao_saude "
                "FROM Aluno a JOIN Pessoa p ON a.fk_Pessoa_id = p.id WHERE p.id = :id",
                {"id": ident},
            )[0]
            with st.form("aluno_editar"):
                nome = st.text_input("Nome", value=atual["nome"])
                cpf = st.text_input("CPF", value=atual["cpf"] or "")
                email = st.text_input("E-mail", value=atual["email"] or "")
                nasc = st.date_input("Data de nascimento", value=atual["data_nasc"],
                                     min_value=DATA_MIN, max_value=DATA_MAX)
                matricula = st.date_input("Data de matricula", value=atual["data_matricula"],
                                          min_value=DATA_MIN, max_value=DATA_MAX)
                saude = st.text_input("Condicao de saude", value=atual["condicao_saude"] or "")
                if st.form_submit_button("Salvar alteracoes"):
                    banco.executar(
                        "UPDATE Pessoa SET nome = :nome, cpf = :cpf, email = :email, "
                        "data_nasc = :nasc WHERE id = :id",
                        {"nome": nome, "cpf": cpf, "email": email, "nasc": nasc, "id": ident},
                    )
                    banco.executar(
                        "UPDATE Aluno SET data_matricula = :matricula, condicao_saude = :saude "
                        "WHERE fk_Pessoa_id = :id",
                        {"matricula": matricula, "saude": saude, "id": ident},
                    )
                    st.success("Aluno atualizado.")
                    st.rerun()

    with aba_remover:
        opcoes = mapa_opcoes(banco, SQL_ALUNOS)
        if not opcoes:
            st.info("Nenhum aluno para remover.")
        else:
            escolhido = st.selectbox("Aluno", list(opcoes.keys()), key="aluno_del_sel")
            st.caption("Remover o aluno tambem remove suas matriculas e vinculos.")
            if st.button("Remover aluno", type="primary"):
                banco.executar("DELETE FROM Pessoa WHERE id = :id", {"id": opcoes[escolhido]})
                st.success("Aluno removido.")
                st.rerun()


# ---------------------------------------------------------------------------
# Pagina: Professores
# ---------------------------------------------------------------------------

def pagina_professores(banco):
    st.header("Professores")

    linhas = banco.consultar(
        "SELECT p.id AS id, p.nome, p.cpf, p.email, p.data_nasc "
        "FROM Professor pr JOIN Pessoa p ON pr.fk_Pessoa_id = p.id ORDER BY p.id"
    )
    mostrar_tabela(linhas)

    aba_add, aba_editar, aba_remover = st.tabs(["Adicionar", "Editar", "Remover"])

    with aba_add:
        with st.form("prof_add", clear_on_submit=True):
            nome = st.text_input("Nome")
            cpf = st.text_input("CPF")
            email = st.text_input("E-mail")
            nasc = st.date_input("Data de nascimento", value=date(1990, 1, 1),
                                 min_value=DATA_MIN, max_value=DATA_MAX)
            if st.form_submit_button("Cadastrar professor"):
                if not nome.strip():
                    st.error("O nome e obrigatorio.")
                else:
                    novo_id = banco.proximo_id("Pessoa")
                    banco.executar(
                        "INSERT INTO Pessoa (id, nome, cpf, email, data_nasc) "
                        "VALUES (:id, :nome, :cpf, :email, :nasc)",
                        {"id": novo_id, "nome": nome, "cpf": cpf, "email": email, "nasc": nasc},
                    )
                    banco.executar(
                        "INSERT INTO Professor (fk_Pessoa_id) VALUES (:id)", {"id": novo_id}
                    )
                    st.success(f"Professor cadastrado com o id {novo_id}.")
                    st.rerun()

    with aba_editar:
        opcoes = mapa_opcoes(banco, SQL_PROFESSORES)
        if not opcoes:
            st.info("Nenhum professor para editar.")
        else:
            escolhido = st.selectbox("Professor", list(opcoes.keys()), key="prof_edit_sel")
            ident = opcoes[escolhido]
            atual = banco.consultar(
                "SELECT nome, cpf, email, data_nasc FROM Pessoa WHERE id = :id", {"id": ident}
            )[0]
            with st.form("prof_editar"):
                nome = st.text_input("Nome", value=atual["nome"])
                cpf = st.text_input("CPF", value=atual["cpf"] or "")
                email = st.text_input("E-mail", value=atual["email"] or "")
                nasc = st.date_input("Data de nascimento", value=atual["data_nasc"],
                                     min_value=DATA_MIN, max_value=DATA_MAX)
                if st.form_submit_button("Salvar alteracoes"):
                    banco.executar(
                        "UPDATE Pessoa SET nome = :nome, cpf = :cpf, email = :email, "
                        "data_nasc = :nasc WHERE id = :id",
                        {"nome": nome, "cpf": cpf, "email": email, "nasc": nasc, "id": ident},
                    )
                    st.success("Professor atualizado.")
                    st.rerun()

    with aba_remover:
        opcoes = mapa_opcoes(banco, SQL_PROFESSORES)
        if not opcoes:
            st.info("Nenhum professor para remover.")
        else:
            escolhido = st.selectbox("Professor", list(opcoes.keys()), key="prof_del_sel")
            st.caption("Remover o professor tambem remove suas alocacoes e especializacoes.")
            if st.button("Remover professor", type="primary"):
                banco.executar("DELETE FROM Pessoa WHERE id = :id", {"id": opcoes[escolhido]})
                st.success("Professor removido.")
                st.rerun()


# ---------------------------------------------------------------------------
# Pagina: Turmas
# ---------------------------------------------------------------------------

def pagina_turmas(banco):
    st.header("Turmas")

    linhas = banco.consultar(
        "SELECT t.id AS id, t.nome, t.vagas_totais, e.nome AS esporte, h.nome AS horario "
        "FROM Turma t LEFT JOIN Esporte e ON t.fk_Esporte_id = e.id "
        "LEFT JOIN HorarioTurma h ON t.fk_HorarioTurma_id = h.id ORDER BY t.id"
    )
    mostrar_tabela(linhas)

    aba_add, aba_editar, aba_remover = st.tabs(["Adicionar", "Editar", "Remover"])

    esportes = mapa_opcoes(banco, SQL_ESPORTES)
    horarios = mapa_opcoes(banco, SQL_HORARIOS_TURMA)

    with aba_add:
        if not esportes or not horarios:
            st.info("Cadastre ao menos um esporte e um horario de turma antes.")
        else:
            with st.form("turma_add", clear_on_submit=True):
                nome = st.text_input("Nome da turma")
                vagas = st.number_input("Vagas totais", min_value=1, value=15, step=1)
                esporte = st.selectbox("Esporte", list(esportes.keys()))
                horario = st.selectbox("Horario", list(horarios.keys()))
                if st.form_submit_button("Cadastrar turma"):
                    if not nome.strip():
                        st.error("O nome e obrigatorio.")
                    else:
                        novo_id = banco.proximo_id("Turma")
                        banco.executar(
                            "INSERT INTO Turma (id, nome, vagas_totais, fk_HorarioTurma_id, fk_Esporte_id) "
                            "VALUES (:id, :nome, :vagas, :horario, :esporte)",
                            {"id": novo_id, "nome": nome, "vagas": int(vagas),
                             "horario": horarios[horario], "esporte": esportes[esporte]},
                        )
                        st.success(f"Turma cadastrada com o id {novo_id}.")
                        st.rerun()

    with aba_editar:
        turmas = mapa_opcoes(banco, SQL_TURMAS)
        if not turmas:
            st.info("Nenhuma turma para editar.")
        else:
            escolhido = st.selectbox("Turma", list(turmas.keys()), key="turma_edit_sel")
            ident = turmas[escolhido]
            atual = banco.consultar(
                "SELECT nome, vagas_totais, fk_Esporte_id, fk_HorarioTurma_id "
                "FROM Turma WHERE id = :id", {"id": ident}
            )[0]
            rotulos_esp = list(esportes.keys())
            rotulos_hor = list(horarios.keys())
            idx_esp = next((i for i, r in enumerate(rotulos_esp)
                            if esportes[r] == atual["fk_Esporte_id"]), 0)
            idx_hor = next((i for i, r in enumerate(rotulos_hor)
                            if horarios[r] == atual["fk_HorarioTurma_id"]), 0)
            with st.form("turma_editar"):
                nome = st.text_input("Nome da turma", value=atual["nome"])
                vagas = st.number_input("Vagas totais", min_value=1,
                                        value=int(atual["vagas_totais"] or 1), step=1)
                esporte = st.selectbox("Esporte", rotulos_esp, index=idx_esp)
                horario = st.selectbox("Horario", rotulos_hor, index=idx_hor)
                if st.form_submit_button("Salvar alteracoes"):
                    banco.executar(
                        "UPDATE Turma SET nome = :nome, vagas_totais = :vagas, "
                        "fk_Esporte_id = :esporte, fk_HorarioTurma_id = :horario WHERE id = :id",
                        {"nome": nome, "vagas": int(vagas), "esporte": esportes[esporte],
                         "horario": horarios[horario], "id": ident},
                    )
                    st.success("Turma atualizada.")
                    st.rerun()

    with aba_remover:
        turmas = mapa_opcoes(banco, SQL_TURMAS)
        if not turmas:
            st.info("Nenhuma turma para remover.")
        else:
            escolhido = st.selectbox("Turma", list(turmas.keys()), key="turma_del_sel")
            st.caption("Remover a turma tambem remove suas matriculas, aulas e alocacoes.")
            if st.button("Remover turma", type="primary"):
                banco.executar("DELETE FROM Turma WHERE id = :id", {"id": turmas[escolhido]})
                st.success("Turma removida.")
                st.rerun()


# ---------------------------------------------------------------------------
# Pagina: Esportes
# ---------------------------------------------------------------------------

def pagina_esportes(banco):
    st.header("Esportes")

    linhas = banco.consultar(
        "SELECT id, nome, descricao, "
        "CASE WHEN eh_coletivo = TRUE THEN 'Coletivo' ELSE 'Individual' END AS tipo "
        "FROM Esporte ORDER BY id"
    )
    mostrar_tabela(linhas)

    aba_add, aba_editar, aba_remover = st.tabs(["Adicionar", "Editar", "Remover"])

    with aba_add:
        with st.form("esporte_add", clear_on_submit=True):
            nome = st.text_input("Nome")
            descricao = st.text_input("Descricao")
            coletivo = st.checkbox("E um esporte coletivo")
            if st.form_submit_button("Cadastrar esporte"):
                if not nome.strip():
                    st.error("O nome e obrigatorio.")
                else:
                    novo_id = banco.proximo_id("Esporte")
                    banco.executar(
                        "INSERT INTO Esporte (id, nome, descricao, eh_coletivo) "
                        "VALUES (:id, :nome, :descricao, :coletivo)",
                        {"id": novo_id, "nome": nome, "descricao": descricao,
                         "coletivo": 1 if coletivo else 0},
                    )
                    st.success(f"Esporte cadastrado com o id {novo_id}.")
                    st.rerun()

    with aba_editar:
        esportes = mapa_opcoes(banco, SQL_ESPORTES)
        if not esportes:
            st.info("Nenhum esporte para editar.")
        else:
            escolhido = st.selectbox("Esporte", list(esportes.keys()), key="esp_edit_sel")
            ident = esportes[escolhido]
            atual = banco.consultar(
                "SELECT nome, descricao, eh_coletivo FROM Esporte WHERE id = :id", {"id": ident}
            )[0]
            with st.form("esporte_editar"):
                nome = st.text_input("Nome", value=atual["nome"])
                descricao = st.text_input("Descricao", value=atual["descricao"] or "")
                coletivo = st.checkbox("E um esporte coletivo", value=bool(atual["eh_coletivo"]))
                if st.form_submit_button("Salvar alteracoes"):
                    banco.executar(
                        "UPDATE Esporte SET nome = :nome, descricao = :descricao, "
                        "eh_coletivo = :coletivo WHERE id = :id",
                        {"nome": nome, "descricao": descricao,
                         "coletivo": 1 if coletivo else 0, "id": ident},
                    )
                    st.success("Esporte atualizado.")
                    st.rerun()

    with aba_remover:
        esportes = mapa_opcoes(banco, SQL_ESPORTES)
        if not esportes:
            st.info("Nenhum esporte para remover.")
        else:
            escolhido = st.selectbox("Esporte", list(esportes.keys()), key="esp_del_sel")
            st.caption("Nao e possivel remover um esporte que tenha turmas vinculadas.")
            if st.button("Remover esporte", type="primary"):
                try:
                    banco.executar("DELETE FROM Esporte WHERE id = :id", {"id": esportes[escolhido]})
                    st.success("Esporte removido.")
                    st.rerun()
                except Exception:
                    st.error("Nao foi possivel remover: ha turma(s) usando este esporte.")


# ---------------------------------------------------------------------------
# Pagina: Vinculos
# ---------------------------------------------------------------------------

def secao_vinculo(banco, chave, tabela, col_a, col_b, sql_pares, ops_a, ops_b, rot_a, rot_b):
    """
    Componente generico para gerenciar uma tabela de vinculo (relacionamento).
    Mostra os vinculos atuais, permite adicionar e remover.
    sql_pares deve retornar as colunas: a, b e rotulo.
    """
    pares = banco.consultar(sql_pares)
    mostrar_tabela([{"vinculo": p["rotulo"]} for p in pares])

    if not ops_a or not ops_b:
        st.info("Cadastre os registros necessarios antes de criar vinculos.")
        return

    with st.form(f"add_{chave}", clear_on_submit=True):
        st.markdown("Adicionar vinculo")
        rotulo_a = st.selectbox(rot_a, list(ops_a.keys()), key=f"a_{chave}")
        rotulo_b = st.selectbox(rot_b, list(ops_b.keys()), key=f"b_{chave}")
        if st.form_submit_button("Adicionar"):
            try:
                banco.executar(
                    f"INSERT INTO {tabela} ({col_a}, {col_b}) VALUES (:a, :b)",
                    {"a": ops_a[rotulo_a], "b": ops_b[rotulo_b]},
                )
                st.success("Vinculo adicionado.")
                st.rerun()
            except Exception:
                st.error("Nao foi possivel adicionar (o vinculo pode ja existir).")

    if pares:
        rotulos = {p["rotulo"]: (p["a"], p["b"]) for p in pares}
        escolhido = st.selectbox("Vinculo para remover", list(rotulos.keys()), key=f"del_{chave}")
        if st.button("Remover vinculo", key=f"btn_{chave}", type="primary"):
            valor_a, valor_b = rotulos[escolhido]
            banco.executar(
                f"DELETE FROM {tabela} WHERE {col_a} = :a AND {col_b} = :b LIMIT 1",
                {"a": valor_a, "b": valor_b},
            )
            st.success("Vinculo removido.")
            st.rerun()


def pagina_vinculos(banco):
    st.header("Vinculos")
    st.caption("Relacionamentos entre alunos, professores, turmas, esportes, responsaveis e planos.")

    alunos = mapa_opcoes(banco, SQL_ALUNOS)
    professores = mapa_opcoes(banco, SQL_PROFESSORES)
    responsaveis = mapa_opcoes(banco, SQL_RESPONSAVEIS)
    turmas = mapa_opcoes(banco, SQL_TURMAS)
    esportes = mapa_opcoes(banco, SQL_ESPORTES)
    planos = mapa_opcoes(banco, SQL_PLANOS)

    abas = st.tabs(["Matriculas", "Alocacoes", "Especializacoes", "Responsaveis", "Planos"])

    with abas[0]:
        st.subheader("Matriculas (aluno em turma)")
        secao_vinculo(
            banco, "matricula", "Matricula_turma",
            "fk_Aluno_fk_Pessoa_id", "fk_Turma_id",
            "SELECT m.fk_Aluno_fk_Pessoa_id AS a, m.fk_Turma_id AS b, "
            "CONCAT(p.nome, ' na turma ', t.nome) AS rotulo "
            "FROM Matricula_turma m JOIN Pessoa p ON m.fk_Aluno_fk_Pessoa_id = p.id "
            "JOIN Turma t ON m.fk_Turma_id = t.id ORDER BY p.nome",
            alunos, turmas, "Aluno", "Turma",
        )

    with abas[1]:
        st.subheader("Alocacoes (professor em turma)")
        secao_vinculo(
            banco, "ministra", "ministra",
            "fk_Professor_fk_Pessoa_id", "fk_Turma_id",
            "SELECT mi.fk_Professor_fk_Pessoa_id AS a, mi.fk_Turma_id AS b, "
            "CONCAT(p.nome, ' ministra ', t.nome) AS rotulo "
            "FROM ministra mi JOIN Pessoa p ON mi.fk_Professor_fk_Pessoa_id = p.id "
            "JOIN Turma t ON mi.fk_Turma_id = t.id ORDER BY p.nome",
            professores, turmas, "Professor", "Turma",
        )

    with abas[2]:
        st.subheader("Especializacoes (professor em esporte)")
        secao_vinculo(
            banco, "especializado", "especiliazado",
            "fk_Professor_fk_Pessoa_id", "fk_Esporte_id",
            "SELECT esp.fk_Professor_fk_Pessoa_id AS a, esp.fk_Esporte_id AS b, "
            "CONCAT(p.nome, ' apto em ', e.nome) AS rotulo "
            "FROM especiliazado esp JOIN Pessoa p ON esp.fk_Professor_fk_Pessoa_id = p.id "
            "JOIN Esporte e ON esp.fk_Esporte_id = e.id ORDER BY p.nome",
            professores, esportes, "Professor", "Esporte",
        )

    with abas[3]:
        st.subheader("Responsaveis (aluno e seu responsavel)")
        secao_vinculo(
            banco, "encarregado", "encarregado",
            "fk_Aluno_fk_Pessoa_id", "fk_Responsavel_fk_Pessoa_id",
            "SELECT en.fk_Aluno_fk_Pessoa_id AS a, en.fk_Responsavel_fk_Pessoa_id AS b, "
            "CONCAT(pa.nome, ' tem responsavel ', pr.nome) AS rotulo "
            "FROM encarregado en JOIN Pessoa pa ON en.fk_Aluno_fk_Pessoa_id = pa.id "
            "JOIN Pessoa pr ON en.fk_Responsavel_fk_Pessoa_id = pr.id ORDER BY pa.nome",
            alunos, responsaveis, "Aluno", "Responsavel",
        )

    with abas[4]:
        st.subheader("Planos (aluno e seu plano de pagamento)")
        secao_vinculo(
            banco, "planoaluno", "PlanoAluno",
            "fk_Aluno_fk_Pessoa_id", "fk_PlanoPagamento_id",
            "SELECT pl.fk_Aluno_fk_Pessoa_id AS a, pl.fk_PlanoPagamento_id AS b, "
            "CONCAT(p.nome, ' no plano ', pp.nome) AS rotulo "
            "FROM PlanoAluno pl JOIN Pessoa p ON pl.fk_Aluno_fk_Pessoa_id = p.id "
            "JOIN PlanoPagamento pp ON pl.fk_PlanoPagamento_id = pp.id ORDER BY p.nome",
            alunos, planos, "Aluno", "Plano",
        )


# ---------------------------------------------------------------------------
# Estrutura principal
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Painel do Dono - Centro de Treinamento", layout="wide")
    st.title("Painel do Dono")
    st.caption("Sistema de Gestao de Centro de Treinamento")

    banco = obter_banco()

    paginas = {
        "Visao geral": pagina_visao_geral,
        "Alunos": pagina_alunos,
        "Professores": pagina_professores,
        "Turmas": pagina_turmas,
        "Esportes": pagina_esportes,
        "Vinculos": pagina_vinculos,
    }

    with st.sidebar:
        st.header("Menu")
        escolha = st.radio("Ir para", list(paginas.keys()))
        st.divider()
        st.caption("Dados em MySQL no Aiven.")

    paginas[escolha](banco)


if __name__ == "__main__":
    main()
