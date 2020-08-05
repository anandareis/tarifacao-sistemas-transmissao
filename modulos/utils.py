def formatar_moeda(valor):
    return "{0:.2f}".format(round(valor, 2))

def dividir(dividendo, divisor):
    return dividendo / divisor if divisor != 0 else 0