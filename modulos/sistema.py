import numpy
from modulos.barras import Barras
from modulos.circuitos import Circuitos

class Sistema:
    def __init__(self, arquivo_barras, arquivo_circuitos, barra_referencia):
        self.barras = Barras(arquivo_barras, barra_referencia)
        self.circuitos = Circuitos(arquivo_circuitos)
        for circuito in self.circuitos:
            circuito.origem = self.barras.obter_barra(circuito.origem)
            circuito.destino = self.barras.obter_barra(circuito.destino)
        self.calcular_fluxos_potencia()
        if any(self.circuitos.construir_vetor_fluxo_potencia() < 0):
            self.corrigir_fluxos_negativos()

    def calcular_fluxos_potencia(self):
        fluxos = self.construir_matriz_beta().dot(self.barras.vetor_potencia_ativa().T)
        for circuito in self.circuitos:
            circuito.fluxo_potencia = round(fluxos[circuito.posicao], 5)

    # Matriz D
    def construir_matriz_susceptancia(self):
        return numpy.diag(self.circuitos.construir_vetor_susceptancias())

    # Matriz C
    def construir_matriz_conectividade(self):
        matriz = numpy.zeros((len(self.circuitos), len(self.barras)))
        for circuito in self.circuitos:
            matriz[circuito.posicao, circuito.origem.posicao] = 1
            matriz[circuito.posicao, circuito.destino.posicao] = -1
        return matriz

    # Matriz B' completa - mudar o nome da função depois
    def construir_matriz_b_linha_completa(self):
        tamanho = len(self.barras)
        matriz = numpy.zeros((tamanho, tamanho))
        for circuito in self.circuitos:
            matriz[circuito.origem.posicao, circuito.destino.posicao] = -circuito.susceptancia
            matriz[circuito.destino.posicao, circuito.origem.posicao] = -circuito.susceptancia

        for i in range(0, len(matriz)):
            matriz[i,i] = -numpy.sum(matriz[i])

        return matriz

    # Matriz B' sem a barra de referência
    def construir_matriz_b_linha(self):
        matriz = self.construir_matriz_b_linha_completa()
        matriz = numpy.delete(matriz, self.barras.barra_referencia.posicao, axis=0)
        matriz = numpy.delete(matriz, self.barras.barra_referencia.posicao, axis=1)
        return matriz

    # Inversa da matriz B' sem a barra de referência
    def construir_inversa_b_linha(self):
        return numpy.linalg.inv(self.construir_matriz_b_linha())

    # Matriz X - inversa com 0 na linha e coluna da barra de referência
    def construir_matriz_x(self):
        matriz = self.construir_inversa_b_linha()
        matriz = numpy.insert(matriz, self.barras.barra_referencia.posicao, 0, axis=0)
        matriz = numpy.insert(matriz, self.barras.barra_referencia.posicao, 0, axis=1)
        return matriz

    # Matriz beta
    def construir_matriz_beta(self):
        D = self.construir_matriz_susceptancia()
        C = self.construir_matriz_conectividade()
        X = self.construir_matriz_x()
        return D.dot(C).dot(X)

    # Corrigir fluxos negativos
    def corrigir_fluxos_negativos(self):
        for circuito in self.circuitos:
            if circuito.fluxo_potencia < 0:
                self.circuitos.inverter_origem_destino(circuito.posicao)
        self.calcular_fluxos_potencia()
