# RELATÓRIO — MODO FOCO: DURAÇÃO PERSONALIZADA ATÉ 24 HORAS

Data: 2026-09-24
Versão: VighnaStudy 0.29.13
Build: `foco-duracao-24h-v1`
Schema: 22 (sem alteração)

## Objetivo

Ampliar a duração personalizada do Modo Foco sem prejudicar a leitura da interface e sem deslocar a ação principal **Iniciar foco**.

## Interface

A linha de duração mantém os atalhos existentes:

- 25 min;
- 50 min;
- 90 min.

O antigo campo único de minutos foi substituído por dois controles compactos na mesma linha:

- horas: 0 a 24;
- minutos: 0 a 59, respeitando duração mínima de 1 minuto.

A ação **Iniciar foco** continua em uma linha própria e centralizada no card **Preparar sessão**, preservando a hierarquia visual atual.

## Regras de duração

- mínimo operacional: 1 minuto;
- máximo absoluto: 24h00min (1440 minutos);
- ao selecionar 24 horas, o campo de minutos passa automaticamente para 00 e fica desabilitado;
- com 0 horas, o campo de minutos não permite 0, evitando uma sessão de duração nula;
- presets continuam convertidos normalmente para horas/minutos (25 → 0h25, 50 → 0h50, 90 → 1h30);
- sessões preparadas por outros fluxos continuam recebendo `minutos` e são decompostas para horas/minutos, com limite seguro de 1440 minutos.

## Compatibilidade interna

O restante do Modo Foco continua trabalhando em minutos/segundos. A alteração é concentrada na entrada visual e na conversão da duração, sem alterar:

- registro de sessão de foco;
- pausas;
- histórico;
- resumo de tempo;
- pós-foco;
- integração com baterias automáticas;
- banco de dados.

## Arquivos alterados

- `foco.py`
- `versao.py`

## Validação realizada neste ambiente

- `python -m py_compile foco.py versao.py main.py banco.py` — OK.
- revisão do diff — somente `foco.py` e `versao.py` foram alterados em relação ao checkpoint recebido, além deste relatório novo.

A renderização Qt não pôde ser executada neste ambiente porque PySide6 não está instalado. A validação visual final deve ser feita no Windows antes de reconstruir o executável.

## Teste manual recomendado

Validar pelo menos:

1. presets 25, 50 e 90 minutos;
2. 0h01min;
3. 1h40min;
4. 12h30min;
5. 23h59min;
6. 24h00min;
7. centralização do botão **Iniciar foco**;
8. início, pausa e encerramento de uma sessão curta;
9. preparação automática de sessão pelo Dashboard;
10. temas Claro, Escuro e Futurista.
