import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os

# Regex para extrair dados do CSV (para compatibilidade com formato antigo)
radio_regex = re.compile(r'ID: (\d+) \| Timestamp: (\d+) \| RadioLatency: (\d+) ms')
mqtt_regex = re.compile(r'Radio Latency: (\d+)ms, MQTT Latency: (\d+)ms, Total: (\d+)ms')

def extrair_latencias_radio(arquivo_csv):
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_csv):
        print(f"Arquivo {arquivo_csv} não encontrado")
        return [], []
        
    df = pd.read_csv(arquivo_csv)
    
    # Extrair latência do rádio das linhas de log
    latencias_radio = []
    ids = []
    
    # Verificar se o arquivo é no formato novo (dados_mqtt_dashboard.csv)
    if 'radio_latency' in df.columns:
        # Formato novo - valores diretos
        latencias_radio = df['radio_latency'].dropna().astype(int).tolist()
        ids = list(range(len(latencias_radio)))
    else:
        # Formato antigo - extrair por regex
        for index, row in df.iterrows():
            match = radio_regex.search(str(row['valor']) if 'valor' in df.columns else '')
            if match:
                id_num, timestamp, radio_latency = match.groups()
                latencias_radio.append(int(radio_latency))
                ids.append(int(id_num))
    
    return ids, latencias_radio

def extrair_latencias_mqtt(arquivo_csv):
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_csv):
        print(f"Arquivo {arquivo_csv} não encontrado")
        return [], [], []
        
    df = pd.read_csv(arquivo_csv)
    
    # Extrair latências do MQTT
    latencias_radio = []
    latencias_mqtt = []
    latencias_total = []
    
    # Verificar se o arquivo é no formato novo (dados_mqtt_dashboard.csv)
    if 'mqtt_latency' in df.columns and 'total_latency' in df.columns:
        # Formato novo - valores diretos
        latencias_mqtt = df['mqtt_latency'].dropna().astype(int).tolist()
        latencias_total = df['total_latency'].dropna().astype(int).tolist()
        if 'radio_latency' in df.columns:
            latencias_radio = df['radio_latency'].dropna().astype(int).tolist()
    else:
        # Formato antigo - extrair por regex
        for index, row in df.iterrows():
            valor = str(row['valor']) if 'valor' in df.columns else ''
            match = mqtt_regex.search(valor)
            if match:
                radio_latency, mqtt_latency, total_latency = match.groups()
                latencias_radio.append(int(radio_latency))
                latencias_mqtt.append(int(mqtt_latency))
                latencias_total.append(int(total_latency))
    
    return latencias_radio, latencias_mqtt, latencias_total

def plotar_comparacao_latencias():    # Carregar dados do rádio
    try:
        ids_radio, latencias_radio = extrair_latencias_radio('dados_radio.csv')
        print(f"Dados de rádio: {len(latencias_radio)} amostras")
    except Exception as e:
        print(f"Erro ao carregar dados do rádio: {e}")
        latencias_radio = []
    
    # Tentar carregar dados do MQTT do novo formato
    try:
        _, latencias_mqtt, latencias_total = extrair_latencias_mqtt('dados_mqtt_dashboard.csv')
        print(f"Dados de MQTT (novo formato): {len(latencias_mqtt)} amostras")
    except Exception as e:
        print(f"Erro ao carregar dados do MQTT do novo formato: {e}")
        # Tentar formato antigo
        try:
            _, latencias_mqtt, latencias_total = extrair_latencias_mqtt('dados_mqtt.csv')
            print(f"Dados de MQTT (formato antigo): {len(latencias_mqtt)} amostras")
        except Exception as e:
            print(f"Erro ao carregar dados do MQTT do formato antigo: {e}")
            latencias_mqtt = []
            latencias_total = []
    
    if not latencias_radio and not latencias_mqtt:
        print("Nenhum dado encontrado para análise.")
        return
    
    # Criar figura para o gráfico
    plt.figure(figsize=(12, 8))
    
    # Plotar dados disponíveis
    x_radio = range(len(latencias_radio))
    x_mqtt = range(len(latencias_mqtt))
    
    # Estatísticas
    stats = {}
    
    if latencias_radio:
        plt.plot(x_radio, latencias_radio, 'b-', label='Latência Rádio (ms)')
        stats['radio'] = {
            'min': min(latencias_radio),
            'max': max(latencias_radio),
            'avg': np.mean(latencias_radio),
            'median': np.median(latencias_radio),
            'std': np.std(latencias_radio)
        }
    
    if latencias_mqtt:
        plt.plot(x_mqtt, latencias_mqtt, 'r-', label='Latência MQTT (ms)')
        plt.plot(x_mqtt, latencias_total, 'g-', label='Latência Total (Rádio + MQTT) (ms)')
        stats['mqtt'] = {
            'min': min(latencias_mqtt),
            'max': max(latencias_mqtt),
            'avg': np.mean(latencias_mqtt),
            'median': np.median(latencias_mqtt),
            'std': np.std(latencias_mqtt)
        }
        stats['total'] = {
            'min': min(latencias_total),
            'max': max(latencias_total),
            'avg': np.mean(latencias_total),
            'median': np.median(latencias_total),
            'std': np.std(latencias_total)
        }
    
    # Configurações do gráfico
    plt.title('Comparação de Latências: Rádio vs MQTT')
    plt.xlabel('Número da amostra')
    plt.ylabel('Latência (ms)')
    plt.grid(True)
    plt.legend()
    
    # Imprimir estatísticas
    print("\nEstatísticas de Latência:")
    for key, data in stats.items():
        print(f"\n{key.upper()}:")
        print(f"Mínimo: {data['min']} ms")
        print(f"Máximo: {data['max']} ms")
        print(f"Média: {data['avg']:.2f} ms")
        print(f"Mediana: {data['median']} ms")
        print(f"Desvio Padrão: {data['std']:.2f} ms")
    
    # Salvar e mostrar o gráfico
    plt.savefig('comparacao_latencias.png')
    plt.show()

if __name__ == "__main__":
    plotar_comparacao_latencias()
