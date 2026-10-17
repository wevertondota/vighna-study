# -*- coding: utf-8 -*-
"""Smoke gráfico com Xvfb: inspeção das páginas, sem homologação Qt Windows."""
import tkinter as tk
from pathlib import Path
from unittest.mock import patch
import painel_homologacao as m

app=m.Painel()
app.deiconify()
app.update_idletasks()
assert len(app.pages)==8, app.pages
for key in ('geral','planejamento','gates','testes','historico','sincronizar','atualizacoes','configuracoes'):
    app._show_page(key)
    app.update()
    assert app.pages[key].winfo_ismapped(),key
assert len(app.gates_tree.get_children())==7
assert hasattr(app, 'g5a_btn')
assert hasattr(app, 'g5b_btn')
assert hasattr(app, 'g5c_btn')
assert hasattr(app, 'update_version')
assert hasattr(app, 'prepare_qt_btn')
assert hasattr(app, 'qt_environment_status')
assert app.gates_report['instalacao_autorizada'] is False
assert app.plano is not None
assert len(app.roadmap_tree.get_children())==9
app._show_page('gates')
app.deiconify()
app.geometry('1150x745+0+0')
app.update()
app.after(300,app.quit)
app.mainloop()
# Screenshot optional if display environment provides one; do not promise Windows fidelity.
print('GUI_V317_SMOKE_PASS: 8 telas, 7 gates, 9 macrolotes, sem autorização de instalação')
app.destroy()
