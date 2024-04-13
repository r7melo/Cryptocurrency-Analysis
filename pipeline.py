import queue
import threading

def processar_elemento(elemento):
    return elemento * 2  # Exemplo: dobrar o valor

def processar_lista(entrada, saida, porcentagem):
    while True:
        elemento = entrada.get()  # Obter elemento da entrada
        if elemento is None:  # Verificar se é o sinal de parada
            saida.put(None)  # Passar o sinal de parada para a próxima thread
            break
        resultado = processar_elemento(elemento)  # Processar o elemento
        saida.put(resultado)  # Passar o resultado para a próxima thread
        porcentagem[0] += 1  # Atualizar a porcentagem

def processamento_paralelo(lista):
    num_elementos = len(lista)
    num_threads = num_elementos

    # Inicializar as filas
    queues = [queue.Queue() for _ in range(num_threads)]

    # Iniciar as threads
    threads = []
    porcentagem = [0]  # Para armazenar o número de elementos processados
    for i in range(num_threads):
        t = threading.Thread(target=processar_lista, args=(queues[i], queues[(i + 1) % num_threads], porcentagem))
        threads.append(t)
        t.start()

    # Passar os elementos para a primeira fila no pipeline
    for elemento in lista:
        queues[0].put(elemento)

    # Aguardar a conclusão de todas as threads
    for t in threads:
        t.join()

    # Coletar os resultados da última fila no pipeline
    resultado = [queues[-1].get() for _ in range(num_elementos)]

    return resultado

# Lista de exemplo com 500 elementos
minha_lista = list(range(1, 501))

# Processar a lista em paralelo
resultado = processamento_paralelo(minha_lista)

print("Resultado do processamento em paralelo:", resultado)
