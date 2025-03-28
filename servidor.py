import socket
import random

# Função que gera cartas aleatórias (apenas os valores numéricos)
def gerar_carta():
    carta = random.randint(1, 13)
    if carta > 10:
        return 10  # J, Q, K valem 10
    elif carta == 1:
        return 11  # Ás começa valendo 11, mas pode mudar para 1
    return carta

# Função que calcula o valor total das cartas dos jogadores (com a mecânica do ás)
def calcular_total(cartas):
    total = sum(cartas)
    num_ases = cartas.count(11)
    
    while total > 21 and num_ases > 0:
        total -= 10  # Converte um Ás de 11 para 1
        num_ases -= 1

    return total

# Configuração do TCP do servidor 
host = '127.0.0.1'  # Endereço IP do servidor (localhost)
port = 12345  # Porta para o servidor

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((host, port))
servidor.listen(2)

print("Aguardando dois jogadores...")

# Aceitando a conexão dos jogadores
cliente1, addr1 = servidor.accept()
print(f"Jogador 1 conectado: {addr1}")

cliente2, addr2 = servidor.accept()
print(f"Jogador 2 conectado: {addr2}")

# Saldo inicial dos jogadores
saldo_jogador1 = 100
saldo_jogador2 = 100

# Função para enviar mensagens para ambos os jogadores
def enviar_para_ambos(mensagem):
    cliente1.send(mensagem.encode())
    cliente2.send(mensagem.encode())

# Função para o servidor (host) jogar como dealer
def jogar_como_host():
    cartas_host = [gerar_carta(), gerar_carta()]
    total_host = calcular_total(cartas_host)
    
    while total_host < 17:
        cartas_host.append(gerar_carta())
        total_host = calcular_total(cartas_host)
    
    return cartas_host, total_host

# Função para as rodadas dos jogadores
def rodada_jogador(cliente, jogador_num):
    cartas_jogador = [gerar_carta(), gerar_carta()]
    cliente.send(f"Suas cartas iniciais: {cartas_jogador}, total: {calcular_total(cartas_jogador)}\n".encode())
    
    while calcular_total(cartas_jogador) < 21:
        cliente.send("Deseja pedir mais uma carta (hit) ou parar (stand)? (h/s)\n".encode())
        resposta = cliente.recv(1024).decode().strip().lower()

        if resposta == 'h':
            cartas_jogador.append(gerar_carta())
            total_jogador = calcular_total(cartas_jogador)
            cliente.send(f"Suas cartas: {cartas_jogador}, total: {total_jogador}\n".encode())

            if total_jogador > 21:
                cliente.send("Você estourou (busted)!\n".encode())
                break
        elif resposta == 's':
            break

    return cartas_jogador, calcular_total(cartas_jogador)

# Loop onde ocorre o jogo
while True:
    enviar_para_ambos("\n=== Nova rodada de Blackjack ===\n")

    # Print do saldo atual de cada jogador
    cliente1.send(f"Seu saldo atual: {saldo_jogador1}\n".encode())
    cliente2.send(f"Seu saldo atual: {saldo_jogador2}\n".encode())

    # Aposta dos jogadores 
    cliente1.send("Quanto deseja apostar?\n".encode())
    aposta_jogador1 = int(cliente1.recv(1024).decode().strip())

    cliente2.send("Quanto deseja apostar?\n".encode())
    aposta_jogador2 = int(cliente2.recv(1024).decode().strip())

    # Rodada do Dealer
    cartas_host, total_host = jogar_como_host()

    # Mostrar a primeira carta do dealer no início da rodada
    enviar_para_ambos(f"Primeira carta do Dealer: {cartas_host[0]}\n")

    # Rodada do Jogador 1
    cartas_jogador1, total_jogador1 = rodada_jogador(cliente1, 1)

    # Rodada do Jogador 2
    cartas_jogador2, total_jogador2 = rodada_jogador(cliente2, 2)

    # Mostrar as cartas completas do dealer ao final da rodada
    enviar_para_ambos(f"\nCartas do Dealer: {cartas_host}, total: {total_host}\n")

    # Verificar o estado de cada jogador antes de considerar o dealer (para não considerar um jogador estourado vencedor)
    jogador1_estourou = total_jogador1 > 21
    jogador2_estourou = total_jogador2 > 21

    # Anunciar o resultado para o jogador 1
    if jogador1_estourou:
        cliente1.send(f"Você estourou e perdeu {aposta_jogador1}!\n".encode())
        saldo_jogador1 -= aposta_jogador1
    else:
        if total_host > 21 or total_jogador1 > total_host:
            cliente1.send(f"Você venceu o Dealer e ganhou {aposta_jogador1 * 2}!\n".encode())
            saldo_jogador1 += aposta_jogador1 * 2
        else:
            cliente1.send(f"Você perdeu para o Dealer e perdeu {aposta_jogador1}!\n".encode())
            saldo_jogador1 -= aposta_jogador1

    # Anunciar o resultado para o jogador 2
    if jogador2_estourou:
        cliente2.send(f"Você estourou e perdeu {aposta_jogador2}!\n".encode())
        saldo_jogador2 -= aposta_jogador2
    else:
        if total_host > 21 or total_jogador2 > total_host:
            cliente2.send(f"Você venceu o Dealer e ganhou {aposta_jogador2 * 2}!\n".encode())
            saldo_jogador2 += aposta_jogador2 * 2
        else:
            cliente2.send(f"Você perdeu para o Dealer e perdeu {aposta_jogador2}!\n".encode())
            saldo_jogador2 -= aposta_jogador2

    # Verificar se os jogadores desejam continuar jogando
    enviar_para_ambos("Desejam continuar jogando? (s/n)\n")
    resposta1 = cliente1.recv(1024).decode().strip().lower()
    resposta2 = cliente2.recv(1024).decode().strip().lower()

    if resposta1 != 's' or resposta2 != 's':
        break

# Fechar conexões
cliente1.close()
cliente2.close()
servidor.close()
