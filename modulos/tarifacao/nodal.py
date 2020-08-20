import numpy
import matplotlib.pyplot as plt

from modulos.utils import distribuir_valores_negativos
class TarifasNodais:
    def __init__(self, sistema, proporcao_geracao):
        self.ro = (100-proporcao_geracao) / proporcao_geracao
        self.sistema = sistema
        self.tarifas_ctn = {
            'kc': 0,
            'kg': 0
        }
        self.tarifas_ctu = []
        self.corrigido = []
        self.calcular_tarifas_nodais()
        self.gerar_grafico_tarifas()

    # Realizar todos os cálculos para tarifação nodal
    def calcular_tarifas_nodais(self):
        self.definir_encargos_ctu()
        self.definir_encargos_ctn()
        encargos_finais_geracao = self.sistema.barras.vetor_encargos_finais('geracao')
        encargos_finais_carga = self.sistema.barras.vetor_encargos_finais('carga')
        if any(encargos_finais_geracao < 0):
            self.corrigir_alocacao_negativa(encargos_finais_geracao, 'geracao')
            self.corrigido.append('geracao')
        if any(encargos_finais_carga < 0):
            self.corrigir_alocacao_negativa(encargos_finais_carga, 'carga')
            self.corrigido.append('carga')

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
    def definir_encargos_ctu(self):
        tar_ctu = self.calcular_tarifa_inicial() + numpy.full_like(self.calcular_tarifa_inicial(), self.calcular_ajuste_m())
        self.tarifas_ctu = tar_ctu
        for barra in self.sistema.barras:
            barra.encargos['geracao']['CTU'] = tar_ctu[barra.posicao] * barra.potencia_gerada
            barra.encargos['carga']['CTU'] = tar_ctu[barra.posicao] * -barra.potencia_consumida

    # Calcular o valor total do CTN
    def calcular_ctn(self):
        ctu_total = numpy.sum(self.sistema.barras.vetor_encargo_ctu())
        ctt = numpy.sum(self.sistema.circuitos.construir_vetor_custos_anuais())
        return ctt - ctu_total

    # Definir as tarifas do CTN de geração e carga
    def definir_encargos_ctn(self):
        ctn_total = self.calcular_ctn()
        kg = (ctn_total/2)/numpy.sum(self.sistema.barras.vetor_capacidade_instalada())
        kc = (ctn_total/2)/numpy.sum(self.sistema.barras.vetor_potencia_consumida())
        self.tarifas_ctn['kg'] = kg
        self.tarifas_ctn['kc'] = kc
        for barra in self.sistema.barras:
            barra.encargos['geracao']['CTN'] = kg * barra.capacidade_instalada
            barra.encargos['carga']['CTN'] = kc * barra.potencia_consumida

    # Corrigir alocação negativa nos circuitos
    def corrigir_alocacao_negativa(self, valores, tipo):
        referencia_proporcao = self.sistema.barras.vetor_potencia_gerada() if tipo == 'geracao' else self.sistema.barras.vetor_potencia_consumida()
        valores_corrigidos = distribuir_valores_negativos(valores, referencia_proporcao)
        for barra in self.sistema.barras:
            barra.encargos[tipo]['nodal_corrigido'] = valores_corrigidos[barra.posicao]

    # Gráfico das tarifas nodais
    def gerar_grafico_tarifas(self):
        plt.clf()
        plt.xlabel('Barra')
        plt.ylabel('Tarifa Locacional [R$/MW.ano]')
        x_range = range(1, len(self.sistema.barras) + 1)
        y_range = self.tarifas_ctu
        plt.scatter(x_range, y_range)
        plt.savefig('template_saida/nodal.png')
