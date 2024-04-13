from ftplib import FTP
import pandas as pd

# Conectar ao servidor FTP
ftp = FTP('10.0.0.92')
ftp.login(user='melu', passwd='001')

# Navegar para o diretório onde estão os arquivos
ftp.cwd('/coinbase')

# Listar os arquivos disponíveis
arquivos = ftp.nlst()

# Escolher o arquivo que deseja baixar (você pode iterar sobre 'arquivos' para baixar todos)
nome_arquivo = 'BTCUSDT.csv'

# Baixar o arquivo
with open(nome_arquivo, 'wb') as file:
    ftp.retrbinary('RETR ' + nome_arquivo, file.write)

# Fechar a conexão FTP
ftp.quit()

# Ler o arquivo baixado e criar o DataFrame
df = pd.read_csv(nome_arquivo)

# Agora você tem o DataFrame pronto para uso
print(df.head())

# Depois de usar o DataFrame, você pode excluir o arquivo local se não precisar mais dele
import os
os.remove(nome_arquivo)
