# DESIGN SYSTEM — ETAPA 3E-B2c — FLAGS DA SESSÃO

**Implementação concluída somente para Dúvida e Análise posterior. Aparência e comportamento preservados. Nenhuma etapa posterior implementada.**

## Base e metadados

Base utilizada diretamente: `VighnaStudy_0.29.59_Etapa_3E_B2b2_COMPLETO(2).zip`, SHA-256 `a736734f9a85825049e4d77f7229e21942b7275aaf36836df5a9fb5fd7113133`. A caracterização B2c e as instruções anexadas orientaram esta implementação.

Versão **0.29.59**, build **calendar-week-forecast-v1**, schema **25**. `versao.py` e o banco preservados byte a byte.

## Arquivos alterados

Código do produto — quatro arquivos:

- `tema.py`: substituição das cores das flags por tokens; separação semântica autorizada da cor normal no grupo final Futurista.
- `ui/design/tokens.py`: registro dos 15 tokens COLOR autorizados.
- `ui/design/themes.py`: valores dos 15 tokens em cada tema.
- `ui/design/palette.py`: inclusão física das seis cores ausentes: #92400E, #AEB5FF, #B45309, #B7C1CD, #F0C47C e #FBBF24. Nenhuma cor existente alterada.

Contratos históricos ajustados — somente contagens, hashes decorrentes da separação autorizada e expectativa de três literais agora migrados:

- `test_design_system_calendario.py`
- `test_design_system_controles_compartilhados.py`
- `test_design_system_resolvedor_acoes_feedback.py`
- `test_design_system_resolvedor_estrutura_leitura.py`
- `test_design_system_resolvedor_navegacao_timer.py`
- `test_design_system_resolvedor_nucleo.py`
- `test_design_system_resolvedor_painel_acoes.py`

Arquivo novo de testes: `test_design_system_resolvedor_flags.py` — 25 testes, cobrindo os 27 requisitos específicos solicitados por verificações e subcasos.

Arquivo novo de documentação: este relatório. Total: **11 arquivos preexistentes alterados e 2 adicionados; nenhuma remoção**.

O contrato passa de 317 para **332 tokens**: 102 semânticos e 230 de componente. Valores, tipos, direções e stops dos **317 tokens anteriores permanecem integralmente iguais** nos três temas.

Os testes históricos continuam executados, sem mudar seus identificadores. O hash Futurista integral e o hash de regressão com navegação removida foram ajustados exclusivamente pela separação cromática autorizada. O teste novo `test_entire_qss_is_identical_after_reversing_only_authorized_split` reverte apenas essa separação e exige os três hashes integrais originais da B2b2. A atualização dos hashes históricos não aceita mudanças em áreas não relacionadas.

No contrato de estrutura/leitura, a quantidade residual de cores literais do bloco final Futurista passa de 16 para 13 e o marcador literal #B7C1CD das flags deixa de ser exigido. Isso corresponde precisamente às três declarações cromáticas migradas e não remove uma expectativa de componente fora do escopo. Nenhum teste foi desabilitado, marcado como skip/xfail ou alterado para ocultar falha preexistente.

## 15 tokens criados

Todos são **COLOR**, nível COMPONENT. Nenhum token adicional, estado adicional ou token geométrico.

| Token | Claro | Escuro | Futurista |
|---|---|---|---|
| `session.flag_indicator_surface` | #FFFFFF | #111827 | #111827 |
| `session.doubt_text` | #475569 | #CBD5E1 | #B7C1CD |
| `session.doubt_checked_text` | #1D4ED8 | #93C5FD | #AEB5FF |
| `session.doubt_indicator_border` | #64748B | #94A3B8 | #94A3B8 |
| `session.doubt_indicator_hover_border` | #2563EB | #60A5FA | #60A5FA |
| `session.doubt_indicator_checked_surface` | #2563EB | #3B82F6 | #3B82F6 |
| `session.doubt_indicator_checked_border` | #1D4ED8 | #93C5FD | #93C5FD |
| `session.doubt_indicator_disabled_surface` | #E2E8F0 | #1F2937 | #1F2937 |
| `session.doubt_indicator_disabled_border` | #94A3B8 | #475569 | #475569 |
| `session.analysis_text` | #64748B | #94A3B8 | #B7C1CD |
| `session.analysis_checked_text` | #92400E | #FBBF24 | #F0C47C |
| `session.analysis_indicator_border` | #94A3B8 | #64748B | #64748B |
| `session.analysis_indicator_hover_border` | #D97706 | #F59E0B | #F59E0B |
| `session.analysis_indicator_checked_surface` | #F59E0B | #D97706 | #D97706 |
| `session.analysis_indicator_checked_border` | #B45309 | #FBBF24 | #FBBF24 |

A superfície neutra compartilhada é consumida somente pelo ::indicator normal das duas flags nas camadas Claro/Escuro. As demais funções mantêm tokens próprios. Texto e borda checked não foram fundidos. Nenhum consumidor usa text.on_action por coincidência de cor.

## Regras migradas e propriedades preservadas

Os seletores legados mantêm os objectNames, a ausência de ancestral adicional e esta ordem:

| Dúvida — QCheckBox#questionSessionDoubt | Análise — QCheckBox#questionSessionAnalysisFlag |
|---|---|
| Base: texto | Base: texto |
| :checked: texto | :checked: texto/peso |
| ::indicator: superfície/borda | ::indicator: superfície/borda |
| ::indicator:hover: somente borda | ::indicator:hover: somente borda |
| ::indicator:checked: superfície/borda | ::indicator:checked: superfície/borda |
| ::indicator:disabled: superfície/borda | Nenhuma regra disabled criada |

Dúvida conserva corpo transparente, peso 700, spacing 9px, padding 4px 0; indicador 20×20px, borda 2px solid, radius 5px. Análise conserva corpo transparente, peso base 600, declaração checked 700, spacing 7px, padding 4px 8px; indicador 16×16px, borda 2px solid, radius 4px.

Hover continua antes de checked. Disabled da Dúvida permanece depois de checked, vencendo superfície/borda; texto checked continua vigente quando disabled. Análise disabled conserva aparência normal ou checked correspondente.

Não foram criados :checked:hover, :pressed, :focus, :focus-visible, :unchecked, :indeterminate, checked:disabled, hover:disabled ou texto disabled. Não houve ajuste Python do peso de fonte.

`main.py` não foi alterado: criação, hierarquia, layout, objectNames, propriedades dinâmicas, sinais, handlers, checked/enabled, textos e persistência intactos.

## Futurista: separação necessária e cascata

Foi preservado literalmente o mecanismo:

```python
return stylesheet_escuro() + render_qss("futurista", ...)
```

O prefixo Escuro é renderizado com valores Escuro antes dos overrides Futuristas e foi comparado byte a byte com stylesheet_escuro(). Os indicadores continuam herdados; nenhuma regra específica de indicador foi acrescentada à camada Futurista. Os genéricos #0D1D2D/#5A8BB1/#2C6FA0/#7FD5EF continuam perdendo para os IDs legados.

O grupo final das flags conserva background: transparent e font-size: 8.6pt. Somente color foi retirada desse grupo e colocada imediatamente depois em dois seletores adjacentes, consumindo session.doubt_text e session.analysis_text. O renderer existente não permite um token diferente para cada seletor dentro de uma única declaração agrupada.

Os dois :checked finais permanecem depois deles, consumindo session.doubt_checked_text e session.analysis_checked_text.

Cada novo seletor normal conserva especificidade **(2 IDs, 0 pseudoestados/atributos, 2 tipos)**, igual a cada membro normal do grupo original. Checked final conserva **(2,1,2)**. Indicadores legados conservam especificidade por ID; hover/checked empatam e a ordem preservada decide. A composição disabled e os pesos declarados de fontes foram conservados.

## Validações

| Verificação | Resultado |
|---|---|
| py_compile | **194 arquivos Python compilados, 0 erros**, bytecode fora do projeto |
| Testes B2c | **25 passed, 71 subtests passed**, 0 falhas |
| Todos os testes Design System | **108 passed, 562 subtests passed**, 0 falhas |
| Smoke | `VighnaStudy 0.29.59: testes smoke OK` |
| Suíte completa | **598 passed, 49 failed, 584 subtests passed**, 0 subtests falhos, 0 skips |
| Completude | **647/647 testes concluídos**, duração 358.47 s |
| Baseline B2b2 | 573 passed, 49 failed, 514 subtests passed |
| Falhas por identificador | **Mesmos 49 identificadores; 0 novas falhas, 0 falhas antigas removidas** |
| SQLite integrity_check | **ok** |
| SQLite foreign_key_check | **[] — nenhuma violação** |
| estudos.db | **Byte a byte igual ao ZIP B2b2** |
| Tokens anteriores | 317 contratos integrais iguais nos três temas |
| Qt offscreen — flags | **36/36 comparações idênticas** de pixels, fontes, sizeHint e indicador |
| Qt offscreen — regressão | **60/60 comparações idênticas**, mais **18/18 comparações entre estados** |
| Dashboard real — árvore de widgets | **3/3 capturas idênticas**, uma por tema |
| Checkpoint | ZIP criado/inspecionado íntegro; seis módulos ui/design incluídos |
| Checkpoint recursivo | ui/future/nested/widget.py, layout.ui, resources.qrc e config.toml incluídos |

A suíte completa acrescenta os 25 testes B2c aos 622 testes anteriores. Os subtests passam de 514 para 584: 71 novos, menos o único subcase histórico que exigia #B7C1CD literal no tema antes da migração.

Suíte, smoke, UI real e checkpoint foram executados em cópias isoladas. py_compile escreveu em pasta auxiliar. O projeto entregue não recebeu bancos de teste, caches novos, bytecode de validação, imagens ou fixtures de checkpoint.

### SQLite e preservação do banco

PRAGMAs executados por conexão SQLite somente leitura e immutable, sem migração ou escrita:

- Arquivo: `estudos.db`.
- Tamanho: **52494336 bytes**.
- SHA-256 antes/depois: `034940a33ea792957d8fafbf5c528db7cd895db69031696fbdd3f0a0ce5a41ef`.
- integrity_check: `ok`.
- foreign_key_check: nenhuma linha.

### Comparação visual

PySide6 6.11.2, Qt offscreen, estilo Fusion. As 36 comparações das flags cobrem exatamente:

- Dúvida normal, hover, checked, checked:hover, disabled unchecked, checked disabled;
- Análise normal, hover, checked, checked:hover, disabled unchecked, checked disabled;
- todos esses estados no Claro, Escuro e Futurista.

Foram usados textos reais de cada checked/unchecked, hierarquia diálogo → painel → flags e QSS completos antes/depois. Nenhum pixel, geometria de indicador, sizeHint ou fonte comparados mudou.

As 60 comparações de regressão cobrem painel inferior, Pular, Encerrar, navegação Dashboard, timer, outros subtleButton dentro/fora da sessão e no contexto de Foco, além da janela real JanelaModoFoco nos três temas. As 18 comparações adicionais confirmam estados antes existentes de Pular/Encerrar.

A árvore real do Dashboard também foi capturada nos três temas. Suas definições foram carregadas sem executar o bootstrap da aplicação; inicialização do banco, restauração de sessão e carregamento de botões de disciplinas foram isolados com mocks nesse teste de pintura. A janela real de Foco isolou consultas de histórico/resumo. Essa validação verifica pintura, não o funcionamento dessas consultas.

### QSS e preservação fora do escopo

No fonte de tema.py, a comparação mascarou somente os **22 blocos legados das flags** (11 por tema) e a transformação final autorizada. Todo o restante do arquivo permaneceu idêntico. Os genéricos, grupos globais e regras de Dashboard, timer, painel, Pular, Encerrar, Confirmar, Próxima, alternativas, enunciado, feedback, explicações, Foco e resumo não foram editados.

A comparação normalizada integral exige igualdade no Claro/Escuro e, no Futurista, igualdade de toda a sequência exceto a separação autorizada. Foi comprovada por substituição inversa e pelo diff completo abaixo.

## SHA-256 QSS normalizado

Normalização igual à base: hexadecimais de cor para maiúsculas, whitespace colapsado, strip, SHA-256 do UTF-8. Comentários e ordem permanecem na sequência normalizada.

| Tema | Antes B2b2 | Depois B2c |
|---|---|---|
| Claro | `ac3740e43bd0bd55188a6cc30b5f9016ab8b67a499375c9304fc3f9164b4bc75` | `ac3740e43bd0bd55188a6cc30b5f9016ab8b67a499375c9304fc3f9164b4bc75` |
| Escuro | `8a703af87ca00b2cf1c2e02a0df189450e6d88d96e9a8784bfc19040560f8a03` | `8a703af87ca00b2cf1c2e02a0df189450e6d88d96e9a8784bfc19040560f8a03` |
| Futurista | `c0d184829a6c718d777b90131470ba42a97a0fcc9e209c2b7ccc7697bd5177a1` | `bf0aff2b3219a4c003a44f9314cad2db1c5b5399231aee9b916adfeec04da4b4` |

Claro e Escuro permanecem normalizados **idênticos**. Futurista muda somente pela separação autorizada de color.

## SHA-256 QSS bruto

| Tema | Antes B2b2 | Depois B2c |
|---|---|---|
| Claro | `15943fa2317191f0a52c9ed8e053c9b9aa84f6910b49f65b334dafcb405e41b8` | `8daecca514671b1c17d15753d4cc6219052f467645c621b99cd00aa952bbc38c` |
| Escuro | `c8175271f189f92c61c2b809e1353d06e5d1bb05fd3af41c1a0a75bc16c62698` | `89386662b2c4d2228fb088d81e15b795338da436192d1ce6970a91c7061f0de2` |
| Futurista | `58fe63f87b06a6857432a13d4190e049e253c449a16cfd73e37902fa2cdf75f3` | `dc5fee91b49d7e91182e2a1da7be7646c4de001543e86a5f128302d58e3b1dc6` |

Diferenças brutas no Claro/Escuro: somente a capitalização de cores hexadecimais, porque ColorValue/renderer serializam valores canônicos maiúsculos. No Futurista, há a mesma capitalização no prefixo Escuro e a separação autorizada do grupo. Valores, geometria e pintura permanecem iguais.

## Diff normalizado completo — Futurista

A sequência normalizada foi separada somente depois de `} ` para permitir leitura por regra. Reunir novamente os segmentos reconstrói exatamente a linha normalizada original. Este é o diff completo dessa representação, com um único hunk; nenhum outro trecho mudou.

```diff
--- Futurista B2b2 normalizado
+++ Futurista B2c normalizado
@@ -2155,7 +2155,9 @@
 QDialog#questionSolverDialog QToolButton#questionSolverEliminateButton { color: #718094; border: none; background: transparent; }
 QDialog#questionSolverDialog QToolButton#questionSolverEliminateButton:hover { background-color: #222C39; color: #CAD4DF; border-radius: 6px; }
 QDialog#questionSolverDialog QFrame#questionSessionActionPanel { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #171F2B, stop:1 #151D28); border: 1px solid #3A4656; border-radius: 13px; }
-QDialog#questionSolverDialog QCheckBox#questionSessionDoubt, QDialog#questionSolverDialog QCheckBox#questionSessionAnalysisFlag { color: #B7C1CD; background: transparent; font-size: 8.6pt; }
+QDialog#questionSolverDialog QCheckBox#questionSessionDoubt, QDialog#questionSolverDialog QCheckBox#questionSessionAnalysisFlag { background: transparent; font-size: 8.6pt; }
+QDialog#questionSolverDialog QCheckBox#questionSessionDoubt { color: #B7C1CD; }
+QDialog#questionSolverDialog QCheckBox#questionSessionAnalysisFlag { color: #B7C1CD; }
 QDialog#questionSolverDialog QCheckBox#questionSessionDoubt:checked { color: #AEB5FF; }
 QDialog#questionSolverDialog QCheckBox#questionSessionAnalysisFlag:checked { color: #F0C47C; }
 QDialog#questionSolverDialog QPushButton#questionSessionSkipButton { background-color: #202833; color: #CED6E0; border: 1px solid #505B69; border-radius: 10px; font-weight: 800; }
```

## Limitações

- Não foi feita validação manual Windows nesta tarefa; a comparação visual Linux/Qt offscreen não a substitui.
- As 49 falhas históricas permanecem. Nenhum código fora do escopo foi ajustado para corrigi-las.
- Executáveis Windows presentes na base foram preservados e **não recompilados**. As alterações estão nas fontes. Para usar o executável atualizado, recompilar no Windows com o atualizar_exe.bat existente.
- O efeito específico de font-weight :checked de Análise no Windows não foi “corrigido”: declaração e comportamento Python preservados, com igualdade visual antes/depois na sonda.
- Nenhuma validação obrigatória pendente. Nenhuma nova falha por identificador.

## Execução no Windows — CMD

Na pasta extraída, usando o ambiente virtual existente:

```bat
cd /d C:\SistemaEstudos
.venv\Scripts\python.exe -m unittest -v test_design_system_resolvedor_flags
.venv\Scripts\python.exe main.py
```

Para atualizar o executável a partir das fontes, com o programa fechado:

```bat
cd /d C:\SistemaEstudos
call atualizar_exe.bat
```

## Identificadores das 49 falhas preservadas

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

**Confirmação final:** versão 0.29.59, build calendar-week-forecast-v1, schema 25, banco, main.py, foco.py e checkpoint.py preservados. Nenhuma alteração de comportamento Python, objectName, propriedade dinâmica ou componente fora do escopo. Migração restrita à Etapa 3E-B2c.
