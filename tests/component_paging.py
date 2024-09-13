import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Inicialize o app
app = dash.Dash(__name__)

# Layout do app
app.layout = html.Div([
    html.Button('Anterior', id='btn-prev', n_clicks=0),
    html.Label(id='page-label', children='Página 1'),
    html.Button('Próximo', id='btn-next', n_clicks=0),
])

# Callback para atualizar o rótulo da página
@app.callback(
    Output('page-label', 'children'),
    [Input('btn-prev', 'n_clicks'),
     Input('btn-next', 'n_clicks')]
)
def update_page(btn_prev, btn_next):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'btn-next'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Inicializa a página com base nos cliques dos botões
    if button_id == 'btn-next':
        update_page.current_page += 1
    elif button_id == 'btn-prev':
        update_page.current_page -= 1

    return f'Página {update_page.current_page}'

# Variável para armazenar a página atual
update_page.current_page = 1

if __name__ == '__main__':
    app.run_server(debug=True)
