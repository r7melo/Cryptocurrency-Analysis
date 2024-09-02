from dash import dcc, html
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, Input, Output, html,  dcc, callback, dash_table
from coin_manage import CoinManage, Coin
import numpy as np
import asyncio

CACHE_GRAPH = Coin()

def generate_options():
    return [{'label': coin.name, 'value': coin.name} for coin in CoinManage.get_coin_list()]
        
def generate_graph_by_symbol(coin:Coin = CACHE_GRAPH):

    df = coin.get_df()

    df['Percentual'] = ((df['Close'] - df['Open']) / df['Open']) * 100

    df['SMA_10'] = df['Close'].rolling(window=10).mean() 
    df['SMA_15'] = df['Close'].rolling(window=15).mean()  
    df['SMA_30'] = df['Close'].rolling(window=30).mean()  

    # Criando subplots
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[.5,.3, .2])

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

    fig.add_trace(go.Bar(
         x=df.index,
         y=df['Percentual'],
         name='Percentual',
         marker=dict(color='red')
    ), row=3, col=1)

    # Atualizando o layout para ter dois eixos y
    fig.update_layout(
        title=coin.name,
        xaxis_title=' ',
        yaxis_title='Price',
        xaxis2_title=' ',
        yaxis2_title='Volume',
        xaxis3_title=' ',
        yaxis3_title='%',
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=800
    )

    return fig


async def calculate_variation(coin):
    df = await asyncio.to_thread(coin.get_df)
    vd = np.nan
    
    if len(df) > 30:
        i0 = df['Open'].iloc[-24]
        i1 = df['Close'].iloc[-1]
        vd = ((i1 - i0) / i0) * 100

    return coin.name, vd

async def generate_data_table():
    coin_list = CoinManage.get_coin_list()
    tasks = [calculate_variation(coin) for coin in coin_list]
    results = await asyncio.gather(*tasks)
    
    # Separando os resultados
    symbols, variations = zip(*results)
    
    # Criando o DataFrame
    result_df = pd.DataFrame({
        'Symbol': symbols,
        'Variation Day': variations
    })
    
    return result_df.sort_values(by='Variation Day', ascending=False)

def get_data_table_sync():
    async def async_wrapper():
        return await generate_data_table()

    return asyncio.run(async_wrapper())

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

@callback(
    Output('combined-graph', 'figure', allow_duplicate=True),
    Input('crypto-dropdown', 'value'),
    prevent_initial_call=True
)
def update_graph(dropdown_value):
    global CACHE_GRAPH

    if dropdown_value is not None:
        CACHE_GRAPH = Coin(dropdown_value)

    return generate_graph_by_symbol(CACHE_GRAPH)


@callback(
    Output('combined-graph', 'figure'),
    Input('update_coin', 'n_clicks')
)
def reflash_coin(n_clicks):
    global CACHE_GRAPH

    if n_clicks > 0:
        CoinManage.update_coin(CACHE_GRAPH)
    
    return generate_graph_by_symbol(CACHE_GRAPH)

# Callback para atualizar a tabela
@app.callback(
    Output('data-table', 'data'),
    [Input('reload-button', 'n_clicks')]
)
def update_table(n_clicks):
    df = get_data_table_sync()
    return df.to_dict('records')

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                # SELECT COIN - REFLASH COIN
                dbc.Col(
                    dcc.Dropdown(
                        id='crypto-dropdown',
                        options=generate_options(),
                        value='BTCUSDT',
                        className="dash-bootstrap"
                    ),
                    width=10
                ),
                dbc.Col(
                    html.Button('Reflash', id='update_coin', n_clicks=0),
                    width=2
                ),            
            ]
        ),
        dbc.Row(
            [
                # GRAPH COIN
                dcc.Graph(id='combined-graph', figure=generate_graph_by_symbol()),
            ]
        ),
        html.Div(
            dash_table.DataTable(
                id='data-table',
                page_size=10,  # Define o número de linhas por página
                style_table={'width': '100%', 'overflowX': 'auto'},  # Para garantir a rolagem horizontal se necessário
                style_data={'whiteSpace': 'normal', 'height': 'auto'},
            ),
            style={'display': 'flex', 'justifyContent': 'center'}
        ),
        html.Div(
            html.Button('Recarregar Dados', id='reload-button', n_clicks=0),
            style={'display': 'flex', 'justifyContent': 'center'}
        ),
        
    ], 
    fluid=True
)


if __name__ == '__main__':

    app.run(debug=True)
