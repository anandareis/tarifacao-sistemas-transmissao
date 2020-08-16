# Tarifação Nodal e Zonal de Sistemas de Transmissão de Energia
Código utilizado no trabalho de conclusão de curso para o cálculo das tarifas de transmissão de sistemas elétricos

## Instalando as dependências necessárias

É necessário ter o Python instalado no seu computador, na versão 3.6 ou superior.
O download do Python pode ser feito através da [página oficial](https://www.python.org/downloads/).

Para instalar as dependências necessárias para a execução do programa, basta executar (na pasta onde está o projeto)
o seguinte comando no seu ambiente Python:

```
$ pip install -r requirements.txt --user
```

É recomendado utilizar um ambiente virtual para a instalação e execução do programa.
Para mais informações sobre ambientes virtuais, veja a [documentação oficial](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

## Executando um sistema de teste

Para executar o programa usando como entrada um dos sistemas de teste disponíveis com
o software, basta executar:

```
$ python tarifacao.py teste <nome do teste>
```

Os testes disponíves até o momento são:
- [5_barras](sistemas_teste/5_barras/): Sistema de 5 barras do IEEE;
- [24_barras](sistemas_teste/24_barras): Sistema de 24 barras do IEEE.


## Executando a partir de arquivos

Para executar o programa fornecendo como entrada os dados de qualquer sistema, é necessário possuir os arquivos com os dados das barras e circuitos do sistema em formato CSV.
Os dados das barras devem estar dispostos da seguinte forma:
```
Num;Potg_MW;Capac_Inst_MW;Potc_MW;coord_X;coord_Y
```
Onde:
- Num: Número da barra. Deve estar em sequência crescente, iniciado em 1;
- Potg_MW: Potência gerada pela barra, em MW;
- Capac_Inst_MW: Capacidade total instalada na barra, em MW.
- Potc_MW: Potência consumida pela barra, em MW;
- coord_X, coord_Y: Coordenadas X e Y do posicionamento da barra (para geração do gráfico posicional)

Os dados das barras devem estar dispostos da seguinte forma:
```
Num;De;Para;r_pu;x_pu;Capac_MW;Custo_Anual_RS
```
Onde:
- Num: Número do circuito. Deve estar em sequência crescente, iniciado em 1;
- De: Número da barra de origem do sistema;
- Para: Número da barra de destino do sistema;
- r_pu: Resistência do circuito, em p.u.
- x_pu: Reatância do circuito, em p.u.
- Capac_MW: Capacidade total instalada no circuito, em MW
- Custo_Anual_RS: Custo total anual para a manutenção do circuito, em reais.


Então, basta executar uma das linhas de comando equivalentes abaixo:

```
$ python tarifacao.py arquivo --arquivo-barras <arquivo de barras> --arquivo-circuitos <arquivo de circuitos>
$ python tarifacao.py arquivo -B <arquivo de barras> -C <arquivo de circuitos>
```

## Definindo parâmetros opcionais de entrada

É possível determinar qual das barras deve ser usada como barra de referência para o cálculo das tarifas,
e também qual a proporção desejada para distribuição das tarifas locacionais entre geração e carga.

Caso os valores não sejam definidos na linha de comando, será adotada a barra **1** como referência e
a proporção de geração será de **50** por cento.

- `-r` ou `--barra-referencia`: Define qual barra de referência deve ser adotada
- `-p` ou `--proporcao-geracao`: Define a porcentagem da tarifa locacional que deve corresponder à geração

Exemplos:

Para definir a barra **5** como barra de referência:

```
$ python tarifacao.py teste 24_barras --barra-referencia 5
$ python tarifacao.py teste 24_barras -r 5
```

Para distribuir a tarifa locacional como 70% para geração e, consequentemente, 30% para carga:

```
$ python tarifacao.py teste 24_barras --proporcao-geracao 70
$ python tarifacao.py teste 24_barras -p 70
```

Para definir a barra 10 como referência e distribuir a tarifa locacional como 40% para geração:
```
$ python tarifacao.py teste 24_barras --barra-referencia 10 --proporcao-geracao 40
$ python tarifacao.py teste 24_barras -r 10 -p 40
```
