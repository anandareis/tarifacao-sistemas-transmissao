import numpy
from modulos.modelos.barras import Barras
from modulos.utils import dividir as d

class Zona:
    def __init__(self):
        self.numero = 0
        self.barras = Barras()
        self.cor = ''
        self.posicao = 0
        self.tipo = ''

    def configurar(self, numero, cor):
        self.numero = numero
        self.cor = cor
        self.posicao = numero - 1

    def definir_tipo(self):
        tipos = self.barras.vetor_tipos()
        if 'G|C' in tipos or ('G' in tipos and 'C' in tipos):
            self.tipo = 'G|C'
        else:
            self.tipo = tipos[0]

    def encargo_total(self, natureza):
        return numpy.sum([barra.custos.obter_encargo(natureza, 'total_zonal') for barra in self.barras])

    def tarifa_total(self, natureza):
        for barra in self.barras:
            if barra.custos.obter_tarifa(natureza, 'total_zonal') != 0:
                return barra.custos.obter_tarifa(natureza, 'total_zonal')
        return 0

    def obter_valor_referencia(self, natureza):
        return numpy.sum(self.barras.vetor_capacidade_instalada()) if natureza == 'geracao' else numpy.sum(self.barras.vetor_potencia_consumida())

    def definir_custos_finais(self, encargo_final, natureza):
        referencia = self.obter_valor_referencia(natureza)
        tarifa_final = d(encargo_final, referencia)
        for barra in self.barras:
            barra.custos.atualizar_tarifa(tarifa_final, natureza, 'final_zonal')
