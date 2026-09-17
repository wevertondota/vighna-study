# Relatório — Refino visual do módulo Foco

Data: 17/09/2026  
Versão: 0.23.6  
Build: `dashboard-foco-modern-v2`

## Objetivo

Modernizar o módulo **Foco** e a **Sessão rápida** sem alterar a arquitetura aprovada e mantendo a mesma linguagem visual do setor **Estudo por questões**.

## Ajustes realizados

- Mantida a estrutura em um container principal com dois cards internos.
- Tipografia refinada no módulo, priorizando `Segoe UI Variable Text` com fallback para `Segoe UI`.
- Hierarquia de títulos, descrições, métricas e legendas reajustada.
- Cores do Modo Foco suavizadas para um vermelho/coral mais sóbrio.
- Sessão rápida recebeu paleta teal mais coesa e menos saturada.
- Fundos internos ficaram mais neutros, com tintas muito suaves e bordas discretas.
- Ícones internos aumentados e padronizados; o raio da Sessão rápida passou a usar um glifo monocromático (`↯`) para evitar aparência de emoji.
- Selo **PROTAGONISTA** foi movido para a mesma linha do título, aproximando o padrão do card **Simulado**.
- Seletor de 5/10/15 minutos recebeu estado selecionado mais discreto e coerente com a cor da Sessão rápida.
- Rodapé **Ações rápidas** passou a usar uma superfície própria, semelhante ao rodapé **Modo manual** de Estudo por questões.
- Botões do rodapé ficaram mais compactos e menos pesados.
- Data e métricas superiores foram refinadas para ficarem mais discretas.
- Ajustes equivalentes foram aplicados aos temas Claro, Escuro e Futurista.

## Validação

- `python -m py_compile main.py tema.py foco.py banco.py checkpoint.py testes_smoke.py versao.py`: OK
- `QT_QPA_PLATFORM=offscreen python testes_smoke.py`: `VighnaStudy 0.23.6: testes smoke OK`

## Arquivos principais alterados

- `main.py`
- `tema.py`
- `versao.py`
