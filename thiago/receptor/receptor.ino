#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN
const byte address[6] = "00001";

unsigned long receivedMessages = 0;

struct Payload {
  uint32_t id;
  char msg[24];
};

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();
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
