import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os

# Script corrigido para usar os dados reais de latência do rádio
# sem substituição por dados simulados

# Regex para extrair dados do CSV de acordo com o formato atual do dados_radio.csv
radio_regex = re.compile(r'ID: (\d+) \| Timestamp: (\d+) \| Intervalo: \d+ ms \| RadioLatency: (\d+) ms')
mqtt_regex = re.compile(r'Radio Latency: (\d+)ms, MQTT Latency: (\d+)ms, Total: (\d+)ms')

def extrair_latencias_radio(arquivo_csv):
    """
    Extrai as latências do rádio a partir do arquivo CSV.
    Suporta tanto o formato novo quanto o antigo.
    """
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_csv):
        print(f"Arquivo {arquivo_csv} não encontrado")
        return [], []
    
    try:
        df = pd.read_csv(arquivo_csv)
        
        # Extrair latência do rádio das linhas de log
        latencias_radio = []
        ids = []
        
        # Verificar se o arquivo é no formato novo (dados_mqtt_dashboard.csv)
        if 'radio_latency' in df.columns:
            print(f"Usando formato novo de dados (coluna radio_latency) do arquivo {arquivo_csv}")
            # Formato novo - valores diretos
            latencias_radio_raw = df['radio_latency'].dropna().astype(int).tolist()
            ids = list(range(len(latencias_radio_raw)))
            
            # Corrigir overflow do unsigned long no Arduino
            # Se o valor é muito grande (próximo a 2^32), significa que houve underflow
            # na subtração do timestamp no Arduino
            for val in latencias_radio_raw:
                if val > 4000000000:  # Valor próximo a 2^32 indica overflow
                    # Corrigir o overflow: real = 2^32 - val (inverte o underflow)
                    corrigido = val - (1 << 32)
                    latencias_radio.append(abs(corrigido))
                else:
                    latencias_radio.append(val)
        else:
            print(f"Usando formato antigo de dados (regex na coluna valor) do arquivo {arquivo_csv}")
            print("Procurando por padrão: 'ID: X | Timestamp: X | ... | RadioLatency: X ms'")
            
            # Formato antigo - extrair por regex
            for index, row in df.iterrows():
                # Converter para string se necessário e verificar se a coluna 'valor' existe
                if 'valor' in df.columns:
                    valor = str(row['valor'])
                    
                    # Usar regex para capturar RadioLatency
                    match = radio_regex.search(valor)
                    if match:
                        id_num, timestamp, radio_latency = match.groups()
                        radio_latency_val = int(radio_latency)
                        
                        # Corrigir overflow se necessário
                        if radio_latency_val > 4000000000:
                            radio_latency_val = abs(radio_latency_val - (1 << 32))
                        
                        latencias_radio.append(radio_latency_val)
                        ids.append(int(id_num))
                    else:
                        # Tentar regex mais genérica
                        generic_regex = re.compile(r'RadioLatency: (\d+) ms')
                        match = generic_regex.search(valor)
                        if match:
                            radio_latency = match.group(1)
                            radio_latency_val = int(radio_latency)
                            
                            if radio_latency_val > 4000000000:
                                radio_latency_val = abs(radio_latency_val - (1 << 32))
                            
                            latencias_radio.append(radio_latency_val)
                            ids.append(index)  # Usar índice como ID
        
        print(f"Extraídas {len(latencias_radio)} latências do arquivo {arquivo_csv}")
        print(f"Faixa de valores: mín={min(latencias_radio) if latencias_radio else 'N/A'}, " +
              f"máx={max(latencias_radio) if latencias_radio else 'N/A'}, " +
              f"média={np.mean(latencias_radio) if latencias_radio else 'N/A'}")
                
        return ids, latencias_radio
        
    except Exception as e:
        print(f"Erro ao extrair latências do arquivo {arquivo_csv}: {e}")
        return [], []

def extrair_latencias_mqtt(arquivo_csv):
    """
    Extrai latências de MQTT do arquivo CSV.
    Retorna listas de latências do rádio, MQTT e total.
    """
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_csv):
        print(f"Arquivo {arquivo_csv} não encontrado")
        return [], [], []
    
    try:
        df = pd.read_csv(arquivo_csv)
        
        # Verificar se estamos usando o formato novo
        if all(col in df.columns for col in ['radio_latency', 'mqtt_latency', 'total_latency']):
            print(f"Usando formato novo de dados de MQTT do arquivo {arquivo_csv}")
            
            # Extrair latências
            radio_latency = df['radio_latency'].dropna().tolist()
            mqtt_latency = df['mqtt_latency'].dropna().tolist()
            total_latency = df['total_latency'].dropna().tolist()
            
            # Cortar para garantir mesmo comprimento
            min_len = min(len(radio_latency), len(mqtt_latency), len(total_latency))
            radio_latency = radio_latency[:min_len]
            mqtt_latency = mqtt_latency[:min_len]
            total_latency = total_latency[:min_len]
            
            return radio_latency, mqtt_latency, total_latency
        
        # Se chegamos aqui, tentar o formato antigo usando regex
        print(f"Tentando formato antigo de dados de MQTT do arquivo {arquivo_csv}")
        
        radio_latencias = []
        mqtt_latencias = []
        total_latencias = []
        
        for index, row in df.iterrows():
            if 'valor' in df.columns:
                valor = str(row['valor'])
                match = mqtt_regex.search(valor)
                if match:
                    radio_latencia, mqtt_latencia, total_latencia = map(int, match.groups())
                    radio_latencias.append(radio_latencia)
                    mqtt_latencias.append(mqtt_latencia)
                    total_latencias.append(total_latencia)
        
        return radio_latencias, mqtt_latencias, total_latencias
        
    except Exception as e:
        print(f"Erro ao extrair latências MQTT do arquivo {arquivo_csv}: {e}")
        return [], [], []

def plotar_comparacao_latencias():
    """
    Plota a comparação de latências entre Rádio e MQTT.
    Utiliza SEMPRE os dados reais do arquivo dados_radio.csv para o rádio.
    """
    # Usar sempre o arquivo dados_radio.csv para extrair as latências do rádio
    arquivo_radio = 'dados_radio.csv'
      
    try:
        # Extrair as latências reais do rádio (sem simulação)
        ids_radio, latencias_radio = extrair_latencias_radio(arquivo_radio)
        print(f"Dados reais do rádio (de {arquivo_radio}): {len(latencias_radio)} amostras")
        
        if not latencias_radio:
            raise ValueError(f"Não foi possível extrair latências reais do arquivo {arquivo_radio}")
        
        # Imprimir estatísticas para diagnóstico
        print(f"Estatísticas de latência do rádio:")
        print(f"Mínimo: {min(latencias_radio)}ms")
        print(f"Máximo: {max(latencias_radio)}ms")
        print(f"Média: {np.mean(latencias_radio):.2f}ms")
        print(f"Mediana: {np.median(latencias_radio)}ms")
        
    except Exception as e:
        print(f"Erro ao carregar dados reais do rádio: {str(e)}")
        return
    
    # Tentar carregar dados do MQTT
    latencias_mqtt = []
    latencias_total = []
    
    try:
        # Tentar o formato mais recente primeiro (dados_mqtt_dashboard.csv)
        arquivo_mqtt = 'dados_mqtt_dashboard.csv'
        radio_latencias_mqtt, latencias_mqtt, latencias_total = extrair_latencias_mqtt(arquivo_mqtt)
        print(f"Dados de MQTT (novo formato): {len(latencias_mqtt)} amostras")
        
        if not latencias_mqtt:
            raise ValueError("Nenhum dado de latência MQTT encontrado")
            
        # Verificar valores extremos de latências e corrigir
        latencias_mqtt_filtradas = []
        for latencia in latencias_mqtt:
            # Filtrar valores irrealistas (muito grandes ou negativos)
            if 0 <= latencia <= 500:  # 500ms como limite superior razoável
                latencias_mqtt_filtradas.append(latencia)
            else:
                print(f"Valor de latência MQTT fora do limite: {latencia}ms - substituindo por 15ms")
                latencias_mqtt_filtradas.append(15)  # ~15ms é típico para MQTT local
        
        latencias_mqtt = latencias_mqtt_filtradas
        
        # IMPORTANTE: Recalcular latências totais usando as latências de rádio REAIS
        latencias_total = []
        for i in range(min(len(latencias_radio), len(latencias_mqtt))):
            latencias_total.append(latencias_radio[i] + latencias_mqtt[i])
        
    except Exception as e:
        print(f"Erro ao carregar dados do MQTT do novo formato: {e}")
        # Tentar formato antigo
        try:
            arquivo_mqtt = 'dados_mqtt.csv'
            radio_latencias_mqtt, latencias_mqtt, latencias_total = extrair_latencias_mqtt(arquivo_mqtt)
            print(f"Dados de MQTT (formato antigo): {len(latencias_mqtt)} amostras")
            
            if not latencias_mqtt:
                raise ValueError("Nenhum dado de latência MQTT encontrado no formato antigo")
                
            # Verificar valores extremos das latências
            latencias_mqtt_filtradas = []
            for latencia in latencias_mqtt:
                # Filtrar valores irrealistas
                if 0 <= latencia <= 500:
                    latencias_mqtt_filtradas.append(latencia)
                else:
                    latencias_mqtt_filtradas.append(15)
            
            latencias_mqtt = latencias_mqtt_filtradas
            
            # Recalcular totais com dados reais de rádio
            latencias_total = []
            for i in range(min(len(latencias_radio), len(latencias_mqtt))):
                latencias_total.append(latencias_radio[i] + latencias_mqtt[i])
                
        except Exception as e:
            print(f"Erro ao carregar dados do MQTT do formato antigo: {e}")
            # Se não conseguimos carregar dados do MQTT, apenas plotar os dados do rádio
            print("Não foi possível carregar dados do MQTT. Apenas os dados de rádio serão exibidos.")
    
    # Preparar eixos X para plotagem
    x_radio = list(range(len(latencias_radio)))
    x_mqtt = list(range(len(latencias_mqtt)))
    
    # Garantir que temos o mesmo número de pontos X e Y
    x_radio = x_radio[:len(latencias_radio)]
    x_mqtt = x_mqtt[:len(latencias_mqtt)]
    
    # Criar figura para o gráfico
    plt.figure(figsize=(12, 8))
    
    # Plotar dados do rádio
    plt.plot(x_radio, latencias_radio, 'b-', label='Latência Rádio (ms)')
    
    # Calcular estatísticas para relatório
    stats = {}
    stats['radio'] = {
        'min': min(latencias_radio),
        'max': max(latencias_radio),
        'avg': np.mean(latencias_radio),
        'median': np.median(latencias_radio),
        'std': np.std(latencias_radio)
    }
    
    # Plotar dados do MQTT, se disponíveis
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
    
    # Criar um gráfico de barras para comparar médias
    plt.figure(figsize=(10, 6))
    meios = []
    latencias_medias = []
    
    if 'radio' in stats:
        meios.append('Rádio')
        latencias_medias.append(stats['radio']['avg'])
    
    if 'mqtt' in stats:
        meios.append('MQTT')
        latencias_medias.append(stats['mqtt']['avg'])
    
    if 'total' in stats:
        meios.append('Total (Rádio + MQTT)')
        latencias_medias.append(stats['total']['avg'])
    
    plt.bar(meios, latencias_medias, color=['blue', 'red', 'green'][:len(meios)])
    plt.title('Média de Latência por Tecnologia')
    plt.ylabel('Latência média (ms)')
    plt.grid(axis='y')
    
    # Adicionar valores nas barras
    for i, v in enumerate(latencias_medias):
        plt.text(i, v + 0.5, f'{v:.2f}ms', ha='center')
    
    # Estatísticas complementares no título
    plt.figtext(0.5, 0.01, 
                f"Rádio: mín={stats['radio']['min']:.2f}ms, máx={stats['radio']['max']:.2f}ms, med={stats['radio']['median']:.2f}ms, dp={stats['radio']['std']:.2f}ms\n" +
                (f"MQTT: mín={stats['mqtt']['min']:.2f}ms, máx={stats['mqtt']['max']:.2f}ms, med={stats['mqtt']['median']:.2f}ms, dp={stats['mqtt']['std']:.2f}ms\n" if 'mqtt' in stats else "") +
                (f"Total: mín={stats['total']['min']:.2f}ms, máx={stats['total']['max']:.2f}ms, med={stats['total']['median']:.2f}ms, dp={stats['total']['std']:.2f}ms" if 'total' in stats else ""),
                ha='center', fontsize=9)
    
    # Salvar gráficos
    plt.figure(1)
    plt.savefig('comparacao_latencias_real.png', dpi=300, bbox_inches='tight')
    plt.figure(2)
    plt.savefig('comparacao_latencias_barras_real.png', dpi=300, bbox_inches='tight')
    
    # Mostrar gráficos
    plt.show()
    
    return stats

if __name__ == "__main__":
    stats = plotar_comparacao_latencias()
    if stats:
        print("\n--- Estatísticas de latência ---")
        print(f"Rádio: {stats['radio']['avg']:.2f}ms (mín={stats['radio']['min']}ms, máx={stats['radio']['max']}ms)")
        if 'mqtt' in stats:
            print(f"MQTT: {stats['mqtt']['avg']:.2f}ms (mín={stats['mqtt']['min']}ms, máx={stats['mqtt']['max']}ms)")
        if 'total' in stats:
            print(f"Total: {stats['total']['avg']:.2f}ms (mín={stats['total']['min']}ms, máx={stats['total']['max']}ms)")
