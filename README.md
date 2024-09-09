# Cryptocurrency-Analysis
Desenvolver um sistema de análise de criptomoedas, com extenções para servidores.

# Mapa

```plaintext
Futures Cripto/
│
├── README.md                     # Descrição do projeto e instruções de uso
├── requirements.txt              # Lista de dependências do projeto
├── environment.yml               # Arquivo de configuração do ambiente (para conda)
├── .gitignore                    # Arquivo para ignorar arquivos no controle de versão
│
├── app.py                        # Arquivo principal para iniciar a aplicação Dash
│
├── assets/                       # Arquivos estáticos como CSS, JavaScript, imagens
│   ├── style.css                 # Arquivo de estilos customizados
│   └── scripts.js                # Arquivo de scripts JavaScript, se necessário
│
├── dashboards/                   # Diretório para os diferentes dashboards
│   ├── dashboard1.py             # Código para o primeiro dashboard
│   ├── dashboard2.py             # Código para o segundo dashboard
│   └── ...                       # Outros dashboards
│
├── components/                   # Componentes reutilizáveis para os dashboards
│   ├── layout.py                 # Layouts reutilizáveis
│   ├── callbacks.py              # Callbacks reutilizáveis
│   └── utils.py                  # Funções utilitárias
│
├── data/                         # Dados do projeto
│   ├── raw/                      # Dados brutos, não processados
│   └── processed/                # Dados processados, prontos para uso
│
├── notebooks/                    # Notebooks Jupyter para exploração e análises
│   ├── exploracao.ipynb          # Exemplo de notebook de exploração de dados
│   └── ...                       # Outros notebooks
│
├── docs/                         # Documentação adicional do projeto
│   ├── api.md                    # Documentação da API do projeto, se houver
│   └── design_decisions.md       # Decisões de design e arquitetura do projeto
│
└── tests/                        # Testes automatizados
    └── test_dashboard1.py        # Exemplo de arquivo de teste para o primeiro dashboard
