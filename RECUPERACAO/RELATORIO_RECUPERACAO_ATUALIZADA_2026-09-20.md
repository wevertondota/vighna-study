# Relatório — recuperação atualizada do banco do VighnaStudy

## Banco recebido

Foi auditado o arquivo `estudos(3).db`, enviado após a inclusão de 14 novas questões.

Contagem confirmada antes da recuperação:

| Item | Quantidade |
|---|---:|
| Questões físicas | 2.522 |
| Questões ativas | 2.509 |
| Lixeira | 13 |
| Direito Penal ativo | 270 |
| Dignidade Sexual ativa | 18 |
| Sessões de questões | 27 |
| Tentativas | 163 |

As 14 questões novas ocupam os IDs **2509 a 2522**, todas em Direito Penal / TÍTULO VI – Dos Crimes Contra a Dignidade Sexual. Elas permanecem exatamente iguais no banco recuperado.

## Recuperação aplicada na cópia

Foram inseridas 42 questões ausentes:

| Origem | Quantidade |
|---|---:|
| VPQ — Liberdade Sexual | 7 |
| VPQ — Crimes Sexuais Contra Vulnerável | 18 |
| VPQ — Exposição da Intimidade Sexual | 5 |
| Histórico — Ultraje Público ao Pudor | 6 |
| Histórico — Título XII / Instituições Democráticas | 6 |
| **Total** | **42** |

Os novos registros receberam IDs **2523 a 2564**. Nenhuma das 42 coincidiu literalmente com uma questão já existente no banco recebido.

## Preservação do banco recebido

Foi feita comparação campo a campo entre o banco recebido e o recuperado:

- **0 questões preexistentes alteradas**;
- **0 alternativas preexistentes alteradas**;
- as 14 questões novas foram preservadas integralmente;
- sessões permanecem em 27;
- tentativas permanecem em 163;
- revisões e estrutura curricular não foram reescritas.

## Resultado final

| Item | Antes | Depois |
|---|---:|---:|
| Questões físicas | 2.522 | 2.564 |
| Questões ativas | 2.509 | 2.551 |
| Lixeira | 13 | 13 |
| Direito Penal ativo | 270 | 312 |
| Dignidade Sexual ativa | 18 | 54 |
| Estado Democrático de Direito ativo | 23 | 29 |

Distribuição atual de Dignidade Sexual após a recuperação:

- sem capítulo interno: 19 (14 recém-adicionadas + 5 de Exposição da Intimidade Sexual);
- Capítulo I — Liberdade Sexual: 7;
- Capítulo II — Crimes Sexuais Contra Vulnerável: 18;
- Capítulo IV — Ultraje Público ao Pudor: 6;
- Capítulo V — Disposições Gerais: 4.

## Auditoria das demais disciplinas

A auditoria histórica sobre 58 bancos recuperáveis extraídos de 73 checkpoints continua apontando apenas 19 versões históricas ausentes literalmente do banco atual, todas em Direito Penal. Dessas, 7 correspondem a reformulações/edições de questões que continuam existentes e 12 são as perdas históricas recuperadas. Não surgiu evidência adicional de perda em CTB, Direito Administrativo, Direito Constitucional, Informática, Leis Complementares ou Português.

## Integridade

- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 problemas;
- teste da proteção de banco único: 4 testes aprovados.

## Observação

As 5 questões de Exposição da Intimidade Sexual ficam temporariamente vinculadas ao Título VI sem capítulo interno porque a taxonomia atual não contém `Capítulo I-A – Da Exposição da Intimidade Sexual`. Nenhum capítulo novo foi criado automaticamente.
