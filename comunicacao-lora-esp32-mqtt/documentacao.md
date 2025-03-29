# Experimento lora - esp32 - mosquitto

### Lora - esp32
- O código feito para utilizar o esp32 com o lora foi reutilizado do usado com o arduiono UNO. Como mostrado na documentação e no código provido pelo professor.
- [Link do site para código fonte](https://osoyoo.com/2018/07/26/osoyoo-lora-tutorial-how-to-use-the-uart-lora-module-with-arduino/)

- Após as conexões serem refeitas e os módulos de placas trocadas o código rodou perfeitamente. Possibilitando usar o ESP32 no lugar do arduino uno.

### esp32 - 3º computador
- Após a conexão entre o receptor e transmissor usando o protocolo P2P foi estabelecida usando o ESP32 foi utilizado o código já utilizado antes para usar o ESP32 como publisher usando o protocolo MQTT.
- Utilizando a biblioteca pub_sub_client no arduino IDE foi possível transmitir as informações passadas pelo lora diretamente para outro dispositivo usando MQTT.

### Vantangens desse modelo
- Utilizando esse modelo é possível facilitar o processo de transmitir as informações que chegam na estação de solo direto para outro aparelho, podendo ser um telefone ou outro computador.

- [Diagrama Comunicação](http://github.com/Julijolie/Cansat/blob/main/assets/modeloesploramqtt.jpg)
