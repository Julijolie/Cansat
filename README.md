# SentinelX - Monitoramento Atmosférico Aéreo

## **1. Introdução**

Este documento define os requisitos técnicos para o desenvolvimento do **SentinelX**, um dispositivo destinado à medição da qualidade do ar em diferentes pontos da cidade, aliado à presença de áreas verdes. O dispositivo será lançado por um drone e deve ser recuperável.

## **2. Requisitos Gerais**

- O SentinelX deve medir variáveis ambientais relacionadas à qualidade do ar.
- Deve ser lançado por um drone e possuir sistema de recuperação seguro.
- Os dados coletados devem ser armazenados localmente e transmitidos remotamente em tempo real.
- O dispositivo deve ter baixo peso e dimensões compatíveis com padrões de sensores ambientais compactos.

## **3. Requisitos Técnicos**

### **3.1 Sensores e Medidas**

O SentinelX deverá conter os seguintes sensores para medição da qualidade do ar e condições ambientais:

- **Gases e Poluentes:**
    - **CO2:** Sensirion SCD30 ou MH-Z19
    - **NO2, CO, SO2, O3:** Alphasense B4 series ou MiCS-6814
- **Condições Ambientais:**
    - **Temperatura e Umidade:** DHT11
    - **Pressão Atmosférica:** BMP280 ou BME680
    - **Umidade relativa:** DHT11
- **Radiação**
    - **Radiação UV:** GUVA-S12SD

### **3.2 Estrutura e Design**

- **Material:** Impressão 3D (PLA ou ABS)
- **Sistema de proteção para aterrissagem:** Paraquedas
- **Modularidade:** Compartimentos separados para sensores, bateria e eletrônicos

### **3.3 Lançamento e Recuperação**

- **Lançamento:** Drone
- **Sistema de recuperação:**
    - Paraquedas com abertura automática

### **3.4 Comunicação e Transmissão de Dados**

- **Armazenamento local:** microSD (mínimo 16GB, FAT32)
- **Transmissão sem fio:** Fs1000a / Mx-rm-5v OEM

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
| Test_03 | Medir temperatura e umidade | Sensor (DHT11) | Média | Precisão dentro da margem de erro | Pendente | Eng. de Sensores |
| Test_04 | Testar integração com armazenamento | MicroSD 16GB | Média | Dados gravados corretamente | Pendente | Eng. de Software |
| Test_05 | Testar estabilidade energética | Bateria Li-Po 3.7V | Alta | Duração conforme especificado | Pendente | Eng. de Energia |
| Test_06 | Testar sistema de recuperação | Paraquedas | Alta | Descida controlada sem danos | Pendente | Eng. de Estrutura |

## Especificação técnica

### **2.1 Sensores Ambientais**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **Sensirion SCD30 / MH-Z19** | Medir concentração de CO2 | Alta precisão, compensação de temperatura e umidade |
| **Alphasense B4 / MiCS-6814** | Medir NO2, CO, SO2, O3 | Sensores multi-gás para maior abrangência |
| **DHT11** | Temperatura, umidade e pressão | Baixa derivação, alta precisão |

### **2.2 Computação e Controle**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **ESP32**  | Microcontrolador | Wi-Fi, Bluetooth, baixo consumo |
| **MicroSD 16GB** | Armazenamento | Registro de dados offline |

### **2.3 Energia e Estrutura**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **Bateria Li-Po 3.7V 2000mAh** | Alimentação | Energia suficiente para operação |
| **PLA/ABS** | Estrutura | Leve, resistente e fácil de fabricar |
| **Paraquedas** | Recuperação | Minimiza impacto na aterrissagem |
