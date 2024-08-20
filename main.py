from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, html, ctx,  dcc, callback
import os

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
    fig = go.Figure()

    # Gráfico de Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick',
        yaxis='y1'
    ))

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_10'],
        mode='lines',
        name='SMA 10',
        line=dict(color='#fbcfb7'),
        yaxis='y1'
    ))

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_15'],
        mode='lines',
        name='SMA 15',
        line=dict(color='#f8ae86'),
        yaxis='y1'
    ))

    # Adicionando média móvel
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_30'],
        mode='lines',
        name='SMA 30',
        line=dict(color='#f58e56'),
        yaxis='y1'
    ))

    # Atualizando o layout para ter dois eixos y
    fig.update_layout(
        title=symbol,
        xaxis_title='Date',
        yaxis_title='Price',
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right'
        ),
        template='plotly_dark'
    )

    return fig

# Inicializando a aplicação Dash
app = Dash(__name__)

# Layout da aplicação
app.layout = html.Div(children=[
    html.H1(children='Cripto Analysis', id="titulo"),
    dcc.Dropdown(
        id='crypto-dropdown',
        options=generate_options(),
        value='BTCUSDT' 
    ),
    dcc.Graph(
        id='combined-graph',
        figure=generate_graph_by_symbol('BTCUSDT')
    )
])

@callback(
    Output('combined-graph', 'figure'),
    Input('crypto-dropdown', 'value'),
    prevent_initial_call=True
)
def update_titulo(dropdown_value):
    tgg = ctx.triggered_id

    if tgg == 'crypto-dropdown' and tgg is not None:
        return generate_graph_by_symbol(dropdown_value)


# Executando a aplicação
if __name__ == '__main__':
    app.run(debug=True)
