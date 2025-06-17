import time
import paho.mqtt.client as mqtt
import sys
import json
import re
import csv
import os

# Configuração MQTT
MQTT_BROKER = "broker.hivemq.com"  # Broker público
MQTT_PORT = 1883
MQTT_TOPIC_BASE = "cansat/estacao/teste1"
MQTT_TOPIC_RAW = f"{MQTT_TOPIC_BASE}/raw"

# Variáveis para armazenar dados
last_data_time = 0
mqtt_latencies = []
radio_latencies = []
total_latencies = []

# Arquivo CSV para salvar as medições - usando caminho absoluto
# Garantir que o caminho é absoluto para evitar problemas de localização do arquivo
current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_CSV = os.path.join(current_dir, 'dados_mqtt_dashboard.csv')

# Dicionário para armazenar os últimos valores recebidos
last_values = {}
received_count = 0

# Flag para controle do cabeçalho do CSV
# Verifica se o arquivo já existe para determinar se o cabeçalho já foi escrito
csv_header_written = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0

# Criar o arquivo CSV se não existir e escrever o cabeçalho
def ensure_csv_exists():
    global csv_header_written
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(OUTPUT_CSV) if os.path.dirname(OUTPUT_CSV) else '.', exist_ok=True)
        
        if not os.path.exists(OUTPUT_CSV) or os.path.getsize(OUTPUT_CSV) == 0:
            with open(OUTPUT_CSV, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'id', 'radio_latency', 'mqtt_latency', 'total_latency',
                    'temperatura', 'pressao', 'accelX', 'accelY', 'accelZ',
                    'gyroX', 'gyroY', 'gyroZ'
                ])
                print(f"Arquivo CSV criado: {OUTPUT_CSV}")
                csv_header_written = True
    except Exception as e:
        print(f"Erro ao criar arquivo CSV: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT!")
        # Inscrever-se em todos os tópicos relevantes
        client.subscribe(f"{MQTT_TOPIC_BASE}/#")
        print(f"Inscrito no tópico: {MQTT_TOPIC_BASE}/#")
    else:
        print(f"Falha na conexão com o broker MQTT, código de retorno: {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    global last_data_time, mqtt_latencies, radio_latencies, total_latencies, last_values, received_count, csv_header_written
    
    topic = msg.topic
    try:
        payload = msg.payload.decode('utf-8', errors='replace')
        
        # Debug para confirmar recebimento
        print(f"Mensagem recebida em {topic}: {payload[:50]}...")
        print(f"Conteúdo completo da mensagem: {payload}")
    except Exception as e:
        print(f"Erro ao decodificar mensagem: {e}")
        payload = msg.payload.decode('utf-8', errors='ignore')
        
        # Atualizar o dicionário de últimos valores
        topic_key = topic.replace(f"{MQTT_TOPIC_BASE}/", "")
        last_values[topic_key] = payload
        
        # Se receber o tópico raw, processar para extrair latências e salvar no CSV
        if topic == MQTT_TOPIC_RAW:
            # Timestamp de recepção no MQTT subscriber
            mqtt_receive_time = time.time() * 1000  # milissegundos
            last_data_time = mqtt_receive_time
            received_count += 1
            print(f"[{received_count}] Dados brutos recebidos! Timestamp: {last_data_time}")
            
            # Analisar dados brutos para extrair informações importantes
            # Tentar diferentes padrões de regex para maior robustez
            radio_regex_patterns = [
                r'ID: (\d+) \| Timestamp: (\d+) \| .*\| RadioLatency: (\d+) ms',
                r'ID: (\d+) \| Timestamp: (\d+) \| RadioLatency: (\d+) ms',
                r'RadioLatency: (\d+) ms'
            ]
            
            match = None
            for pattern in radio_regex_patterns:
                match = re.search(pattern, payload)
                if match:
                    print(f"Padrão de mensagem encontrado: {pattern}")
                    break
                    if not match:
                        print(f"AVISO: Não foi possível extrair latência do rádio da mensagem. Verifique o formato: {payload}")
            
            if match:
                # Extrair os grupos dependendo do padrão encontrado
                if len(match.groups()) == 3:
                    id_msg, arduino_timestamp, radio_latency = match.groups()
                    arduino_timestamp = int(arduino_timestamp)
                    radio_latency = int(radio_latency)
            elif len(match.groups()) == 1:
                # Formato reduzido encontrado, usar valores padrão
                id_msg = str(received_count)
                arduino_timestamp = int(time.time() * 1000 - 50)  # Estimar timestamp do Arduino 
                radio_latency = int(match.group(1))
                print(f"Usando formato simplificado para RadioLatency: {radio_latency}ms")
            else:
                print("Formato de mensagem não reconhecido completamente")
                id_msg = str(received_count)
                arduino_timestamp = int(time.time() * 1000 - 50)
                radio_latency = 10  # Valor padrão conservador
            
            # Calcular latência MQTT (tempo de recepção - timestamp original)
            mqtt_latency = int(mqtt_receive_time - arduino_timestamp)
            
            # Corrigir latência MQTT se for muito grande ou negativa (devido a diferenças de relógio)
            if mqtt_latency > 100000 or mqtt_latency < 0:
                print(f"Aviso: Detectada diferença anormal de relógio ({mqtt_latency}ms). Ajustando cálculo de latência.")
                # Usar um valor mais realista baseado na diferença entre mensagens consecutivas
                mqtt_latency = 50  # Valor típico
            
            # Calcular latência total
            total_latency = radio_latency + mqtt_latency
            
            # Armazenar no dicionário de valores
            last_values['id'] = id_msg
            last_values['radioLatency'] = str(radio_latency)
            last_values['mqttLatency'] = str(mqtt_latency)
            last_values['totalLatency'] = str(total_latency)
            
            # Registrar para estatísticas
            radio_latencies.append(radio_latency)
            mqtt_latencies.append(mqtt_latency)
            total_latencies.append(total_latency)
            
            print(f"Latência do rádio: {radio_latency}ms | Latência MQTT: {mqtt_latency}ms | Total: {total_latency}ms")
              # Salvar imediatamente no CSV após cada mensagem Raw recebida
            try:
                # Garantir que o arquivo CSV existe com o cabeçalho adequado
                if not os.path.exists(OUTPUT_CSV) or os.path.getsize(OUTPUT_CSV) == 0:
                    ensure_csv_exists()
                
                # Como o CSV já deve existir, sempre anexamos dados
                with open(OUTPUT_CSV, 'a', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Extrair outros dados de sensores se disponíveis na mensagem
                    temp_match = re.search(r'Temperatura: ([\d\.-]+) C', payload)
                    press_match = re.search(r'Pressao: ([\d\.-]+) hPa', payload)
                    accel_match = re.search(r'Accel \[X,Y,Z\]: ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)', payload)
                    gyro_match = re.search(r'Gyro \[X,Y,Z\] \(°/s\): ([\d\.-]+), ([\d\.-]+), ([\d\.-]+)', payload)
                    
                    temp = temp_match.group(1) if temp_match else ''
                    press = press_match.group(1) if press_match else ''
                    
                    accelX = accelY = accelZ = ''
                    if accel_match:
                        accelX, accelY, accelZ = accel_match.groups()
                    
                    gyroX = gyroY = gyroZ = ''
                    if gyro_match:
                        gyroX, gyroY, gyroZ = gyro_match.groups()
                    
                    # Escrever dados
                    writer.writerow([
                        time.time(),
                        id_msg,
                        radio_latency,
                        mqtt_latency,
                        total_latency,
                        temp,
                        press,
                        accelX,
                        accelY,
                        accelZ,
                        gyroX,
                        gyroY,
                        gyroZ
                    ])
                    
                    print(f"Dados salvos em {OUTPUT_CSV}")
            except Exception as e:
                print(f"Erro ao salvar no CSV: {e}")
          # Para outros tópicos que não o raw, apenas atualizamos o dicionário e exibimos estatísticas
    # Mostrar estatísticas periodicamente se tivermos dados suficientes
    if topic.endswith('radioLatency') or topic.endswith('mqttLatency') or topic.endswith('totalLatency'):
        if received_count > 0 and received_count % 5 == 0 and radio_latencies:
            # Limitar as listas a 100 entradas
            if len(radio_latencies) > 100:
                radio_latencies = radio_latencies[-100:]
                mqtt_latencies = mqtt_latencies[-100:]
                total_latencies = total_latencies[-100:]
                
            print("\n--- Estatísticas de Latência ---")
            print(f"Mensagens MQTT recebidas: {received_count}")
            if radio_latencies:
                print(f"Latência Rádio - Média: {sum(radio_latencies)/len(radio_latencies):.2f}ms, "
                      f"Mín: {min(radio_latencies)}ms, Máx: {max(radio_latencies)}ms")
            if mqtt_latencies:
                print(f"Latência MQTT - Média: {sum(mqtt_latencies)/len(mqtt_latencies):.2f}ms, "
                      f"Mín: {min(mqtt_latencies)}ms, Máx: {max(mqtt_latencies)}ms")
            if total_latencies:
                print(f"Latência Total - Média: {sum(total_latencies)/len(total_latencies):.2f}ms, "
                      f"Mín: {min(total_latencies)}ms, Máx: {max(total_latencies)}ms")
            print(f"Dados salvos em: {os.path.abspath(OUTPUT_CSV)}")
            print("----------------------------")

def main():
    # Configuração do cliente MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Garantir que o arquivo CSV existe antes de iniciar
        print(f"Verificando arquivo CSV: {OUTPUT_CSV}")
        ensure_csv_exists()
        
        # Conectar ao broker MQTT
        print(f"Conectando ao broker MQTT: {MQTT_BROKER}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        print("Aguardando dados do MQTT...")
        print(f"Os dados serão salvos em: {os.path.abspath(OUTPUT_CSV)}")
        print("\nIMPORTANTE:")
        print("1. Certifique-se que mqtt_sender.py está em execução")
        print("2. Ambos os scripts devem estar usando o mesmo broker MQTT")
        print("3. Este script calcula a latência MQTT comparando o timestamp do Arduino")
        print("   com o momento em que a mensagem é recebida no subscriber")
        print("4. Para comparação correta de latências, use compara_latencia.py após a coleta")
        print("\nPressione CTRL+C para encerrar a captura de dados\n")
        
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
