import numpy

def formatar_decimal(valor, casas=2, tratar_zero=False):
    if tratar_zero and valor == 0:
        return '---'
    return "{0:.{c}f}".format(round(valor, casas), c=casas)

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

cores = [
    "#FF0000",
    "#00008B",
    "#FFD700",
    "#008000",
    "#1E90FF",
    "#8B4513",
    "#6B8E23",
    "#008B8B",
    "#FF4500",
    "#BDB76B",
    "#696969",
    "#C71585",
    "#F08080",
    "#32CD32",
    "#DAA520",
    "#FF00FF",
    "#FF1493",
    "#3CB371",
    "#FA8072",
    "#6495ED"
]
