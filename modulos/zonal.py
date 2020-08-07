import numpy
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.cluster import KMeans
from sympy import Symbol, lambdify

class TarifasZonais:
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
