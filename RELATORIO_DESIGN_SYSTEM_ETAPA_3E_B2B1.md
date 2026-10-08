# VighnaStudy — Etapa 3E-B2b1

Implementada somente navegação/retorno da sessão + cronômetro. Não houve avanço para 3E-B2b2.

## Resultado

- Versão **0.29.59**, build **calendar-week-forecast-v1**, schema de aplicação **25**, intactos.
- Criados exatamente os 9 tokens autorizados: `session.navigation_surface`, `session.navigation_text`, `session.navigation_border`, `session.navigation_hover_surface`, `session.navigation_hover_text`, `session.navigation_hover_border`, `session.timer_surface`, `session.timer_text`, `session.timer_border`. Todos os valores reproduzem os fornecidos.
- O Dashboard preserva `subtleButton` e recebe a propriedade `sessionNavigation=true`. As novas regras exigem simultaneamente `QDialog#questionSolverDialog` e essa propriedade; nenhum outro botão recebe a propriedade.
- Não foram criados estados pressed/disabled nem usado `text.on_action`. Dimensões, fontes, espaçamentos, eventos e demais controles preservados.
- O timer usa tokens nas três regras originais, sem mover seletores. O Futurista continua concatenando o QSS Escuro e seus overrides; o timer Futurista mantém as dimensões herdadas.
- `checkpoint.py` inclui `ui/` via a recursão existente, abrangendo qualquer subpasta futura e as extensões de projeto (inclusive `.ui`, `.qrc`, `.toml`). Mantidos os filtros existentes para caches, pastas ignoradas e tamanho máximo de recursos.

## Arquivos

Alterados:
- `checkpoint.py`
- `main.py`
- `tema.py`
- `test_design_system_calendario.py`
- `test_design_system_controles_compartilhados.py`
- `test_design_system_resolvedor_acoes_feedback.py`
- `test_design_system_resolvedor_estrutura_leitura.py`
- `test_design_system_resolvedor_nucleo.py`
- `ui/design/palette.py`
- `ui/design/themes.py`
- `ui/design/tokens.py`

Adicionados:
- `test_design_system_resolvedor_navegacao_timer.py`
- `RELATORIO_DESIGN_SYSTEM_ETAPA_3E_B2B1.md`

Os cinco testes antigos do Design System tiveram atualizados apenas os hashes de referência e, quando aplicável, as contagens do contrato: 102 tokens semânticos + 200 de componente = 302.

## Validações

- `py_compile`: 192 arquivos Python, incluindo fontes e backups históricos; zero erros. Também conferidos os arquivos finais alterados.
- Design System: **72 testes aprovados + 424 subtestes aprovados** (inclui os 5 testes da nova etapa).
- Smoke: `VighnaStudy 0.29.59: testes smoke OK`.
- Suíte completa atual: `49 failed, 562 passed, 446 subtests passed in 430.42s (0:07:10)`.
- Suíte completa do ZIP original: `49 failed, 557 passed, 446 subtests passed in 421.38s (0:07:01)`.
- Novas falhas por identificador em relação ao original: **0**.
- Banco original: `PRAGMA integrity_check` = `ok`; `PRAGMA foreign_key_check` = `[]`; nenhuma violação. O arquivo entregue conserva exatamente os bytes do banco anexado.
- SHA-256 de `estudos.db`: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`.
- Checkpoint real criado com snapshot do banco, inspecionado e validado: **todos os 7 módulos de ui/design incluídos**. Teste adicional com `ui/future/nested/` confirmou inclusão de `.py`, `.ui`, `.qrc` e `.toml`.
- AST de `main.py` igual ao original após remover a única atribuição da propriedade do Dashboard. Isso inclui os métodos de navegação e timer.
- Timer testado sem modo simulado, sem início, em tempo decorrido, contagem regressiva, expiração e sessão já finalizada. Parada e finalização por tempo esgotado preservadas.
- **21 comparações de imagens offscreen idênticas**: 18 amostras de controles em normal/hover e contextos de sessão/externos, além da janela real do Modo Foco nos três temas (dados auxiliares substituídos por fixtures estáveis).
- Removendo apenas as novas regras de navegação do QSS normalizado final, os três hashes voltam exatamente aos fornecidos. Isso comprova que nenhuma regra alheia foi alterada e que a ordem das demais regras permanece igual.

## SHA-256 do QSS normalizado

Os hashes fornecidos são do formato adotado pelos testes existentes: cores hexadecimais em maiúsculas, espaços normalizados e remoção de espaços nas extremidades. Não são hashes dos bytes brutos do QSS.

| Tema | Antes | Depois |
|---|---|---|
| Claro | `139709f8c57e00f16848668f9226703c7f8ff391dd9aea2bba8b2eae20ac2c5f` | `ac3740e43bd0bd55188a6cc30b5f9016ab8b67a499375c9304fc3f9164b4bc75` |
| Escuro | `ebbc21363d0035058301d060eb099fb2d33b992e8537c20f9bf1e77f8a2b4f3e` | `8a703af87ca00b2cf1c2e02a0df189450e6d88d96e9a8784bfc19040560f8a03` |
| Futurista | `0e588bb372946b4a6f61ad406c817fd155cac8c3c4286e9f93b7a09d06dc8622` | `c0d184829a6c718d777b90131470ba42a97a0fcc9e209c2b7ccc7697bd5177a1` |

As alterações correspondem à adição escopada das duas regras de navegação por tema. As diferenças do timer no QSS bruto são apenas maiúsculas/minúsculas das mesmas cores. Futurista também contém as novas regras herdadas do Escuro, antes dos próprios overrides.

## SHA-256 dos bytes brutos do QSS

| Tema | Antes | Depois |
|---|---|---|
| Claro | `96d08193aa5a529d4778b35d4bf666d653b77d9aecbb0bab1f4e28af3fb2d57b` | `15943fa2317191f0a52c9ed8e053c9b9aa84f6910b49f65b334dafcb405e41b8` |
| Escuro | `b0b15df6bdcd639b723706cff3da3f047db08491b25570dde4d85cd2f7b478e4` | `c8175271f189f92c61c2b809e1353d06e5d1bb05fd3af41c1a0a75bc16c62698` |
| Futurista | `4a375d8f0ce28231a1332e1946eb3ca99949e77b61a7e54a2ec7446ec0dbb377` | `25813cdfd735a70671a731659035660f05f909f5969cd27d3382076fd6e7a39e` |

## Limitações

- Execução e renderização automatizadas em Linux/Qt offscreen. Não foi executado teste manual no Windows.
- Os executáveis Windows já presentes no ZIP original foram preservados e não recompilados. Para executar as alterações, usar Python (`python main.py`) ou reconstruir o executável no Windows.
- A suíte histórica contém falhas anteriores, inclusive verificações de versões/builds antigos. Elas foram registradas sem mudar comportamentos fora do escopo para fazê-las passar.

### Falhas da suíte atual

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

### Novas falhas em relação ao original

Nenhuma.

## Execução no Windows (CMD)

Na pasta extraída do projeto, com o ambiente virtual existente:

```bat
call .venv\Scriptsctivate.bat
python -m unittest -v test_design_system_resolvedor_navegacao_timer
python main.py
```
