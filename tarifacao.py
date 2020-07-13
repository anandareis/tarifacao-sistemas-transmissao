import argparse
import sys
from jinja2 import Template
from modulos.tarifa import GeradorDeTarifas
from weasyprint import HTML, CSS

parser = argparse.ArgumentParser(description='Calcula as tarifas nodais e zonais para um sistema de transmissão de energia', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
opcoes = parser.add_subparsers(required=True)

teste = opcoes.add_parser('teste', help='Utilizar um dos sistemas-teste disponíveis no programa')
teste.add_argument('sistema_teste', type=str, choices=['5_barras', '24_barras'], help='Sistema-teste a ser utilizado')
teste.add_argument('-r', '--barra-referencia', metavar='B_REF', type=int, help='Número da barra de referência para o cálculo', default=1)
teste.add_argument('-p', '--proporcao-geracao', metavar='PROP', type=float, help='Proporção da tarifa correspondente à geração, em relação à carga', default=50)

personalizado = opcoes.add_parser('arquivo', help='Utilizar arquivos de barras e circuitos personalizados')
personalizado.add_argument('-B', '--arquivo-barras', required=True, type=str, help='Arquivo CSV com dados de barras')
personalizado.add_argument('-C', '--arquivo-circuitos', required=True, type=str, help='Arquivo CSV com dados de circuitos')
personalizado.add_argument('-r', '--barra-referencia', metavar='B_REF', type=int, help='Número da barra de referência para o cálculo', default=1)
personalizado.add_argument('-p', '--proporcao-geracao', metavar='PROP', type=float, help='Proporção da tarifa correspondente à geração, em relação à carga', default=50)

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)

try:
    args = parser.parse_args()
except TypeError:
    parser.print_help(sys.stderr)
    sys.exit(1)

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
        barra_referencia=args.barra_referencia,
        proporcao_geracao=args.proporcao_geracao
    )

except FileNotFoundError:
    print("Não foi possível encontrar o arquivo de barras ou o arquivo de circuitos.")
    print("Certifique-se de que o caminho está correto e que os arquivos existem")
    sys.exit(2)

except IndexError:
    print("Certifique-se de que a barra de referência definida existe no sistema")
    sys.exit(3)

with open('./template_saida/template.html') as html_entrada:
    template = Template(html_entrada.read())

saida = template.render(
    barras=sistema_tarifacao.sistema.barras, 
    circuitos=sistema_tarifacao.sistema.circuitos
    )

with open('./template_saida/index.html', 'w+') as html_saida:
    html_saida.write(saida)

HTML('./template_saida/index.html').write_pdf('resultado.pdf', stylesheets=[CSS('./template_saida/style.css')])
