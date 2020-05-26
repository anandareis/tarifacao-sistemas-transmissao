import numpy
import pandas

#-------
class Barra:
    def __init__(self, numero, potencia_gerada, capacidade_instalada, potencia_consumida):
        self.numero = numero
        self.potencia_gerada = potencia_gerada
        self.capacidade_instalada = capacidade_instalada
        self.potencia_consumida = potencia_consumida
        self.posicao = numero - 1

#-------
class Circuito:
    def __init__(self, numero, origem, destino, r_pu, x_pu, capacidade, custo_anual):
        self.numero = numero
        self.origem = origem
        self.destino = destino
        self.r_pu = r_pu
        self.x_pu = x_pu
        self.capacidade = capacidade
        self.custo_anual = custo_anual
        self.posicao = numero - 1

    @property
    def susceptancia(self): # é o 'd' da matriz D
        return self.x_pu/(self.x_pu**2+self.r_pu**2)

#-------
class Sistema:
    def __init__(self, arquivo_barras, arquivo_circuitos, barra_referencia, prop_g):
        self.barras = []
        self.circuitos = []
        self._criar_barras(arquivo_barras)
        self._criar_circuitos(arquivo_circuitos)
        self.numero_barras = len(self.barras)
        self.numero_circuitos = len(self.circuitos)
        self.posicao_barra_referencia = barra_referencia-1
        self.ro = (100-prop_g) / prop_g

    def _criar_barras(self, arquivo_barras):
        tabela_barras = pandas.read_csv(arquivo_barras, sep=";")
        for _, barra in tabela_barras.iterrows():
            self.barras.append(Barra(
                numero=int(barra['Num']),
                potencia_gerada=barra['Potg_MW'],
                capacidade_instalada=barra['Capac_Inst_MW'],
                potencia_consumida=barra['Potc_MW']
            ))

    def _criar_circuitos(self, arquivo_circuitos):
        tabela_circuitos = pandas.read_csv(arquivo_circuitos, sep=";")
        for _, circuito in tabela_circuitos.iterrows():
            self.circuitos.append(Circuito(
                numero=int(circuito['Num']),
                origem=self.get_barra(circuito['De']),
                destino=self.get_barra(circuito['Para']),
                r_pu=circuito['r_pu'],
                x_pu=circuito['x_pu'],
                capacidade=circuito['Capac_MW'],
                custo_anual=circuito['Custo_Anual_RS']
            ))

    def get_barra(self, numero):
        for barra in self.barras:
            if barra.numero == numero:
                return barra
        return None

    # Matriz D
    def construir_matriz_susceptancia(self):
        matriz = numpy.zeros((self.numero_circuitos, self.numero_circuitos))
        for circuito in self.circuitos:
            matriz[circuito.posicao, circuito.posicao] = circuito.susceptancia
        return matriz

    # Matriz C
    def construir_matriz_conectividade(self):
        matriz = numpy.zeros((self.numero_circuitos, self.numero_barras))
        for circuito in self.circuitos:
            matriz[circuito.posicao, circuito.origem.posicao] = 1
            matriz[circuito.posicao, circuito.destino.posicao] = -1
        return matriz

    # Matriz B' completa - mudar o nome da função depois
    def construir_matriz_b_linha_completa(self):
        matriz = numpy.zeros((self.numero_barras, self.numero_barras))
        for circuito in self.circuitos:
            matriz[circuito.origem.posicao, circuito.destino.posicao] = -circuito.susceptancia
            matriz[circuito.destino.posicao, circuito.origem.posicao] = -circuito.susceptancia

        for i in range(0, len(matriz)):
            matriz[i,i] = -numpy.sum(matriz[i])

        return matriz

    # Matriz B' sem a barra de referência
    def construir_matriz_b_linha(self):
        matriz = self.construir_matriz_b_linha_completa()
        matriz = numpy.delete(matriz, self.posicao_barra_referencia, axis=0)
        matriz = numpy.delete(matriz, self.posicao_barra_referencia, axis=1)
        return matriz

    # Inversa da matriz B' sem a barra de referência
    def construir_inversa_b_linha(self):
        return numpy.linalg.inv(self.construir_matriz_b_linha())

    # Matriz X - inversa com 0 na linha e coluna da barra de referência
    def construir_matriz_x(self):
        matriz = self.construir_inversa_b_linha()
        matriz = numpy.insert(matriz, self.posicao_barra_referencia, 0, axis=0)
        matriz = numpy.insert(matriz, self.posicao_barra_referencia, 0, axis=1)
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

    def vetor_pc(self):
        pc = []
        for barra in self.barras:
            pc.append(barra.potencia_consumida)
        return numpy.array(pc)

    def soma_pc(self):
        return numpy.sum(self.vetor_pc())

    #  TODO: reimplementar
    def vetor_pg(self):
        pg = numpy.zeros(self.numero_barras)
        for barra in self.barras:
            if barra.posicao != self.posicao_barra_referencia:
                pg[barra.posicao] = barra.potencia_gerada
        soma_sem_ref = numpy.sum(pg)
        pg[self.posicao_barra_referencia] = self.soma_pc() - soma_sem_ref

        return pg

    #  Vetor F
    def vetor_fluxo_potencia(self):
        return self.construir_matriz_beta().dot(self.vetor_potencia_ativa().T)

    # Ajuste das tarifas iniciais
    def ajuste_m(self):
        return - self.tarifa_inicial() .dot((self.ro*self.vetor_pg() + self.vetor_pc()).T) / (self.ro * (numpy.sum(self.vetor_pg()))+self.soma_pc())

    # TARCTU
    def tar_ctu(self):
        return self.tarifa_inicial() + numpy.full_like(self.tarifa_inicial(), self.ajuste_m())

    # CTU
    def calcular_CTU(self):
        return self.tar_ctu().dot((self.vetor_pg() - self.vetor_pc()).T)

    # CTU PG
    def calcular_CTUPG(self):
        return self.tar_ctu().dot(self.vetor_pg().T)

    # CTU PC
    def calcular_CTUPC(self):
        return self.tar_ctu().dot((-self.vetor_pc()).T)

    # CTU PG Barras
    def ctu_PG_barras(self):
        return self.tar_ctu() * self.vetor_pg()

    # CTU PC Barras
    def ctu_PC_barras(self):
        return self.tar_ctu() * (-self.vetor_pc())

    # CTT
    def calcular_CTT(self):
        ctt = 0
        for circuito in self.circuitos:
            ctt += circuito.custo_anual
        return ctt
    
    # CTN
    def calcular_CTN(self):
        return self.calcular_CTT() - self.calcular_CTU()

    # P
    def vetor_potencia_ativa(self):
        p = []
        for barra in self.barras:
            p.append(barra.potencia_gerada - barra.potencia_consumida)
        return p

    # Capacidade de geração instalada
    def capacidade_instalada(self):
        c_inst = []
        for barra in self.barras:
            c_inst.append(barra.capacidade_instalada)
        return numpy.array(c_inst)

    # CTN dos geradores e cargas
    def ctn_g_c(self):
        kg = (self.calcular_CTN()/2)/numpy.sum(self.capacidade_instalada())
        kc = (self.calcular_CTN()/2)/self.soma_pc()

        ctn_g = kg * self.capacidade_instalada()
        ctn_c = kc * self.vetor_pc()

        return (ctn_g, ctn_c)

    def encargos_finais(self):
        ctn_g, ctn_c = self.ctn_g_c()
        total_g = self.ctu_PG_barras() + ctn_g
        total_c = self.ctu_PC_barras() + ctn_c

        return (total_g, total_c)

    def tarifas_finais(self):
        final_g, final_c = self.encargos_finais()

        tar_g = numpy.divide(final_g, self.capacidade_instalada(), out=numpy.zeros_like(final_g), where=self.capacidade_instalada()!=0)
        tar_c = numpy.divide(final_c, self.vetor_pc(), out=numpy.zeros_like(final_c), where=self.vetor_pc()!=0)

        return (tar_g, tar_c)

#-------
cinco_barras = Sistema(
    arquivo_barras="5B-barras.csv",
    arquivo_circuitos="5B-circuitos.csv",
    barra_referencia=1,
    prop_g=50
)

print(cinco_barras.tarifas_finais())
