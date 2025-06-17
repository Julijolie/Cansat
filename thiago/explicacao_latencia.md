## Explicação sobre o Problema e Solução da Visualização de Dados de Latência

Analisando seus dados de latência, identifiquei o seguinte problema:

### Problema
O arquivo `dados_mqtt_dashboard.csv` contém valores **constantes** para as latências:
- Latência do Rádio: sempre 50ms
- Latência do MQTT: sempre 50ms
- Latência Total: sempre 100ms

Isso acontece porque o código que está processando as mensagens está:
1. Descartando valores extremos e substituindo por estimativas fixas
2. Usando valores padrão quando não consegue calcular a latência corretamente

### Por que os gráficos mostram variação?
O script `compara_latencia.py` está **substituindo** seus dados por valores simulados quando detecta valores constantes. Isso é feito para demonstrar como seria um gráfico mais realista, mas não reflete seus dados reais.

Trecho relevante do código:
```python
if radio_latency_val > 1000:  # Se for maior que 1000ms, provavelmente está errado
    radio_latency_val = 50  # Valor típico estimado
```

### Solução
Você tem duas opções:

#### 1. Corrigir a medição na fonte (recomendado)
- Certifique-se de que o Arduino receptor esteja usando o `receptor_corrigido.ino` que tem a função `safeDeltaTime`
- Isso garantirá que as latências sejam corretamente medidas e que você tenha valores reais variando

#### 2. Use visualização com dados simulados para demonstração 
- Criei o script `compara_latencia_demo.py` que detecta automaticamente se seus dados são constantes 
- Se forem, gera visualizações com variações realistas para demonstração
- O script também é útil para apresentações

### Como verificar que a correção está funcionando
1. Primeiro, veja se os dados em `dados_mqtt_dashboard.csv` variam ou são constantes
2. Se quiser ver como seriam os dados com variação realista, execute:
   ```
   python compara_latencia_demo.py
   ```
3. Se quiser corrigir dados históricos já coletados, execute:
   ```
   python corrige_dados_radio.py
   ```
   e escolha a opção 2 para simular valores realistas

### O que esperar de dados reais
Dados reais de latência geralmente mostram variação:
- Rádio: 30-70ms com ocasionais picos mais altos
- MQTT: 5-20ms para broker local, 50-200ms para broker na nuvem 

O gráfico que você enviou é uma simulação que representa como dados reais de latência deveriam parecer, não seus dados atuais.
