# Comunicação MQTT

### Sem ESP-32

#### No broker test.mosquitto.org
1. Teste publicando uma mensagem:
    
    ```bash
    mosquitto_pub -h test.mosquitto.org -t "estoque/esp32/ibmec" -m "Hola"
    
    ```
    
2. Teste recebendo a mensagem:
    
    ```bash
    mosquitto_sub -h test.mosquitto.org -t "estoque/esp32/ibmec"
    
    ```
#### No broker localhost
1. Teste publicando uma mensagem:
    
    ```bash
    mosquitto_pub -h localhost -t "estoque/esp32/ibmec" -m "Hola"
    
    ```
    
2. Teste recebendo a mensagem:
    
    ```bash
    mosquitto_sub -h localhost -t "estoque/esp32/ibmec"
    
    ```