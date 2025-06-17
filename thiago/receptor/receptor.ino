#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN
const byte address[6] = "00001";

unsigned long receivedMessages = 0;

// Struct igual à do transmissor
struct Payload {
  uint32_t id;
  unsigned long timestamp; // Timestamp de envio para medir latência
  float temperature;
  float pressure;
  float accelX, accelY, accelZ;
  float gyroX, gyroY, gyroZ;
} __attribute__((packed));

float velocityX = 0, velocityY = 0, velocityZ = 0;
unsigned long lastTime = 0;

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();
  lastTime = millis();
}

void loop() {
  if (radio.available()) {
    Payload data;
    radio.read(&data, sizeof(data));
    receivedMessages++;

    // Calcular latência (tempo atual - timestamp de envio)
    unsigned long currentTime = millis();
    unsigned long radioLatency = currentTime - data.timestamp;

    Serial.print("ID: "); Serial.print(data.id);
    Serial.print(" | Timestamp: "); Serial.print(data.timestamp);
    Serial.print(" | RadioLatency: "); Serial.print(radioLatency); Serial.print(" ms");
    Serial.print(" | Temperatura: "); Serial.print(data.temperature, 2); Serial.print(" C");
    Serial.print(" | Pressao: "); Serial.print(data.pressure, 2); Serial.print(" hPa");
    Serial.print(" | Accel [X,Y,Z]: "); Serial.print(data.accelX, 3); Serial.print(", "); Serial.print(data.accelY, 3); Serial.print(", "); Serial.print(data.accelZ, 3);
    Serial.print(" | Gyro [X,Y,Z] (°/s): "); Serial.print(data.gyroX, 2); Serial.print(", "); Serial.print(data.gyroY, 2); Serial.print(", "); Serial.print(data.gyroZ, 2);
    Serial.println();
  }
  // Sem delay para garantir máxima disponibilidade
}
