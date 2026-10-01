# Ajuste de autonomia referencial — Crimes Contra a Pessoa — 30/09/2026

## Resultado

- Questões ativas preservadas: **353**.
- Alternativas ativas preservadas: **1765**.
- Questões com texto ajustado: **234**.
- Alternativas com referente explicitado: **581**.
- Gabaritos, IDs e ordem das alternativas: **preservados**.

## Bateria já iniciada

O ciclo de revisão existente foi mantido **sem reinicialização**:

- ciclo ativo: **#5**;
- respondidas: **131**;
- pendentes: **222**;
- tentativas históricas preservadas: **131**.

Os snapshots das questões já respondidas foram mantidos intactos. Foram atualizados somente os snapshots ainda não respondidos/não alcançados, para que a continuação da bateria mostre o texto corrigido sem apagar o progresso.

## Estratégia

A correção foi feita **in-place**, alterando apenas o texto das alternativas quando faltava autonomia referencial. Não houve exclusão, recriação ou troca de IDs das questões.

Exemplo de correção:

- Antes: `As condutas equiparadas recebem apenas multa, sem reclusão.`
- Depois: `Redução a condição análoga à de escravo — As condutas equiparadas recebem apenas multa, sem reclusão.`

## Validação

- `PRAGMA integrity_check`: **ok**.
- violações de foreign key: **0**.
- questões com estrutura inválida de alternativas/gabarito: **0**.
- testes direcionados de ciclo persistente e banco único: **9/9 OK**.
