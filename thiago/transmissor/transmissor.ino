#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Wire.h>
#include <Adafruit_BMP085.h> // Biblioteca para BMP180
#include <MPU6050.h>         // Biblioteca para GY-521 (MPU6050)

RF24 radio(9, 10); // CE, CSN
const byte address[6] = "00001";

unsigned long sentMessages = 0;

Adafruit_BMP085 bmp;
MPU6050 mpu;

// Nova struct para payload com dados dos sensores
struct Payload {
  uint32_t id;
  float temperature;
  float pressure;
  float accelX, accelY, accelZ;
  float gyroX, gyroY, gyroZ;
} __attribute__((packed));

float velocityX = 0, velocityY = 0, velocityZ = 0;
float lastAccelX = 0, lastAccelY = 0, lastAccelZ = 0;
unsigned long lastTime = 0;

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_MIN);
  radio.setRetries(3, 5);
  radio.stopListening();

  // Inicializa BMP180
  if (!bmp.begin()) {
    Serial.println("BMP180 não encontrado!");
    while (1);
  }
  // Inicializa MPU6050
  Wire.begin();
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 não encontrado!");
    while (1);
  }
  lastTime = millis();
}

void loop() {
  Payload data;
  data.id = sentMessages;
  // Leitura BMP180
  data.temperature = bmp.readTemperature();
  data.pressure = bmp.readPressure() / 100.0; // hPa
  // Leitura MPU6050
  data.accelX = mpu.getAccelerationX() / 16384.0;
  data.accelY = mpu.getAccelerationY() / 16384.0;
  data.accelZ = mpu.getAccelerationZ() / 16384.0;
  data.gyroX = mpu.getRotationX() / 131.0;
  data.gyroY = mpu.getRotationY() / 131.0;
  data.gyroZ = mpu.getRotationZ() / 131.0;

  bool success = radio.write(&data, sizeof(data));
  if (success) {
    sentMessages++;
    Serial.print("ID: "); Serial.print(data.id);
    Serial.print(" | Temperatura: "); Serial.print(data.temperature, 2); Serial.print(" C");
    Serial.print(" | Pressao: "); Serial.print(data.pressure, 2); Serial.print(" hPa");
    Serial.print(" | Accel [X,Y,Z]: "); Serial.print(data.accelX, 3); Serial.print(", "); Serial.print(data.accelY, 3); Serial.print(", "); Serial.print(data.accelZ, 3);
    Serial.print(" | Gyro [X,Y,Z] (°/s): "); Serial.print(data.gyroX, 2); Serial.print(", "); Serial.print(data.gyroY, 2); Serial.print(", "); Serial.print(data.gyroZ, 2);
    Serial.println();
  } else {
    Serial.println("Falha no envio, tentando novamente...");
  }
  delay(1000); // 1 segundo para garantir tempo de processamento
}
