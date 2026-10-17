# VighnaStudy — Painel de Homologação V2-B

**NÃO INSTALAR NO VIGHNASTUDY PRINCIPAL.** O painel é ferramenta independente.

## Substituir a V2-A com segurança

1. Extraia este ZIP em **uma pasta nova**; não misture com os arquivos da V2-A.
2. Execute `ABRIR_PAINEL_HOMOLOGACAO.cmd` normalmente, sem privilégios administrativos.
3. Abra **Configurações** e confirme o caminho de `python.exe` que possui PySide6 6.11.2.
4. Em **Histórico de testes**, use **Importar ZIPs anteriores...** para selecionar os arquivos
   `RESULTADOS_HOMOLOGACAO_WINDOWS_*.zip` das execuções anteriores.
5. Os novos ZIPs gerados pelo painel passam a ser registrados **automaticamente**.
6. Teste a interface V2-B e só depois considere apagar a pasta da V2-A.

## Uso do Histórico

- Filtre por **Qt, SQLite / Atualização, Segurança, PyInstaller, Integridade** e por situação.
- Selecione uma execução para ver as etapas individuais. Use **Ctrl + clique** para selecionar
  duas execuções e escolher **Comparar duas execuções**.
- **Importar ZIPs anteriores** valida CRC e hashes internos, conserva uma cópia e rejeita duplicados por SHA-256.
- **Exportar histórico ZIP** cria um backup do índice e das evidências guardadas.
- O histórico permanece entre reinícios e entre atualizações do painel.

## Onde fica o histórico?

O painel mantém arquivos separados da instalação principal em:
`%LOCALAPPDATA%\VighnaStudy_Homologador_V2B\`

Há um índice SQLite exclusivo do painel e cópias dos ZIPs selecionados. **Não contém o banco de
questões do VighnaStudy**, mas os relatórios originais podem incluir capturas ou caminhos do Windows.
Guarde os backups exportados em local privado. O envio ao ChatGPT é sempre manual.

## Restrições

- M2 permanece candidato RC2; homologação e instalação **não autorizadas automaticamente**.
- M3 permanece experimental R35, sem integração.
- V2-C (futuro): importação verificada do planejamento do desenvolvimento.
- Esta entrega passou testes Python e renderização gráfica em Linux/Xvfb; a V2-B precisa
  de validação visual final no seu Windows.

O motor de testes e seus insumos continuam idênticos aos da V2-A.
