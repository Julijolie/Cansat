import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def testar_comparacao_latencia():
    """
    Script para testar se os dados de latência estão sendo coletados corretamente.
    Abre o arquivo dados_mqtt_dashboard.csv e verifica sua estrutura e conteúdo.
    """
    arquivo_mqtt = 'dados_mqtt_dashboard.csv'
    arquivo_radio = 'dados_radio.csv'
    
    # Verificar se os arquivos existem
    if not os.path.exists(arquivo_mqtt):
        print(f"ERRO: Arquivo {arquivo_mqtt} não encontrado!")
        print("Execute primeiro reading_mqtt_bridge_corrigido.py e mqtt_sender.py para gerar o arquivo.")
        return
    
    if not os.path.exists(arquivo_radio):
        print(f"AVISO: Arquivo {arquivo_radio} não encontrado. Verificando apenas os dados MQTT.")
    
    # Carregar dados MQTT
    try:
        df_mqtt = pd.read_csv(arquivo_mqtt)
        print(f"\nDados MQTT carregados com sucesso!")
        print(f"Número de registros: {len(df_mqtt)}")
        print("\nPrimeiros registros:")
        print(df_mqtt.head())
        
        # Verificar se temos colunas de latência
        colunas_latencia = ['radio_latency', 'mqtt_latency', 'total_latency']
        if all(col in df_mqtt.columns for col in colunas_latencia):
            print("\nColunas de latência encontradas!")
            
            # Estatísticas básicas
            print("\nEstatísticas de Latência:")
            for col in colunas_latencia:
                if df_mqtt[col].count() > 0:
                    print(f"\n{col}:")
                    print(f"  Média: {df_mqtt[col].mean():.2f} ms")
                    print(f"  Mediana: {df_mqtt[col].median():.2f} ms")
                    print(f"  Mínimo: {df_mqtt[col].min():.2f} ms")
                    print(f"  Máximo: {df_mqtt[col].max():.2f} ms")
            
            # Plotar histogramas das latências
            plt.figure(figsize=(15, 5))
            
            # Radio latency
            plt.subplot(131)
            plt.hist(df_mqtt['radio_latency'], bins=20, alpha=0.7, color='blue')
            plt.title('Latência do Rádio (ms)')
            plt.xlabel('Latência (ms)')
            plt.ylabel('Frequência')
            
            # MQTT latency
            plt.subplot(132)
            plt.hist(df_mqtt['mqtt_latency'], bins=20, alpha=0.7, color='green')
            plt.title('Latência do MQTT (ms)')
            plt.xlabel('Latência (ms)')
            plt.ylabel('Frequência')
            
            # Total latency
            plt.subplot(133)
            plt.hist(df_mqtt['total_latency'], bins=20, alpha=0.7, color='red')
            plt.title('Latência Total (ms)')
            plt.xlabel('Latência (ms)')
            plt.ylabel('Frequência')
            
            plt.tight_layout()
            plt.savefig('latencias_histograma.png')
            plt.show()
            
            # Verificar distribuição das latências
            plt.figure(figsize=(10, 6))
            
            # Criar boxplots lado a lado
            latencias = [df_mqtt['radio_latency'], df_mqtt['mqtt_latency'], df_mqtt['total_latency']]
            plt.boxplot(latencias, labels=['Rádio', 'MQTT', 'Total'])
            plt.title('Comparação de Latências: Rádio vs MQTT')
            plt.ylabel('Latência (ms)')
            plt.grid(True, alpha=0.3)
            
            plt.savefig('latencias_boxplot.png')
            plt.show()
            
            print(f"\nGráficos salvos como 'latencias_histograma.png' e 'latencias_boxplot.png'")
            
        else:
            print("\nERRO: Colunas de latência não encontradas no arquivo CSV!")
            print(f"Colunas disponíveis: {df_mqtt.columns.tolist()}")
    
    except Exception as e:
        print(f"Erro ao processar arquivo {arquivo_mqtt}: {e}")
    
    # Verificar se temos dados do rádio para comparar
    if os.path.exists(arquivo_radio):
        try:
            # Aqui podemos adicionar código para carregar e comparar os dados do rádio
            print(f"\nArquivo de dados do rádio encontrado: {arquivo_radio}")
            print("Para uma análise completa das latências de rádio vs MQTT, execute o script compara_latencia.py")
        except Exception as e:
            print(f"Erro ao verificar arquivo {arquivo_radio}: {e}")

if __name__ == "__main__":
    print("=== Teste de Comparação de Latência ===")
    testar_comparacao_latencia()
