"""Núcleo sem Qt do relógio de pausa da bateria.

O tempo restante deriva de um prazo absoluto de relógio de parede, e não
contando pulsos do timer Qt: isso permite detectar expiração após suspensão do PC.
"""
from datetime import datetime, timedelta
import math


class RelogioPausa:
    def __init__(self, minutos, agora=None):
        minutos = int(minutos)
        if not 1 <= minutos <= 240:
            raise ValueError("A pausa deve durar de 1 a 240 minutos.")
        self.prazo = (agora or datetime.now()) + timedelta(minutes=minutos)

    def segundos_restantes(self, agora=None):
        delta = (self.prazo - (agora or datetime.now())).total_seconds()
        return max(0, math.ceil(delta))

    def expirou(self, agora=None):
        return self.segundos_restantes(agora) == 0

    def adiar(self, minutos=5, agora=None):
        minutos = int(minutos)
        if not 1 <= minutos <= 240:
            raise ValueError("A prorrogação deve durar de 1 a 240 minutos.")
        self.prazo = (agora or datetime.now()) + timedelta(minutes=minutos)


def texto_contagem(segundos):
    segundos = max(0, int(segundos))
    minutos, segundos = divmod(segundos, 60)
    horas, minutos = divmod(minutos, 60)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}" if horas else f"{minutos:02d}:{segundos:02d}"
