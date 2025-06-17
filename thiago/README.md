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

## Workflow para Medição e Análise de Latência

### Passo 1: Upload dos Códigos nos Arduinos

1. Faça o upload do código `transmissor_com_latencia.ino` para o Arduino transmissor
2. Faça o upload do código `receptor_com_latencia.ino` para o Arduino receptor

Os códigos já estão modificados para incluir timestamp de envio e cálculo de latência.

### Passo 2: Coleta de Dados de Latência via Rádio

1. Conecte o Arduino receptor ao computador via USB
2. Execute o script `mqtt_sender.py` para capturar os dados do receptor:
   ```
   python mqtt_sender.py
   ```
   
   Este script:
   - Lê os dados do monitor serial do Arduino receptor
   - Salva os dados brutos no arquivo `dados_radio.csv`
   - Publica os dados em tópicos MQTT

3. Deixe o script executando por alguns minutos para coletar amostras suficientes (pelo menos 30 segundos)
4. Pressione `CTRL+C` para encerrar a coleta

### Passo 3: Coleta de Dados de Latência via MQTT

1. Em uma nova janela do terminal, execute o script:
   ```
   python mqtt_dashboard/backend/reading_mqtt_bridge.py
   ```
   
   Este script:
   - Se conecta ao broker MQTT para receber os dados
   - Calcula latências adicionais da transmissão MQTT
   - Salva os dados em `dados_mqtt_dashboard.csv`

2. Deixe o script executando por alguns minutos (mesmo tempo do passo anterior)
3. Pressione `CTRL+C` para encerrar

### Passo 4: Análise Básica de Latência

Execute o script de comparação para visualizar os resultados:
```
python compara_latencia.py
```

Este script:
- Lê os dados coletados dos arquivos CSV
- Processa e limpa os dados, removendo valores inválidos
- Gera gráficos comparando a latência do rádio vs. MQTT
- Apresenta estatísticas como média, mediana e desvio padrão
- Salva os gráficos como `comparacao_latencias.png` e `comparacao_latencias_barras.png`

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

1. **Latência de Rádio**: Tempo entre o envio do dado pelo transmissor e sua recepção pelo receptor
2. **Latência de MQTT**: Tempo adicional para o dado ser publicado e recebido via MQTT
3. **Latência Total**: Soma das latências de rádio e MQTT

Tipicamente, a latência do rádio está na faixa de 5-50ms, enquanto a latência MQTT pode variar de 5-100ms dependendo da conexão com o broker.

## Solução de Problemas

### Valores de Latência Muito Altos

Se os valores de latência parecerem irrealistas (por exemplo, milhões de milissegundos), o problema provavelmente está na medição de timestamp. Os scripts de análise tentam corrigir esses problemas automaticamente, mas você também pode:

1. Verificar se há overflow no cálculo do Arduino (quando `currentTime - timestamp` resulta em valores negativos)
2. Executar `analisa_timestamp_arduino.py` para diagnóstico detalhado

### Erro de Acesso à Porta Serial

Lembre-se que apenas um processo pode acessar a porta serial por vez. Certifique-se de encerrar o `mqtt_sender.py` antes de iniciar qualquer outro script que precise acessar a porta.

### Inconsistência nos Dados

Se a soma das latências individuais não corresponder à latência total, o script `compara_latencia.py` corrigirá isso automaticamente, garantindo que a latência total seja sempre a soma das latências de rádio e MQTT.

## Otimizações

Com base nos resultados das análises, você pode:

1. Ajustar a taxa de dados do rádio (RF24_250KBPS vs RF24_1MBPS)
2. Otimizar o tamanho do payload
3. Experimentar diferentes brokers MQTT ou ajustar parâmetros de QoS
4. Implementar compressão de dados para reduzir o tamanho das mensagens

## Observações Importantes

- Os scripts executam filtragem para remover valores absurdos, mas é sempre bom analisar os dados brutos
- A precisão das medições depende da sincronização de relógio entre os dispositivos
- Em alguns casos, a latência do rádio pode parecer 0ms devido à limitação de resolução do `millis()` do Arduino
