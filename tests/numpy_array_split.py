import pandas as pd

# Exemplo de DataFrame
data = {'col1': range(1,101), 'col2': range(1, 101)}
df = pd.DataFrame(data)


df = df.iloc[::-1]
tamanho_do_bloco = 10
blocos = [df[i:i + tamanho_do_bloco] for i in range(0, len(df), tamanho_do_bloco)]


for i in range(len(blocos)):
    bloco = blocos[i][::-1]
    print(f'Bloco {i} \n {bloco}\n')
