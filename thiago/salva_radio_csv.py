import serial
import time
import csv

# Configuração da porta serial (ajuste conforme necessário)
SERIAL_PORT = 'COM3'  # Altere para a porta correta do seu receptor
BAUDRATE = 9600

# Nome do arquivo CSV de saída
destino_csv = 'dados_radio.csv'

with open(destino_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'valor'])  # Cabeçalho
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    print(f'Lendo dados do receptor em {SERIAL_PORT} e salvando em {destino_csv}...')
    try:
        while True:
            linha = ser.readline().decode(errors='ignore').strip()
            if not linha:
                continue
            t = time.time()
            print(f'{t:.3f}, {linha}')
            writer.writerow([t, linha])
            f.flush()
    except KeyboardInterrupt:
        print('Encerrando...')
    finally:
        ser.close()
