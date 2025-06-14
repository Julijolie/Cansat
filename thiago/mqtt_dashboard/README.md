# CanSat Dashboard

Dashboard em React para visualização em tempo real dos dados do CanSat enviados via MQTT.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
mqtt_dashboard/
  ├── frontend/        # Aplicação React
  └── backend/         # Backend para processamento de dados MQTT
```

## Requisitos

- Node.js 14+ e npm para o frontend
- Python 3.6+ para o backend
- paho-mqtt (biblioteca Python)
- Broker MQTT (utilizamos HiveMQ como broker público)

## Configuração e Execução

### Frontend (React)

1. Navegue até a pasta do frontend:
   ```
   cd mqtt_dashboard/frontend
   ```

2. Instale as dependências:
   ```
   npm install
   ```

3. Execute a aplicação em modo de desenvolvimento:
   ```
   npm start
   ```

4. Para gerar a versão de produção para o GitHub Pages:
   ```
   npm run build
   npm run deploy
   ```

> **Nota:** Antes de realizar o deploy para o GitHub Pages, edite o campo `homepage` no arquivo `package.json` para refletir o seu nome de usuário no GitHub.

### Backend (Python)

1. Navegue até a pasta do backend:
   ```
   cd mqtt_dashboard/backend
   ```

2. Instale as dependências:
   ```
   pip install paho-mqtt pyserial
   ```

3. Execute o script para processar os dados do CanSat e enviar para o MQTT:
   ```
   python reading_mqtt.py
   ```

## Tecnologias Utilizadas

### Frontend
- React
- Chart.js para gráficos em tempo real
- MQTT.js para conexão com o broker MQTT via WebSocket

### Backend
- Python
- paho-mqtt para publicação e consumo de dados MQTT
- pyserial para leitura de dados da porta serial

## Broker MQTT

Este projeto utiliza o broker público HiveMQ (broker.hivemq.com) para que possa ser acessado de qualquer lugar sem necessidade de configuração de servidor próprio. Os dados são publicados nos seguintes tópicos:

- `cansat/estacao/teste1/raw` - Dados brutos
- `cansat/estacao/teste1/temperatura` - Temperatura
- `cansat/estacao/teste1/pressao` - Pressão
- `cansat/estacao/teste1/accelX` - Aceleração X
- `cansat/estacao/teste1/accelY` - Aceleração Y
- `cansat/estacao/teste1/accelZ` - Aceleração Z
- `cansat/estacao/teste1/gyroX` - Giroscópio X
- `cansat/estacao/teste1/gyroY` - Giroscópio Y
- `cansat/estacao/teste1/gyroZ` - Giroscópio Z
- `cansat/estacao/teste1/json` - Todos os dados em formato JSON

## GitHub Pages

Para disponibilizar o dashboard para muitas pessoas, você pode hospedá-lo no GitHub Pages:

1. Crie um repositório no GitHub
2. Configure a origem do Git no seu projeto local
3. Atualize o campo `homepage` no `package.json` com o seu nome de usuário
4. Execute `npm run deploy`

## Customização

Você pode personalizar o dashboard editando os arquivos na pasta `frontend/src/`. Os principais arquivos para customização são:

- `App.js` - Componente principal que controla a lógica do dashboard
- `App.css` - Estilos CSS do dashboard
