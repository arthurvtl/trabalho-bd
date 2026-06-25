# Programa com Acesso ao Banco - Sistema de Gestao de Centro de Treinamento (CT)

Programa em Python (orientado a objetos) que acessa o banco de dados do
projeto **Sistema de Gestao de Centro de Treinamento**, modelado no relatorio
do trabalho. Ele atende as duas opcoes previstas na Secao 10 do Template do
trabalho ao mesmo tempo:

1. **Um CRUD completo** (inserir, listar, alterar e excluir) da tabela
   **Esporte** e, como bonus, da entidade **Aluno**.
2. **Um menu de consultas** que executa as **8 consultas SQL** da Secao 9 do
   relatorio e mostra os resultados em tabela.

## O que o programa faz

Ao iniciar, o programa cria o banco de dados na primeira execucao (esquema +
carga de dados) e abre um menu de terminal com tres areas:

- **CRUD de Esporte**: cadastra, lista, altera e remove modalidades
  esportivas. A exclusao respeita a integridade do banco (nao deixa apagar um
  esporte que esteja sendo usado por uma turma).
- **CRUD de Aluno**: como Aluno e uma especializacao de Pessoa, cada operacao
  cuida das duas tabelas (Pessoa e Aluno) de forma coordenada.
- **Relatorios**: executa as 8 consultas gerenciais (ocupacao de turmas,
  arrecadacao por periodicidade, carga por professor, resumo financeiro, vagas
  por categoria, alunos por bairro, especializacoes e concentracao etaria).

## Tecnologias utilizadas

- **Linguagem**: Python 3 (testado na versao 3.14).
- **Banco de dados**: SQLite, acessado pela biblioteca **sqlite3**, que ja vem
  embutida no Python.
- **Dependencias externas**: nenhuma. Nao e preciso instalar nada com `pip`.

O SQLite foi escolhido porque o banco inteiro fica em um unico arquivo
(`ct.db`), criado automaticamente. Nao exige instalar um servidor de banco nem
configurar usuario e senha, entao o programa roda em qualquer maquina que
tenha Python.

## Pre-requisitos

- Ter o **Python 3** instalado. Para conferir:

```bash
python3 --version
```

(No Windows, em geral o comando e `python` no lugar de `python3`.)

## Como rodar

1. Abra o terminal dentro desta pasta (`programa_ct`):

```bash
cd programa_ct
```

2. Execute o programa:

```bash
python3 main.py
```

No Windows:

```bash
python main.py
```

Na primeira execucao aparece a mensagem informando que o banco foi criado.
A partir dai, basta navegar pelo menu digitando o numero da opcao e
pressionando Enter.

## Como recriar o banco do zero

O banco fica no arquivo `ct.db`. Para zerar tudo e recarregar os dados
iniciais, basta apagar esse arquivo e rodar o programa de novo:

```bash
rm ct.db        # no Windows: del ct.db
python3 main.py
```

## Estrutura dos arquivos

| Arquivo          | Para que serve                                                        |
|------------------|----------------------------------------------------------------------|
| `main.py`        | Interface de menu (ponto de entrada do programa).                    |
| `database.py`    | Classe que abre a conexao e inicializa o banco (le os `.sql`).        |
| `models.py`      | Classes das entidades (Pessoa, Aluno, Esporte) com heranca.           |
| `repository.py`  | Operacoes de CRUD de Esporte e Aluno.                                 |
| `relatorios.py`  | As 8 consultas da Secao 9 organizadas como metodos.                  |
| `schema.sql`     | Criacao das tabelas (Secao 7 do relatorio, em dialeto SQLite).        |
| `seed.sql`       | Carga inicial de dados (Secao 8 do relatorio, em dialeto SQLite).     |
| `consultas.sql`  | As 8 consultas em SQL puro, para consulta e documentacao.            |
| `ct.db`          | Banco gerado automaticamente (nao versionado no Git).                |

A separacao em camadas (modelo, repositorio, banco e interface) e proposital:
deixa o codigo organizado e mostra a orientacao a objetos na pratica.

## Diferencas entre o SQL do relatorio (MySQL) e esta versao (SQLite)

O conteudo logico do banco e identico ao do relatorio. As tabelas, os dados e
as consultas sao os mesmos. So foi preciso adaptar tres pontos de **sintaxe**,
porque o relatorio usa o dialeto MySQL/PostgreSQL e aqui usamos SQLite:

1. **Chaves estrangeiras**: o relatorio adiciona as FKs com
   `ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY`. O SQLite nao suporta esse
   comando, entao as mesmas FKs foram declaradas **dentro do `CREATE TABLE`**
   (inline). Por causa disso, as tabelas sao criadas em ordem (a tabela
   referenciada vem antes). As regras `ON DELETE` (CASCADE, RESTRICT, SET NULL)
   foram mantidas.

2. **Funcao de data (Consulta 8)**: o relatorio usa
   `EXTRACT(YEAR FROM data_nasc)`. No SQLite o equivalente e
   `CAST(strftime('%Y', data_nasc) AS INTEGER)`. O resultado e o mesmo (o ano
   de nascimento).

3. **Tipo booleano**: o SQLite nao tem um tipo booleano proprio; ele guarda
   `0` (falso) ou `1` (verdadeiro). As palavras `TRUE` e `FALSE` continuam
   funcionando normalmente nos scripts.

A integridade referencial do SQLite so vale com
`PRAGMA foreign_keys = ON`, que o programa ativa automaticamente em toda
conexao (ver `database.py`).

## Observacao sobre os dados

A carga inicial (`seed.sql`) tem duas partes:

- **Secao A**: os dados exatamente como aparecem na Secao 8 do relatorio.
- **Secao B**: dados complementares para as tabelas que o relatorio nao
  populou (Horario, Aula, Frequencia, ItemHorario, PlanoAluno, encarregado e
  Cancelamento_Aula), apenas para deixar o banco completo com pelo menos 5
  registros por tabela. Eles nao afetam as consultas da Secao 9.

## Repositorio

O codigo deve ficar disponivel em um repositorio do GitHub. Substitua a linha
abaixo pelo endereco real apos subir o projeto:

```
https://github.com/arthurvtl/trabalho-bd
```
