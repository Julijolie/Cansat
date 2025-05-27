import paho.mqtt.client as mqtt
import serial
import time
import re

# Configurações do broker MQTT
BROKER = 'test.mosquitto.org'  # Ou o endereço do seu broker
PORT = 1883
TOPIC_BASE = 'cansat/estacao/teste1'

# Configuração da porta serial (ajuste conforme necessário)
SERIAL_PORT = 'COM3'  # Altere para a porta correta do seu receptor
BAUDRATE = 9600

# Regex para extrair os dados do print do receptor
regex = re.compile(r'ID: (\d+) \| Temperatura: ([\d\.-]+) C \| Pressao: ([\d\.-]+) hPa \| Accel \[X,Y,Z\]: ([\d\.-]+), ([\d\.-]+), ([\d\.-]+) \| Gyro \[X,Y,Z\] \(°/s\): ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)')

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

def main():
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    print(f'Lendo dados do receptor em {SERIAL_PORT}...')
    try:
        while True:
            linha = ser.readline().decode(errors='ignore').strip()
            if not linha:
                continue
            print(f'Recebido serial: {linha}')
            envia_mqtt_string(linha, client)
    except KeyboardInterrupt:
        print('Encerrando...')
    finally:
        ser.close()
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    main()
