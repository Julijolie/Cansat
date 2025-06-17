import serial
import time
import paho.mqtt.client as mqtt
import sys
import json
import re


# Regex para extrair os dados do print do receptor
DATA_REGEX = re.compile(r'ID: (\d+) \| Timestamp: (\d+) \| RadioLatency: (\d+) ms \| Temperatura: ([\d\.-]+) C \| Pressao: ([\d\.-]+) hPa \| Accel \[X,Y,Z\]: ([\d\.-]+), ([\d\.-]+), ([\d\.-]+) \| Gyro \[X,Y,Z\] \(°/s\): ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)')

# Configuração MQTT
MQTT_BROKER = "broker.hivemq.com"  # Broker público acessível de qualquer lugar
MQTT_PORT = 1883
MQTT_TOPIC_BASE = "cansat/estacao/teste1"  # Tópico base para os dados do CanSat
MQTT_TOPIC_RAW = f"{MQTT_TOPIC_BASE}/raw"  # Dados brutos
MQTT_TOPIC_TIMESTAMP = f"{MQTT_TOPIC_BASE}/timestamp"  # Timestamp original de envio
MQTT_TOPIC_RADIO_LATENCY = f"{MQTT_TOPIC_BASE}/radioLatency"  # Latência do rádio
MQTT_TOPIC_MQTT_LATENCY = f"{MQTT_TOPIC_BASE}/mqttLatency"  # Latência do MQTT
MQTT_TOPIC_TOTAL_LATENCY = f"{MQTT_TOPIC_BASE}/totalLatency"  # Latência total
MQTT_TOPIC_TEMP = f"{MQTT_TOPIC_BASE}/temperatura"  # Temperatura
MQTT_TOPIC_PRESS = f"{MQTT_TOPIC_BASE}/pressao"  # Pressão
MQTT_TOPIC_ACCEL_X = f"{MQTT_TOPIC_BASE}/accelX"  # Aceleração X
MQTT_TOPIC_ACCEL_Y = f"{MQTT_TOPIC_BASE}/accelY"  # Aceleração Y
MQTT_TOPIC_ACCEL_Z = f"{MQTT_TOPIC_BASE}/accelZ"  # Aceleração Z
MQTT_TOPIC_GYRO_X = f"{MQTT_TOPIC_BASE}/gyroX"  # Giroscópio X
MQTT_TOPIC_GYRO_Y = f"{MQTT_TOPIC_BASE}/gyroY"  # Giroscópio Y
MQTT_TOPIC_GYRO_Z = f"{MQTT_TOPIC_BASE}/gyroZ"  # Giroscópio Z

# Configuração Serial
# Observe que você precisa alterar a PORTA_COM para a porta COM do seu Arduino
# Exemplo: 'COM3' no Windows ou '/dev/ttyUSB0' no Linux
PORTA_COM = 'COM8'  # Altere conforme necessário
BAUD_RATE = 9600   # Baud rate igual ao do receptor Arduino

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT")
        print(f"Publicando para o tópico: {MQTT_TOPIC_BASE}")
    else:
        print(f"Falha na conexão com o broker MQTT, código de retorno: {rc}")

def main():
    # Configuração do cliente MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    
    try:
        # Conectar ao broker MQTT
        print(f"Conectando ao broker MQTT: {MQTT_BROKER}")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Conectar à porta serial
        try:
            print(f"Abrindo porta serial {PORTA_COM} a {BAUD_RATE} bps...")
            ser = serial.Serial(PORTA_COM, BAUD_RATE, timeout=1)
            print("Porta serial aberta com sucesso!")
        except serial.SerialException as e:
            print(f"Erro ao abrir a porta serial: {e}")
            client.loop_stop()
            client.disconnect()
            sys.exit(1)
              # Loop principal - ler serial e publicar no MQTT
        print("Iniciando leitura da porta serial. Pressione CTRL+C para encerrar.")
        while True:
            if ser.in_waiting > 0:
                # Ler linha da porta serial
                linha = ser.readline().decode('utf-8').strip()
                if linha:
                    print(f"Dados recebidos: {linha}")
                    
                    # Publicar dados brutos no MQTT
                    client.publish(MQTT_TOPIC_RAW, linha)
                    print(f"Dados brutos enviados para o tópico: {MQTT_TOPIC_RAW}")
                    
                    # Tentar extrair os dados individuais com regex
                    match = DATA_REGEX.search(linha)
                    if match:
                        id_num, timestamp, radio_latency, temp, press, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = match.groups()
                        
                        # Registrar o timestamp de recepção no backend
                        backend_receive_time = time.time() * 1000  # Para compatibilidade com milissegundos
                        
                        # Calcular latências
                        radio_latency_ms = int(radio_latency)
                        mqtt_latency_ms = int(backend_receive_time) - int(timestamp)
                        total_latency_ms = radio_latency_ms + mqtt_latency_ms
                        
                        # Publicar dados em tópicos separados
                        client.publish(MQTT_TOPIC_TIMESTAMP, timestamp)
                        client.publish(MQTT_TOPIC_RADIO_LATENCY, str(radio_latency_ms))
                        client.publish(MQTT_TOPIC_MQTT_LATENCY, str(mqtt_latency_ms))
                        client.publish(MQTT_TOPIC_TOTAL_LATENCY, str(total_latency_ms))
                        client.publish(MQTT_TOPIC_TEMP, temp)
                        client.publish(MQTT_TOPIC_PRESS, press)
                        client.publish(MQTT_TOPIC_ACCEL_X, accel_x)
                        client.publish(MQTT_TOPIC_ACCEL_Y, accel_y)
                        client.publish(MQTT_TOPIC_ACCEL_Z, accel_z)
                        client.publish(MQTT_TOPIC_GYRO_X, gyro_x)
                        client.publish(MQTT_TOPIC_GYRO_Y, gyro_y)
                        client.publish(MQTT_TOPIC_GYRO_Z, gyro_z)
                        
                        # Também publicar como JSON para consumo mais fácil
                        json_data = {
                            "id": int(id_num),
                            "timestamp": int(timestamp),
                            "systemTime": time.time(),
                            "radioLatency": radio_latency_ms,
                            "mqttLatency": mqtt_latency_ms,
                            "totalLatency": total_latency_ms,
                            "temperatura": float(temp),
                            "pressao": float(press),
                            "aceleracao": {
                                "x": float(accel_x),
                                "y": float(accel_y),
                                "z": float(accel_z)
                            },
                            "giroscopio": {
                                "x": float(gyro_x),
                                "y": float(gyro_y),
                                "z": float(gyro_z)
                            }
                        }
                        client.publish(f"{MQTT_TOPIC_BASE}/json", json.dumps(json_data))
                        print("Dados processados e publicados em tópicos individuais")
            time.sleep(0.1)  # Pequena pausa para não sobrecarregar a CPU
                
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        # Limpeza ao sair
        print("Fechando conexões...")
        try:
            ser.close()
            print("Porta serial fechada")
        except:
            pass
        
        try:
            client.loop_stop()
            client.disconnect()
            print("Desconectado do broker MQTT")
        except:
            pass

if __name__ == "__main__":
    main()