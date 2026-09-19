# RELATÓRIO — CABEÇALHO ASSIMÉTRICO EM DUAS LINHAS

Data: 2026-09-18
Versão: 0.27.2
Build: `dashboard-header-two-row`
Schema: 19

## Objetivo
Reorganizar o cabeçalho do Dashboard para eliminar o congestionamento horizontal observado na versão 0.27.1.

## Estrutura final

### Coluna esquerda
A marca VighnaStudy ocupa verticalmente as duas linhas do cabeçalho.

### Linha superior
- Busca global com maior largura útil;
- Central de Questões com largura suficiente para o texto completo;
- Configurações em botão compacto de engrenagem.

### Linha inferior
- Perfil ativo com seletor e botão Gerenciar;
- chip de gamificação em área própria, separado do perfil.

## Gamificação no cabeçalho
O chip mostra somente:
- nível;
- XP total;
- percentual para o próximo nível;
- barra visual curta.

A quantidade de marcos foi removida do cabeçalho para reduzir ruído visual. O chip continua clicável e abre `Estatísticas → Conquistas`.

## Dashboard principal
Os antigos painéis horizontais de Regularidade e Conquistas permanecem ocultos. As informações completas continuam disponíveis em Estatísticas.

## Arquivos alterados
- `main.py`
- `versao.py`

## Validação
- `python -m py_compile main.py versao.py` ✅
- suíte unittest: **199 testes aprovados** ✅
- smoke test ✅
- `PRAGMA integrity_check = ok` ✅
- `PRAGMA foreign_key_check`: 0 violações ✅
- checkpoint nativo completo e validado ✅

## Resultado esperado
Visualmente, o topo segue a hierarquia:

```text
VighnaStudy        Buscar no Vighna...        Central de Questões   ⚙
                   PERFIL ATIVO ...            Nível / XP / progresso
```

A disposição deve manter melhor legibilidade em larguras de janela próximas de 1366 px.
