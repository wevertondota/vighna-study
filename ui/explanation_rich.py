"""Persistência compatível para explicações formatadas do VighnaStudy.

O campo questoes.explicacao permanece TEXT, sem migração de schema.
Conteúdo legado permanece texto simples. Apenas texto formatado pelo editor
interno usa a marca explícita, evitando interpretar HTML colado/importado
como código de apresentação.
"""
from html.parser import HTMLParser

MARCADOR_EXPLICACAO_RICA = "<!--VIGHNA_EXPLICACAO_RICA_V1-->"


def explicacao_eh_rica(valor):
    return str(valor or "").startswith(MARCADOR_EXPLICACAO_RICA)


def explicacao_html(valor):
    """Retorna HTML para Qt apenas quando a marca interna está presente."""
    texto = str(valor or "")
    return texto[len(MARCADOR_EXPLICACAO_RICA):] if explicacao_eh_rica(texto) else None


def explicacao_serializada(editor, *, formatada=False):
    """Grava texto simples, ou HTML Qt com marcador, usando mesmo campo."""
    if not editor.toPlainText().strip():
        return ""
    if formatada:
        return MARCADOR_EXPLICACAO_RICA + editor.toHtml()
    return editor.toPlainText().strip()


class _TextoExplicacao(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes = []
        self.ignorar = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in ("head", "style", "script"):
            self.ignorar += 1
            return
        if self.ignorar:
            return
        if tag == "br":
            self.partes.append("\n")
        elif tag == "li":
            self.partes.append("\n• ")
        elif tag in ("p", "div", "tr") and self.partes:
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag.lower() in ("head", "style", "script") and self.ignorar:
            self.ignorar -= 1
        elif not self.ignorar and tag.lower() in ("p", "div", "li", "tr"):
            self.partes.append("\n")

    def handle_data(self, data):
        if not self.ignorar:
            self.partes.append(data)


def explicacao_texto_simples(valor):
    """Para exportações e resumos que são propositalmente só texto."""
    conteudo = explicacao_html(valor)
    if conteudo is None:
        return str(valor or "")
    parser = _TextoExplicacao()
    parser.feed(conteudo)
    linhas = [linha.rstrip() for linha in "".join(parser.partes).splitlines()]
    return "\n".join(linhas).strip()
