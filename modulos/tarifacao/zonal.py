import numpy
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.cluster import KMeans
from sympy import Symbol, lambdify

from modulos.modelos.zonas import Zona
from modulos.utils import dividir as d
from modulos.utils import distribuir_valores_negativos, cores

class TarifasZonais:
    def __init__(self, sistema):
        self.sistema = sistema
        self.zonas = []
        self.calcular_tarifas_zonais()
        self.gerar_grafico_tarifas()
        self.gerar_grafico_posicional()

    def calcular_tarifas_zonais(self):
        numero_zonas = self.cotovelo()
        self.definir_zonas(numero_zonas)
        self.definir_tarifas_encargos_zonais()
        encargos_totais_geracao = numpy.array([zona.encargo_total('geracao') for zona in self.zonas])
        encargos_totais_carga = numpy.array([zona.encargo_total('carga') for zona in self.zonas])
        self.corrigir_alocacao_negativa(encargos_totais_geracao, 'geracao')
        self.corrigir_alocacao_negativa(encargos_totais_carga, 'carga')

    def definir_tarifas_encargos_zonais(self):
        for zona in self.zonas:
            ctu_geracao = numpy.sum(zona.barras.vetor_encargos('geracao', 'locacional_nodal'))
            ctu_carga = numpy.sum(zona.barras.vetor_encargos('carga', 'locacional_nodal'))
            potencia_instalada = numpy.sum(zona.barras.vetor_capacidade_instalada())
            potencia_consumida = numpy.sum(zona.barras.vetor_potencia_consumida())

            tarifa_geracao = d(ctu_geracao, potencia_instalada)
            tarifa_carga = d(ctu_carga, potencia_consumida)
            for barra in zona.barras:
                barra.custos.atualizar_tarifa(tarifa_geracao, 'geracao', 'locacional_zonal')
                barra.custos.atualizar_tarifa(tarifa_carga, 'carga', 'locacional_zonal')

    def definir_zonas(self, n_zonas):
        zonas = KMeans(n_clusters=n_zonas).fit_predict(self.sistema.barras.vetor_tarifas('geracao', 'locacional_nodal').reshape(-1, 1))
        for i in range(n_zonas):
            zona = Zona(numero=i+1, cor=cores[i])
            for barra in self.sistema.barras :
                if zonas[barra.posicao] == i:
                    zona.barras.adicionar_barra(barra)
                    barra.zona = zona
            self.zonas.append(zona)

    def cotovelo(self):
        plt.clf()
        _figura, eixo1 = plt.subplots()
        eixo1.set_xlabel('Número de zonas')
        eixo1.set_ylabel('Erro estimado do K-Médias')
        eixo2 = eixo1.twinx()
        eixo2.set_ylabel('Curvatura')

        numero_zonas = range(2, len(self.sistema.barras))
        eixo_x_continuo = numpy.linspace(2, len(self.sistema.barras), len(self.sistema.barras) *10)

        # Erros do K-médias
        erros = []
        for n in numero_zonas:
            kmeans = KMeans(n_clusters=n).fit(self.sistema.barras.vetor_tarifas('geracao', 'locacional_nodal').reshape(-1,1))
            erros.append(kmeans.inertia_)
        eixo1.scatter(numero_zonas, erros)

        # Linha de tendência
        def funcao_exponencial_negativa(x, a, b, c):
            return a*x**(-b)+c
        popt, _pcov = curve_fit(funcao_exponencial_negativa, numero_zonas, erros)
        x = Symbol('x')
        equacao_tendencia = popt[0]*x**(-popt[1])+popt[2]
        funcao_tendencia = lambdify(x, equacao_tendencia)
        valores_tendencia = [funcao_tendencia(k) for k in eixo_x_continuo]
        eixo1.plot(eixo_x_continuo, valores_tendencia, 'yellow')

        # Curvatura da linha de tendência
        primeira_derivada = equacao_tendencia.diff(x)
        segunda_derivada = primeira_derivada.diff(x)
        primeira_derivada = lambdify(x, primeira_derivada)
        segunda_derivada = lambdify(x, segunda_derivada)

        def calcular_curvatura(x):
            return abs(segunda_derivada(x))*(1 + primeira_derivada(x)**2)**-1.5

        valores_curvatura = [calcular_curvatura(k) for k in eixo_x_continuo]
        eixo2.plot(eixo_x_continuo, valores_curvatura, 'red')

        # Calcula o ponto estimado para o cotovelo
        maior_curvatura = max(valores_curvatura)
        cotovelo_aproximado = eixo_x_continuo[valores_curvatura.index(maior_curvatura)]
        eixo2.axvline(cotovelo_aproximado, 0, 1, color='r', linestyle='--')

        legenda = plt.legend(handles=[
            mpatches.Patch(color='yellow', label='Erro quadrático'),
            mpatches.Patch(color='red', label='Curvatura')
        ], loc='upper left', bbox_to_anchor=(1.12, 1))
        # Salva o plot como arquivo
        plt.savefig('template_saida/cotovelo.png', bbox_extra_artists=(legenda,), bbox_inches = 'tight')

        return int(round(cotovelo_aproximado))

    # Corrigir alocação negativa nas zonas
    def corrigir_alocacao_negativa(self, valores, natureza):
        referencia_proporcao = numpy.array([zona.obter_valor_referencia(natureza) for zona in self.zonas])
        valores_corrigidos = distribuir_valores_negativos(valores, referencia_proporcao)
        for zona in self.zonas:
            zona.definir_custos_finais(valores_corrigidos[zona.posicao], natureza)

    # Gráfico das tarifas zonais
    def gerar_grafico_tarifas(self):
        plt.clf()
        plt.xlabel('Barra')
        plt.ylabel('Tarifa Locacional [R$/MW.ano]')
        handles = []
        for zona in self.zonas:
            for barra in zona.barras:
                plt.scatter(barra.numero, barra.custos.obter_tarifa('geracao', 'locacional_nodal'), color=zona.cor)
            handles.append(mpatches.Patch(color=zona.cor, label=f'Zona {zona.numero}'))
        legenda = plt.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.02, 1))
        plt.savefig('template_saida/zonal.png', bbox_extra_artists=(legenda,), bbox_inches='tight')

    def gerar_grafico_posicional(self):
        plt.clf()
        plt.xticks([])
        plt.yticks([])
        handles = []
        for zona in self.zonas:
            for barra in zona.barras:
                plt.scatter(barra.coordenadas['X'], barra.coordenadas['Y'], color=zona.cor, s=100)
                plt.annotate(barra.numero, (barra.coordenadas['X'], barra.coordenadas['Y']), xytext=(5, 5), textcoords='offset pixels')
            handles.append(mpatches.Patch(color=zona.cor, label=f'Zona {zona.numero}'))
        legenda = plt.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.02, 1))
        plt.savefig('template_saida/posicional.png', bbox_extra_artists=(legenda,), bbox_inches='tight')
