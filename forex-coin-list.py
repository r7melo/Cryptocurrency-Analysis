import requests
import xml.etree.ElementTree as ET

url = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
response = requests.get(url)
pares_usd = []
if response.status_code == 200:
    tree = ET.ElementTree(ET.fromstring(response.content))
    root = tree.getroot()
    for cube in root.findall('.//{*}Cube[@currency]'):
        currency = cube.get('currency')
        if currency != 'USD':
            pares_usd.append(f'{currency}USD')
else:
    print("Falha ao obter dados:", response.status_code)

# Exibe a lista de pares de moedas com USD
for par in pares_usd:
    print(par)
