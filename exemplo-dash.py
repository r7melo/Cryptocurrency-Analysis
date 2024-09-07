import requests
import xml.etree.ElementTree as ET

# URL para obter dados do ECB em XML
url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'

# Fazendo a requisição
response = requests.get(url)

# Verifica se a requisição foi bem-sucedida
if response.status_code == 200:
    # Analisando o XML
    tree = ET.ElementTree(ET.fromstring(response.content))
    root = tree.getroot()
    
    # Iterando sobre as taxas de câmbio no XML
    for cube in root.findall('.//{*}Cube[@currency]'):
        currency = cube.get('currency')
        rate = cube.get('rate')
        print(f'{currency}: {rate}')
else:
    print("Falha ao obter dados:", response.status_code)

import yfinance as yf

# Defina o símbolo do par de moedas Forex no Yahoo Finance
symbol = 'EURUSD=X'

# Obtenha dados históricos de 1 hora para a última semana
data = yf.download(symbol, interval='1h', period='7d')

# Exiba os dados
print(data)
