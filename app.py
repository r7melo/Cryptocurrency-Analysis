from dash import dcc, html
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, Input, Output, html,  dcc, callback
import os
import vectorbt as vbt


CACHE_GRAPH = 'BTCUSDT'
COIN_BASE_PATH = 'C:/CoinsBase/1h/{}.csv'

def generate_options():
        
        options = []
        try:
            for file in os.listdir('C:/CoinsBase/1h/'):
                name, _ = os.path.splitext(file)
                options.append({'label': name, 'value': name})
            
        except:
            print("Falha ao acessar a lista de símbolos.")
        return options

def generate_graph_by_symbol(symbol):

    filename = f'C:/CoinsBase/1h/{symbol}.csv'
    df = pd.read_csv(filename, index_col=0, parse_dates=True)


    df['SMA_10'] = df['Close'].rolling(window=10).mean() 
    df['SMA_15'] = df['Close'].rolling(window=15).mean()  
    df['SMA_30'] = df['Close'].rolling(window=30).mean()  

    # Criando subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=('Candlestick','Volume'), row_heights=[.7,.3])

    # Gráfico de Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick',
    ), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_10'],
        mode='lines',
        name='SMA 10',
        line=dict(color='#fbcfb7'),
    ), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_15'],
        mode='lines',
        name='SMA 15',
        line=dict(color='#f8ae86'),
    ), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_30'],
        mode='lines',
        name='SMA 30',
        line=dict(color='#f58e56'),
    ), row=1, col=1)

    fig.add_trace(go.Bar(
         x=df.index,
         y=df['Volume'],
         name='Volume',
         marker=dict(color='blue')
    ), row=2, col=1)

    # Atualizando o layout para ter dois eixos y
    fig.update_layout(
        title=symbol,
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis2_title='Data',
        yaxis2_title='Volume',
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=800
    )

    return fig


# Inicializando a aplicação Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


# Layout do aplicativo usando componentes Bootstrap
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.H1("Cripto Analysis", className="text-center text-primary mb-4"), width=12),
                dcc.Dropdown(
                    id='crypto-dropdown',
                    options=generate_options(),
                    value='BTCUSDT',
                    className="dash-bootstrap"
                ),
                html.Button('Reflash', id='update_coin', n_clicks=0),
                dcc.Graph(id='combined-graph', figure=generate_graph_by_symbol('BTCUSDT')),
            ]
        ),
    ],
    fluid=True
)

@callback(
    Output('combined-graph', 'figure', allow_duplicate=True),
    Input('crypto-dropdown', 'value'),
    prevent_initial_call=True
)
def update_titulo(dropdown_value):
    global CACHE_GRAPH

    if dropdown_value is not None:
        CACHE_GRAPH = dropdown_value
        return generate_graph_by_symbol(dropdown_value)
    else:
        return generate_graph_by_symbol(CACHE_GRAPH)


@callback(
    Output('combined-graph', 'figure'),
    Input('update_coin', 'n_clicks')
)
def update_coin(n_clicks):
    global CACHE_GRAPH, COIN_BASE_PATH

    def download(symbol, start):
        
        try:
            binance_data = vbt.BinanceData.download(
                symbol,
                start=start, 
                end='now UTC',
                interval='1h'
            )

            return binance_data.get()
        
        except:
            return []

    start = '7 day ago UTC'
    path = COIN_BASE_PATH.format(CACHE_GRAPH)
    
    try:
        data = pd.read_csv(path, index_col=0, parse_dates=True)
        print(CACHE_GRAPH+" - Dados carregados do arquivo local.")
        
        start = data.index[-1]
        data = pd.concat([data.iloc[:-1], download(CACHE_GRAPH, start)])
        data.to_csv(path)
        print(CACHE_GRAPH+" - Arquivo local atualizado.")

    except:
        
        data = download(CACHE_GRAPH, start)

        if len(data) > 1:
            data.to_csv(path)
            print(CACHE_GRAPH+" - Arquivo local gerado.")

    return generate_graph_by_symbol(CACHE_GRAPH)

# Executando a aplicação
if __name__ == '__main__':
    app.run(debug=True)
