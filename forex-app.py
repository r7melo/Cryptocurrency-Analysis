import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, Input, Output, html,  dcc, callback, dash_table
from coin_manage import CoinManage, Coin
import numpy as np
import asyncio

CACHE_GRAPH_FOREX = Coin("EURUSD")

def generate_options(context):
    return [{'label': coin.name, 'value': coin.name} for coin in CoinManage.get_coin_list(context)]
        
def generate_graph_by_symbol(coin:Coin):

    df = coin.get_df()[-900:]

    df['Percentual'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    df['MP'] = df['Percentual'].rolling(window=30).mean() * 10

    df['SMA_10'] = df['Close'].rolling(window=10).mean() 
    df['SMA_15'] = df['Close'].rolling(window=15).mean()  
    df['SMA_30'] = df['Close'].rolling(window=30).mean()  
    df['EMA_9'] = ((df['Close']+df['Open'])/2).ewm(span=9, adjust=False).mean()


    df['LOSS_BUY'] = (df['Low'].shift(-9).rolling(window=9).min()).shift(9)
    df['LOSS_SELL'] = (df['High'].shift(-9).rolling(window=9).max()).shift(9)

    # Criando subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[.9, .1])

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
        visible='legendonly'
    ), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_15'],
        mode='lines',
        name='SMA 15',
        line=dict(color='#f8ae86'),
        visible='legendonly'

    ), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_30'],
        mode='lines',
        name='SMA 30',
        line=dict(color='#f58e56'),
        visible='legendonly'
    ), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['LOSS_BUY'],
        mode='lines',
        name='LOSS_BUY',
        line=dict(color='#030'),
    ), row=1, col=1)

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['LOSS_SELL'],
        mode='lines',
        name='LOSS_SELL',
        line=dict(color='#300'),
    ), row=1, col=1)


    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['EMA_9'],
        mode='lines',
        name='EMA 9',
        line=dict(color='#1bf'),
    ), row=1, col=1)

    # Atualizando o layout para ter dois eixos y
    fig.update_layout(
        title=coin.name,
        xaxis_title=' ',
        yaxis_title='Price',
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=500,
        legend=dict(
            orientation='h',      # Define a orientação da legenda como horizontal
            bgcolor='rgba(0,0,0,0.5)',  # Cor de fundo semitransparente
            bordercolor='white',
            borderwidth=1,
            font=dict(
                size=12,
                color='white'
            )
        )
    )

    return fig


async def calculate_variation(coin:Coin):
    df = await asyncio.to_thread(coin.get_df)
    if df is not None:

        vd = np.nan
        
        if len(df) > 30:
            i0 = df['Open'].iloc[-24]
            i1 = df['Close'].iloc[-1]
            vd = ((i1 - i0) / i0) * 100

       
        return coin.name, vd

    else:
        return coin.name, 0, 0, 0, 0, 0, 0

async def generate_data_table(context):
    coin_list = CoinManage.get_coin_list(context)
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

def get_data_table_async(context):
    async def async_wrapper():
        return await generate_data_table(context)

    return asyncio.run(async_wrapper())

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

#region FOREX
@callback(
    Output('combined-graph-forex', 'figure', allow_duplicate=True),
    Input('forex-dropdown', 'value'),
    prevent_initial_call=True
)
def update_graph(dropdown_value):
    global CACHE_GRAPH_FOREX

    if dropdown_value is not None:
        aux = Coin(dropdown_value)
        if aux.get_df() is not None:
            CACHE_GRAPH_FOREX = aux

    return generate_graph_by_symbol(CACHE_GRAPH_FOREX)


@callback(
    Output('combined-graph-forex', 'figure'),
    Input('update_coin_forex', 'n_clicks')
)
def reflash_coin_forex(n_clicks):
    global CACHE_GRAPH_FOREX

    if n_clicks > 0:
        CoinManage.update_coin(CACHE_GRAPH_FOREX)
    
    return generate_graph_by_symbol(CACHE_GRAPH_FOREX)

# Callback para atualizar a tabela
@app.callback(
    Output('data-table-forex', 'data'),
    [Input('reload-button-forex', 'n_clicks')]
)
def update_table_forex(n_clicks):
    df = get_data_table_async("FOREX")
    return df.to_dict('records')
#endregion


app.layout = dbc.Container(
    [

        # FOREX
        dbc.Row(
            [
                # SELECT COIN - REFLASH COIN
                dbc.Col(
                    dcc.Dropdown(
                        id='forex-dropdown',
                        options=generate_options("FOREX"),
                        value='EURUSD',
                        className="dash-bootstrap"
                    ),
                    width=10
                ),
                dbc.Col(
                    html.Button('Reflash', id='update_coin_forex', n_clicks=0),
                    width=2
                ),            
            ]
        ),
        dbc.Row(
            [
                # GRAPH COIN
                dcc.Graph(id='combined-graph-forex', figure=generate_graph_by_symbol(CACHE_GRAPH_FOREX)),
            ]
        ),
        html.Div(
            dash_table.DataTable(
                id='data-table-forex',
                page_size=10,  # Define o número de linhas por página
                style_table={
                        'width': '100%',  # Largura fixa
                        'height': '400px',  # Altura fixa
                        'overflowX': 'auto',  # Adiciona rolagem horizontal se necessário
                        'overflowY': 'auto'   # Adiciona rolagem vertical se necessário
                    }, 
                style_cell={'textAlign': 'left'},  # Alinha o texto à esquerda
            )
        ),
        html.Div(
            html.Button('Recarregar Dados', id='reload-button-forex', n_clicks=0),
            style={'display': 'flex', 'justifyContent': 'center'}
        ),
        
    ], 
    fluid=True
)


if __name__ == '__main__':

   app.run(debug=False, host='0.0.0.0', port=80)
