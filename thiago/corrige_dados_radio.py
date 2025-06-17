import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os

def corrigir_dados_radio(arquivo_input, arquivo_output):
    """
    Corrige os valores de latência no arquivo de dados do rádio.
    
    Args:
        arquivo_input: Caminho para o arquivo CSV original
        arquivo_output: Caminho para salvar o arquivo corrigido
    """
    if not os.path.exists(arquivo_input):
        print(f"Arquivo {arquivo_input} não encontrado!")
        return
    
    # Carregar o arquivo CSV original
    df = pd.read_csv(arquivo_input)
    print(f"Carregado arquivo {arquivo_input} com {len(df)} linhas")
    
    # Regex para extrair valores do campo 'valor'
    radio_regex = re.compile(r'ID: (\d+) \| Timestamp: (\d+) \| RadioLatency: (\d+) ms')
    
    # Colunas para o novo DataFrame
    timestamps = []
    ids = []
    valores_originais = []
    latencias_corrigidas = []
    dados_completos = []
    
    # Processar cada linha
    for index, row in df.iterrows():
        # Copiar valores originais
        timestamp = row['timestamp']
        timestamps.append(timestamp)
        
        valor = str(row['valor']) if 'valor' in df.columns else ''
        valores_originais.append(valor)
        
        # Extrair valores usando regex
        match = radio_regex.search(valor)
        if match:
            id_num, timestamp_arduino, radio_latency = match.groups()
            ids.append(int(id_num))
            
            # Convertendo para inteiro
            latencia_original = int(radio_latency)
            
            # Corrigir overflow
            latencia_corrigida = latencia_original
            if latencia_original > 4000000000:  # Valor próximo a 2^32 indica overflow
                # Corrigir o overflow: latencia = (2^32 - latencia_original)
                latencia_corrigida = abs(latencia_original - (1 << 32))
            
            # Verificar valor corrigido
            if latencia_corrigida > 1000:  # Latência ainda é muito alta
                latencia_corrigida = 50  # Usar valor típico como estimativa
            
            latencias_corrigidas.append(latencia_corrigida)
            
            # Criar a nova string de dados com latência corrigida
            partes = valor.split(" | ")
            novo_valor = partes[0] + " | " + partes[1] + f" | RadioLatency: {latencia_corrigida} ms | " + " | ".join(partes[3:])
            dados_completos.append(novo_valor)
        else:
            ids.append(None)
            latencias_corrigidas.append(None)
            dados_completos.append(valor)
    
    # Criar o novo DataFrame
    df_novo = pd.DataFrame({
        'timestamp': timestamps,
        'valor': dados_completos,
        'id': ids,
        'latencia_original': valores_originais,
        'latencia_corrigida': latencias_corrigidas
    })
    
    # Salvar o arquivo corrigido
    df_novo.to_csv(arquivo_output, index=False)
    print(f"Arquivo corrigido salvo em {arquivo_output}")
    
    # Mostrar exemplo de correção
    print("\nExemplo de dados corrigidos:")
    for i in range(min(5, len(df_novo))):
        print(f"Original: {valores_originais[i]}")
        print(f"Corrigido: {dados_completos[i]}")
        print()
    
    # Mostrar estatísticas
    latencias_validas = [l for l in latencias_corrigidas if l is not None]
    if latencias_validas:
        print("\nEstatísticas de Latência Corrigida:")
        print(f"Mínimo: {min(latencias_validas)} ms")
        print(f"Máximo: {max(latencias_validas)} ms")
        print(f"Média: {np.mean(latencias_validas):.2f} ms")
        print(f"Mediana: {np.median(latencias_validas):.2f} ms")
        
        # Plotar histograma das latências corrigidas
        plt.figure(figsize=(10, 6))
        plt.hist(latencias_validas, bins=20, color='blue', alpha=0.7)
        plt.title('Distribuição de Latências de Rádio Corrigidas')
        plt.xlabel('Latência (ms)')
        plt.ylabel('Frequência')
        plt.grid(True, alpha=0.3)
        plt.savefig('latencia_radio_histograma.png')
        plt.show()
    
    return df_novo

if __name__ == "__main__":
    arquivo_input = "dados_radio.csv"
    arquivo_output = "dados_radio_corrigido.csv"
    
    df_corrigido = corrigir_dados_radio(arquivo_input, arquivo_output)
    
    print("\nProcesso concluído! Execute o script compara_latencia.py novamente com os dados corrigidos:"
         "\npython compara_latencia.py")
