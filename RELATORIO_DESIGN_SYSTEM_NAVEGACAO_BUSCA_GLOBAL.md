# RELATÓRIO — DESIGN SYSTEM — NAVEGAÇÃO PRINCIPAL — BUSCA GLOBAL

**Projeto:** VighnaStudy 0.29.59
**Data:** 2026-10-07
**Base:** `VighnaStudy_0.29.59_DesignSystem_Dashboard_Bloco_I_COMPLETO.zip`
**Escopo:** `JanelaBuscaGlobal` / command palette (`Ctrl+K`)
**Fase:** centralização estrutural sem redesenho

## 1. Objetivo

Centralizar no Design System as cores ainda físicas da Busca global, preservando integralmente a aparência, a estrutura da janela, os `objectName`, atalhos, filtragem, navegação, fechamento, seleção de resultados e demais comportamentos.

A implementação segue a caracterização previamente aprovada em `RELATORIO_DESIGN_SYSTEM_NAVEGACAO_PRINCIPAL_CARACTERIZACAO.md`.

## 2. Limites do recorte

### Incluído

- `QDialog#globalSearchDialog`;
- título, subtítulo, status e hint;
- badge do atalho;
- campo de busca em estado normal e foco;
- seleção de texto do campo;
- tabela de resultados;
- cabeçalho e divisores;
- seleção de linha na tabela.

### Excluído

- `globalSearchTrigger` do Dashboard, já centralizado no Dashboard — Bloco A;
- `globalSearchCloseButton`, que permanece oculto e sem necessidade de novo contrato cromático;
- botões `← Voltar` das telas secundárias;
- comportamento de `JanelaBuscaGlobal` em `navegacao.py`;
- roteamento, atalhos e lógica de pesquisa;
- qualquer redesign da Busca global;
- qualquer alteração de banco, versão, build ou schema.

## 3. Implementação

Foi criada em `tema.py` a camada aditiva final:

`ESTILO_NAVEGACAO_BUSCA_GLOBAL`

Todos os seletores novos estão subordinados a `QDialog#globalSearchDialog`, evitando vazamento para `QLineEdit`, tabelas, cabeçalhos ou labels de outras áreas do programa.

A camada foi renderizada ao final dos três temas usando `render_qss()` e, se removida, o QSS do checkpoint Dashboard I é recuperado byte por byte no conteúdo renderizado.

## 4. Tokens

Foram adicionados **20 tokens de componente, todos de cor e nenhum gradiente**:

- `navigation.command_canvas`
- `navigation.command_title_text`
- `navigation.command_meta_text`
- `navigation.command_shortcut_surface`
- `navigation.command_shortcut_text`
- `navigation.command_shortcut_border`
- `navigation.command_input_surface`
- `navigation.command_input_text`
- `navigation.command_input_border`
- `navigation.command_input_selection`
- `navigation.command_input_focus_border`
- `navigation.command_results_surface`
- `navigation.command_results_text`
- `navigation.command_results_border`
- `navigation.command_results_selection_surface`
- `navigation.command_results_selection_text`
- `navigation.command_results_divider`
- `navigation.command_header_surface`
- `navigation.command_header_text`
- `navigation.command_header_border`

Contagem do Design System:

- antes: **972 tokens** = 102 semânticos + 870 de componente;
- depois: **992 tokens** = 102 semânticos + 890 de componente.

Para registrar os valores físicos necessários nos temas foram acrescentadas **41 cores à palette física**. Esses registros não são tokens semânticos ou de componente; apenas disponibilizam valores físicos já existentes na aparência histórica.

## 5. Arquivos de produção alterados

- `tema.py`
- `ui/design/tokens.py`
- `ui/design/themes.py`
- `ui/design/palette.py`

Hashes SHA-256 finais:

- `tema.py`: `b665457ded9b550505bf9a61a53c73f8c9641ab8b6292238c5c3941294c7a308`
- `ui/design/tokens.py`: `695b84d6f0258727f285845ed337d5327523401f04ab1b030022a3435cc60dcf`
- `ui/design/themes.py`: `a0007bba86141f37e231a4c18de5a4fbe16498155d65139dad16bcfdebf0f2e5`
- `ui/design/palette.py`: `f1545db7520fe5ec6f471ac84257c85a1fe8e89dc8ad060a85ad7fba8cc07aed`

## 6. Arquivos funcionais protegidos

Permaneceram byte a byte idênticos ao checkpoint Dashboard I:

- `main.py`: `0ef8b3214a566cfaf1d329e84d701bb0ca776b15bdf2e647dccbc6e4fb2a7cb7`
- `navegacao.py`: `2cb3439a580cf867af9870750a82e06777718961dd84819e0705a96838c8b862`
- `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`
- `versao.py`: `8436214451a591c0a3d3429f62d53c0c01cfc0cc7311d71e57fcf060f5b39642`
- `foco.py`: `8fbe4659f3371683738a3fa239a789b3bca26ab47dc68f38a69829a33afd03ed`
- `jogos.py`: `498aab65a2a13efa070ae2f912536b5ddc1aada31e23a28846def6a617492286`
- `checkpoint.py`: `947295fdf2035d6f65d5d43f70e1d6e5e1c411d92eaca264a469a221b6b61c38`

## 7. QSS final e reversibilidade

Hashes do QSS completo após a nova camada:

- Claro: `0e7a1298205211d0526e06c0c6bcbb77b0fbb33e917d8a347819549ebd51243c`
- Escuro: `f69025da433b27bc72f0b754c142a44cbd2b392a9f13cb4826aae0976fc90445`
- Futurista: `96678da0b086d2b6d68202b7794120aa44df9deae284c170590f0320b6e29ee5`

Resultado da resolução de tokens nos três temas:

- `{{color:...}}` não resolvido: **0**;
- `{{gradient:...}}` não resolvido: **0**.

Ao remover somente a camada da Busca global, os hashes recuperados são exatamente os do checkpoint Dashboard I:

- Claro: `43a889513b8b66814eba82e843b969f733f84eab74ab638f7ee622f82c7ab96c`
- Escuro: `56dfdb0b68dfa37f58774c361d2f5809bea10cf05526f4fc88599ca13c5a87d0`
- Futurista: `bac2f89881f1989aa89bc464a95b872b41bb06ee4f8f32b93134e42cc794fd70`

Isso confirma que o recorte é aditivo e reversível.

## 8. Testes

### Teste específico da Busca global

`test_design_system_navegacao_busca_global.py`

**9/9 aprovados.**

Ele verifica contagem e valores dos tokens, registro físico na palette, escopo dos seletores, estados materiais, ausência de vazamento para `globalSearchTrigger`, ausência de contrato desnecessário para o botão oculto, resolução dos três temas, rollback e preservação dos arquivos funcionais.

### Bateria dirigida cumulativa

**121/121 testes aprovados — 0 falhas e 0 erros.**

A bateria inclui Dashboard A–I, recortes já centralizados do Resolvedor, resumo final, jogos e a nova Busca global.

### Suíte ampla do Design System

Baseline Dashboard I: **265 testes, 8 falhas históricas e 6 erros ambientais/Qt**.
Após esta implementação: **274 testes, as mesmas 8 falhas históricas e os mesmos 6 erros ambientais/Qt**.

As 9 unidades adicionais correspondem ao teste específico deste recorte. Não apareceu nova falha atribuível à Busca global.

Os testes históricos de snapshot foram ajustados apenas para desconsiderar a nova camada final antes de comparar seus próprios baselines antigos; seus contratos originais continuam sendo testados sem regravar artificialmente os hashes históricos.

### Compilação

`py_compile` aprovado para os arquivos de produção alterados e para os principais arquivos funcionais protegidos.

## 9. Banco de dados

- `PRAGMA integrity_check`: **ok**;
- `PRAGMA foreign_key_check`: **0 violações**;
- `estudos.db`: byte a byte idêntico ao checkpoint Dashboard I.

## 10. Limitação do ambiente de teste

O ambiente Linux usado nesta implementação não possui a instalação real de PySide6 utilizada no Windows. Os testes estruturais/QSS foram executados com o mesmo stub mínimo já empregado nas auditorias anteriores para permitir a importação de `tema.py`.

Por isso, a validação visual e funcional real da GUI continua dependendo da execução manual no Windows.

## 11. Validação manual recomendada no Windows

1. Abrir a Busca global com `Ctrl+K` nos temas Claro, Escuro e Futurista.
2. Conferir fundo da janela, título, subtítulo, status e hint.
3. Conferir badge do atalho.
4. Conferir campo de busca normal, foco, cursor/texto e seleção de texto.
5. Conferir tabela vazia e preenchida, cabeçalho, divisores e linha selecionada.
6. Digitar consultas e verificar filtragem em tempo real.
7. Abrir um resultado por Enter e por clique.
8. Fechar por Esc e confirmar que o comportamento anterior continua intacto.
9. Verificar histórico/comandos recentes, quando aplicável.
10. Confirmar que o gatilho de Busca global no Dashboard permanece visualmente inalterado.
11. Conferir rapidamente outros dialogs, `QLineEdit` e tabelas para excluir vazamento visual.

## 12. Conclusão

A centralização da **Busca global / command palette** foi concluída de forma isolada, aditiva e reversível, sem alterações em `main.py`, `navegacao.py`, banco ou comportamento.

**Estado técnico: APROVADO NOS TESTES AUTOMATIZADOS.**
**Pendente: validação manual no Windows pelo usuário.**

Somente após essa validação deve ser feita a auditoria curta do macroescopo **Navegação principal**, especialmente para decidir se os botões `← Voltar` justificam um segundo recorte próprio.
