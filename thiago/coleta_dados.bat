@echo off
echo ==================================================
echo Coleta de Dados de Latencia: Radio vs MQTT
echo ==================================================
echo.
echo Este script ajuda a automatizar o workflow de coleta de dados
echo para comparar a latencia entre transmissao via Radio e MQTT.
echo.
echo Por favor, certifique-se de que:
echo 1. O Arduino transmissor esta ligado
echo 2. O Arduino receptor esta conectado via USB
echo.
echo IMPORTANTE: As medicoes serao feitas na porta serial %1
echo Pressione CTRL+C para parar a coleta a qualquer momento.
echo.
echo ==================================================

SET COM_PORT=%1
if "%COM_PORT%"=="" (
    echo ERRO: Porta COM nao especificada
    echo Uso: coleta_dados.bat COM8
    exit /b
)

:MENU
echo Selecione uma opcao:
echo [1] Iniciar coleta de dados de Radio (mqtt_sender.py)
echo [2] Iniciar coleta de dados de MQTT (reading_mqtt_bridge.py)
echo [3] Analisar e comparar dados coletados
echo [4] Executar analise detalhada de timestamps
echo [5] Sair
echo.

SET /P OPCAO="Digite o numero da opcao desejada: "

if "%OPCAO%"=="1" (
    echo.
    echo Iniciando coleta de dados de Radio...
    echo Executando mqtt_sender.py para coletar dados do receptor via serial...
    echo Dados serao salvos em dados_radio.csv
    echo Pressione CTRL+C para encerrar a coleta
    echo.
    python mqtt_sender.py
    goto MENU
)

if "%OPCAO%"=="2" (
    echo.
    echo Iniciando coleta de dados de MQTT...
    echo Executando reading_mqtt_bridge.py para medir latencia MQTT...
    echo Dados serao salvos em dados_mqtt_dashboard.csv
    echo Pressione CTRL+C para encerrar a coleta
    echo.
    python mqtt_dashboard/backend/reading_mqtt_bridge.py
    goto MENU
)

if "%OPCAO%"=="3" (
    echo.
    echo Analisando dados coletados...
    echo Executando compara_latencia.py...
    echo Resultados serao exibidos em um grafico
    echo.
    python compara_latencia.py
    goto MENU
)

if "%OPCAO%"=="4" (
    echo.
    echo Executando analise detalhada de timestamps...
    echo Executando analisa_timestamp_arduino.py...
    echo.
    python analisa_timestamp_arduino.py
    
    echo.
    echo Executando analise de latencia estimada MQTT...
    echo Executando latencia_estimada_mqtt.py...
    echo.
    python latencia_estimada_mqtt.py
    goto MENU
)

if "%OPCAO%"=="5" (
    echo.
    echo Encerrando o programa...
    exit /b
) else (
    echo.
    echo Opcao invalida. Tente novamente.
    goto MENU
)
