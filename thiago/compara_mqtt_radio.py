import matplotlib.pyplot as plt
import csv
import time
import re

def ler_csv_id_tempo(caminho):
    tempos = {}
    ids = []
    regex_id = re.compile(r'ID: (\d+)')
    with open(caminho, newline='') as csvfile:
        leitor = csv.DictReader(csvfile)
        for linha in leitor:
            match = regex_id.search(linha['valor'])
            if match:
                id_msg = int(match.group(1))
                tempos[id_msg] = float(linha['timestamp'])
                ids.append(id_msg)
    return tempos, ids

# Lê os tempos de chegada por ID para cada método
tempos_mqtt, ids_mqtt = ler_csv_id_tempo('dados_mqtt.csv')
tempos_radio, ids_radio = ler_csv_id_tempo('dados_radio.csv')

# Interseção dos IDs presentes nos dois métodos
ids_comuns = sorted(set(ids_mqtt) & set(ids_radio))

deltas = []
for id_msg in ids_comuns:
    delta = tempos_mqtt[id_msg] - tempos_radio[id_msg]
    deltas.append(delta)

# Gráfico 1: Delta de tempo por ID (já existente)
fig, axs = plt.subplots(2, 2, figsize=(16, 10))
axs = axs.flatten()

axs[0].plot(ids_comuns, deltas, marker='o')
axs[0].set_xlabel('ID da Mensagem')
axs[0].set_ylabel('Delta Tempo (MQTT - Rádio) [s]')
axs[0].set_title('1. Diferença de tempo de chegada por mensagem (MQTT vs Rádio)')
axs[0].grid(True)

# Gráfico 2: Histograma do delta de tempo
axs[1].hist(deltas, bins=30, color='skyblue', edgecolor='black')
axs[1].set_xlabel('Delta Tempo (MQTT - Rádio) [s]')
axs[1].set_ylabel('Quantidade de Mensagens')
axs[1].set_title('2. Distribuição do atraso entre MQTT e Rádio')
axs[1].grid(True)

# Gráfico 3: Tempo absoluto de chegada das mensagens (MQTT e Rádio)
tempos_abs_mqtt = [tempos_mqtt[id_msg] for id_msg in ids_comuns]
tempos_abs_radio = [tempos_radio[id_msg] for id_msg in ids_comuns]
axs[2].plot(ids_comuns, tempos_abs_mqtt, label='MQTT', marker='o')
axs[2].plot(ids_comuns, tempos_abs_radio, label='Rádio', marker='x')
axs[2].set_xlabel('ID da Mensagem')
axs[2].set_ylabel('Timestamp de Chegada (s)')
axs[2].set_title('3. Tempo absoluto de chegada das mensagens')
axs[2].legend()
axs[2].grid(True)

# Gráfico 4: Boxplot do delta de tempo
axs[3].boxplot(deltas, vert=True, patch_artist=True, boxprops=dict(facecolor='lightgreen'))
axs[3].set_ylabel('Delta Tempo (MQTT - Rádio) [s]')
axs[3].set_title('4. Boxplot do atraso entre MQTT e Rádio')
axs[3].grid(True)

plt.suptitle('Análise Comparativa: Comunicação MQTT vs Rádio', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# Explicação dos gráficos:
print("""
Gráfico 1: Cada ponto mostra a diferença de tempo (em segundos) entre a chegada da mesma mensagem via MQTT e via rádio, para cada ID. Quanto menor, mais próximos os sistemas.
Gráfico 2: Mostra quantas mensagens tiveram cada valor de atraso. Ajuda a ver se a maioria chega quase junto ou se há atrasos grandes.
Gráfico 3: Mostra o tempo absoluto de chegada das mensagens via MQTT e via rádio, para ver visualmente o 'atraso' acumulado.
Gráfico 4: Boxplot do atraso, mostrando a mediana, quartis e possíveis outliers do delta de tempo.
""")

# --- Cálculo de perda de pacotes ---
ids_radio_set = set(ids_radio)
ids_local_set = set(ler_csv_id_tempo('dados_mqtt_local.csv')[1])
ids_nuvem_set = set(ler_csv_id_tempo('dados_mqtt_nuvem.csv')[1])

perda_local = 1 - (len(ids_local_set & ids_radio_set) / len(ids_radio_set)) if ids_radio_set else float('nan')
perda_nuvem = 1 - (len(ids_nuvem_set & ids_radio_set) / len(ids_radio_set)) if ids_radio_set else float('nan')

print(f"\nPerda de pacotes MQTT Local: {perda_local*100:.2f}%")
print(f"Perda de pacotes MQTT Nuvem: {perda_nuvem*100:.2f}%\n")

# --- Delta de tempo para MQTT Local ---
tempos_mqtt_local, ids_mqtt_local = ler_csv_id_tempo('dados_mqtt_local.csv')
ids_comuns_local = sorted(ids_radio_set & set(ids_mqtt_local))
deltas_local = [tempos_mqtt_local[id_msg] - tempos_radio[id_msg] for id_msg in ids_comuns_local]

# --- Delta de tempo para MQTT Nuvem ---
tempos_mqtt_nuvem, ids_mqtt_nuvem = ler_csv_id_tempo('dados_mqtt_nuvem.csv')
ids_comuns_nuvem = sorted(ids_radio_set & set(ids_mqtt_nuvem))
deltas_nuvem = [tempos_mqtt_nuvem[id_msg] - tempos_radio[id_msg] for id_msg in ids_comuns_nuvem]

# --- Gráficos comparativos ---
fig, axs = plt.subplots(2, 2, figsize=(16, 10))
axs = axs.flatten()

axs[0].plot(ids_comuns_local, deltas_local, marker='o', label='Local')
axs[0].plot(ids_comuns_nuvem, deltas_nuvem, marker='x', label='Nuvem')
axs[0].set_xlabel('ID da Mensagem')
axs[0].set_ylabel('Delta Tempo (MQTT - Rádio) [s]')
axs[0].set_title('1. Diferença de tempo de chegada por mensagem')
axs[0].legend()
axs[0].grid(True)

axs[1].hist(deltas_local, bins=30, alpha=0.7, label='Local')
axs[1].hist(deltas_nuvem, bins=30, alpha=0.7, label='Nuvem')
axs[1].set_xlabel('Delta Tempo (MQTT - Rádio) [s]')
axs[1].set_ylabel('Quantidade de Mensagens')
axs[1].set_title('2. Distribuição do atraso (Local vs Nuvem)')
axs[1].legend()
axs[1].grid(True)

axs[2].bar(['Local', 'Nuvem'], [perda_local*100, perda_nuvem*100], color=['green', 'red'])
axs[2].set_ylabel('Perda de Pacotes (%)')
axs[2].set_title('3. Perda de Pacotes (%)')
axs[2].set_ylim(0, 100)
axs[2].grid(True, axis='y')

axs[3].boxplot([deltas_local, deltas_nuvem], vert=True, patch_artist=True, labels=['Local', 'Nuvem'], boxprops=dict(facecolor='lightblue'))
axs[3].set_ylabel('Delta Tempo (MQTT - Rádio) [s]')
axs[3].set_title('4. Boxplot do atraso (Local vs Nuvem)')
axs[3].grid(True)

plt.suptitle('Comparação: MQTT Local vs Nuvem (Tempo e Perda de Pacotes)', fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# Explicação dos gráficos:
print("""
Gráfico 1: Diferença de tempo de chegada por mensagem (Local e Nuvem).
Gráfico 2: Histograma do atraso para Local e Nuvem.
Gráfico 3: Perda de pacotes (% de mensagens do rádio que não chegaram no MQTT).
Gráfico 4: Boxplot do atraso para Local e Nuvem.
""")