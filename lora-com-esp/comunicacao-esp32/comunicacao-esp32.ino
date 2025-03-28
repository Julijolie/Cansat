#include <HardwareSerial.h>

#define RXD2 19  // RX do ESP32 (Conecte ao TX do LoRa)
#define TXD2 18  // TX do ESP32 (Conecte ao RX do LoRa)

HardwareSerial LoRaSerial(1);  // Criando uma instância da serial 1

void setup() {
  Serial.begin(115200);  // Inicializa a Serial do ESP32 (para Monitor Serial)
  LoRaSerial.begin(9600, SERIAL_8N1, RXD2, TXD2); // Inicializa a comunicação com LoRa
  
  Serial.println("ESP32 pronto para receber mensagens do LoRa!");
}

void loop() {
  if (LoRaSerial.available()) { // Se houver dados na Serial do LoRa
    String mensagem = LoRaSerial.readString(); // Lê a mensagem recebida
    Serial.print("Mensagem Recebida do LoRa: ");
    Serial.println(mensagem); // Exibe a mensagem no Monitor Serial
  }

  delay(20); // Pequena pausa para estabilidade
}
