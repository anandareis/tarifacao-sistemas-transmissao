import pandas
import numpy
import sys

from modulos.modelos.custos import Custos

class Barra:
    def __init__(self, numero, potencia_gerada, capacidade_instalada, potencia_consumida, coordenada_X, coordenada_Y):
        self.numero = numero
        self.potencia_gerada = potencia_gerada
        self.capacidade_instalada = capacidade_instalada
        self.potencia_consumida = potencia_consumida
        self.posicao = numero - 1
        self.zona = None
        self.custos = Custos(self)
        self.coordenadas = {
            'X': coordenada_X,
            'Y': coordenada_Y
        }
        self.encargos = {
            'geracao': {
                'CTU': 0,
                'CTN': 0,
                'nodal_corrigido': 0
            },
            'carga': {
                'CTU': 0,
                'CTN': 0,
                'nodal_corrigido': 0
            }
        }

    @property
    def potencia_ativa(self):
        return self.potencia_gerada - self.potencia_consumida


class Barras:
    def __init__(self):
        self._elementos = []
        self.barra_referencia = None

    def __len__(self):
        return len(self._elementos)

    def __iter__(self):
        return iter(self._elementos)

    def __str__(self):
        return ", ".join([str(barra.numero) for barra in self._elementos])

    @classmethod
    def criar_do_arquivo(cls, arquivo_barras):
        barras = Barras()
        tabela_barras = pandas.read_csv(arquivo_barras, sep=";")
        for _, barra in tabela_barras.iterrows():
            barras.adicionar_barra(Barra(
                numero=int(barra['Num']),
                potencia_gerada=barra['Potg_MW'],
                capacidade_instalada=barra['Capac_Inst_MW'],
                potencia_consumida=barra['Potc_MW'],
                coordenada_X=barra['coord_X'],
                coordenada_Y=barra['coord_Y']
            ))
        return barras

    def adicionar_barra(self, barra):
        self._elementos.append(barra)

    def obter_barra(self, numero):
        if numero == 0:
            return self._elementos[0]
        for barra in self._elementos:
            if barra.numero == numero:
                return barra
        return None

    def definir_referencia(self, numero_barra_referencia):
        self.barra_referencia = self.obter_barra(numero_barra_referencia)
        self._definir_geracao_referencia()

    def _definir_geracao_referencia(self, ):
        self.barra_referencia.potencia_gerada = 0
        geracao_referencia = numpy.sum(self.vetor_potencia_consumida()) - numpy.sum(self.vetor_potencia_gerada())
        if geracao_referencia < 0:
            print('ERRO: A barra de referência definida não pode ser usada para este sistema.')
            print('O valor obtido para a geração de referência foi negativo.')
            print('Defina uma barra de referência com maior valor de potência gerada.')
            sys.exit(4)
        if geracao_referencia > self.barra_referencia.capacidade_instalada:
            print('ERRO: A barra de referência definida não pode ser usada para este sistema.')
            print('O valor obtido para a geração de referência excede a capacidade instalada.')
            print('Defina uma barra de referência com maior capacidade instalada.')
            sys.exit(4)
        self.barra_referencia.potencia_gerada = geracao_referencia

    # Vetor PG
    def vetor_potencia_gerada(self):
        return numpy.array([barra.potencia_gerada for barra in self._elementos])

    # Vetor PC
    def vetor_potencia_consumida(self):
        return numpy.array([barra.potencia_consumida for barra in self._elementos])

    # P
    def vetor_potencia_ativa(self):
        return numpy.array([barra.potencia_ativa for barra in self._elementos])

    # Capacidade de geração instalada
    def vetor_capacidade_instalada(self):
        return numpy.array([barra.capacidade_instalada for barra in self._elementos])

    def vetor_encargos(self, natureza, tipo):
        return numpy.array([barra.custos.obter_encargo(natureza, tipo) for barra in self._elementos])

    def vetor_tarifas(self, natureza, tipo):
        return numpy.array([barra.custos.obter_tarifa(natureza, tipo) for barra in self._elementos])
