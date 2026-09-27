# VighnaStudy 0.29.26 — Centralização vertical da recomendação

## Diagnóstico do checkpoint recebido

O checkpoint `2026-09-26_18-01-33` ainda estava em **0.29.25**. O código mantinha `acao_layout.setAlignment(Qt.AlignTop)`, portanto todo o conteúdo da recomendação permanecia ancorado no topo e o espaço excedente ficava no rodapé.

Também foi identificado um erro no `.bat` do patch anterior: a checagem da versão usava aspas aninhadas de forma inválida no `findstr`, podendo abortar antes de copiar os arquivos.

## Correção

- removido o alinhamento global `Qt.AlignTop` do `acao_layout`;
- mantido o cabeçalho no topo pela própria ordem do layout;
- inseridos `addStretch(1)` simétricos antes e depois de `algorithmRecommendationBody`;
- o painel **PRÓXIMA SESSÃO PRONTA** passa a ser centralizado apenas no espaço vertical restante abaixo do cabeçalho;
- o card **Planejamento de hoje** permanece inalterado;
- schema e banco de dados não foram alterados.

## Aplicação

O novo `.bat` usa uma verificação simples da string `0.29.25`, evitando o problema de aspas do patch anterior.
