#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Juli";      // Nome da rede Wi-Fi
const char* password = "bolo1234678"; // Senha do Wi-Fi
const char* mqtt_server = "test.mosquitto.org"; // Broker MQTT

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
    Serial.begin(115200);
    
    // Conectando ao Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWi-Fi conectado!");

    // Conectar ao broker MQTT
    client.setServer(mqtt_server, 1883);
    while (!client.connected()) {
        Serial.print("Conectando ao MQTT...");
        if (client.connect("ESP32_Client")) {
            Serial.println("Conectado!");
        } else {
            Serial.print("Falha, rc=");
            Serial.print(client.state());
            Serial.println(" Tentando novamente em 5 segundos...");
            delay(5000);
        }
    }
}

void loop() {
    if (!client.connected()) {
        client.connect("ESP32_Client");
    }

    // Publicando mensagem no tópico
    client.publish("teste/topico/esp32/ibmec", "Mensagem do ESP32!");
    Serial.println("Mensagem enviada!");

    delay(2000); // Enviar a cada 2 segundos
}
