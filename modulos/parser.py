import argparse

parser = argparse.ArgumentParser(description='Calcula as tarifas nodais e zonais para um sistema de transmissão de energia', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
opcoes = parser.add_subparsers(required=True)

teste = opcoes.add_parser('teste', help='Utilizar um dos sistemas-teste disponíveis no programa')
teste.add_argument('sistema_teste', type=str, choices=['5_barras', '24_barras', '118_barras'], help='Sistema-teste a ser utilizado')
teste.add_argument('-r', '--barra-referencia', metavar='B_REF', type=int, help='Número da barra de referência para o cálculo', default=1)
teste.add_argument('-p', '--proporcao-geracao', metavar='PROP', type=float, help='Proporção da tarifa correspondente à geração, em relação à carga', default=50)

personalizado = opcoes.add_parser('arquivo', help='Utilizar arquivos de barras e circuitos personalizados')
personalizado.add_argument('-B', '--arquivo-barras', required=True, type=str, help='Arquivo CSV com dados de barras')
personalizado.add_argument('-C', '--arquivo-circuitos', required=True, type=str, help='Arquivo CSV com dados de circuitos')
personalizado.add_argument('-r', '--barra-referencia', metavar='B_REF', type=int, help='Número da barra de referência para o cálculo', default=1)
personalizado.add_argument('-p', '--proporcao-geracao', metavar='PROP', type=float, help='Proporção da tarifa correspondente à geração, em relação à carga', default=50)
