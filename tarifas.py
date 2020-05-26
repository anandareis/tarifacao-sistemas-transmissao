import numpy

from barras import Barras
from circuitos import Circuitos

class Sistema:
    def __init__(self, arquivo_barras, arquivo_circuitos, barra_referencia, prop_g):
        self.barras = Barras(arquivo_barras, barra_referencia)
        self.circuitos = Circuitos(arquivo_circuitos)
        for circuito in self.circuitos:
            circuito.origem = self.barras.obter_barra(circuito.origem)
            circuito.destino = self.barras.obter_barra(circuito.destino)

        self.ro = (100-prop_g) / prop_g

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

    # Matriz de tarifas iniciais sem ajuste
    def tarifa_inicial(self):
        CT = []
        DT = []
        for circuito in self.circuitos:
             CT.append(circuito.custo_anual)
             DT.append(1 / circuito.capacidade)
        CT = numpy.array(CT)
        DT = numpy.diag(DT)
        return CT.dot(DT).dot(self.construir_matriz_beta())

    #  Vetor F
    def vetor_fluxo_potencia(self):
        return self.construir_matriz_beta().dot(self.barras.vetor_potencia_ativa().T)

    # Ajuste das tarifas iniciais
    def ajuste_m(self):
        return - self.tarifa_inicial() .dot((self.ro*self.barras.vetor_potencia_gerada(True) + self.barras.vetor_potencia_consumida()).T) / (self.ro * (numpy.sum(self.barras.vetor_potencia_gerada(True)))+numpy.sum(self.barras.vetor_potencia_consumida()))

    # TARCTU
    def tar_ctu(self):
        return self.tarifa_inicial() + numpy.full_like(self.tarifa_inicial(), self.ajuste_m())

    # CTU
    def calcular_CTU(self):
        return self.tar_ctu().dot((self.barras.vetor_potencia_gerada(True) - self.barras.vetor_potencia_consumida()).T)

    # CTU PG
    def calcular_CTUPG(self):
        return self.tar_ctu().dot(self.barras.vetor_potencia_gerada(True).T)

    # CTU PC
    def calcular_CTUPC(self):
        return self.tar_ctu().dot((-self.barras.vetor_potencia_consumida()).T)

    # CTU PG Barras
    def ctu_PG_barras(self):
        return self.tar_ctu() * self.barras.vetor_potencia_gerada(True)

    # CTU PC Barras
    def ctu_PC_barras(self):
        return self.tar_ctu() * (-self.barras.vetor_potencia_consumida())

    # CTT
    def calcular_CTT(self):
        ctt = 0
        for circuito in self.circuitos:
            ctt += circuito.custo_anual
        return ctt

    # CTN
    def calcular_CTN(self):
        return self.calcular_CTT() - self.calcular_CTU()

    # CTN dos geradores e cargas
    def ctn_g_c(self):
        kg = (self.calcular_CTN()/2)/numpy.sum(self.barras.vetor_capacidade_instalada())
        kc = (self.calcular_CTN()/2)/numpy.sum(self.barras.vetor_potencia_consumida())

        ctn_g = kg * self.barras.vetor_capacidade_instalada()
        ctn_c = kc * self.barras.vetor_potencia_consumida()

        return (ctn_g, ctn_c)

    def encargos_finais(self):
        ctn_g, ctn_c = self.ctn_g_c()
        total_g = self.ctu_PG_barras() + ctn_g
        total_c = self.ctu_PC_barras() + ctn_c

        return (total_g, total_c)

    def tarifas_finais(self):
        final_g, final_c = self.encargos_finais()

        tar_g = numpy.divide(final_g, self.barras.vetor_capacidade_instalada(), out=numpy.zeros_like(final_g), where=self.barras.vetor_capacidade_instalada()!=0)
        tar_c = numpy.divide(final_c, self.barras.vetor_potencia_consumida(), out=numpy.zeros_like(final_c), where=self.barras.vetor_potencia_consumida()!=0)

        return (tar_g, tar_c)

#-------
cinco_barras = Sistema(
    arquivo_barras="5B-barras.csv",
    arquivo_circuitos="5B-circuitos.csv",
    barra_referencia=1,
    prop_g=50
)

print(cinco_barras.tarifas_finais())
