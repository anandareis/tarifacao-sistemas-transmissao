from collections import namedtuple

from modulos.utils import dividir as d

Custo = namedtuple('Custo', 'tarifa encargo')

class Custos:
    def __init__(self, barra):
        self._barra= barra
        self._valores_geracao = {
            'locacional_nodal': Custo(0, 0),
            'selo': Custo(0, 0),
            'total_nodal': Custo(0, 0),
            'final_nodal': Custo(0, 0),
            'locacional_zonal': Custo(0, 0),
            'total_zonal': Custo(0, 0),
            'final_zonal': Custo(0, 0)
        }
        self._valores_carga = {
            'locacional_nodal': Custo(0, 0),
            'selo': Custo(0, 0),
            'total_nodal': Custo(0, 0),
            'final_nodal': Custo(0, 0),
            'locacional_zonal': Custo(0, 0),
            'total_zonal': Custo(0, 0),
            'final_zonal': Custo(0, 0)
        }

    def _atualizar_totais(self):
        for natureza in ['geracao', 'carga']:
            for tipo in ['nodal', 'zonal']:
                self._atualizar_total(natureza, tipo)

    def _atualizar_total(self, natureza, tipo):
        base = self._valores_geracao if natureza == 'geracao' else self._valores_carga
        encargo = base[f'locacional_{tipo}'].encargo + base['selo'].encargo
        self.atualizar_encargo(encargo, natureza, f'total_{tipo}', False)

    def atualizar_encargo(self, valor, natureza, tipo, atualizar_totais=True):
        if natureza not in ['geracao', 'carga'] or tipo not in self._valores_geracao:
            raise TypeError('Natureza ou tipo do custo não existe.')
        if natureza == 'geracao':
            base = self._valores_geracao
            referencia = self._barra.capacidade_instalada
            if tipo == 'locacional_nodal':
                referencia = self._barra.potencia_gerada
        else:
            base = self._valores_carga
            referencia = self._barra.potencia_consumida
            if tipo == 'locacional_nodal':
                referencia = -referencia
        base[tipo] = Custo(d(valor, referencia), valor)
        if atualizar_totais:
            self._atualizar_totais()

    def atualizar_tarifa(self, valor, natureza, tipo):
        if natureza not in ['geracao', 'carga'] or tipo not in self._valores_geracao:
            raise TypeError('Natureza ou tipo do custo não existe.')
        if natureza == 'geracao':
            base = self._valores_geracao
            referencia = self._barra.capacidade_instalada
            if tipo == 'locacional_nodal':
                referencia = self._barra.potencia_gerada
        else:
            base = self._valores_carga
            referencia = self._barra.potencia_consumida
            if tipo == 'locacional_nodal':
                referencia = -referencia
        base[tipo] = Custo(valor, valor*referencia)
        self._atualizar_totais()

    def obter_encargo(self, natureza, tipo):
        if natureza not in ['geracao', 'carga'] or tipo not in self._valores_geracao:
            raise TypeError('Natureza ou tipo do custo não existe.')
        if natureza == 'geracao':
            base = self._valores_geracao
        else:
            base = self._valores_carga
        return base[tipo].encargo

    def obter_tarifa(self, natureza, tipo):
        if natureza not in ['geracao', 'carga'] or tipo not in self._valores_geracao:
            raise TypeError('Natureza ou tipo do custo não existe.')
        if natureza == 'geracao':
            base = self._valores_geracao
        else:
            base = self._valores_carga
        return base[tipo].tarifa
