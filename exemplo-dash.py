import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

# Dados de exemplo (substitua pelos seus dados reais)
data = {
    'Data': pd.date_range(start='2024-01-01', periods=10, freq='D'),
    'Abertura': [100, 105, 110, 108, 107, 112, 115, 118, 120, 125],
    'Alta': [105, 110, 115, 112, 110, 115, 118, 121, 125, 130],
    'Baixa': [95, 100, 105, 104, 103, 110, 113, 116, 118, 122],
    'Fechamento': [102, 108, 110, 106, 109, 113, 117, 119, 123, 128],
    'Volume': [1000, 1500, 2000, 1800, 1600, 2200, 2100, 2300, 2500, 2700]
}
df = pd.DataFrame(data)

# Inicializar o aplicativo Dash
app = dash.Dash(__name__)

# Criar subplots
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    subplot_titles=('Candlestick', 'Volume'),
                    row_heights=[0.7, 0.3])

# Adicionar gráfico de candlestick
fig.add_trace(go.Candlestick(
    x=df['Data'],
    open=df['Abertura'],
    high=df['Alta'],
    low=df['Baixa'],
    close=df['Fechamento'],
    name='Candlestick'
), row=1, col=1)

# Adicionar gráfico de volume
fig.add_trace(go.Bar(
    x=df['Data'],
    y=df['Volume'],
    name='Volume',
    marker=dict(color='blue')
), row=2, col=1)

# Atualizar layout do gráfico
fig.update_layout(
    title='Candlestick e Volume',
    xaxis_title='Data',
    yaxis_title='Preço',
    xaxis2_title='Data',
    yaxis2_title='Volume',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_rangeslider_visible=False,
    height=800  # Ajuste a altura total do gráfico conforme necessário
)

app.layout = html.Div([
    html.H1('Gráfico de Candlestick e Volume'),
    dcc.Graph(
        id='candlestick-volume-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
