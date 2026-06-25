# Sistema de Gestao de Centro de Treinamento (CT)

Este projeto acessa o banco de dados do Sistema de Gestao de Centro de
Treinamento, modelado no relatorio do trabalho. Ele esta disponivel em duas
versoes:

1. **Painel do Dono** (recomendado): aplicacao visual feita em Streamlit, que se
   conecta a um banco MySQL hospedado na nuvem (Aiven). Permite ver e gerenciar
   alunos, professores, turmas, esportes e os vinculos entre eles, com
   relatorios gerenciais.
2. **Versao em terminal**: programa de linha de comando que usa um banco SQLite
   local, sem precisar instalar nada. Serve como alternativa offline.

---

## Painel do Dono (aplicacao visual)

### O que o programa faz

O painel abre no navegador e tem um menu lateral com as seguintes areas:

- **Visao geral**: indicadores do centro (total de alunos, professores, turmas,
  esportes, matriculas, mensalidades em aberto e vagas) e relatorios como
  ocupacao das turmas, resumo financeiro, arrecadacao por periodicidade, vagas
  por categoria e carga por professor.
- **Alunos, Professores, Turmas e Esportes**: cada area permite o CRUD completo
  (cadastrar, listar, editar e remover).
- **Vinculos**: gerencia os relacionamentos entre as entidades, ou seja,
  matriculas (aluno em turma), alocacoes (professor em turma), especializacoes
  (professor em esporte), responsaveis (aluno e seu responsavel) e planos (aluno
  e seu plano de pagamento). Da para adicionar e remover cada vinculo.

### Tecnologias utilizadas

- **Linguagem**: Python 3 (recomendado Python 3.10 ou superior).
- **Interface**: Streamlit.
- **Banco de dados**: MySQL hospedado no Aiven, acessado com SQLAlchemy e o
  driver PyMySQL, usando conexao SSL.

### Como rodar na sua maquina

1. Tenha o **Python 3** instalado. Para conferir:

   ```bash
   python --version
   ```

2. Baixe este repositorio (botao Code, Download ZIP) ou clone:

   ```bash
   git clone https://github.com/arthurvtl/trabalho-bd.git
   cd trabalho-bd
   ```

3. (Recomendado) Crie e ative um ambiente virtual:

   No Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   No macOS ou Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Instale as dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Rode a aplicacao:

   ```bash
   streamlit run app.py
   ```

   O navegador abre sozinho no endereco `http://localhost:8501`. Se nao abrir,
   acesse esse endereco manualmente.

Nao e preciso configurar banco de dados: a conexao com o Aiven ja vem pronta no
arquivo `config.py`, e o programa cria o esquema e carrega os dados
automaticamente caso o banco esteja vazio.

### Sobre o banco de dados (Aiven MySQL)

A conexao com o banco ja esta configurada em `config.py`. Na primeira execucao,
se as tabelas nao existirem, o programa roda o `schema_mysql.sql` e o
`seed_mysql.sql` automaticamente (ver `banco.py`). Se as tabelas forem apagadas,
o programa as reconstroi na proxima execucao.

As credenciais de acesso estao embutidas no codigo de proposito, para que o
programa funcione assim que baixado, sem configuracao manual. O proposito do
projeto e educacional. Para trocar a senha, gere uma nova no painel do Aiven e
atualize a variavel `SENHA` em `config.py`.

### Estrutura dos arquivos (Painel do Dono)

| Arquivo             | Para que serve                                              |
|---------------------|-------------------------------------------------------------|
| `app.py`            | Interface visual em Streamlit (ponto de entrada).           |
| `banco.py`          | Conexao com o MySQL e inicializacao automatica do banco.    |
| `config.py`         | Dados de conexao com o Aiven (host, usuario, senha, banco). |
| `schema_mysql.sql`  | Criacao das tabelas (MySQL).                                |
| `seed_mysql.sql`    | Carga inicial de dados (MySQL).                             |
| `requirements.txt`  | Bibliotecas necessarias para o painel.                      |
| `.streamlit/config.toml` | Configuracao do tema (modo claro).                     |

---

## Versao em terminal (SQLite)

Alternativa simples que roda sem instalar nada, usando um banco SQLite local em
arquivo. Util quando nao ha internet.

```bash
python3 main.py
```

Na primeira execucao, o banco `ct.db` e criado e populado automaticamente. Esta
versao usa os arquivos `schema.sql`, `seed.sql` e `consultas.sql` (dialeto
SQLite) e os modulos `database.py`, `models.py`, `repository.py` e
`relatorios.py`.

---

## Scripts SQL incluidos

| Arquivo            | Banco   | Conteudo                                  |
|--------------------|---------|-------------------------------------------|
| `schema_mysql.sql` | MySQL   | Criacao do esquema (Aiven).               |
| `seed_mysql.sql`   | MySQL   | Carga inicial de dados (Aiven).           |
| `schema.sql`       | SQLite  | Criacao do esquema (versao terminal).     |
| `seed.sql`         | SQLite  | Carga inicial de dados (versao terminal). |
| `consultas.sql`    | SQLite  | As 8 consultas da Secao 9 do relatorio.   |

A carga de dados reproduz a Secao 8 do relatorio e complementa as tabelas que
nao foram populadas la, para deixar o banco completo com pelo menos 5 registros
por tabela.

---

## Repositorio

https://github.com/arthurvtl/trabalho-bd
