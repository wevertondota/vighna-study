# VighnaStudy — Central de Desenvolvimento e Homologação V2-A

**Esta entrega altera somente o painel de homologação, não o VighnaStudy instalado.**

## Como utilizar

1. Extraia o ZIP completo numa pasta nova do Windows (não reutilize nem sobrescreva a pasta V1).
2. Execute `ABRIR_PAINEL_HOMOLOGACAO.cmd` com dois cliques, sem privilégios de administrador.
3. Em **Visão geral**, consulte o último estado registrado dos trabalhos.
4. Em **Planejamento M1–M9**, selecione cada macrolote para consultar os próximos passos.
5. Em **Configurações**, selecione ou confirme o Python que contém PySide6 6.11.2 (o painel poderá sugerir o caminho conhecido).
6. Em **Executar testes**, use os mesmos controles da versão anterior: *Executar testes Qt + SQLite* ou *Testes + compilar EXE*.
7. Em **Resultados**, consulte o ZIP mais recente ou selecione um ZIP existente. Envie manualmente os resultados aqui para auditoria.

### O que mudou na V2-A

- Menu lateral: Visão geral, Planejamento, Executar testes, Resultados e Configurações.
- Resumo de M1, M2 e M3, com situação e pendências claramente diferenciadas.
- Quadro M1–M9 com detalhes de escopo e próxima ação de cada frente.
- Área de testes preservada, com os mesmos comandos e o mesmo motor da V1.
- Visualização do último resultado; **o histórico persistente completo virá na V2-B**.
- Fonte do acompanhamento: `estado_planejamento_v2a.json`, carregado localmente e validado.

### O que a V2-A **não** faz

- Não acompanha em tempo real o que está sendo desenvolvido nesta conversa.
- Não se conecta a contas, APIs ou servidores.
- Não importa automaticamente arquivos ou códigos do ChatGPT.
- Não executa nenhuma modificação no banco pessoal ou no programa instalado.
- Não autoriza a instalação do M2 RC2 ou do M3 experimental.
- Não envia ZIPs para esta conversa; o usuário anexa manualmente.

A importação verificada de novos checkpoints e a exportação organizada de evidências fazem parte de uma proposta posterior **V2-C**, não desta entrega.

### Situação documentada

- **M1:** baseline R1D preservado, referência histórica.
- **M2:** RC2 em homologação; Qt/SQLite aprovados em laboratório Windows; build com `.spec` original R1D pendente.
- **M3:** R35 experimental, sem integração nem instalação.
- **M4–M9:** macrolotes planejados, sem implementação assumida.

O estado exibido tem data explícita e pode ficar desatualizado se novas etapas forem desenvolvidas em outra conversa. Ele é um checkpoint informativo, não uma fonte de autorização.

### Recuperação

Mantenha uma cópia do ZIP antigo e salve o novo ZIP completo. Se a V2-A tiver algum problema no Windows, simplesmente feche-a e use novamente a versão V1 do painel em sua pasta anterior. **Não há instalação nem migração necessária.**
