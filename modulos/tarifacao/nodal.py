import numpy
import matplotlib.pyplot as plt

from modulos.utils import distribuir_valores_negativos
class TarifasNodais:
    def __init__(self, sistema, proporcao_geracao):
        self.ro = (100-proporcao_geracao) / proporcao_geracao
        self.sistema = sistema
        self.corrigido = False
        self.calcular_tarifas_nodais()
        self.gerar_grafico_tarifas()

    # Realizar todos os cálculos para tarifação nodal
    def calcular_tarifas_nodais(self):
        self.definir_tarifas_ctu()
        self.definir_tarifas_ctn()
        encargos_totais_geracao = self.sistema.barras.vetor_encargos('geracao', 'total_nodal')
        encargos_totais_carga = self.sistema.barras.vetor_encargos('carga', 'total_nodal')
        self.corrigir_alocacao_negativa(encargos_totais_geracao, 'geracao')
        self.corrigir_alocacao_negativa(encargos_totais_carga, 'carga')

    # Matriz de tarifas iniciais sem ajuste
    def calcular_tarifa_inicial(self):
        CT = self.sistema.circuitos.construir_vetor_custos_anuais()
        DT = self.sistema.circuitos.construir_vetor_capacidades()
        DT = numpy.diag(1 / DT)
        return CT.dot(DT).dot(self.sistema.construir_matriz_beta())

    # Ajuste das tarifas iniciais
    def calcular_ajuste_m(self):
        vetor_pg = self.sistema.barras.vetor_potencia_gerada()
        vetor_pc = self.sistema.barras.vetor_potencia_consumida()
        return - self.calcular_tarifa_inicial() .dot((self.ro*vetor_pg + vetor_pc).T) / (self.ro * (numpy.sum(vetor_pg))+numpy.sum(vetor_pc))

    # Definir as tarifas do CTU nas barras
    def definir_tarifas_ctu(self):
        tar_ctu = self.calcular_tarifa_inicial() + numpy.full_like(self.calcular_tarifa_inicial(), self.calcular_ajuste_m())
        for barra in self.sistema.barras:
            barra.custos.atualizar_tarifa(tar_ctu[barra.posicao], 'geracao', 'locacional_nodal')
            barra.custos.atualizar_tarifa(tar_ctu[barra.posicao], 'carga', 'locacional_nodal')

    # Calcular o valor total do CTN
    def calcular_ctn(self):
        ctu_geracao = numpy.sum(self.sistema.barras.vetor_encargos('geracao', 'locacional_nodal'))
        ctu_carga = numpy.sum(self.sistema.barras.vetor_encargos('carga', 'locacional_nodal'))
        ctu_total = ctu_geracao + ctu_carga
        ctt = numpy.sum(self.sistema.circuitos.construir_vetor_custos_anuais())
        return ctt - ctu_total

    # Definir as tarifas do CTN de geração e carga
    def definir_tarifas_ctn(self):
        ctn_total = self.calcular_ctn()
        kg = (ctn_total/2)/numpy.sum(self.sistema.barras.vetor_capacidade_instalada())
        kc = (ctn_total/2)/numpy.sum(self.sistema.barras.vetor_potencia_consumida())
        for barra in self.sistema.barras:
            barra.custos.atualizar_tarifa(kg, 'geracao', 'selo')
            barra.custos.atualizar_tarifa(kc, 'carga', 'selo')

    # Corrigir alocação negativa nos circuitos
    def corrigir_alocacao_negativa(self, valores, natureza):
        if any(valores  < 0):
            self.corrigido = True
        referencia_proporcao = self.sistema.barras.vetor_potencia_gerada() if natureza == 'geracao' else self.sistema.barras.vetor_potencia_consumida()
        valores_corrigidos = distribuir_valores_negativos(valores, referencia_proporcao)
        for barra in self.sistema.barras:
            barra.custos.atualizar_encargo(valores_corrigidos[barra.posicao], natureza, 'final_nodal')

    # Gráfico das tarifas nodais
    def gerar_grafico_tarifas(self):
        plt.clf()
        plt.xlabel('Barra')
        plt.ylabel('Tarifa Locacional [R$/MW.ano]')
        x = range(1, len(self.sistema.barras) + 1)
        y = self.sistema.barras.vetor_tarifas('geracao', 'locacional_nodal')
        plt.scatter(x, y)
        plt.savefig('template_saida/nodal.png')
