#include <HardwareSerial.h>
#include <WiFi.h>
#include <PubSubClient.h>

#define RXD2 19  // RX do ESP32 (Conecte ao TX do LoRa)
#define TXD2 18  // TX do ESP32 (Conecte ao RX do LoRa)

HardwareSerial LoRaSerial(1);  // Criando uma instância da serial 1 para LoRa

// Credenciais Wi-Fi
const char* ssid = "Juli";
const char* password = "bolo1234678";

// Configurações MQTT
const char* mqttServer = "test.mosquitto.org"; // Servidor MQTT
const int mqttPort = 1883; // Porta do MQTT
WiFiClient espClient; // Cliente Wi-Fi
PubSubClient client(espClient); // Cliente MQTT

void setup() {
  Serial.begin(115200); // Inicializa a Serial do ESP32 (Monitor Serial)
  LoRaSerial.begin(9600, SERIAL_8N1, RXD2, TXD2); // Inicializa a comunicação com LoRa

  // Conecta ao Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando ao Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Conectado ao Wi-Fi!");

  // Conecta ao servidor MQTT
  client.setServer(mqttServer, mqttPort);
  while (!client.connected()) {
    Serial.print("Conectando ao MQTT...");
    if (client.connect("ESP32LoRaClient")) {
      Serial.println(" Conectado ao MQTT!");
    } else {
      Serial.print("Falha, erro: ");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void loop() {
  // Verifica se há dados no LoRa
  if (LoRaSerial.available()) {
    String mensagem = LoRaSerial.readString(); // Lê a mensagem recebida do LoRa
    Serial.print("Mensagem Recebida do LoRa: ");
    Serial.println(mensagem); // Exibe a mensagem no Monitor Serial

    // Publica a mensagem no MQTT
    if (client.publish("ibmec/topico/mqtt", mensagem.c_str())) {
      Serial.println("Mensagem enviada ao MQTT!");
    } else {
      Serial.println("Falha ao enviar mensagem ao MQTT.");
    }
  }

  client.loop(); // Mantém a conexão com o MQTT
  delay(20); // Pequena pausa
}
