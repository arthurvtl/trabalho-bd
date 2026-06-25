"""
config.py
=========
Dados de conexao com o banco MySQL hospedado no Aiven.

A senha fica embutida aqui de proposito, para que o programa funcione assim que
for baixado, sem nenhuma configuracao manual. O proposito do projeto e
educacional.

Para trocar a senha (recomendado depois da entrega): gere uma nova no painel do
Aiven, na pagina do servico, e atualize apenas a variavel SENHA abaixo.
"""

HOST = "mysql-ct-arthurvtl.j.aivencloud.com"
PORT = 11651
USUARIO = "avnadmin"
SENHA = "AVNS_U8rUqc8Mh_2iKnF4RoS"
BANCO = "defaultdb"
