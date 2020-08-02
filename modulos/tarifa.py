import numpy
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.cluster import KMeans
from sympy import Symbol, lambdify

from modulos.sistema import Sistema

class GeradorDeTarifas:
    def __init__(self, arquivo_barras, arquivo_circuitos, numero_barra_referencia, proporcao_geracao):
        self.ro = (100-proporcao_geracao) / proporcao_geracao
        self.sistema = Sistema(arquivo_barras, arquivo_circuitos, numero_barra_referencia)
        self.correcoes = []
        self.definir_encargos_ctu()
        self.definir_encargos_ctn()
        encargos_finais_geracao = self.sistema.barras.vetor_encargos_finais('geracao')
        encargos_finais_carga = self.sistema.barras.vetor_encargos_finais('carga')
        if any(encargos_finais_geracao < 0):
            self.corrigir_alocacao_negativa(encargos_finais_geracao, 'geracao')
            self.correcoes.append('geracao')
        if any(encargos_finais_carga < 0):
            self.corrigir_alocacao_negativa(encargos_finais_carga, 'carga')
            self.correcoes.append('carga')

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
        for barra in self.sistema.barras:
            barra.encargos['geracao']['CTN'] = kg * barra.capacidade_instalada
            barra.encargos['carga']['CTN'] = kc * barra.potencia_consumida

    # Corrigir alocação negativa nos circuitos
    def corrigir_alocacao_negativa(self, valores, tipo):
        valores_negativos = numpy.where(valores < 0, valores, 0)
        valores_positivos = numpy.where(valores > 0, valores, 0)

        montante_negativo = numpy.sum(valores_negativos)

        referencia_proporcao = self.sistema.barras.vetor_potencia_gerada() if tipo == 'geracao' else self.sistema.barras.vetor_potencia_consumida()
        valores_proporcao = numpy.where(valores_positivos > 0, referencia_proporcao, 0)
        proporcao = valores_proporcao / numpy.sum(valores_proporcao)

        valores_corrigidos = valores_positivos + (montante_negativo*proporcao)

        if any(valores_corrigidos < 0):
            self.corrigir_alocacao_negativa(valores_corrigidos, tipo)
        else:
            for barra in self.sistema.barras:
                barra.encargos[tipo]['total_corrigido'] = valores_corrigidos[barra.posicao]

    def calcular_k_medias(self, n_clusters):
        kmeans = KMeans(n_clusters=n_clusters).fit_predict(self.definir_tarifas_ctu().reshape(-1, 1))
        return (kmeans)

    def cotovelo(self):
        _figura, eixo1 = plt.subplots()
        eixo1.set_xlabel('Número de zonas')
        eixo1.set_ylabel('Erro estimado')
        eixo2 = eixo1.twinx()
        eixo2.set_ylabel('Curvatura', color='red')
        eixo2.tick_params(axis='y', labelcolor='red')

        numero_zonas = range(2, len(self.sistema.barras))
        eixo_x_continuo = numpy.linspace(2, len(self.sistema.barras), len(self.sistema.barras) *10)

        # Erros do K-médias
        erros = []
        for n in numero_zonas:
            kmeans = KMeans(n_clusters=n).fit(self.definir_tarifas_ctu().reshape(-1,1))
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
        plt.show()
        # Retorna o ponto estimado para o cotovelo
        maior_curvatura = max(valores_curvatura)
        return round(eixo_x_continuo[valores_curvatura.index(maior_curvatura)])
