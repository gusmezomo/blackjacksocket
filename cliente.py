import socket

host = '127.0.0.1'  # IP do servidor
port = 12345  # Porta do servidor

#Conectando ao servidor 
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((host, port))

while True:
    # Receber mensagens do servidor
    mensagem = cliente.recv(1024).decode()

    if not mensagem:
        break

    print(mensagem)

    # Responder quando chamado
    if "Quanto deseja apostar?" in mensagem:
        aposta = input("Digite sua aposta: ")
        cliente.send(aposta.encode())
    elif "Deseja pedir" in mensagem or "Desejam continuar" in mensagem:
        resposta = input("Sua resposta: ")
        cliente.send(resposta.encode())

# Fechar conexão
cliente.close()
