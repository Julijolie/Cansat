#include <HardwareSerial.h>
#include <WiFi.h>
#include <PubSubClient.h>

#define RXD2 19  
#define TXD2 18  

HardwareSerial LoRaSerial(1);  


const char* ssid = "Juli";
const char* password = "bolo1234678";

const char* mqttServer = "test.mosquitto.org"; 
const int mqttPort = 1883; 
WiFiClient espClient; 
PubSubClient client(espClient); 

void setup() {
  Serial.begin(115200); 
  LoRaSerial.begin(9600, SERIAL_8N1, RXD2, TXD2); 

  WiFi.begin(ssid, password);
  Serial.print("Conectando ao Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Conectado ao Wi-Fi!");

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

  if (LoRaSerial.available()) {
    String mensagem = LoRaSerial.readString(); 
    Serial.print("Mensagem Recebida do LoRa: ");
    Serial.println(mensagem); 


    if (client.publish("estoque/esp32/ibmec", mensagem.c_str())) {
      Serial.println("Mensagem enviada ao MQTT!");
    } else {
      Serial.println("Falha ao enviar mensagem ao MQTT.");
    }
  }

  client.loop(); 
  delay(20); 
}