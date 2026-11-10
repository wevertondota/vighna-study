"""VighnaStudy H35 R2: adaptação compatível da nova Home à base M35 R1.

Conserva os nomes de API exigidos por main.py sem substituir seu conteúdo.
A barra lateral, os dados do perfil, o banco e os controladores permanecem no main.py.
"""

from ui.portal_inicio_maduro import criar_portal_inicio, aplicar_estilo_portal


def atualizar_perfil_mini_edital(pagina, concurso_nome):
    """A nova Home não tem minicard de edital; o seletor real é compartilhado.

    O método é mantido apenas pela compatibilidade com o controlador existente.
    O próprio QComboBox do cabeçalho original acompanha as trocas de perfil.
    """
    if not getattr(pagina, "_home_maduro", False):
        return
    return None
