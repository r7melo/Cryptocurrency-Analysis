from dash import Dash
import dash

# Inicializa o aplicativo Dash
app = Dash(__name__, suppress_callback_exceptions=True, use_pages=True)
server = app.server  # Necessário para deploy em algumas plataformas

# Configura o layout principal com suporte a múltiplas páginas
app.layout = dash.page_container

if __name__ == "__main__":
    app.run_server(debug=True, port=80)
