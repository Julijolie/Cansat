#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// Pinos do ESP8266 (NodeMCU)
#define CE_PIN 4    // GPIO4 = D2
#define CSN_PIN 15  // GPIO15 = D8

RF24 radio(CE_PIN, CSN_PIN); // CE, CSN
const byte address[6] = "00001";

unsigned long receivedMessages = 0;

struct Payload {
  uint32_t id;
  char msg[24];
} __attribute__((packed));

void setup() {
  Serial.begin(115200); // Velocidade maior no ESP8266
  delay(100); // Pequeno delay para estabilizar a porta serial

  if (!radio.begin()) {
    Serial.println("Erro ao iniciar o rádio!");
    while (1); // Trava se não iniciar corretamente
  }

  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_MIN); // Potência mínima
  radio.startListening();
  radio.setDataRate(RF24_250KBPS);  // ou RF24_1MBPS


  Serial.println("Receptor iniciado...");
}

void loop() {
  if (radio.available()) {
    Payload data;
    radio.read(&data, sizeof(data));
    receivedMessages++;

    Serial.print("Recebido: ");
    Serial.print(data.msg);
    Serial.print(" | ID: ");
    Serial.print(data.id);
    Serial.print(" | Total Recebido: ");
    Serial.println(receivedMessages);
  }
}
