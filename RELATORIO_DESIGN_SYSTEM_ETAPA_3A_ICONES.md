# Relatório — Design System Vighna — Etapa 3A: Ícones

## Resultado

Foi concluído o primeiro piloto de migração real do Design System. Exclusivamente as decisões de cor da tabela `CORES_ICONES`, em `icones.py`, passaram a consumir a API pública `qtawesome_color()`.

A migração é de caracterização: os valores exibidos por tema e papel permanecem idênticos aos anteriores. Nomes de glifos, tamanhos, chamadas, fallbacks, lógica QtAwesome, layout e comportamento não foram alterados.

Versão preservada: VighnaStudy `0.29.59`, build `calendar-week-forecast-v1`, schema `25`.

## Estado anterior

`icones.py` mantinha uma segunda tabela temática com nove literais de cor, cinco valores distintos:

| Tema | `acao` | `destaque` | `configuracao` |
|---|---|---|---|
| Claro | `#355874` | `#FFFFFF` | `#0F3989` |
| Escuro | `#BED0E1` | `#FFFFFF` | `#BED0E1` |
| Futurista | `#B6D9E8` | `#FFFFFF` | `#B6D9E8` |

`cor_icone()` normalizava o tema, consultava essa tabela e usava `acao` como fallback de papel. `criar_icone()` encaminhava a cor para `qta.icon()` e, em caso de ausência ou erro no QtAwesome, preservava o fallback opcional por arquivo e depois um `QIcon` vazio.

## Incompatibilidade encontrada

Os tokens necessários já existiam no contrato, mas seus valores iniciais da Etapa 2 eram representativos e não correspondiam ao subsistema legado de ícones:

| Token | Claro anterior no DS | Escuro anterior no DS | Futurista anterior no DS |
|---|---|---|---|
| `icon.action` | `#5965D8` | `#7882E8` | `#757FFF` |
| `icon.highlight` | `#28679E` | `#8FD8FF` | `#8FD8FF` |
| `icon.configuration` | `#64748B` | `#94A3B8` | `#BCE7FF` |

Esses valores não foram impostos ao componente. Conforme a regra de equivalência visual, os três tokens foram ajustados em cada tema para representar exatamente a linha de base de `icones.py`.

## Arquivos alterados

- `icones.py`: substitui os nove literais em `CORES_ICONES` por caminhos de token e resolve a cor por `qtawesome_color()`.
- `ui/design/palette.py`: registra `#355874`, `#0F3989` e `#BED0E1`, valores legados que ainda não estavam na paleta física. `#FFFFFF` e `#B6D9E8` já existiam.
- `ui/design/themes.py`: alinha somente `icon.action`, `icon.highlight` e `icon.configuration` com os valores legados nos três temas.
- `test_design_system.py`: atualiza a caracterização do adaptador para o valor real de `icon.action` no Futurista.
- `test_design_system_icones.py`: adiciona testes específicos do piloto.
- `DESIGN_SYSTEM.md`: registra `icones.py` como primeiro consumidor real e mantém explícitos os limites da integração.
- `RELATORIO_DESIGN_SYSTEM_ETAPA_3A_ICONES.md`: registra esta etapa.

`tema.py`, `main.py`, banco, schema, glifos, assets e demais componentes não foram alterados.

## Tokens utilizados

| Papel legado | Token público |
|---|---|
| `acao` | `icon.action` |
| `destaque` | `icon.highlight` |
| `configuracao` | `icon.configuration` |

Não foi necessário criar token novo nem promover `specific.*`.

## Valores antes e depois

| Tema | Papel | Antes | Depois via token | Equivalente |
|---|---|---|---|:---:|
| Claro | ação | `#355874` | `#355874` | sim |
| Claro | destaque | `#FFFFFF` | `#FFFFFF` | sim |
| Claro | configuração | `#0F3989` | `#0F3989` | sim |
| Escuro | ação | `#BED0E1` | `#BED0E1` | sim |
| Escuro | destaque | `#FFFFFF` | `#FFFFFF` | sim |
| Escuro | configuração | `#BED0E1` | `#BED0E1` | sim |
| Futurista | ação | `#B6D9E8` | `#B6D9E8` | sim |
| Futurista | destaque | `#FFFFFF` | `#FFFFFF` | sim |
| Futurista | configuração | `#B6D9E8` | `#B6D9E8` | sim |

Foram removidas de `icones.py` nove ocorrências hardcoded, correspondentes a cinco cores distintas. Os valores não foram eliminados do produto: foram centralizados na paleta física e nas definições temáticas.

## Preservação de comportamento

- `normalizar_tema()` continua sendo usado antes da resolução.
- Papel desconhecido continua usando `acao` como fallback.
- `criar_icone()` continua encaminhando o mesmo nome de glifo ao QtAwesome.
- Exceções de `qta.icon()` continuam capturadas para não impedir a abertura da aplicação.
- `fallback_path` continua criando `QIcon` quando o arquivo existe.
- Ausência de QtAwesome e de arquivo continua retornando `QIcon()` vazio.
- Glifos Unicode e ícones que herdam cor de QSS não entraram no escopo.

## Testes

Os testes específicos cobrem:

1. igualdade exata dos nove valores anteriores nos três temas;
2. ausência de hexadecimal em `CORES_ICONES`;
3. uso da API pública `qtawesome_color()`;
4. fallback de papel para `icon.action`;
5. encaminhamento de nome e cor por `criar_icone()`;
6. fallback por arquivo com QtAwesome ausente;
7. fallback por arquivo quando QtAwesome lança exceção;
8. retorno de ícone vazio sem QtAwesome e sem arquivo;
9. resolução de cor sem `QApplication` ativo.

A validação final obteve:

- `py_compile` de `icones.py`, infraestrutura relacionada e testes: aprovado;
- `test_design_system.py`, `test_qtawesome_integracao.py` e `test_design_system_icones.py`: **22/22 testes aprovados**;
- `testes_smoke.py`: `VighnaStudy 0.29.59: testes smoke OK`.

## Problemas encontrados

O teste inicial tentou inspecionar materialmente o PNG do fallback sem uma aplicação gráfica. O Qt exige infraestrutura de GUI para carregar o conteúdo do ícone e encerrou esse processo de teste. A caracterização foi corrigida para validar diretamente a chamada preservada `QIcon(str(caminho))`, enquanto a importação e a resolução de cores continuam testadas separadamente sem `QApplication`.

Não foi necessário alterar o código funcional de fallback por causa dessa limitação de teste.

## Lições para as próximas migrações

1. Existência do token não garante equivalência: valores devem ser confrontados por tema antes de conectar o consumidor.
2. Tokens representativos da fundação devem ceder à linha de base real do primeiro componente migrado, sem aproximação de cor.
3. Testes devem separar resolução sem estado de operações Qt que materializam recursos gráficos.
4. Fallbacks precisam ser caracterizados pelo contrato observável, não reimplementados para facilitar testes.
5. Uma migração pequena permite validar todo o fluxo paleta física → tema → token → adaptador → consumidor antes de atacar QSS ou componentes maiores.

## Limite desta etapa

Nenhum outro componente foi migrado. A subpaleta de splash/tarefas, os estilos de `tema.py`, QPainter, QSS, glifos Unicode e recursos bitmap permanecem para etapas futuras mediante nova autorização.
