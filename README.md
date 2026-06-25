# Sistema de Gestao de Centro de Treinamento (CT)

Este projeto acessa o banco de dados do Sistema de Gestao de Centro de
Treinamento, modelado no relatorio do trabalho. A aplicacao e um painel visual
feito em Streamlit, conectado a um banco MySQL hospedado na nuvem (Aiven).

---

## O que o programa faz

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

---

## Tecnologias utilizadas

- **Linguagem**: Python 3 (recomendado Python 3.10 ou superior).
- **Interface**: Streamlit.
- **Banco de dados**: MySQL hospedado no Aiven, acessado com SQLAlchemy e o
  driver PyMySQL, usando conexao SSL.

---

## Como rodar na sua maquina

Os passos sao os mesmos nos tres sistemas; o que muda sao alguns comandos.
Em todos, primeiro baixe o projeto (botao Code, Download ZIP, ou clone):

```bash
git clone https://github.com/arthurvtl/trabalho-bd.git
cd trabalho-bd
```

### Windows

```bat
python --version
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### macOS

```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Linux

Em algumas distribuicoes e preciso instalar o modulo de ambiente virtual antes
(por exemplo, no Ubuntu: `sudo apt install python3-venv`). Depois:

```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Em todos os casos, o navegador abre sozinho no endereco
`http://localhost:8501`. Se nao abrir, acesse esse endereco manualmente. Para
parar a aplicacao, pressione `Ctrl+C` no terminal.

Nao e preciso configurar banco de dados: a conexao com o Aiven ja vem pronta no
arquivo `config.py`, e o programa cria o esquema e carrega os dados
automaticamente caso o banco esteja vazio.

---

## Como tudo funciona por dentro

O programa e dividido em camadas, o que deixa o codigo organizado e mostra a
separacao de responsabilidades.

**1. config.py (dados de conexao).** Guarda host, porta, usuario, senha e nome do
banco do Aiven. E o unico lugar a mexer caso a senha mude.

**2. banco.py (camada de acesso ao banco).** A classe `Banco` faz tres coisas:

- Abre a conexao com o MySQL usando SQLAlchemy e o driver PyMySQL, com SSL
  (exigido pelo Aiven). A conexao fica em um pool e e reaproveitada.
- Ao iniciar, verifica se o banco ja tem dados. Se estiver vazio (maquina nova
  ou tabelas apagadas), executa sozinho o `schema_mysql.sql` (cria as tabelas) e
  o `seed_mysql.sql` (insere os dados). Isso e a recuperacao automatica: se as
  tabelas sumirem, na proxima execucao tudo e reconstruido.
- Oferece os metodos `consultar` (para SELECT) e `executar` (para INSERT, UPDATE
  e DELETE). Os comandos usam parametros nomeados (por exemplo `:nome`), o que
  evita SQL injection e cuida do escape dos valores.

**3. app.py (interface visual).** Monta as telas em Streamlit e chama os metodos
do `banco.py`. Cada botao de cadastro vira um INSERT, cada edicao um UPDATE e
cada remocao um DELETE. Os relatorios da Visao geral sao consultas SELECT com
JOIN, GROUP BY e funcoes de agregacao (COUNT, SUM).

### A parte de SQL

Sim, a parte de SQL esta funcionando e foi testada diretamente no Aiven. Os
arquivos sao:

- `schema_mysql.sql`: cria as 23 tabelas, com chaves primarias, chaves
  estrangeiras e regras de integridade (ON DELETE CASCADE, RESTRICT e SET NULL).
  As tabelas usam `CREATE TABLE IF NOT EXISTS`, entao rodar o script de novo nao
  causa erro.
- `seed_mysql.sql`: insere os dados iniciais. A primeira parte reproduz os dados
  do relatorio e a segunda completa as tabelas que o relatorio nao populou, para
  o banco ficar com pelo menos cinco registros por tabela.

As consultas dos relatorios ficam dentro do `app.py`, cada uma com o seu
objetivo (ocupacao das turmas, situacao financeira das mensalidades, e assim por
diante).

### Desempenho

Como o banco fica na nuvem, cada consulta tem o custo de ir e voltar pela
internet. Para o painel ficar agil:

- As leituras passam por um cache de curta duracao (`st.cache_data`), entao
  revisitar uma tela ja carregada e praticamente instantaneo.
- Os indicadores da Visao geral sao obtidos em uma unica consulta, em vez de
  varias.
- Apos qualquer alteracao (inserir, editar ou remover), o cache e limpo
  automaticamente para os dados aparecerem atualizados. Tambem ha um botao
  "Atualizar dados" no menu lateral.

A primeira carga leva alguns segundos (tempo de abrir a conexao com o servidor
na nuvem); as telas seguintes ficam rapidas.

---

## Estrutura dos arquivos

| Arquivo                  | Para que serve                                              |
|--------------------------|-------------------------------------------------------------|
| `app.py`                 | Interface visual em Streamlit (ponto de entrada).           |
| `banco.py`               | Conexao com o MySQL, recuperacao automatica e consultas.    |
| `config.py`              | Dados de conexao com o Aiven (host, usuario, senha, banco). |
| `schema_mysql.sql`       | Criacao das tabelas (MySQL).                                |
| `seed_mysql.sql`         | Carga inicial de dados (MySQL).                             |
| `requirements.txt`       | Bibliotecas necessarias para o painel.                      |
| `.streamlit/config.toml` | Configuracao do tema (modo claro).                          |

---

## Sobre o banco de dados (Aiven MySQL)

As credenciais de acesso estao embutidas em `config.py` de proposito, para que o
programa funcione assim que baixado, sem configuracao manual. O proposito do
projeto e educacional. Para trocar a senha, gere uma nova no painel do Aiven e
atualize a variavel `SENHA` em `config.py`.

---

## Repositorio

https://github.com/arthurvtl/trabalho-bd
