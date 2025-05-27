import paho.mqtt.client as mqtt
import time
import csv

BROKER = 'test.mosquitto.org'
PORT = 1883
TOPIC = 'cansat/estacao/teste1/raw'
destino_csv = 'dados_mqtt_nuvem.csv'

with open(destino_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'valor'])

    def on_connect(client, userdata, flags, rc):
        print('Conectado ao broker MQTT NUVEM')
        client.subscribe(TOPIC)

    def on_message(client, userdata, msg):
        t = time.time()
        valor = msg.payload.decode()
        print(f'{t:.3f}, {valor}')
        writer.writerow([t, valor])
        f.flush()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    print(f'Inscrito no tópico {TOPIC} e salvando em {destino_csv}...')
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print('Encerrando...')
