import argparse
import sys
from tarifa import GeradorDeTarifas

parser = argparse.ArgumentParser(description='Calcula as tarifas nodais e zonais para um sistema de transmissão de energia')
opcoes = parser.add_subparsers(required=True)

teste = opcoes.add_parser('teste', help='Utilizar um dos sistemas-teste disponíveis no programa')
teste.add_argument('sistema_teste', type=str, choices=['5_barras', '24_barras'], help='Sistema-teste a ser utilizado')

personalizado = opcoes.add_parser('arquivo', help='Utilizar arquivos de barras e circuitos personalizados')
personalizado.add_argument('-B', '--arquivo-barras', required=True, type=str, help='Arquivo CSV com dados de barras')
personalizado.add_argument('-C', '--arquivo-circuitos', required=True, type=str, help='Arquivo CSV com dados de circuitos')

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()

if hasattr(args, 'sistema_teste'):
    csv_barras = f"sistemas_teste/{args.sistema_teste}/barras.csv"
    csv_circuitos = f"sistemas_teste/{args.sistema_teste}/circuitos.csv"
else:
    csv_barras = args.arquivo_barras
    csv_circuitos = args.arquivo_circuitos

try:
    sistema_tarifacao = GeradorDeTarifas(
        arquivo_barras=csv_barras,
        arquivo_circuitos=csv_circuitos,
        barra_referencia=1,
        proporcao_geracao=50
    )
    print(sistema_tarifacao.cotovelo())

except FileNotFoundError:
    print("Não foi possível encontrar o arquivo de barras ou o arquivo de circuitos.")
    print("Certifique-se de que o caminho está correto e que os arquivos existem")
    sys.exit(2)
