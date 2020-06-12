import numpy

from sistema import Sistema

class GeradorDeTarifas:
    def __init__(self, arquivo_barras, arquivo_circuitos, barra_referencia, proporcao_geracao):
        self.ro = (100-proporcao_geracao) / proporcao_geracao
        self.sistema = Sistema(arquivo_barras, arquivo_circuitos, barra_referencia)

    # Matriz de tarifas iniciais sem ajuste
    def tarifa_inicial(self):
        CT = self.sistema.circuitos.construir_vetor_custos_anuais()
        DT = self.sistema.circuitos.construir_vetor_capacidades()
        DT = numpy.diag(1 / DT)
        return CT.dot(DT).dot(self.sistema.construir_matriz_beta())

    # Ajuste das tarifas iniciais
    def ajuste_m(self):
        vetor_pg = self.sistema.barras.vetor_potencia_gerada(usar_referencia=True)
        vetor_pc = self.sistema.barras.vetor_potencia_consumida()
        return - self.tarifa_inicial() .dot((self.ro*vetor_pg + vetor_pc).T) / (self.ro * (numpy.sum(vetor_pg))+numpy.sum(vetor_pc))

    # TARCTU
    def tar_ctu(self):
        return self.tarifa_inicial() + numpy.full_like(self.tarifa_inicial(), self.ajuste_m())

    # CTU PC
    def calcular_CTUPC(self):
        return self.tar_ctu().dot((-self.sistema.barras.vetor_potencia_consumida()).T)
    
    # CTU PG
    def calcular_CTUPG(self):
        return self.tar_ctu().dot(self.sistema.barras.vetor_potencia_gerada(True).T)

    # CTU
    def calcular_CTU(self):
        return self.tar_ctu().dot((self.sistema.barras.vetor_potencia_gerada(True) - self.sistema.barras.vetor_potencia_consumida()).T)

    # CTU PG Barras
    def ctu_PG_barras(self):
        return self.tar_ctu() * self.sistema.barras.vetor_potencia_gerada(True)

    # CTU PC Barras
    def ctu_PC_barras(self):
        return self.tar_ctu() * (-self.sistema.barras.vetor_potencia_consumida())

    # CTT
    def calcular_CTT(self):
        return numpy.sum(self.sistema.circuitos.construir_vetor_custos_anuais())

    # CTN
    def calcular_CTN(self):
        return self.calcular_CTT() - self.calcular_CTU()

    # CTN dos geradores e cargas
    def ctn_g_c(self):
        kg = (self.calcular_CTN()/2)/numpy.sum(self.sistema.barras.vetor_capacidade_instalada())
        kc = (self.calcular_CTN()/2)/numpy.sum(self.sistema.barras.vetor_potencia_consumida())

        ctn_g = kg * self.sistema.barras.vetor_capacidade_instalada()
        ctn_c = kc * self.sistema.barras.vetor_potencia_consumida()

        return (ctn_g, ctn_c)

    def encargos_finais(self):
        ctn_g, ctn_c = self.ctn_g_c()
        total_g = self.ctu_PG_barras() + ctn_g
        total_c = self.ctu_PC_barras() + ctn_c

        if any(total_g < 0):
            total_g = self.corrigir_alocacao_negativa(total_g, 'geracao')
        if any(total_c < 0):
            total_c = self.corrigir_alocacao_negativa(total_c, 'carga')

        return (total_g, total_c)

    def tarifas_finais(self):
        final_g, final_c = self.encargos_finais()

        tar_g = numpy.divide(final_g, self.sistema.barras.vetor_capacidade_instalada(), out=numpy.zeros_like(final_g), where=self.sistema.barras.vetor_capacidade_instalada()!=0)
        tar_c = numpy.divide(final_c, self.sistema.barras.vetor_potencia_consumida(), out=numpy.zeros_like(final_c), where=self.sistema.barras.vetor_potencia_consumida()!=0)

        return (tar_g, tar_c)

    def corrigir_alocacao_negativa(self, valores, tipo_correcao):
        valores_negativos = numpy.where(valores < 0, valores, 0)
        valores_positivos = numpy.where(valores > 0, valores, 0)
    
        montante_negativo = numpy.sum(valores_negativos)

        referencia_proporcao = self.sistema.barras.vetor_potencia_gerada(True) if tipo_correcao == 'geracao' else self.sistema.barras.vetor_potencia_consumida()
        valores_proporcao = numpy.where(valores_positivos > 0, referencia_proporcao, 0)
        proporcao = valores_proporcao / numpy.sum(valores_proporcao)

        valores_corrigidos = valores_positivos + (montante_negativo*proporcao)
        
        if any(valores_corrigidos < 0):
            return self.corrigir_alocacao_negativa(valores_corrigidos, tipo_correcao)

        return valores_corrigidos

# ----------------------------------------------------------------
cinco_barras = GeradorDeTarifas(
    arquivo_barras="5B-barras.csv",
    arquivo_circuitos="5B-circuitos.csv",
    barra_referencia=1,
    proporcao_geracao=50
)

print(cinco_barras.encargos_finais())
