from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, html, ctx,  dcc, callback

def generate_graph_by_symbol(symbol):

    filename = f'C:/CoinsBase/{symbol}.csv'
    df = pd.read_csv(filename, index_col=0, parse_dates=True)


    df['SMA_10'] = df['Close'].rolling(window=10).mean()  # Média móvel de 10 períodos

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
        line=dict(color='orange'),
        yaxis='y1'
    ))

    # Atualizando o layout para ter dois eixos y
    fig.update_layout(
        title='Bitcoin Market Dashboard',
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
    html.H1(children='Bitcoin Market Dashboard', id="titulo"),
    html.Button('COIN 1', id='coin1'),
    html.Button('COIN 2', id='coin2'),
    dcc.Graph(
        id='combined-graph',
        figure=generate_graph_by_symbol('BTCUSDT')
    )
])

@callback(
    Output('combined-graph', 'figure'),
    Input('coin1', 'n_clicks'),
    Input('coin2', 'n_clicks'),
    prevent_initial_call=True
)
def update_titulo(b1, b2):
    tgg = ctx.triggered_id
    print(tgg)

    if tgg == 'coin1':
        return generate_graph_by_symbol('BTCUSDT')
    elif tgg == 'coin2':
        return generate_graph_by_symbol('BBUSDT')


# Executando a aplicação
if __name__ == '__main__':
    app.run(debug=True)
