# SentinelX - Monitoramento Atmosférico Aéreo

## **1. Introdução**

Este documento define os requisitos técnicos para o desenvolvimento de um **Cansat** destinado à medição da qualidade do ar em diferentes pontos da cidade, aliado à presença de áreas verdes. O dispositivo será lançado por um drone e deve ser recuperável.

## **2. Requisitos Gerais**

- O Cansat deve medir variáveis ambientais relacionadas à qualidade do ar.
- Deve ser lançado por um drone e possuir sistema de recuperação seguro.
- Os dados coletados devem ser armazenados localmente e transmitidos remotamente em tempo real.
- O dispositivo deve ter baixo peso e dimensões compatíveis com padrões Cansat.
- Deve medir a aceleração da gravidade com base no peso do Cansat quando o paraquedas abrir.

## **3. Requisitos Técnicos**

### **3.1 Sensores e Medidas**

O Cansat deverá conter os seguintes sensores para medição da qualidade do ar, condições ambientais e gravidade:

- **Gases e Poluentes:**
    - **CO2:** Sensirion SCD30 ou MH-Z19
    - **NO2, CO, SO2, O3:** Alphasense B4 series ou MiCS-6814
- **Condições Ambientais:**
    - **Temperatura e Umidade:** DHT11
    - **Pressão Atmosférica:** BMP280 ou BME680
- **Medição da Gravidade:**
    - **Extensômetro:** Sensor de deformação resistivo (Strain Gauge) acoplado a um suporte fixo
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

### **3.7 Cálculo da Gravidade com Extensômetro**

O extensômetro medirá a deformação da estrutura onde está fixado quando o paraquedas abrir. Essa deformação será convertida em força aplicada usando a equação:

F=ΔRR×KF = \frac{\Delta R}{R} \times K

Onde:

- ΔR\Delta R é a variação da resistência do extensômetro;
- RR é a resistência inicial;
- KK é o fator de calibração do extensômetro.

A força FF é usada para determinar a aceleração da gravidade gg a partir da relação:

g=Fmg = \frac{F}{m}

Onde mm é a massa do Cansat.

## Planilha de teste de bancada

| Test ID | Test Description | Component | Priority | Expected Result | Test Status | Assigned To |
| --- | --- | --- | --- | --- | --- | --- |
| Test_01 | Medir CO2 em ambiente interno | Sensor de CO2 (SCD30/MH-Z19) | Alta | Leitura entre 400-1000 ppm | Pendente | Eng. de Sensores |
| Test_02 | Medir NO2, CO, SO2, O3 | Sensor multi-gás (Alphasense/MiCS-6814) | Alta | Resposta para cada gás testado | Pendente | Eng. de Sensores |
| Test_03 | Medir temperatura e umidade | Sensor (DHT11) | Média | Precisão dentro da margem de erro | Pendente | Eng. de Sensores |
| Test_04 | Testar integração com armazenamento | MicroSD 16GB | Média | Dados gravados corretamente | Pendente | Eng. de Software |
| Test_05 | Testar estabilidade energética | Bateria Li-Po 3.7V | Alta | Duração conforme especificado | Pendente | Eng. de Energia |
| Test_06 | Testar sistema de recuperação | Paraquedas | Alta | Descida controlada sem danos | Pendente | Eng. de Estrutura |
| Test_07 | Medir deformação e calcular gravidade | Extensômetro | Alta | Valor consistente com aceleração gravitacional | Pendente | Eng. de Sensores |

## Especificação técnica

### **2.1 Sensores Ambientais**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **Sensirion SCD30 / MH-Z19** | Medir concentração de CO2 | Alta precisão, compensação de temperatura e umidade |
| **Alphasense B4 / MiCS-6814** | Medir NO2, CO, SO2, O3 | Sensores multi-gás para maior abrangência |
| **DTH 11** | Temperatura, umidade e pressão | Baixa derivação, alta precisão |
| **Extensômetro (Strain Gauge)** | Medir deformação devido à força gravitacional | Permite estimar a aceleração da gravidade |
| **GUVA-S12SD** | Radiação UV | Sensor UV compacto e de baixo custo. |

### **2.2 Computação e Controle**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **ESP32 / STM32** | Microcontrolador | Wi-Fi, Bluetooth, baixo consumo |
| **MicroSD 16GB** | Armazenamento | Registro de dados offline |

### **2.3 Energia e Estrutura**

| Componente | Função | Justificativa |
| --- | --- | --- |
| **Bateria Li-Po 3.7V 2000mAh** | Alimentação | Energia suficiente para operação |
| **PLA/ABS** | Estrutura | Leve, resistente e fácil de fabricar |
| **Paraquedas** | Recuperação | Minimiza impacto na aterrissagem |
