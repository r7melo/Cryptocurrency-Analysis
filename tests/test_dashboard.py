import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd

# Inicializa o aplicativo Dash
app = dash.Dash(__name__)

# Configura a conexão com o MetaTrader 5
mt5.initialize()

app.layout = html.Div([
    html.H1("Gráfico em Tempo Real do EURUSD"),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Atualiza a cada 30 segundos
        n_intervals=0
    )
])

# Função para buscar os dados mais recentes do MetaTrader 5
def fetch_data():
    # Define o símbolo e o período
    symbol = 'EURUSD'
    timeframe = mt5.TIMEFRAME_M1  # 1 minuto
    
    # Obtém os dados históricos
    now = datetime.now()
    from_time = now - timedelta(days=1)  # Dados do último dia
    rates = mt5.copy_rates_range(symbol, timeframe, from_time, now)
    
    # Converte para DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    
    return df

# Callback para atualizar o gráfico em tempo real
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    data = fetch_data()

    # Criação do gráfico de velas
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                         open=data['open'],
                                         high=data['high'],
                                         low=data['low'],
                                         close=data['close'])])

    fig.update_layout(title='EUR/USD - Atualização a Cada 30 Segundos',
                      xaxis_title='Hora',
                      yaxis_title='Preço (USD)',
                      xaxis_rangeslider_visible=False)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
