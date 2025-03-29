#include <HardwareSerial.h>

#define RXD2 19 
#define TXD2 18 

HardwareSerial LoRaSerial(1);  

void setup() {
  Serial.begin(115200);   
  LoRaSerial.begin(9600, SERIAL_8N1, RXD2, TXD2);
  
  Serial.println("ESP32 pronto para receber mensagens do LoRa!");
}

void loop() {
  if (LoRaSerial.available()) 
    String mensagem = LoRaSerial.readString(); 
    Serial.print("Mensagem Recebida do LoRa: ");
    Serial.println(mensagem); 
  }

  delay(20); 
}
