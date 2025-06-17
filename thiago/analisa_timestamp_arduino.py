import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os

# Regex para extrair todos os componentes importantes
arduino_regex = re.compile(r'ID: (\d+) \| Timestamp: (\d+) \| RadioLatency: (\d+) ms')

def analisar_timestamps_arduino(arquivo_csv):
    """
    Analisa os timestamps e latências relatados pelo Arduino para detectar possíveis problemas
    """
    if not os.path.exists(arquivo_csv):
        print(f"Arquivo {arquivo_csv} não encontrado")
        return
        
    df = pd.read_csv(arquivo_csv)
    
    # Extrair dados
    ids = []
    timestamps = []
    latencias = []
    timestamps_sistema = []
    
    for index, row in df.iterrows():
        if 'valor' in df.columns:
            match = arduino_regex.search(str(row['valor']))
            if match:
                id_num, timestamp, radio_latency = match.groups()
                ids.append(int(id_num))
                timestamps.append(int(timestamp))
                latencias.append(int(radio_latency))
                timestamps_sistema.append(float(row['timestamp']))
    
    if not ids:
        print("Nenhum dado encontrado para análise")
        return
        
    # Verificar se há overflow no cálculo de latência
    overflow_count = 0
    for latencia in latencias:
        if latencia > 4000000000:  # Próximo a 2^32
            overflow_count += 1
    
    print(f"\nAnálise de Timestamps do Arduino:")
    print(f"Total de amostras: {len(ids)}")
    print(f"IDs: Min={min(ids)}, Max={max(ids)}")
    print(f"Timestamps Arduino: Min={min(timestamps)}, Max={max(timestamps)}")
    print(f"Latências reportadas: Min={min(latencias)}, Max={max(latencias)}")
    print(f"Número de prováveis overflows: {overflow_count} ({overflow_count/len(latencias)*100:.2f}%)")
    
    # Calcular diferenças entre timestamps consecutivos (Arduino)
    diferenca_arduino = []
    for i in range(1, len(timestamps)):
        diferenca_arduino.append(timestamps[i] - timestamps[i-1])
    
    # Calcular diferenças entre timestamps consecutivos (sistema)
    diferenca_sistema = []
    for i in range(1, len(timestamps_sistema)):
        diferenca_sistema.append((timestamps_sistema[i] - timestamps_sistema[i-1]) * 1000)  # converter para ms
    
    # Calcular latências corrigidas
    latencias_corrigidas = []
    for latencia in latencias:
        if latencia > 4000000000:
            # Corrigir overflow usando complemento de 2^32
            latencia_corrigida = abs(latencia - (1 << 32))
            latencias_corrigidas.append(latencia_corrigida)
        else:
            latencias_corrigidas.append(latencia)
    
    # Criar figura
    plt.figure(figsize=(12, 12))
    
    # Gráfico de timestamps do Arduino
    plt.subplot(3, 1, 1)
    plt.plot(ids, timestamps, 'b-', marker='o')
    plt.title('Timestamps do Arduino')
    plt.xlabel('ID da mensagem')
    plt.ylabel('Timestamp (ms)')
    plt.grid(True)
    
    # Gráfico de intervalos entre mensagens
    plt.subplot(3, 1, 2)
    plt.plot(ids[1:], diferenca_arduino, 'g-', marker='o', label='Arduino')
    plt.plot(ids[1:], diferenca_sistema[:len(diferenca_arduino)], 'r-', marker='x', label='Sistema')
    plt.title('Intervalo entre Mensagens Consecutivas')
    plt.xlabel('ID da mensagem')
    plt.ylabel('Intervalo (ms)')
    plt.legend()
    plt.grid(True)
    
    # Gráfico de latências
    plt.subplot(3, 1, 3)
    plt.plot(ids, latencias_corrigidas, 'r-', marker='o')
    plt.title('Latências Corrigidas')
    plt.xlabel('ID da mensagem')
    plt.ylabel('Latência (ms)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('analise_timestamps_arduino.png')
    plt.show()
    
    print("\nLatências corrigidas:")
    print(f"Mínimo: {min(latencias_corrigidas)} ms")
    print(f"Máximo: {max(latencias_corrigidas)} ms")
    print(f"Média: {np.mean(latencias_corrigidas):.2f} ms")
    print(f"Mediana: {np.median(latencias_corrigidas):.2f} ms")
    
    return latencias_corrigidas

if __name__ == "__main__":
    analisar_timestamps_arduino('dados_radio.csv')
