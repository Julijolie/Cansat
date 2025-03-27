# Comunicação MQTT

### Sem ESP-32

1. Teste publicando uma mensagem:
    
    ```bash
    mosquitto_pub -h test.mosquitto.org -t "estoque/esp32/ibmec" -m "Hola"
    
    ```
    
2. Teste recebendo a mensagem:
    
    ```bash
    mosquitto_sub -h test.mosquitto.org -t "estoque/esp32/ibmec"
    
    ```