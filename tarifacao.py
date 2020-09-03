import sys

from jinja2 import Template
from weasyprint import CSS, HTML

from modulos.sistema import Sistema
from modulos.tarifacao.nodal import TarifasNodais
from modulos.tarifacao.zonal import TarifasZonais
from modulos.utils import formatar_decimal
from parser import parser

if len(sys.argv) == 1:
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
    sistema = Sistema(
        arquivo_barras=csv_barras,
        arquivo_circuitos=csv_circuitos,
        numero_barra_referencia=args.barra_referencia
    )
    tarifacao_nodal = TarifasNodais(
        sistema=sistema,
        proporcao_geracao=args.proporcao_geracao
    )
    tarifacao_zonal = TarifasZonais(
        sistema=sistema
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
    barras=sistema.barras,
    circuitos=sistema.circuitos,
    zonas=tarifacao_zonal.zonas,
    corrigido_nodal=tarifacao_nodal.corrigido,
    corrigido_zonal=tarifacao_zonal.corrigido,
    f=formatar_decimal
    )

with open('./template_saida/index.html', 'w+') as html_saida:
    html_saida.write(saida)

HTML('./template_saida/index.html').write_pdf('resultado.pdf', stylesheets=[CSS('./template_saida/style.css')])
