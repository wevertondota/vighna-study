# VighnaStudy 0.29.25 — Ajuste vertical do Dashboard

## Objetivo
Aplicar duas mudanças pontuais no Dashboard sem alterar os demais cards:

1. **Recomendação do algoritmo**: reduzir o vazio superior e manter o conteúdo ancorado no topo do card, deixando eventual espaço excedente no rodapé.
2. **Planejamento de hoje**: remover a linha compacta **“Próximos 7 dias”**, manter essa informação somente na seção completa de Planejamento e puxar o conteúdo restante para cima.

## Alterações
- `main.py`
  - `dashboardTodayAction`: margens verticais levemente reduzidas e layout alinhado ao topo.
  - bloco de títulos da recomendação alinhado ao topo.
  - `dashboardInsightSummary`: margem superior reduzida e layout alinhado ao topo.
  - removida apenas a linha compacta “Próximos 7 dias” do card “Planejamento de hoje”.
  - mantidos os cálculos e a exibição dos próximos 7 dias na seção completa de Planejamento.
- `versao.py`
  - versão: `0.29.25`
  - build: `dashboard-planejamento-ajuste-vertical-v1`
- `test_dashboard_inteligencia.py`
  - atualizado para validar a ausência da linha compacta de 7 dias e o alinhamento superior dos dois cards.

## Preservado
- Foco.
- Seu progresso.
- Conteúdo e ação da Recomendação do algoritmo.
- Seção completa de Planejamento, incluindo “Próximos 7 dias”.
- Acessos rápidos e todos os blocos inferiores.
- Schema do banco: `23`.
- `estudos.db`: sem alteração.

## Validação
- `python -m py_compile main.py versao.py tema.py`: OK.
- `python -m unittest -v test_dashboard_inteligencia.py`: 7/7 OK.
- `PRAGMA integrity_check`: `ok`.
- `PRAGMA foreign_key_check`: 0 violações.
- SHA-256 do `estudos.db` antes/depois: idêntico.

## Observação visual
A validação final de espaçamento deve ser feita no Windows/PySide6, em especial em 1366×768, verificando se:
- o texto da recomendação sobe e o grande vazio superior desaparece;
- o botão “VER PLANEJAMENTO ↓” fica totalmente visível;
- nenhum outro card muda de posição ou aparência além do necessário pela redução natural da altura da linha.
