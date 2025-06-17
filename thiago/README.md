# Análise de Latência: Rádio vs MQTT

Este projeto permite medir e comparar a latência entre a transmissão de dados por rádio (nRF24L01+) e por MQTT para aplicações Cansat. Aqui você encontra instruções para coletar dados, executar as análises e interpretar os resultados.

## Requisitos

- Arduino com código do transmissor e receptor
- Módulos nRF24L01+ configurados
- Python 3.x com as bibliotecas:
  - pandas
  - matplotlib
  - numpy
  - paho-mqtt
  - serial
  - Para a interface web (opcional):
    - Node.js e npm
    - React

## Passo a Passo: Obtenção e Comparação de Dados

### 1. Preparação dos Arduinos

1. **Upload do código no transmissor**: 
   - Conecte o Arduino transmissor ao computador
   - Abra o arquivo `transmissor/transmissor.ino` no Arduino IDE
   - Selecione a placa e porta corretas no menu Ferramentas
   - Clique em "Upload"

2. **Upload do código no receptor**:
   - Conecte o Arduino receptor ao computador
   - Abra o arquivo `receptor/receptor.ino` no Arduino IDE
   - Selecione a placa e porta corretas no menu Ferramentas
   - Clique em "Upload"

### 2. Coleta Simultânea de Dados (Rádio e MQTT)

1. **Execute o script de coleta em um terminal**:
   ```
   # No Windows
   coleta_dados.bat
   
   # No Linux/Mac
   ./coleta_dados.sh
   ```
   
   Este script automaticamente:
   - Inicia o `mqtt_sender.py` para capturar dados do receptor via serial
   - Inicia o `reading_mqtt_bridge_corrigido_new.py` para processar os dados via MQTT
   - Os dados são salvos nos arquivos `dados_radio.csv` e `dados_mqtt_dashboard.csv`

2. **Tempo de coleta**:
   - Deixe o script executando por pelo menos 2 minutos para obter dados suficientes
   - Pressione `CTRL+C` duas vezes para encerrar a coleta

### 3. Processamento e Análise dos Dados

1. **Execute o script de análise corrigida**:
   ```
   python compara_latencia_corrigido.py
   ```
   
   Este script:
   - Lê os dados coletados dos arquivos CSV
   - Aplica correções para sincronização de relógios
   - Gera gráficos comparando as latências de rádio vs. MQTT
   - Salva os gráficos como `comparacao_latencias_real.png` e `comparacao_latencias_barras_real.png`

2. **Verificação dos resultados**:
   - Abra os arquivos PNG gerados para visualizar os gráficos
   - Verifique as estatísticas exibidas no terminal (médias, medianas, etc.)

3. **Análise detalhada** (opcional):
   ```
   python validar_latencia.py
   ```
   Este script oferece análises adicionais e valida os cálculos de latência.

### Passo 5: Análises Adicionais (opcional)

Para análises mais detalhadas:

1. **Análise de timestamps do Arduino**
   ```
   python analisa_timestamp_arduino.py
   ```
   Este script analisa os timestamps gerados pelo Arduino para detectar problemas de overflow ou inconsistências.

2. **Estimativa de latência MQTT**
   ```
   python latencia_estimada_mqtt.py
   ```
   Este script faz uma estimativa mais precisa da latência MQTT com base nas diferenças de tempo do sistema.

## Interpretação dos Resultados

Os resultados mostrarão três métricas principais:

1. **Latência de Rádio**: Tempo entre o envio do dado pelo transmissor e sua recepção pelo receptor (tipicamente 5-50ms)
2. **Latência de MQTT**: Tempo adicional para o dado ser publicado e recebido via MQTT (tipicamente 5-500ms, dependendo da rede)
3. **Latência Total**: Soma das latências de rádio e MQTT

### Fatores que Afetam a Latência

- **Rádio**:
  - Distância entre transmissor e receptor
  - Interferências ambientais/físicas
  - Taxa de dados configurada no rádio (1Mbps vs 250Kbps)
  - Tamanho do payload

- **MQTT**:
  - Qualidade da conexão com a internet
  - Distância geográfica até o broker
  - Carga no broker MQTT
  - Configuração de QoS (0, 1 ou 2)

## Otimizações e Experimentos

Para otimizar a latência, você pode experimentar:

1. **Otimizações de Rádio**:
   - Reduzir o tamanho do payload
   - Aumentar a potência de transmissão (RF24_PA_LOW/MEDIUM/HIGH)
   - Alterar o canal RF para evitar interferências
   - Ajustar os parâmetros de retry (radio.setRetries)

2. **Otimizações de MQTT**:
   - Usar um broker local para menor latência
   - Ajustar o QoS (0 para menor latência, 1 ou 2 para maior confiabilidade)
   - Reduzir o tamanho das mensagens MQTT

3. **Experimentos Sugeridos**:
   - Compare a latência com diferentes tamanhos de payload
   - Teste diferentes brokers MQTT e compare os resultados
   - Avalie o impacto da distância física entre os dispositivos

## Arquivos do Projeto

- **/transmissor**: Códigos para o Arduino transmissor
- **/receptor**: Códigos para o Arduino receptor
- **/mqtt_dashboard**:
  - **/backend**: Scripts para processamento de dados MQTT
  - **/frontend**: Interface web em React

## Referências e Recursos

- [Documentação do nRF24L01+](https://nRF24.github.io/RF24)
- [Protocolo MQTT](https://mqtt.org/)
- [Medição de Latência em Sistemas Distribuídos](https://en.wikipedia.org/wiki/Network_delay)

---

Desenvolvido para projeto Cansat IBMEC Rio - 2025.1

## GUIA RÁPIDO: EXECUTANDO A INTERFACE

Siga este guia passo a passo para iniciar rapidamente a interface do dashboard:

### Windows

#### Iniciar o Backend (Terminal 1)
```powershell
# Navegue para a pasta do backend
cd c:\Users\Arthur\Documents\ibmecRio\2025.1\Cansat\thiago\mqtt_dashboard\backend

# Execute o script de processamento MQTT
python reading_mqtt_bridge_corrigido_new.py
```

#### Iniciar o Frontend (Terminal 2)
```powershell
# Navegue para a pasta do frontend
cd c:\Users\Arthur\Documents\ibmecRio\2025.1\Cansat\thiago\mqtt_dashboard\frontend

# Instale as dependências (apenas na primeira vez)
npm install

# Inicie o servidor de desenvolvimento React
npm start
```

### Linux/Mac

#### Iniciar o Backend (Terminal 1)
```bash
# Navegue para a pasta do backend
cd ~/ibmecRio/2025.1/Cansat/thiago/mqtt_dashboard/backend

# Execute o script de processamento MQTT
python reading_mqtt_bridge_corrigido_new.py
```

#### Iniciar o Frontend (Terminal 2)
```bash
# Navegue para a pasta do frontend
cd ~/ibmecRio/2025.1/Cansat/thiago/mqtt_dashboard/frontend

# Instale as dependências (apenas na primeira vez)
npm install

# Inicie o servidor de desenvolvimento React
npm start
```

### O que esperar:
1. O backend irá mostrar mensagens de conexão com o broker MQTT
2. O frontend abrirá automaticamente em seu navegador padrão (ou acesse http://localhost:3000)
3. Os dados aparecerão no dashboard assim que o backend começar a receber as mensagens MQTT

### Para encerrar:
- Pressione `CTRL+C` em ambos os terminais para encerrar os processos
