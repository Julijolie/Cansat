import serial
import time
import re
import pandas as pd
import matplotlib.pyplot as plt

# Configuração da porta serial (ajuste conforme necessário)
SERIAL_PORT = 'COM3'  # Altere para a porta correta do seu receptor
BAUDRATE = 9600

# Padrão para extrair latência da saída do Arduino
LATENCIA_REGEX = re.compile(r'RadioLatency: (\d+) ms')
LATENCIA_TRADICIONAL_REGEX = re.compile(r'LatTrad: (\d+) ms')
ID_REGEX = re.compile(r'ID: (\d+)')
TIMESTAMP_REGEX = re.compile(r'Timestamp: (\d+)')
CURRENT_TIME_REGEX = re.compile(r'CurrentTime: (\d+)')

def validar_medicao_latencia():
    print("=== Validador de Medição de Latência ===")
    print(f"Conectando à porta {SERIAL_PORT}...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=5)
        print("Conexão estabelecida!")
        print("\nSendos comandos para ativar testes...")
        
        # Ativar modo de teste
        ser.write(b'L1\n')
        time.sleep(0.5)
        
        # Lista para armazenar medidas
        medidas = []
        
        # Menu de interação
        while True:
            print("\n=== MENU DE TESTES ===")
            print("1. Definir latência artificial")
            print("2. Ativar simulação de overflow")
            print("3. Desativar simulação de overflow")
            print("4. Mostrar configuração atual")
            print("5. Coletar 10 medidas e plotar gráfico")
            print("6. Sair")
            
            opcao = input("\nEscolha uma opção: ")
            
            if opcao == '1':
                latencia = input("Digite a latência artificial em ms (ex: 100): ")
                ser.write(f"A{latencia}\n".encode())
                print(f"Comando enviado: A{latencia}")
                time.sleep(0.5)
                
            elif opcao == '2':
                ser.write(b'O1\n')
                print("Simulação de overflow ATIVADA")
                time.sleep(0.5)
                
            elif opcao == '3':
                ser.write(b'O0\n')
                print("Simulação de overflow DESATIVADA")
                time.sleep(0.5)
                
            elif opcao == '4':
                ser.write(b'S\n')
                time.sleep(0.5)
                # Ler configuração
                print("\nConfiguração atual:")
                for _ in range(10):
                    linha = ser.readline().decode('utf-8', errors='ignore').strip()
                    if linha:
                        print(linha)
                    
            elif opcao == '5':
                # Limpar buffer antes de coletar
                ser.reset_input_buffer()
                
                print("\nColetando 10 medidas...")
                medidas.clear()
                
                # Coleta de dados
                contador = 0
                while contador < 10:
                    linha = ser.readline().decode('utf-8', errors='ignore').strip()
                    if not linha:
                        continue
                        
                    match_id = ID_REGEX.search(linha)
                    match_latencia = LATENCIA_REGEX.search(linha)
                    match_latencia_trad = LATENCIA_TRADICIONAL_REGEX.search(linha)
                    match_timestamp = TIMESTAMP_REGEX.search(linha)
                    match_current = CURRENT_TIME_REGEX.search(linha)
                    
                    if match_id and match_latencia and match_latencia_trad and match_timestamp and match_current:
                        id_msg = int(match_id.group(1))
                        latencia = int(match_latencia.group(1))
                        latencia_trad = int(match_latencia_trad.group(1))
                        timestamp = int(match_timestamp.group(1))
                        current_time = int(match_current.group(1))
                        
                        # Armazenar medida
                        medidas.append({
                            'id': id_msg,
                            'timestamp': timestamp,
                            'current_time': current_time,
                            'latencia': latencia,
                            'latencia_tradicional': latencia_trad
                        })
                        
                        print(f"Medida {contador+1}/10: ID={id_msg}, Latência={latencia}ms, "
                              f"Lat.Tradicional={latencia_trad}ms")
                        contador += 1
                
                # Análise e plot dos resultados
                if medidas:
                    df = pd.DataFrame(medidas)
                    
                    # Criar gráfico comparativo
                    plt.figure(figsize=(10, 6))
                    plt.plot(df['id'], df['latencia'], 'o-', label='Método safeDeltaTime')
                    plt.plot(df['id'], df['latencia_tradicional'], 'x-', label='Método tradicional')
                    plt.xlabel('ID da Mensagem')
                    plt.ylabel('Latência (ms)')
                    plt.title('Comparação dos Métodos de Cálculo de Latência')
                    plt.legend()
                    plt.grid(True)
                    
                    # Calcular diferença entre millis atual e timestamp
                    timestamp_diff = [ct - ts for ct, ts in zip(df['current_time'], df['timestamp'])]
                    print("\nDiferença entre current_time e timestamp:")
                    for id_msg, diff in zip(df['id'], timestamp_diff):
                        print(f"ID={id_msg}, Diferença={diff}")
                    
                    # Salvar gráfico
                    plt.savefig('validacao_latencia.png')
                    plt.show()
                    
                    # Mostrar resumo estatístico
                    print("\nResumo da validação:")
                    print(f"Média latência (safeDeltaTime): {df['latencia'].mean():.2f} ms")
                    print(f"Média latência (tradicional): {df['latencia_tradicional'].mean():.2f} ms")
                    
                    # Verificar casos de overflow detectados
                    overflow_casos = sum(1 for lt, l in zip(df['latencia_tradicional'], df['latencia']) if lt != l)
                    print(f"Casos de overflow detectados: {overflow_casos}")
                    
            elif opcao == '6':
                print("Desativando testes...")
                ser.write(b'L0\n')
                time.sleep(0.5)
                break
            
            else:
                print("Opção inválida. Tente novamente.")
                
    except serial.SerialException as e:
        print(f"Erro ao conectar à porta serial: {e}")
    finally:
        print("Encerrando validador...")
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    validar_medicao_latencia()
