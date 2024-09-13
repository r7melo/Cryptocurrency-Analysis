import os
from datetime import datetime

class Logger:
    log_directory = "logs"  # Diretório onde os logs serão salvos

    @staticmethod
    def log(message: str, ex: Exception = None):
        # Obtém a data atual no formato YYYY-MM-DD
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Define o nome do arquivo de log com a data atual
        log_filename = f"{current_date}.log"
        
        # Verifica se o diretório de logs existe, se não, cria
        if not os.path.exists(Logger.log_directory):
            os.makedirs(Logger.log_directory)
        
        # Caminho completo para o arquivo de log
        log_path = os.path.join(Logger.log_directory, log_filename)
        
        # Monta a mensagem de log
        log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}"
        
        # Adiciona a mensagem da exceção se houver
        if ex:
            log_message += f" | Exception: {str(ex)}"
        
        # Escreve a mensagem de log no arquivo
        with open(log_path, "a", encoding='utf-8') as log_file:
            log_file.write(log_message + "\n")
