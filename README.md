# SentinelAir - Monitoramento Atmosférico Aéreo

## **1. Introdução**

Este documento define os requisitos técnicos para o desenvolvimento de um **Cansat** destinado à medição da qualidade do ar em diferentes pontos da cidade, aliado à presença de áreas verdes. O dispositivo será lançado por um drone e deve ser recuperável.

## **2. Requisitos Gerais**

- O Cansat deve medir variáveis ambientais relacionadas à qualidade do ar.
- Deve ser lançado por um drone e possuir sistema de recuperação seguro.
- Os dados coletados devem ser armazenados localmente e transmitidos remotamente em tempo real.
- O dispositivo deve ter baixo peso e dimensões compatíveis com padrões Cansat.

## **3. Requisitos Técnicos**

### **3.1 Sensores e Medidas**

O Cansat deverá conter os seguintes sensores para medição da qualidade do ar e condições ambientais:

- **Gases e Poluentes:**
    - **CO2:** Sensirion SCD30 ou MH-Z19
    - **NO2, CO, SO2, O3:** Alphasense B4 series ou MiCS-6814
- **Condições Ambientais:**
    - **Temperatura e Umidade:** DHT22 ou BME280
    - **Pressão Atmosférica:** BMP280 ou BME680
- **Posicionamento e Movimento:**
    - **GPS para localização:** u-blox NEO-M8N
    - **Acelerômetro e Giroscópio:** MPU6050 ou BNO055

### **3.2 Estrutura e Design**

- **Material:** Impressão 3D (PLA ou ABS)
- **Dimensões:** A~~proximadamente 65mm de diâmetro por 125mm de altura~~
- **Sistema de proteção para aterrissagem:** Paraquedas
- **Modularidade:** Compartimentos separados para sensores, bateria e eletrônicos

### **3.3 Lançamento e Recuperação**

- **Lançamento:** Drone
- **Sistema de recuperação:**
    - Paraquedas com abertura automática
    - GPS e Beacon RF (LoRa, 915 MHz) para rastreamento
    - Transmissão d~~e dados em tempo real (LoRaWAN ou NB-IoT)~~

### **3.4 Comunicação e Transmissão de Dados**

- **Armazenamento local:** microSD (mínimo 16GB, FAT32)
- **Transmissão sem fio:**
    - **Curta distância:** LoRa SX1276 (até 15 km)
    - **Longa distância:** NB-IoT (SIM7000G) ou 4G LTE

### **3.5 Energia e Alimentação**

- **Bateria:** Li-Po 3.7V, 2000mAh (mínimo)

### **3.6 Processamento e Controle**

- **Firmware:**
    - Desenvolvido em C (Arduino IDE)
    - Algoritmos de calibração para ajuste de medições

## Planilha de teste de bancada

| Test ID | Test Description | Component | Priority | Expected Result | Test Status | Assigned To |
| --- | --- | --- | --- | --- | --- | --- |
| Test_01 | Medir CO2 em ambiente interno | Sensor de CO2 (SCD30/MH-Z19) | Alta | Leitura entre 400-1000 ppm | Pendente | Eng. de Sensores |
| Test_02 | Medir NO2, CO, SO2, O3 | Sensor multi-gás (Alphasense/MiCS-6814) | Alta | Resposta para cada gás testado | Pendente | Eng. de Sensores |
| Test_03 | Medir material particulado | Sensor PM (PMS5003/SPS30) | Alta | Valores dentro do esperado | Pendente | Eng. de Sensores |
| Test_04 | Medir temperatura e umidade | Sensor (BME280/DHT22) | Média | Precisão dentro da margem de erro | Pendente | Eng. de Sensores |
| Test_05 | Testar GPS em ambiente aberto | u-blox NEO-M8N | Alta | Precisão < 5 metros | Pendente | Eng. de Navegação |
| Test_06 | Testar transmissão LoRa | Módulo SX1276 | Alta | Alcance acima de 1 km | Pendente | Eng. de Comunicação |
| Test_07 | Testar transmissão via NB-IoT | Módulo SIM7000G | Média | Conexão estável e upload de dados | Pendente | Eng. de Comunicação |
| Test_08 | Testar integração com armazenamento | MicroSD 16GB | Média | Dados gravados corretamente | Pendente | Eng. de Software |
| Test_09 | Testar estabilidade energética | Bateria Li-Po 3.7V | Alta | Duração conforme especificado | Pendente | Eng. de Energia |
| Test_10 | Testar sistema de recuperação | Paraquedas | Alta | Descida controlada sem danos | Pendente | Eng. de Estrutura |

## Especificação técnia

### **2.1 Sensores Ambientais**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **Sensirion SCD30 / MH-Z19** | Medir concentração de CO2 | Alta precisão, compensação de temperatura e umidade |
| **Alphasense B4 / MiCS-6814** | Medir NO2, CO, SO2, O3 | Sensores multi-gás para maior abrangência |
| **PMS5003 / SPS30** | Medir material particulado (PM1.0, PM2.5, PM10) | Baixo consumo, alta precisão, baixo custo |
| **BME280 / DHT22** | Temperatura, umidade e pressão | Baixa derivação, alta precisão |
| **VEML6075** | Medir radiação UV | Pequeno, preciso e fácil integração |
| **TSL2591** | Medir intensidade luminosa | Alta faixa dinâmica, ideal para uso externo |

### **2.2 Posicionamento e Navegação**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **u-blox NEO-M8N** | GPS para localização | Alta precisão e baixo consumo |
| **MPU6050 / BNO055** | Acelerômetro e giroscópio | Detecção de queda, ajuste de orientação |

### **2.3 Computação e Controle**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **ESP32 / STM32** | Microcontrolador | Wi-Fi, Bluetooth, baixo consumo |
| **MicroSD 16GB** | Armazenamento | Registro de dados offline |
| **LoRa SX1276** | Transmissão de dados | Baixo consumo e longo alcance |
| **NB-IoT SIM7000G** | Conectividade remota | Backup para transmissão |

### **2.4 Energia e Estrutura**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **Bateria Li-Po 3.7V 2000mAh** | Alimentação | Energia suficiente para operação |
| **Painel Solar 5V / 1W** | Recarregamento | Prolonga tempo de operação |
| **PLA/ABS** | Estrutura | Leve, resistente e fácil de fabricar |
| **Paraquedas** | Recuperação | Minimiza impacto na aterrissagem |
