#include <WiFi.h>
#include <PubSubClient.h>

// Definições da comunicação com o LoRa
#define RXD2 19  // RX do ESP32 (Conecte ao TX do LoRa)
#define TXD2 18  // TX do ESP32 (Conecte ao RX do LoRa)

HardwareSerial LoRa(2);

// Configuração do Wi-Fi
const char* ssid = "SUA_REDE_WIFI";
const char* password = "SUA_SENHA_WIFI";

// Configuração do broker MQTT
const char* mqtt_server = "test.mosquitto.org";
WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
    Serial.begin(115200);
    LoRa.begin(9600, SERIAL_8N1, RXD2, TXD2); // Inicia a comunicação LoRa no Serial2

    // Conectar ao Wi-Fi
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
        if (client.connect("ESP32_LoRa_Client")) {
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
        client.connect("ESP32_LoRa_Client");
    }

    // Verifica se recebeu mensagem via LoRa
    if (LoRa.available()) {
        String receivedData = LoRa.readString();
        Serial.print("Recebido via LoRa: ");
        Serial.println(receivedData);

        // Publica a mensagem no tópico MQTT
        client.publish("meu/topico/lora", receivedData.c_str());
        Serial.println("Mensagem enviada para MQTT!");
    }

    client.loop();
}
