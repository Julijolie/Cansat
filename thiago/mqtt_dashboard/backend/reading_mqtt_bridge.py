import time
import paho.mqtt.client as mqtt
import sys
import json
import re
import csv

# Configuração MQTT
MQTT_BROKER = "broker.hivemq.com"  # Broker público
MQTT_PORT = 1883
MQTT_TOPIC_BASE = "cansat/estacao/teste1"
MQTT_TOPIC_RAW = f"{MQTT_TOPIC_BASE}/raw"

# Tempo para medir latências
last_data_time = 0
mqtt_latencies = []
radio_latencies = []
total_latencies = []

# Arquivo CSV para salvar as medições
OUTPUT_CSV = 'dados_mqtt_dashboard.csv'

# Dicionário para armazenar os últimos valores recebidos
last_values = {}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT")
        # Inscrever-se em todos os tópicos relevantes
        client.subscribe(f"{MQTT_TOPIC_BASE}/#")
        print(f"Inscrito no tópico: {MQTT_TOPIC_BASE}/#")
    else:
        print(f"Falha na conexão com o broker MQTT, código de retorno: {rc}")

def on_message(client, userdata, msg):
    global last_data_time, mqtt_latencies, radio_latencies, total_latencies, last_values
    
    topic = msg.topic
    payload = msg.payload.decode()
    
    # Atualizar o dicionário de últimos valores
    topic_key = topic.replace(f"{MQTT_TOPIC_BASE}/", "")
    last_values[topic_key] = payload
    
    # Se receber o tópico raw, registrar o timestamp para calcular latência de processamento
    if topic == MQTT_TOPIC_RAW:
        last_data_time = time.time() * 1000  # milissegundos
        
    # Registrar latências se estiverem disponíveis
    if topic == f"{MQTT_TOPIC_BASE}/radioLatency" and payload:
        try:
            radio_latencies.append(int(payload))
            # Manter apenas os últimos 100 valores para economia de memória
            if len(radio_latencies) > 100:
                radio_latencies = radio_latencies[-100:]
        except:
            pass
            
    if topic == f"{MQTT_TOPIC_BASE}/mqttLatency" and payload:
        try:
            mqtt_latencies.append(int(payload))
            if len(mqtt_latencies) > 100:
                mqtt_latencies = mqtt_latencies[-100:]
        except:
            pass
            
    if topic == f"{MQTT_TOPIC_BASE}/totalLatency" and payload:
        try:
            total_latencies.append(int(payload))
            if len(total_latencies) > 100:
                total_latencies = total_latencies[-100:]
                
            # Salvar os dados em CSV regularmente
            with open(OUTPUT_CSV, 'a', newline='') as f:
                writer = csv.writer(f)
                # Pegar os valores mais recentes que temos
                data_row = [
                    time.time(),  # Timestamp atual
                    last_values.get('radioLatency', ''),
                    last_values.get('mqttLatency', ''),
                    last_values.get('totalLatency', ''),
                    last_values.get('temperatura', ''),
                    last_values.get('pressao', ''),
                    # Adicionar outros dados conforme necessário
                ]
                writer.writerow(data_row)
                
            # Calcular e mostrar estatísticas periodicamente
            if len(total_latencies) % 10 == 0:  # a cada 10 medidas
                print("\n--- Estatísticas de Latência ---")
                if radio_latencies:
                    print(f"Latência Rádio - Média: {sum(radio_latencies)/len(radio_latencies):.2f}ms, Mín: {min(radio_latencies)}ms, Máx: {max(radio_latencies)}ms")
                if mqtt_latencies:
                    print(f"Latência MQTT - Média: {sum(mqtt_latencies)/len(mqtt_latencies):.2f}ms, Mín: {min(mqtt_latencies)}ms, Máx: {max(mqtt_latencies)}ms")
                if total_latencies:
                    print(f"Latência Total - Média: {sum(total_latencies)/len(total_latencies):.2f}ms, Mín: {min(total_latencies)}ms, Máx: {max(total_latencies)}ms")
                    
        except Exception as e:
            print(f"Erro ao processar latência: {e}")

def main():
    # Configuração do cliente MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Inicializar o arquivo CSV
        with open(OUTPUT_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'radio_latency', 'mqtt_latency', 'total_latency', 'temperatura', 'pressao'])
            
        # Conectar ao broker MQTT
        print(f"Conectando ao broker MQTT: {MQTT_BROKER}")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Loop para manter a conexão MQTT ativa
        client.loop_forever()
                
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        # Limpeza ao sair
        print("Fechando conexões...")
        try:
            client.disconnect()
            print("Desconectado do broker MQTT")
        except:
            pass

if __name__ == "__main__":
    main()
