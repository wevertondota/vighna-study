"""Componentes leves de ordenação para Relatórios.

Não consulta nem altera dados acadêmicos.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class ItemOrdenavelRelatorio(QTableWidgetItem):
    """Usa uma chave de ordenação por tipo em vez do texto formatado."""
    SORT_ROLE = Qt.UserRole + 15

    def __lt__(self, other):
        atual = self.data(self.SORT_ROLE)
        outro = other.data(self.SORT_ROLE) if isinstance(other, QTableWidgetItem) else None
        if atual is not None and outro is not None:
            try:
                return atual < outro
            except TypeError:
                pass
        return super().__lt__(other)
