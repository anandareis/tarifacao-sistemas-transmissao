import pandas
import numpy

class Barra:
    def __init__(self, numero, potencia_gerada, capacidade_instalada, potencia_consumida):
        self.numero = numero
        self.potencia_gerada = potencia_gerada
        self.capacidade_instalada = capacidade_instalada
        self.potencia_consumida = potencia_consumida
        self.posicao = numero - 1

    @property
    def potencia_ativa(self):
        return self.potencia_gerada - self.potencia_consumida


class Barras:
    def __init__(self, arquivo_barras, barra_referencia):
        self.elementos = []
        self._criar_barras(arquivo_barras)
        self.barra_referencia = self.elementos[barra_referencia-1]

    def __len__(self):
        return len(self.elementos)

    def __iter__(self):
        return iter(self.elementos)

    def _criar_barras(self, arquivo_barras):
        tabela_barras = pandas.read_csv(arquivo_barras, sep=";")
        for _, barra in tabela_barras.iterrows():
            self.elementos.append(Barra(
                numero=int(barra['Num']),
                potencia_gerada=barra['Potg_MW'],
                capacidade_instalada=barra['Capac_Inst_MW'],
                potencia_consumida=barra['Potc_MW']
            ))

    def obter_barra(self, numero):
        for barra in self.elementos:
            if barra.numero == numero:
                return barra
        return None

    # Vetor PG
    def vetor_potencia_gerada(self, usar_referencia=False):
        vetor = numpy.array([barra.potencia_gerada for barra in self.elementos])
        if usar_referencia:
            vetor[self.barra_referencia.posicao] = 0
            vetor[self.barra_referencia.posicao] = numpy.sum(self.vetor_potencia_consumida()) - numpy.sum(vetor)
        return vetor

    # Vetor PC
    def vetor_potencia_consumida(self):
        return numpy.array([barra.potencia_consumida for barra in self.elementos])

    # P
    def vetor_potencia_ativa(self):
        return numpy.array([barra.potencia_ativa for barra in self.elementos])

    # Capacidade de geração instalada
    def vetor_capacidade_instalada(self):
        return numpy.array([barra.capacidade_instalada for barra in self.elementos])
