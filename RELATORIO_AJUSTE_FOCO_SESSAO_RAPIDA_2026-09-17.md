# Ajuste do Dashboard — Foco + Sessão rápida

Versão: 0.23.5
Build: `dashboard-foco-sessao-rapida-v1`

## Objetivo

Substituir o antigo card "Hoje" por um módulo exclusivamente dedicado ao tempo de estudo, mantendo a recomendação de conteúdo em seu card próprio e aproximando a linguagem visual do bloco "Estudo por questões".

## O que foi alterado

1. O card "Hoje" foi removido da interface principal e substituído por **Foco**.
2. O cabeçalho do novo módulo segue a mesma lógica visual de "Estudo por questões": ícone, título recolhível, subtítulo e métricas compactas.
3. O bloco **Modo Foco** permanece como protagonista, agora em um card interno mais compacto e com destaque vermelho usado apenas como acento visual.
4. Foi criado o bloco **Sessão rápida**, com durações de **5, 10 e 15 minutos**.
5. A duração de 10 minutos fica selecionada por padrão.
6. O botão **Começar** inicia imediatamente o Modo Foco com a duração escolhida, sem exigir disciplina ou tópico e sem alterar o planejamento do usuário.
7. Se já existir uma sessão de foco ativa, o atalho de Sessão rápida apenas traz essa sessão para frente, evitando iniciar um segundo cronômetro.
8. As métricas superiores exibem tempo de foco hoje, quantidade de sessões no dia e situação da meta semanal.
9. A faixa de **Ações rápidas** foi mantida no rodapé do módulo de Foco.
10. A antiga área visual de "Resumo do dia" foi retirada. Os objetos internos necessários para compatibilidade com a lógica atual foram mantidos ocultos, evitando regressões enquanto a lógica é desacoplada gradualmente.
11. O estado recolhível existente foi preservado; a antiga seção `hoje` passa a aparecer visualmente como **Foco**.
12. Foram adicionados estilos específicos para os temas **Claro**, **Escuro** e **Futurista**.

## Arquivos alterados

- `main.py`
- `tema.py`
- `versao.py`

## Validação

- `python -m py_compile main.py tema.py foco.py banco.py testes_smoke.py versao.py` — OK.
- `QT_QPA_PLATFORM=offscreen python testes_smoke.py` — **VighnaStudy 0.23.5: testes smoke OK**.
- `PRAGMA integrity_check` no `estudos.db` — **ok**.

Observação: o ambiente de validação utilizado aqui não possui PySide6 instalado para renderização gráfica real da janela, portanto a checagem visual final deve ser feita no Windows ao abrir o projeto.
