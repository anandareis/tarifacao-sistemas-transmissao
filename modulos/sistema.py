import numpy
from modulos.modelos.barras import Barras
from modulos.modelos.circuitos import Circuitos

class Sistema:
    def __init__(self, arquivo_barras, arquivo_circuitos, numero_barra_referencia):
        self.barras = Barras.criar_do_arquivo(arquivo_barras)
        self.barras.definir_referencia(numero_barra_referencia)
        self.circuitos = Circuitos.criar_do_arquivo(arquivo_circuitos)
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

    # Matriz X
    def construir_matriz_x(self):
        # Definir tamanho da matriz
        tamanho = len(self.barras)

        # Criar a matriz completa
        b_linha = numpy.zeros((tamanho, tamanho))
        for circuito in self.circuitos:
            b_linha[circuito.origem.posicao, circuito.destino.posicao] = -circuito.susceptancia
            b_linha[circuito.destino.posicao, circuito.origem.posicao] = -circuito.susceptancia
        for i in range(0, len(b_linha)):
            b_linha[i,i] = -numpy.sum(b_linha[i])

        # Remover linha e coluna da barra de referência
        b_linha = numpy.delete(b_linha, self.barras.barra_referencia.posicao, axis=0)
        b_linha = numpy.delete(b_linha, self.barras.barra_referencia.posicao, axis=1)

        # Inverter a matriz
        matriz_x = numpy.linalg.inv(b_linha)

        # Preencher os valores de linha e coluna da referência com zerro
        matriz_x = numpy.insert(matriz_x, self.barras.barra_referencia.posicao, 0, axis=0)
        matriz_x = numpy.insert(matriz_x, self.barras.barra_referencia.posicao, 0, axis=1)
        return matriz_x

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
