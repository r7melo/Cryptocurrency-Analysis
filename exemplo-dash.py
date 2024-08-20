import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
import datetime

# Cria a aplicação Dash
app = dash.Dash(__name__)

# Layout da aplicação
app.layout = html.Div([
    html.H1("Análise de Mercado Cripto com Dash"),
    
    # Componente para selecionar a criptomoeda
    dcc.Dropdown(
        id='crypto-dropdown',
        options=[
            {'label': 'Bitcoin (BTC)', 'value': 'BTC-USD'},
            {'label': 'Ethereum (ETH)', 'value': 'ETH-USD'},
            # Adicione mais opções conforme necessário
        ],
        value='BTC-USD'  # Valor padrão
    ),

    # Componente para selecionar o período da SMA
    dcc.Input(
        id='sma-period',
        type='number',
        value=20,  # Período padrão
        placeholder="Período da SMA"
    ),
    
    # Gráfico de linha para o preço e SMA
    dcc.Graph(id='price-graph'),

    # Intervalo de atualização para dados em tempo real
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Atualiza a cada 60 segundos
        n_intervals=0
    )
])

# Callback para atualizar o gráfico em tempo real
@app.callback(
    Output('price-graph', 'figure'),
    [Input('crypto-dropdown', 'value'),
     Input('sma-period', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_graph(selected_crypto, sma_period, n_intervals):
    # Obtém os dados da criptomoeda
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=60)
    df = yf.download(selected_crypto, start=start, end=end, interval='1m')

    # Calcula a média móvel simples (SMA)
    df['SMA'] = df['Close'].rolling(window=sma_period).mean()

    # Cria o gráfico de linhas
    fig = go.Figure()
    
    # Adiciona a linha do preço
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'],
                             mode='lines', name='Preço'))
    
    # Adiciona a linha da SMA
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'],
                             mode='lines', name=f'SMA {sma_period}'))

    # Layout do gráfico
    fig.update_layout(title=f'Preço e SMA ({sma_period} períodos) de {selected_crypto}',
                      xaxis_title='Tempo',
                      yaxis_title='Preço (USD)')
    
    return fig

# Executa a aplicação
if __name__ == '__main__':
    app.run_server(debug=True)
