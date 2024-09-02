import dash
from dash import dcc, html, Input, Output
import dash_table
import pandas as pd
import numpy as np

# Crie alguns dados iniciais
def generate_data():
    return pd.DataFrame({
        'Coluna 1': np.random.randint(1, 100, size=10),
        'Coluna 2': np.random.choice(['A', 'B', 'C'], size=10)
    })

# Inicialize o app Dash
app = dash.Dash(__name__)

# Layout da aplicação
app.layout = html.Div([
    html.Button('Recarregar Dados', id='reload-button', n_clicks=0),
    dash_table.DataTable(id='data-table')
])

# Callback para atualizar a tabela
@app.callback(
    Output('data-table', 'data'),
    [Input('reload-button', 'n_clicks')]
)
def update_table(n_clicks):
    # Gere novos dados toda vez que o botão for clicado
    df = generate_data()
    return df.to_dict('records')

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
