import numpy

def formatar_moeda(valor):
    return "{0:.2f}".format(round(valor, 2))

def dividir(dividendo, divisor):
    return dividendo / divisor if divisor != 0 else 0

def distribuir_valores_negativos(valores, referencia):
        valores_negativos = numpy.where(valores < 0, valores, 0)
        valores_positivos = numpy.where(valores > 0, valores, 0)

        montante_negativo = numpy.sum(valores_negativos)

        valores_proporcao = numpy.where(valores_positivos > 0, referencia, 0)
        proporcao = valores_proporcao / numpy.sum(valores_proporcao)

        valores_corrigidos = valores_positivos + (montante_negativo*proporcao)

        if any(valores_corrigidos < 0):
            return distribuir_valores_negativos(valores_corrigidos, referencia)
        else:
            return valores_corrigidos
