import pandas
import numpy

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


class Circuitos:
    def __init__(self, arquivo_circuitos):
        self.elementos = []
        self._criar_circuitos(arquivo_circuitos)

    def __len__(self):
        return len(self.elementos)

    def __iter__(self):
        return iter(self.elementos)

    def _criar_circuitos(self, arquivo_circuitos):
        tabela_circuitos = pandas.read_csv(arquivo_circuitos, sep=";")
        for _, circuito in tabela_circuitos.iterrows():
            self.elementos.append(Circuito(
                numero=int(circuito['Num']),
                origem=int(circuito['De']),
                destino=int(circuito['Para']),
                r_pu=circuito['r_pu'],
                x_pu=circuito['x_pu'],
                capacidade=circuito['Capac_MW'],
                custo_anual=circuito['Custo_Anual_RS']
            ))

    def construir_vetor_susceptancias(self):
        return numpy.array([circuito.susceptancia for circuito in self.elementos])
