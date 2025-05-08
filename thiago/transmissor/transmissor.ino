#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN
const byte address[6] = "00001";

unsigned long sentMessages = 0;
unsigned long ackMessages = 0;

struct Payload {
  uint32_t id;
  char msg[24];
};

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_MIN);
  radio.setRetries(3, 5); // tenta 3 vezes, delay de 5*250us
  radio.stopListening();
}

void loop() {
  Payload data;
  data.id = sentMessages;
  snprintf(data.msg, sizeof(data.msg), "Hello World %lu", sentMessages);

  bool success = radio.write(&data, sizeof(data));
  sentMessages++;

  if (success) {
    ackMessages++;
    Serial.print("Enviado e ACK recebido: ");
  } else {
    Serial.print("Falha no envio (sem ACK): ");
  }

  Serial.print(data.msg);
  Serial.print(" | Total: ");
  Serial.print(sentMessages);
  Serial.print(" | Recebidos: ");
  Serial.print(ackMessages);
  Serial.print(" | Perda: ");
  Serial.print(100.0 * (sentMessages - ackMessages) / sentMessages);
  Serial.println(" %");

  delay(1000);
}
