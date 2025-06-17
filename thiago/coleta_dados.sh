#!/bin/bash

echo "=================================================="
echo "Coleta de Dados de Latência: Rádio vs MQTT"
echo "=================================================="
echo
echo "Este script ajuda a automatizar o workflow de coleta de dados"
echo "para comparar a latência entre transmissão via Rádio e MQTT."
echo
echo "Por favor, certifique-se de que:"
echo "1. O Arduino transmissor está ligado"
echo "2. O Arduino receptor está conectado via USB"
echo
echo "IMPORTANTE: As medições serão feitas na porta serial $1"
echo "Pressione CTRL+C para parar a coleta a qualquer momento."
echo
echo "=================================================="

COM_PORT=$1
if [ -z "$COM_PORT" ]; then
    echo "ERRO: Porta serial não especificada"
    echo "Uso: ./coleta_dados.sh /dev/ttyUSB0"
    exit 1
fi

while true; do
    echo "Selecione uma opção:"
    echo "[1] Iniciar coleta de dados de Rádio (mqtt_sender.py)"
    echo "[2] Iniciar coleta de dados de MQTT (reading_mqtt_bridge.py)"
    echo "[3] Analisar e comparar dados coletados"
    echo "[4] Executar análise detalhada de timestamps"
    echo "[5] Sair"
    echo

    read -p "Digite o número da opção desejada: " OPCAO
    
    case $OPCAO in
        1)
            echo
            echo "Iniciando coleta de dados de Rádio..."
            echo "Executando mqtt_sender.py para coletar dados do receptor via serial..."
            echo "Dados serão salvos em dados_radio.csv"
            echo "Pressione CTRL+C para encerrar a coleta"
            echo
            python mqtt_sender.py
            ;;
        2)
            echo
            echo "Iniciando coleta de dados de MQTT..."
            echo "Executando reading_mqtt_bridge.py para medir latência MQTT..."
            echo "Dados serão salvos em dados_mqtt_dashboard.csv"
            echo "Pressione CTRL+C para encerrar a coleta"
            echo
            python mqtt_dashboard/backend/reading_mqtt_bridge.py
            ;;
        3)
            echo
            echo "Analisando dados coletados..."
            echo "Executando compara_latencia.py..."
            echo "Resultados serão exibidos em um gráfico"
            echo
            python compara_latencia.py
            ;;
        4)
            echo
            echo "Executando análise detalhada de timestamps..."
            echo "Executando analisa_timestamp_arduino.py..."
            echo
            python analisa_timestamp_arduino.py
            
            echo
            echo "Executando análise de latência estimada MQTT..."
            echo "Executando latencia_estimada_mqtt.py..."
            echo
            python latencia_estimada_mqtt.py
            ;;
        5)
            echo
            echo "Encerrando o programa..."
            exit 0
            ;;
        *)
            echo
            echo "Opção inválida. Tente novamente."
            ;;
    esac
done
