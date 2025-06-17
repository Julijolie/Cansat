import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import random

def gerar_latencias_realistas():
    """
    Gera valores de latência realistas para demonstração e visualização.
    
    Este script é usado quando os valores no CSV são constantes, para
    demonstrar como seriam dados de latência mais realistas.
    """
    # Definir sementes para reprodutibilidade
    np.random.seed(42)
    random.seed(42)
    
    # Número de amostras
    n_samples = 40
    
    # Gerar latências realistas para rádio (média 50ms, variação de ±15ms)
    base_radio = 50
    radio_latencias = [max(35, min(65, base_radio + random.randint(-15, 15))) for _ in range(n_samples)]
    
    # Adicionar algumas variações maiores em pontos específicos para simular interferências
    interference_points = [8, 15, 19, 25, 28, 32, 38]
    for idx in interference_points:
        if idx < n_samples:
            radio_latencias[idx] = radio_latencias[idx] + random.randint(3, 8)
    
    # Gerar latências MQTT constantes (média 50ms)
    mqtt_latencias = [50] * n_samples
    
    # Calcular latência total
    total_latencias = [radio + mqtt for radio, mqtt in zip(radio_latencias, mqtt_latencias)]
    
    # Criar DataFrame para simular dados no formato do dashboard
    df = pd.DataFrame({
        'timestamp': [1750133523.62 + i for i in range(n_samples)],
        'id': [4529 + i for i in range(n_samples)],
        'radio_latency': radio_latencias,
        'mqtt_latency': mqtt_latencias,
        'total_latency': total_latencias,
        'temperatura': [23.60] * n_samples,
        'pressao': [1023.60 + random.randint(-5, 5)/100 for _ in range(n_samples)]
    })
    
    # Salvar dados simulados
    output_file = 'dados_mqtt_simulados.csv'
    df.to_csv(output_file, index=False)
    print(f"Dados simulados salvos em {output_file}")
    
    return radio_latencias, mqtt_latencias, total_latencias

def plotar_comparacao(radio_latencias, mqtt_latencias, total_latencias):
    """
    Plota gráficos de comparação para os dados de latência.
    """
    # Criar figura para o gráfico
    plt.figure(figsize=(12, 8))
    
    # Estatísticas
    radio_avg = np.mean(radio_latencias)
    mqtt_avg = np.mean(mqtt_latencias)
    total_avg = np.mean(total_latencias)
    
    # Plotar linhas
    x = range(len(radio_latencias))
    plt.plot(x, radio_latencias, 'b-', label='Latência Rádio (ms)')
    plt.plot(x, mqtt_latencias, 'r-', label='Latência MQTT (ms)')
    plt.plot(x, total_latencias, 'g-', label='Latência Total (Rádio + MQTT) (ms)')
    
    # Formatar gráfico
    plt.title('Comparação de Latências: Rádio vs MQTT')
    plt.xlabel('Número da amostra')
    plt.ylabel('Latência (ms)')
    plt.grid(True)
    plt.legend()
    
    # Salvar gráfico
    plt.savefig('comparacao_latencias_simuladas.png')
    plt.show()
    
    # Criar gráfico de barras para comparar médias
    plt.figure(figsize=(10, 6))
    meios = ['Rádio', 'MQTT', 'Total (Rádio + MQTT)']
    latencias_medias = [radio_avg, mqtt_avg, total_avg]
    
    # Criar gráfico de barras com cores diferentes
    bars = plt.bar(meios, latencias_medias, color=['blue', 'red', 'green'])
    plt.ylim(0, max(latencias_medias) * 1.2)  # Limitar a altura do gráfico
    
    # Adicionar valores nas barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 2,
                 f'{height:.2f} ms',
                 ha='center', va='bottom')
    
    plt.title('Médias de Latência por Meio de Comunicação')
    plt.ylabel('Latência Média (ms)')
    plt.grid(True, axis='y', alpha=0.3)
    
    plt.savefig('medias_latencias_simuladas.png')
    plt.show()
    
    # Mostrar estatísticas
    print("\nEstatísticas de Latência:")
    print(f"Rádio - Média: {radio_avg:.2f}ms, Min: {min(radio_latencias)}ms, Max: {max(radio_latencias)}ms")
    print(f"MQTT - Média: {mqtt_avg:.2f}ms, Min: {min(mqtt_latencias)}ms, Max: {max(mqtt_latencias)}ms")
    print(f"Total - Média: {total_avg:.2f}ms, Min: {min(total_latencias)}ms, Max: {max(total_latencias)}ms")

def verificar_dados_reais():
    """
    Verifica se os dados reais têm variação ou são constantes.
    """
    arquivo_mqtt = 'dados_mqtt_dashboard.csv'
    if not os.path.exists(arquivo_mqtt):
        print(f"Arquivo {arquivo_mqtt} não encontrado!")
        return False
    
    try:
        df = pd.read_csv(arquivo_mqtt)
        
        if 'radio_latency' in df.columns:
            radio_values = df['radio_latency'].unique()
            mqtt_values = df['mqtt_latency'].unique() if 'mqtt_latency' in df.columns else []
            
            print(f"\nValores únicos de latência do rádio: {radio_values}")
            print(f"Valores únicos de latência do MQTT: {mqtt_values}")
            
            # Verificar se todos os valores são iguais
            if len(radio_values) <= 1 and len(mqtt_values) <= 1:
                print("\nDetectados valores constantes no arquivo CSV. Gerando dados simulados para visualização.")
                return True
            else:
                print("\nDados reais com variação encontrados. Usando dados do arquivo CSV.")
                return False
        else:
            print("\nFormato de arquivo inesperado. Gerando dados simulados.")
            return True
    except Exception as e:
        print(f"\nErro ao verificar arquivo: {e}")
        print("Gerando dados simulados para visualização.")
        return True

if __name__ == "__main__":
    print("=== Comparação de Latências: Rádio vs MQTT ===")
    
    # Verificar se os dados reais têm variação
    usar_simulacao = verificar_dados_reais()
    
    if usar_simulacao:
        # Gerar e plotar dados simulados
        radio_latencias, mqtt_latencias, total_latencias = gerar_latencias_realistas()
        plotar_comparacao(radio_latencias, mqtt_latencias, total_latencias)
    else:
        # Usar dados reais do arquivo CSV
        try:
            df = pd.read_csv('dados_mqtt_dashboard.csv')
            
            radio_latencias = df['radio_latency'].tolist()
            mqtt_latencias = df['mqtt_latency'].tolist()
            total_latencias = df['total_latency'].tolist()
            
            plotar_comparacao(radio_latencias, mqtt_latencias, total_latencias)
        except Exception as e:
            print(f"Erro ao processar dados reais: {e}")
            print("Continuando com simulação...")
            
            radio_latencias, mqtt_latencias, total_latencias = gerar_latencias_realistas()
            plotar_comparacao(radio_latencias, mqtt_latencias, total_latencias)
