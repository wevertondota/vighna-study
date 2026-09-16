# VighnaStudy — Continuação do Projeto

## Ponto atual
Projeto desktop em Python + PySide6 + SQLite.

Último checkpoint estável:
- VighnaStudy_checkpoint_estavel_pos_redesign.zip

Esse checkpoint consolida:
- Dashboard redesenhado
- Concurso + Perfis centralizados no topo
- Estudar agora centralizado e sem moldura
- Disciplinas + Edição centralizados
- Estatísticas e Relatórios alinhados
- Configurações redesenhadas
- Tema Claro/Escuro
- Logo e ícone VighnaStudy
- Estrelas de importância
- Chamas de prioridade
- Backups
- Perfis de concurso
- Relatórios
- Estatísticas
- Matriz de espaçamento configurável

## Banco de dados
NÃO substituir nem perder:
C:\SistemaEstudos\estudos.db

Também preservar:
C:\SistemaEstudos\backups

## Arquivos principais
- main.py
- tema.py
- banco.py
- backup.py
- espacamento.py
- vighnastudy.ico
- atualizar_exe.bat

## Executável esperado
C:\SistemaEstudos\dist\SistemaEstudos\VighnaStudy.exe

## Próxima etapa planejada
Implementar o CALENDÁRIO DE REVISÕES.

Ideia inicial:
- visualização por mês/dia
- mostrar revisões previstas
- destacar hoje e atrasadas
- clicar em uma revisão para abrir o tópico
- permitir iniciar/registrar revisão a partir do calendário
- respeitar o perfil/concurso ativo
- integrar com a lógica já existente de próxima revisão

## Como continuar em uma nova conversa
Envie:
1. VighnaStudy_checkpoint_estavel_pos_redesign.zip
2. Este arquivo VighnaStudy_CONTINUAR_PROJETO.md

E escreva:

"Quero continuar o desenvolvimento do VighnaStudy a partir deste checkpoint.
A próxima etapa é o Calendário de Revisões. Preserve todas as funcionalidades,
o banco estudos.db e a arquitetura atual."

## Regra importante
Sempre testar primeiro com:

cd C:\SistemaEstudos
.venv\Scripts\activate
python -m py_compile main.py
python -m py_compile tema.py
python main.py

Só depois executar:
atualizar_exe.bat

## Segurança
O checkpoint não contém estudos.db.
O banco ativo do usuário deve ser preservado.
