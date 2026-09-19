# Relatório — Otimização de responsividade de Relatórios

Data: 18/09/2026  
Versão: 0.26.1  
Build: `responsividade-relatorios-lazy`  
Schema: 18

## 1. Problema observado

Ao clicar em **Relatórios**, a implementação anterior executava `atualizar_relatorios()` antes de trocar a página visível. Essa atualização carregava, em uma única passagem:

- resumo do período atual;
- resumo do período anterior;
- relatório por disciplina;
- relatório por tópico;
- relatório por dia;
- relatório estratégico;
- montagem de todas as tabelas correspondentes.

Assim, mesmo que o usuário quisesse apenas visualizar a primeira aba, todas as demais consultas e tabelas eram produzidas antes de a navegação terminar.

## 2. Medição do estado atual do banco

Medições isoladas no banco do checkpoint, em janela de 30 dias:

- resumo atual: ~0,67 ms;
- resumo anterior: ~0,61 ms;
- disciplinas: ~0,70 ms;
- tópicos: ~0,79 ms;
- diário: ~0,67 ms;
- estratégico: ~44,59 ms em média.

O principal custo de banco é o relatório estratégico. Além dele, a implementação antiga ainda construía todas as tabelas Qt, mesmo quando invisíveis.

## 3. Alterações implementadas

### 3.1 Navegação primeiro

`abrir_relatorios()` agora:

1. ajusta o período;
2. troca imediatamente para `tela_relatorios`;
3. agenda o carregamento após uma janela curta para repaint do Qt.

O clique deixa de aguardar o processamento antes da mudança de tela.

### 3.2 Carregamento preguiçoso por aba

Foi criado `relatorios_lazy.py`, com `EstadoRelatoriosLazy`.

Abas controladas:

- Estratégico;
- Por disciplina;
- Por tópico;
- Por dia.

Ao entrar em Relatórios são carregados somente:

- o resumo/comparação visível no topo;
- a aba atualmente selecionada.

As demais abas são carregadas apenas quando abertas.

### 3.3 Reentrada sem recomputação

Se concurso, período e dados acadêmicos não mudaram, voltar para Relatórios não recalcula o conteúdo já carregado.

Uma mudança real de dados chama `invalidar_relatorios()`, deixando as informações marcadas para atualização na próxima visualização necessária.

### 3.4 Troca de aba

`QTabWidget.currentChanged` agenda a atualização apenas da aba escolhida.

Isso evita carregar tabelas de tópicos, disciplinas e dias enquanto continuam invisíveis.

### 3.5 Tabelas

As tabelas de:

- estratégico por disciplina;
- relatório por disciplina;
- relatório por tópico;
- relatório por dia;

passaram a suspender `updates` e sinais durante preenchimento, reduzindo repaint intermediário.

### 3.6 Exportação CSV

A exportação continua completa. Se alguma aba ainda não foi aberta, `_garantir_dados_relatorio_exportacao()` busca os dados faltantes diretamente para o CSV, sem precisar montar visualmente as abas invisíveis.

### 3.7 Alterações de dados

O barramento `notificar_dados_alterados()` agora invalida Relatórios junto das demais áreas analíticas. Assim, o ganho de cache não produz informação antiga depois de questões, revisões ou outras mudanças acadêmicas.

## 4. Comportamento esperado

Primeira abertura:

- página aparece imediatamente;
- resumo e aba atual são preenchidos em seguida;
- abas invisíveis não geram trabalho.

Segunda abertura sem mudança de dados:

- troca de página praticamente imediata;
- nenhum recálculo relevante.

Ao abrir uma aba pela primeira vez:

- somente aquela aba é carregada;
- revisitas reutilizam o estado enquanto os dados permanecerem válidos.

## 5. Arquivos principais alterados

- `main.py`
- `relatorios_lazy.py`
- `test_relatorios_lazy.py`
- `test_responsividade_relatorios.py`
- `versao.py`

## 6. Validação

- 190 testes unittest: OK;
- smoke test: OK;
- `py_compile`: OK;
- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações.

Foram observados `ResourceWarning` antigos da suíte relacionados a conexões SQLite em fixtures de `fila_candidata.py`; não foram introduzidos por esta alteração e não causaram falha de teste.

## 7. Validação visual pendente

O ambiente de execução desta revisão não reproduz a interface PySide6 do Windows de forma adequada para aferição perceptiva. A validação final deve testar repetidamente:

- Dashboard → Relatórios → Voltar;
- Relatórios → Por disciplina → Por tópico → Por dia → Estratégico;
- sair de Relatórios e entrar novamente sem alterar dados;
- responder questões/revisar e reabrir Relatórios para confirmar invalidação correta.

## 8. Resultado esperado

A área de Relatórios passa a seguir o mesmo princípio de responsividade já adotado em Estatísticas e Central de Questões: **navegar primeiro, calcular apenas o que está visível e reutilizar resultados quando nada mudou**.
