import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import yfinance as yf

# Inicializa o aplicativo Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Gráfico em Tempo Real do EURUSD"),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*60*1000,  # Atualiza a cada 15 minutos (15 * 60 * 1000 milissegundos)
        n_intervals=0
    )
])

# Função para buscar os dados mais recentes
def fetch_data():
    # Busca os dados de 1 dia com intervalo de 15 minutos
    data = yf.download(tickers='EURUSD=X', period='1d', interval='15m')
    return data

# Callback para atualizar o gráfico em tempo real
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    data = fetch_data()

    # Criação do gráfico de velas
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                         open=data['Open'],
                                         high=data['High'],
                                         low=data['Low'],
                                         close=data['Close'])])

    fig.update_layout(title='EUR/USD - Atualização a Cada 15 Minutos',
                      xaxis_title='Hora',
                      yaxis_title='Preço (USD)',
                      xaxis_rangeslider_visible=False)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
