# VighnaStudy 0.29.20 — Substituição de questões de Direito Penal por versões Âncora de Memória

**Versão:** 0.29.20  
**Build:** `penal-ancora-memoria-titulos-iv-viii`  
**Schema:** 22 (sem migração)  
**Base:** checkpoint completo de 25/09/2026 13:13:50.

## Objetivo
Substituir, no banco do VighnaStudy, as questões ativas dos Títulos IV a VIII da Parte Geral de Direito Penal pelas cinco versões reformuladas em **Âncora de Memória + Distratores Plausíveis** fornecidas pelo usuário.

## Tópicos atualizados
- TÍTULO IV – DO CONCURSO DE PESSOAS: **6 questões**.
- TÍTULO V – DAS PENAS: **179 questões**.
- TÍTULO VI – DAS MEDIDAS DE SEGURANÇA: **17 questões**.
- TÍTULO VII – DA AÇÃO PENAL: **22 questões**.
- TÍTULO VIII – DA EXTINÇÃO DA PUNIBILIDADE: **50 questões**.
- Total substituído: **274 questões**.

## Estratégia de preservação
A substituição foi feita **em lugar**, mantendo os IDs das 274 questões e os IDs das 1.370 alternativas existentes. Isso evita criar questões novas ou deslocar vínculos internos.

Foram alterados apenas:
- enunciado;
- explicação;
- texto das alternativas;
- marcação da alternativa correta;
- ordem A–E;
- data de atualização da questão.

Foram preservados:
- `questoes.id`;
- `alternativas_questoes.id`;
- tópico e capítulo;
- banca, ano, fonte e dificuldade já cadastrados;
- tipo de questão;
- controle do tópico e demais dados do motor de estudo;
- tabelas históricas e sessões.

## Título V — capítulos preservados
As 179 questões continuaram distribuídas nos capítulos já existentes no banco:
- Capítulo I – Das Espécies de Pena: 27;
- Capítulo II – Da Cominação das Penas: 8;
- Capítulo III – Da Aplicação da Pena: 49;
- Capítulo IV – Da Suspensão Condicional da Pena: 22;
- Capítulo V – Do Livramento Condicional: 24;
- Capítulo VI – Dos Efeitos da Condenação: 37;
- Capítulo VII – Da Reabilitação: 12.

## Validação
- 274/274 questões do TXT conferidas contra o banco após a substituição.
- 5 alternativas A–E por questão.
- gabaritos conferidos contra os TXT.
- explicações conferidas contra os TXT.
- IDs das questões preservados.
- IDs das alternativas preservados.
- `PRAGMA integrity_check`: **ok**.
- `PRAGMA foreign_key_check`: **sem violações**.
- schema permanece em **22**.

## Observação sobre histórico
No snapshot recebido, os cinco tópicos não possuíam tentativas registradas vinculadas às questões substituídas. Ainda assim, a atualização foi executada mantendo os mesmos IDs, para preservar compatibilidade com dados históricos caso o banco continue sendo utilizado a partir deste checkpoint.
