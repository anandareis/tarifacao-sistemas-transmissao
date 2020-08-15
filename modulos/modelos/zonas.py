from modulos.modelos.barras import Barras

class Zona:
    def __init__(self, numero, cor):
        self.numero = numero
        self.barras = Barras()
        self.tarifas  = {}
        self.encargos = {}
        self.cor = cor
