import requests
from bs4 import BeautifulSoup
import time
import asyncio
from telegram import Bot


SLEEP = 10

async def send_message(message):
    bot = Bot(token=API_KEY)

    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)

    except Exception as e:
        print("Ocorreu um erro ao enviar a mensagem: ",e)



def extrair_dados_tabela(html):
    dados = []
    soup = BeautifulSoup(html, 'html.parser')
    linhas = soup.find_all('tr')
    for linha in linhas:
        colunas = linha.find_all('td')
        dados_linha = [coluna.get_text(strip=True) for coluna in colunas]
        dados.append(dados_linha)
    return dados

    

if __name__ == "__main__":
    
    # Chama a função para fazer o login e acessar a página desejada
    with requests.Session() as session:
        try:
            # Faz o login enviando os dados do formulário
            response = session.post(URL_LOGIN, data=DATA_LOGIN)
            
            # Verifica se o login foi bem-sucedido (código de status 200)
            if response.status_code == 200:

                tabela = None

                while True:
                    # Acessa a página desejada após o login
                    response = session.get(URL_DATA_SITE)
                    
                    # Verifica se a página foi acessada com sucesso
                    if response.status_code == 200:
                        # Retorna o conteúdo da página
                        resposta = response.text
                    
                        # Verifica se a resposta foi recebida com sucesso e imprime na tela
                        if resposta:

                            if tabela is None:
                                tabela = extrair_dados_tabela(resposta)

                            else:
                                nova_tabela = extrair_dados_tabela(resposta)

                                set_anterior = set(tuple(linha) for linha in tabela)
                                set_atual = set(tuple(linha) for linha in nova_tabela)

                                diferenca = set_atual - set_anterior

                                resultado = [list(linha) for linha in diferenca]

                                msg = ""
                                for r in resultado:
                                    msg += r[0]+" "+r[6]+" "+r[4]+"\n"
                                    msg += r[1]+" "+r[2]+" "+r[3]


                                    asyncio.run(send_message(msg))

                                for r in tabela[1:5]:                                    

                                    asyncio.run(send_message(r))
                                
                                asyncio.run(send_message("teste line"))

                        else:
                            print("Não foi possível fazer o login e acessar a página desejada.")
                    else:
                        print("Acesso à página falhou com o código de status: ", response.status_code)

                    time.sleep(SLEEP)

            else:
                print("O login falhou com o código de status: ", response.status_code)
        except Exception as e:
            print("Ocorreu um erro durante o processo: ", e)
