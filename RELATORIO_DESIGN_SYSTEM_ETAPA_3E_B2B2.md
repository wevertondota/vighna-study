# VighnaStudy — Etapa 3E-B2b2

Implementada somente a migração do painel inferior, Pular e Encerrar. Base: `VighnaStudy_0.29.59_Etapa_3E_B2b1_COMPLETO(1).zip`, conferido por SHA-256 `8875147844c04c2cd6bede1c44bb3f1e6d483f15f9d94b6e2c58a8ee1b00dc41`. Especificação: caracterização da 3E-B2b2 e instruções anexadas. Nenhum avanço para 3E-B2c.

## Resultado e preservação

- Versão **0.29.59**, build **calendar-week-forecast-v1**, schema de aplicação **25**, intactos.
- Exatamente **15 tokens novos**: 14 COLOR + 1 GRADIENT, todos de componente, sob `session.*`. Contrato: 102 semânticos + 215 de componente = **317**.
- Todos os 302 tokens anteriores mantêm os mesmos valores nos três temas. Foram registrados somente os 31 valores físicos ausentes da paleta; não são tokens adicionais.
- Substituídos somente os literais das cinco regras finais por tema. Preservados seletores, propriedades, ordem, especificidade, estados, valores finais e cascata.
- `main.py`, `foco.py`, `checkpoint.py`, `versao.py` e `estudos.db` são byte a byte iguais à base. ObjectNames, propriedades dinâmicas, dimensões, fontes, layouts, margens, spacing, textos, tooltips, handlers e habilitação permanecem intactos.
- Dashboard/retorno e cronômetro da B2b1, flags, Confirmar/Próxima, conteúdo, alternativas, feedback, explicações, Modo Foco, resumo final e telas externas não foram migrados.

## Arquivos

Existentes alterados:

- `tema.py`
- `test_design_system_controles_compartilhados.py`
- `test_design_system_resolvedor_acoes_feedback.py`
- `test_design_system_resolvedor_estrutura_leitura.py`
- `test_design_system_resolvedor_nucleo.py`
- `ui/design/palette.py`
- `ui/design/themes.py`
- `ui/design/tokens.py`
- `test_design_system_resolvedor_navegacao_timer.py`

Adicionados:

- `test_design_system_resolvedor_painel_acoes.py`
- `RELATORIO_DESIGN_SYSTEM_ETAPA_3E_B2B2.md`

Código de produção: apenas `tema.py` e os três arquivos do contrato/paleta/temas. Nos cinco testes existentes, os ajustes se limitam às contagens de tokens/gradientes/literais e às expectativas de painel/Pular/Encerrar que deixaram de ser literais. Nenhum hash de referência foi alterado e nenhuma falha histórica foi mascarada. As sete expectativas de literais agora autorizados foram substituídas pela cobertura dos novos contratos e hashes integrais.

## Seletores migrados

| Elemento / estado | Seletor |
|---|---|
| Painel normal (P) | `QDialog#questionSolverDialog QFrame#questionSessionActionPanel` |
| Pular normal (S) | `QDialog#questionSolverDialog QPushButton#questionSessionSkipButton` |
| Pular hover | `QDialog#questionSolverDialog QPushButton#questionSessionSkipButton:hover` |
| Encerrar normal (E) | `QDialog#questionSolverDialog QPushButton#questionSessionEndButton` |
| Encerrar hover | `QDialog#questionSolverDialog QPushButton#questionSessionEndButton:hover` |

Claro/Escuro continuam consumindo `action_panel_surface` por `background-color` sólido. Futurista continua consumindo `action_panel_gradient` por `background`. Surface Futurista e gradientes constantes Claro/Escuro completam o contrato sem criar consumidor novo.

Não há `color` nova nos hovers Claro/Escuro: continuam herdando o texto normal. Somente os hovers Futuristas consomem explicitamente `skip_hover_text` e `end_hover_text`. Não há uso de `text.on_action` para o Pular.

Não foram criados tokens ou seletores pressed/disabled/checked. Regras globais e grupos compartilhados de Encerrar permanecem intactos. Pular continua sendo desabilitado após confirmação pelo código Python original.

| Propriedade preservada | Claro / Escuro | Futurista |
|---|---|---|
| Painel border | 1px solid | 1px solid |
| Painel radius | 13px | 13px |
| Botões radius | 9px | 10px |
| Botões font-weight | 750 | 800 |
| Pular padding | 6px 12px | 6px 12px, herdado do legado Escuro |
| Encerrar padding | 6px 10px | 6px 10px, herdado do legado Escuro |
| Fonte / min-height QSS | Segoe UI 10pt / 30px | Herdados do Escuro |

Dimensões Python intactas: painel min-height 58, margens 12/10/12/10, spacing 9; Pular altura fixa 40 e largura mínima 110; Encerrar altura fixa 34. Encerrar permanece no cabeçalho.

## Tokens criados e valores

| Token | Tipo / função semântica | Claro | Escuro | Futurista | Consumidor |
|---|---|---|---|---|---|
| `session.action_panel_surface` | COLOR / superfície do painel de ações | `#FFFFFF` | `#182230` | `#171F2B` | P / background-color Claro/Escuro; contrato Futurista |
| `session.action_panel_border` | COLOR / borda do painel de ações | `#DDE4EC` | `#344154` | `#3A4656` | P / border |
| `session.skip_surface` | COLOR / Pular / superfície normal | `#F5F7FA` | `#202B39` | `#202833` | S normal |
| `session.skip_text` | COLOR / Pular / texto normal | `#4F5D6E` | `#C8D1DC` | `#CED6E0` | S normal |
| `session.skip_border` | COLOR / Pular / borda normal | `#CCD5DF` | `#445265` | `#505B69` | S normal |
| `session.skip_hover_surface` | COLOR / Pular / superfície hover | `#EDF1F5` | `#273444` | `#293341` | S :hover |
| `session.skip_hover_text` | COLOR / Pular / texto hover | `#4F5D6E` | `#C8D1DC` | `#FFFFFF` | S :hover; explícito somente no Futurista |
| `session.skip_hover_border` | COLOR / Pular / borda hover | `#AFBAC8` | `#607086` | `#707C8B` | S :hover |
| `session.end_surface` | COLOR / Encerrar / superfície normal | `#FFF7F8` | `#2B2027` | `#2A2026` | E normal |
| `session.end_text` | COLOR / Encerrar / texto normal | `#A54050` | `#FFB8C2` | `#FFBAC4` | E normal |
| `session.end_border` | COLOR / Encerrar / borda normal | `#E9BCC4` | `#724350` | `#70434F` | E normal |
| `session.end_hover_surface` | COLOR / Encerrar / superfície hover | `#FFF0F2` | `#38262D` | `#38262E` | E :hover |
| `session.end_hover_text` | COLOR / Encerrar / texto hover | `#A54050` | `#FFB8C2` | `#FFD5DB` | E :hover; explícito somente no Futurista |
| `session.end_hover_border` | COLOR / Encerrar / borda hover | `#DC929E` | `#985766` | `#9A5968` | E :hover |
| `session.action_panel_gradient` | GRADIENT / preenchimento horizontal do painel de ações | `#FFFFFF → #FFFFFF` | `#182230 → #182230` | `#171F2B → #151D28` | P / background somente Futurista |

O gradiente mantém direção **(0,0,1,0)**, stops **0 e 1**, cores opacas. Nomes e funções seguem o contrato autorizado; não houve aliases/reutilização por coincidência de cor nem tokens de texto para o painel.

## Testes e validações

| Verificação | Resultado |
|---|---|
| `py_compile` | **193 arquivos Python; zero erros**, incluindo fontes e backups existentes |
| Específicos B2b2 | **11 testes + 75 subtestes aprovados** |
| Todo Design System | **83 testes + 492 subtestes aprovados** |
| Smoke | `VighnaStudy 0.29.59: testes smoke OK` |
| Suíte completa B2b2 | `49 failed, 573 passed, 514 subtests passed in 345.75s` |
| Baseline B2b1 | **49 failed, 562 passed, 446 subtests passed** |
| Identificadores de falha | **As mesmas 49 falhas; zero novas e zero removidas** |
| SQLite integrity_check | `ok` |
| SQLite foreign_key_check | `[]`; nenhuma violação |
| Banco entregue | Byte a byte idêntico ao ZIP base |
| Qt offscreen | **60 comparações de imagens antes/depois idênticas** |
| Checkpoint completo | Criação e inspeção aprovadas; ZIP íntegro, snapshot SQLite presente |

A suíte completa foi executada com `QT_QPA_PLATFORM=offscreen python -m pytest -q --tb=no test_*.py` e repetida com o plugin terminal desativado. Um hook de pytest registrou diretamente em JSON cada resultado, subteste e o encerramento da sessão, sem depender da saída de texto. A rodada instrumentada confirmou 622 coletados e 622 concluídos, zero skips, 573 aprovados, 49 falhas e 514 subtestes aprovados. Nenhum teste foi omitido ou modificado pelo hook. O acréscimo de 11 aprovados corresponde ao novo módulo. Subtestes: 446 + 75 novos − 7 expectativas antigas de literais migrados = **514**.

Todos os testes, inclusive smoke e imports da aplicação, usaram cópias isoladas. Bytecode, imagens, QSS auxiliares, fixtures e checkpoints de validação ficam fora do projeto entregue.

### Qt: aparência e comportamento de estados

PySide6 6.11.2, estilo Fusion, Linux/Qt offscreen:

- **39 imagens**: painel e Pular/Encerrar nos três temas; botões em normal, hover, pressed, pressed+hover, disabled e disabled+hover. A amostra disabled de Encerrar apenas observa a classe, sem introduzir esse fluxo na aplicação.
- **18 imagens**: Dashboard/retorno, outros subtleButton, barra de foco e timer em contextos de sessão, Modo Foco e diálogo externo, normal/hover.
- **3 imagens**: janela real do Modo Foco com dados auxiliares substituídos por fixtures estáveis.
- **18 comparações adicionais entre estados** confirmaram pressed sem hover = normal, pressed com hover = hover e disabled = normal visualmente. A desabilitação funcional continua real.

A comparação de fonte de `tema.py`, retirando somente os 15 blocos autorizados, resultou em igualdade integral. O QSS normalizado inteiro também permaneceu idêntico. Assim, nenhuma regra externa, grupo harmonizado de Encerrar, regra global de QPushButton, subtleButton/sessionNavigation, primaryButton ou dangerButton mudou. Ordem, declarações, valores efetivos, especificidade e estados de P/S/E estão preservados.

### Banco

SHA-256 de `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`.

Tamanho: **52494336 bytes**. Integridade/foreign keys conferidas em leitura imutável. Bytes conferidos com o ZIP original e novamente na validação do ZIP entregue. Schema da aplicação **25**, sem migração.

### Checkpoint recursivo

`checkpoint.py` mantém exatamente os bytes da B2b1. Um checkpoint real completo foi criado com snapshot SQLite, inspecionado e validado. Inclui todos os **6 módulos de `ui/design/`** (`__init__.py`, `adapters.py`, `gradients.py`, `palette.py`, `themes.py`, `tokens.py`) e `ui/__init__.py`. Fixture `ui/future/nested/` confirmou inclusão recursiva de `.py`, `.ui`, `.qrc` e `.toml`. Não há tratamento específico apenas para ui/design; os filtros de recursos existentes continuam intactos.

## Cascata Futurista

Preservada a arquitetura `stylesheet_escuro() + render_qss("futurista", ...)`: o Escuro continua resolvido com valores Escuro primeiro, seguido pelos overrides Futuristas. O QSS Futurista começa exatamente pelo QSS Escuro completo. Não houve re-renderização da camada Escura com tokens Futuristas. Padding, fonte e min-height herdados permanecem conforme a caracterização.

## SHA-256 QSS normalizado

Normalização adotada pelos testes existentes: hexadecimais em maiúsculas, sequências de whitespace reduzidas a um espaço, trim, UTF-8. **Antes/depois idênticos nos três temas; diff normalizado vazio.**

| Tema | Antes | Depois |
|---|---|---|
| Claro | `ac3740e43bd0bd55188a6cc30b5f9016ab8b67a499375c9304fc3f9164b4bc75` | `ac3740e43bd0bd55188a6cc30b5f9016ab8b67a499375c9304fc3f9164b4bc75` |
| Escuro | `8a703af87ca00b2cf1c2e02a0df189450e6d88d96e9a8784bfc19040560f8a03` | `8a703af87ca00b2cf1c2e02a0df189450e6d88d96e9a8784bfc19040560f8a03` |
| Futurista | `c0d184829a6c718d777b90131470ba42a97a0fcc9e209c2b7ccc7697bd5177a1` | `c0d184829a6c718d777b90131470ba42a97a0fcc9e209c2b7ccc7697bd5177a1` |

## SHA-256 QSS bruto

| Tema | Antes | Depois |
|---|---|---|
| Claro | `15943fa2317191f0a52c9ed8e053c9b9aa84f6910b49f65b334dafcb405e41b8` | `15943fa2317191f0a52c9ed8e053c9b9aa84f6910b49f65b334dafcb405e41b8` |
| Escuro | `c8175271f189f92c61c2b809e1353d06e5d1bb05fd3af41c1a0a75bc16c62698` | `c8175271f189f92c61c2b809e1353d06e5d1bb05fd3af41c1a0a75bc16c62698` |
| Futurista | `25813cdfd735a70671a731659035660f05f909f5969cd27d3382076fd6e7a39e` | `58fe63f87b06a6857432a13d4190e049e253c449a16cfd73e37902fa2cdf75f3` |

Claro e Escuro também são idênticos nos bytes brutos. A única diferença bruta no Futurista é a serialização do gradiente pelo renderer existente:

```diff
-    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
-        stop:0 #171F2B, stop:1 #151D28);
+    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #171F2B, stop:1 #151D28);
```

Apenas quebra de linha/indentação. Direção, stops, cores, propriedade, seletor, posição e pintura Qt permanecem idênticos.

## Limitações

- Não foi feita validação manual no Windows nesta execução. A B2b1 validada manualmente é o estado informado pelo usuário; esta entrega foi validada em Linux/Qt offscreen.
- Executáveis Windows presentes na base foram preservados e **não recompilados**. Executar as fontes por Python ou reconstruir o executável no Windows.
- As 49 falhas históricas permanecem; nenhuma correção fora do escopo foi aplicada para alterar o baseline.
- Após a indisponibilidade anterior do ambiente, a base foi recuperada, a implementação reaplicada e todas as validações foram repetidas nesta execução. Não há validação obrigatória pendente.

## Execução no Windows (CMD)

Na pasta extraída, com ambiente virtual existente:

```bat
call .venv\Scripts\activate.bat
python -m unittest -v test_design_system_resolvedor_painel_acoes
python main.py
```

## Falhas históricas preservadas

- `test_alternativas_interacao_0_29_51.py::AlternativasInteracao051Tests::test_versao_build`
- `test_cache_persistente_startup_0_29_43.py::CachePersistenteStartupTests::test_versao_da_otimizacao`
- `test_central_selecao_resultado_0_29_27.py::TestCentralSelecaoResultado02927::test_versao_e_build`
- `test_cobertura_pulo_reincidente.py::TestCoberturaEPulo::test_primeiro_pulo_reagenda_para_o_fim`
- `test_correcao_real_0_29_54.py::CorrecaoReal054Tests::test_versao_build`
- `test_dashboard_futurista_neo_0_29_34.py::DashboardFuturistaNeoTests::test_paleta_neo_tem_hierarquia_semantica`
- `test_dashboard_futurista_neo_0_29_34.py::DashboardFuturistaNeoTests::test_versao`
- `test_dashboard_inteligencia.py::DashboardInteligenciaTests::test_recomendacao_centralizada_no_espaco_restante`
- `test_dashboard_palette_reference_0_29_35.py::DashboardPaletteReferenceTests::test_version_updated`
- `test_dashboard_planejamento_compacto_0_29_39.py::TestDashboardPlanejamentoCompacto::test_versao_atualizada`
- `test_dashboard_planejamento_fundo_0_29_38.py::TestDashboardPlanejamentoFundo::test_versao_atualizada`
- `test_dashboard_planejamento_meta_protagonista_0_29_29.py::TestDashboardPlanejamentoMetaProtagonista02929::test_estilos_do_hero_presentes_nos_tres_temas`
- `test_dashboard_planejamento_meta_protagonista_0_29_29.py::TestDashboardPlanejamentoMetaProtagonista02929::test_versao_build_schema`
- `test_dashboard_planejamento_protagonista_0_29_28.py::TestDashboardPlanejamentoProtagonista02928::test_semana_tem_tres_sinais_independentes`
- `test_dashboard_planejamento_protagonista_0_29_28.py::TestDashboardPlanejamentoProtagonista02928::test_versao_build_schema`
- `test_dashboard_planejamento_referencia_0_29_37.py::TestDashboardPlanejamentoReferencia::test_estilos_planejamento_verde`
- `test_dashboard_planejamento_referencia_0_29_37.py::TestDashboardPlanejamentoReferencia::test_versao_atualizada`
- `test_eliminated_option_emphasis_0_29_53.py::EliminatedOptionEmphasis053Tests::test_versao_build`
- `test_foco_acessibilidade_0_29_14.py::FocoAcessibilidadeRuntimeTests::test_duracoes_e_pausa_desafios_permanecem_disponiveis`
- `test_focus_visual_0_29_47.py::FocusVisual047Tests::test_versao_e_build`
- `test_inline_explanation_editor_0_29_58.py::InlineExplanationEditor058Tests::test_versao_build_schema`
- `test_janelas_operacionais_0_29_45.py::JanelasOperacionais045Tests::test_versao_build`
- `test_keyboard_navigation_0_29_56.py::KeyboardNavigation056Tests::test_versao_build`
- `test_keyboard_navigation_0_29_57.py::KeyboardNavigationEnterNextTests::test_versao`
- `test_microtemas_crimes_pessoa_0_29_42.py::MicrotemasCrimesPessoaTests::test_backfill_liga_evidencia_a_versao_historica_quando_snapshot_mudou`
- `test_microtemas_crimes_pessoa_0_29_42.py::MicrotemasCrimesPessoaTests::test_catalogo_cobre_todas_as_alternativas_e_preserva_ciclo`
- `test_navegacao_estatisticas_fast_path_0_29_40.py::TestNavegacaoEstatisticasFastPath::test_versao`
- `test_resolvedor_moderno_0_29_46.py::ResolvedorModerno046Tests::test_versao_e_build`
- `test_resolver_transicao_0_29_15.py::TestTransicaoResolverSemFlicker::test_schema_permanece_compativel`
- `test_rotacao_visual_layout_0_29_18.py::RotacaoVisualLayoutSourceTests::test_grade_reserva_altura_para_as_seis_alternativas`
- `test_rotacao_visual_layout_0_29_18.py::RotacaoVisualLayoutSourceTests::test_layout_da_forma_original_ganha_espaco_horizontal`
- `test_rotacao_visual_layout_0_29_18.py::RotacaoVisualLayoutSourceTests::test_tres_temas_preservam_altura_da_opcao_de_rotacao`
- `test_rotacao_visual_layout_0_29_18.py::RotacaoVisualLayoutSourceTests::test_versao_foi_avancada_sem_migracao_de_schema`
- `test_rotacao_visual_layout_0_29_19.py::RotacaoVisualLayoutScrollSourceTests::test_versao_avancada_sem_migracao`
- `test_sincronizacao_topicos_pos_bateria_0_29_41.py::TestSincronizacaoTopicosPosBateria::test_resolvedor_invalida_cache_apos_sessao`
- `test_sincronizacao_topicos_pos_bateria_0_29_41.py::TestSincronizacaoTopicosPosBateria::test_versao`
- `test_startup_precarregamento_completo_0_29_30.py::StartupPrecarregamentoCompletoTests::test_versao_e_schema`
- `test_startup_splash_alinhamento_0_29_33.py::StartupSplashAlinhamentoTests::test_versao_schema_e_build`
- `test_startup_splash_harmonia_0_29_32.py::StartupSplashHarmoniaTests::test_eixo_do_card_coincide_com_texto_do_cabecalho`
- `test_startup_splash_harmonia_0_29_32.py::StartupSplashHarmoniaTests::test_fallback_repete_a_nova_composicao`
- `test_startup_splash_harmonia_0_29_32.py::StartupSplashHarmoniaTests::test_rodape_pertence_ao_mesmo_eixo_do_card`
- `test_startup_splash_harmonia_0_29_32.py::StartupSplashHarmoniaTests::test_splash_externo_ficou_mais_compacto`
- `test_startup_splash_harmonia_0_29_32.py::StartupSplashHarmoniaTests::test_versao_schema_e_build`
- `test_startup_splash_vivo_0_29_31.py::StartupSplashVivoTests::test_versao_e_schema`
- `test_tarefas_assincronas_0_29_44.py::TarefasAssincronas044Tests::test_versao_build`
- `test_topic_details_redesign_0_29_48.py::TopicDetailsRedesign048Tests::test_versao`
- `test_transient_window_embedded_0_29_52.py::EmbeddedTaskIndicator052Tests::test_versao_build`
- `test_transparent_text_backgrounds_0_29_49.py::TransparentTextBackgrounds049Tests::test_versao_e_schema`
- `test_viewer_alternatives_0_29_55.py::ViewerAlternatives055Tests::test_versao`

Nenhuma falha nova por identificador. Nenhuma alteração fora do escopo autorizado. Nenhum avanço para 3E-B2c.
