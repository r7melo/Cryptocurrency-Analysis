import pandas as pd

# Carregar o DataFrame a partir do arquivo CSV
df = pd.read_csv('C:/RepoPy/Criptor Maper/trend_base/trend_list_20240322114522148910.csv')

# Exibir o DataFrame antes da ordenação
print("DataFrame antes da ordenação:")
print(df)

# Ordenar o DataFrame pelo ângulo em ordem ascendente
df_ordenado = df.sort_values(by='Angle')

# Exibir o DataFrame ordenado
print("\nDataFrame ordenado pelo ângulo:")
print(df_ordenado)
