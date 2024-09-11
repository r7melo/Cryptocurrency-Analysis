# components/graph.py
from dash import html, dcc, callback, Output, Input
from plotly.subplots import make_subplots

config_layout_component_graph = {
    'title':dict(
        font=dict(size=20, color='white')  # Cor e tamanho do título
    ),
    'xaxis':dict(
        title='',  # Título do eixo x
        title_font=dict(size=14, color='white'),  # Cor e tamanho do título do eixo x
        type='date',  # Define o tipo de dado como data
        tickformat='%d-%m-%Y %H:%M',  # Formato dos ticks para o eixo de tempo
        tickfont=dict(color='lightgray'),  # Cor das marcações dos ticks
        tickangle=45,  # Ângulo dos ticks para melhor visualização
        gridcolor='gray',  # Cor das linhas de grade verticais
        showline=True,  # Mostra a linha do eixo x
        linecolor='white',  # Cor da linha do eixo x
    ),
    'yaxis':dict(
        title='',  # Título do eixo y
        title_font=dict(size=14, color='white'),  # Cor e tamanho do título do eixo y
        tickfont=dict(color='lightgray'),  # Cor das marcações dos ticks no eixo y
        gridcolor='gray',  # Cor das linhas de grade horizontais
        showline=True,  # Mostra a linha do eixo y
        linecolor='white',  # Cor da linha do eixo y
    ),
    'template':'plotly_dark',  # Tema escuro
    'height':900,
    'legend':dict(
        orientation='h',
        bgcolor='rgba(0,0,0,0.5)',
        bordercolor='white',
        borderwidth=1,
        font=dict(
            size=12,
            color='white'
        )
    )
}

class GraphComponent:
    def __init__(self, update_function=None) -> None:
        self.update_function = update_function
        self.interval_update = 5 # minutos
        self.fig = None
        
        self.graph = html.Div(
            [
                dcc.Graph(id='graph-forex'),
                dcc.Interval(
                    id='interval-graph-forex',
                    interval=self.interval_update*60*1000, 
                    n_intervals=0
                ),
            ], 
            className='graph'
        )

        self.fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[.9, .1])
        self.fig.update_layout(**config_layout_component_graph)
    
    def init_callback(self, app):

        @app.callback(
            Output('graph-forex', 'figure'),
            Input('interval-graph-forex', 'n_intervals')
        )
        def update_graph_forex(n):
            return self.fig