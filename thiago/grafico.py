import csv
import matplotlib.pyplot as plt

# Listas para armazenar os dados
totais = []
recebidos = []
perdas = []

# Abrir o CSV
with open('dados.csv', newline='') as csvfile:
    leitor = csv.DictReader(csvfile)
    for linha in leitor:
        try:
            totais.append(int(linha['Total']))
            recebidos.append(int(linha['Recebidos']))
            perdas.append(float(linha['Perda']))
        except ValueError:
            # Pula linhas mal formatadas
            continue

# Plotar gráfico
plt.figure(figsize=(10, 6))
plt.plot(totais, perdas, marker='o', color='red', label='Perda de Pacotes (%)')

plt.xlabel('Mensagens Enviadas (Total)')
plt.ylabel('Perda (%)')
plt.title('Gráfico de Perda de Pacotes - Comunicação nRF24L01')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
