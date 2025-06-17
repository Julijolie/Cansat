import paho.mqtt.client as mqtt
import serial
import time
import re

# Configurações do broker MQTT
BROKER = 'broker.hivemq.com'  # Broker público acessível de qualquer lugar
PORT = 1883
TOPIC_BASE = 'cansat/estacao/teste1'

# Configuração da porta serial (ajuste conforme necessário)
SERIAL_PORT = 'COM8'  # Altere para a porta correta do seu receptor
BAUDRATE = 9600

# Regex para extrair os dados do print do receptor
regex = re.compile(r'ID: (\d+) \| Timestamp: (\d+) \| RadioLatency: (\d+) ms \| Temperatura: ([\d\.-]+) C \| Pressao: ([\d\.-]+) hPa \| Accel \[X,Y,Z\]: ([\d\.-]+), ([\d\.-]+), ([\d\.-]+) \| Gyro \[X,Y,Z\] \(°/s\): ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)')

def envia_mqtt(dado, client):
    for chave, valor in dado.items():
        if chave == 'id':
            continue  # Não envia o id
        topico = TOPIC_BASE + '/' + chave  # Adiciona barra para criar sub-tópicos
        client.publish(topico, str(valor))
        print(f'Enviado para {topico}: {valor}')
        time.sleep(0.05)

def envia_mqtt_string(linha, client):
    topico = TOPIC_BASE + '/raw'
    client.publish(topico, linha)
    print(f'Enviado para {topico}: {linha}')
    time.sleep(0.05)

def envia_mqtt_string_multibroker(linha, clients):
    # Registrar o timestamp de recepção no MQTT
    mqtt_receive_time = time.time() * 1000  # Timestamp em milissegundos
    
    for client, broker_name in clients:
        topico = TOPIC_BASE + '/raw'
        result = client.publish(topico, linha, qos=1)
        # Verificar se o envio foi bem sucedido
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f'Enviado para {broker_name}: {topico}: {linha}')
        else:
            print(f'ERRO ao enviar para {broker_name}: {result.rc}')
        
        # Tentar analisar os dados e enviar para tópicos separados
        match = regex.search(linha)
        if match:
            # Se conseguiu extrair todos os dados
            id_num, timestamp, radio_latency, temp, press, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = match.groups()
              # Calcular a latência MQTT (tempo atual - timestamp de envio original)
            mqtt_latency = mqtt_receive_time - int(timestamp)
            total_latency = int(mqtt_latency) + int(radio_latency)  # Latência total = latência do rádio + latência do MQTT
            
            # Publicar em tópicos individuais
            client.publish(f"{TOPIC_BASE}/timestamp", timestamp)
            client.publish(f"{TOPIC_BASE}/radioLatency", radio_latency)
            client.publish(f"{TOPIC_BASE}/mqttLatency", str(int(mqtt_latency)))
            client.publish(f"{TOPIC_BASE}/totalLatency", str(int(total_latency)))
            client.publish(f"{TOPIC_BASE}/temperatura", temp)
            client.publish(f"{TOPIC_BASE}/pressao", press)
            client.publish(f"{TOPIC_BASE}/accelX", accel_x)
            client.publish(f"{TOPIC_BASE}/accelY", accel_y)
            client.publish(f"{TOPIC_BASE}/accelZ", accel_z)
            client.publish(f"{TOPIC_BASE}/gyroX", gyro_x)
            client.publish(f"{TOPIC_BASE}/gyroY", gyro_y)
            client.publish(f"{TOPIC_BASE}/gyroZ", gyro_z)
            
            print(f'Enviados dados separados para {broker_name}')
            print(f'Radio Latency: {radio_latency}ms, MQTT Latency: {int(mqtt_latency)}ms, Total: {int(total_latency)}ms')
        
        time.sleep(0.01)

def main():
    import csv
    radio_csv = 'dados_radio.csv'
    first_write = True    # Configuração dos dois brokers
    BROKERS = [
        ('localhost', 'Local'),
        ('broker.hivemq.com', 'Nuvem')
    ]
    clients = []
    for broker, broker_name in BROKERS:
        client = mqtt.Client()
        client.connect(broker, 1883, 60)
        client.loop_start()
        clients.append((client, broker_name))

    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    print(f'Lendo dados do receptor em {SERIAL_PORT}...')
    try:
        with open(radio_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            if first_write:
                writer.writerow(['timestamp', 'valor'])
                first_write = False
            while True:
                linha = ser.readline().decode(errors='ignore').strip()
                if not linha:
                    continue
                t = time.time()
                writer.writerow([t, linha])
                f.flush()
                print(f'Recebido serial: {linha}')
                envia_mqtt_string_multibroker(linha, clients)
    except KeyboardInterrupt:
        print('Encerrando...')
    finally:
        ser.close()
        for client, _ in clients:
            client.loop_stop()
            client.disconnect()

if __name__ == '__main__':
    main()
