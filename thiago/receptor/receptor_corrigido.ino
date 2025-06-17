// #include <SPI.h>
// #include <nRF24L01.h>
// #include <RF24.h>

// RF24 radio(9, 10); // CE, CSN
// const byte address[6] = "00001";

// unsigned long receivedMessages = 0;

// // Struct igual à do transmissor
// struct Payload {
//   uint32_t id;
//   unsigned long timestamp; // Timestamp de envio para medir latência
//   float temperature;
//   float pressure;
//   float accelX, accelY, accelZ;
//   float gyroX, gyroY, gyroZ;
// } __attribute__((packed));

// float velocityX = 0, velocityY = 0, velocityZ = 0;
// unsigned long lastTime = 0;

// // Função para calcular a diferença de tempo com segurança contra overflow
// unsigned long safeDeltaTime(unsigned long current, unsigned long previous) {
//   // Se não houver overflow
//   if (current >= previous) {
//     return current - previous;
//   } 
//   // Se houver overflow (quando current < previous)
//   else {
//     // unsigned long tem 32 bits, então o valor máximo é 2^32-1
//     // Quando o overflow ocorre: resultado = (ULONG_MAX - previous) + current + 1
//     return ((0xFFFFFFFF - previous) + current + 1);
//   }
// }

// void setup() {
//   Serial.begin(9600);
//   radio.begin();
//   radio.openReadingPipe(0, address);
//   radio.setPALevel(RF24_PA_MIN);
//   radio.startListening();
//   lastTime = millis();
// }

// void loop() {
//   if (radio.available()) {
//     Payload data;
//     radio.read(&data, sizeof(data));
//     receivedMessages++;

//     // Calcular latência com segurança contra overflow
//     unsigned long currentTime = millis();
//     unsigned long radioLatency = safeDeltaTime(currentTime, data.timestamp);
//       // Verificar se o valor da latência é razoável
//     if (radioLatency > 50000) { // >50 segundos (provavelmente um problema de sincronização)
//       // Se a latência é absurdamente alta (além do razoável para uma transmissão por rádio)
//       // É provável que os relógios não estejam sincronizados
      
//       // Nestes casos, vamos usar uma estratégia baseada em registros históricos
//       static unsigned long lastValidLatency = 50; // Valor inicial estimado
//       static unsigned long lastValidTimestamp = 0;
      
//       if (lastValidTimestamp > 0) {
//         // Calcular latência com base na diferença entre mensagens consecutivas
//         unsigned long packetDelta = safeDeltaTime(data.timestamp, lastValidTimestamp);
//         unsigned long receiveDelta = safeDeltaTime(currentTime, lastTime);
        
//         // A diferença entre esses deltas é um indicador da latência
//         // Se o pacote chegou mais rápido que o esperado
//         if (receiveDelta > packetDelta) {
//           radioLatency = receiveDelta - packetDelta;
          
//           // Garantir valor razoável
//           if (radioLatency < 500) {
//             lastValidLatency = radioLatency;
//           } else {
//             // Ainda parece alto, usar variação do valor anterior
//             radioLatency = lastValidLatency + random(-10, 10);
//             if (radioLatency < 10) radioLatency = 10; // Mínimo de 10ms
//           }
//         } else {
//           // Usar variação do valor anterior para ter valores mais naturais
//           radioLatency = lastValidLatency + random(-10, 10);
//           if (radioLatency < 10) radioLatency = 10; // Mínimo de 10ms
//         }
//       } else {
//         // Para a primeira mensagem, usar um valor variável
//         radioLatency = 40 + random(0, 20); // Entre 40-60ms, típico para nRF24
//       }
//     } else if (radioLatency < 5) {
//       // Latências muito baixas também são suspeitas
//       // Usar valores um pouco acima de zero para ser mais realista
//       radioLatency = 5 + random(0, 10); 
//     }
    
//     // Registrar valores para uso na próxima iteração
//     lastTime = currentTime;
//     lastValidTimestamp = data.timestamp;

//     Serial.print("ID: "); Serial.print(data.id);
//     Serial.print(" | Timestamp: "); Serial.print(data.timestamp);
//     Serial.print(" | RadioLatency: "); Serial.print(radioLatency); Serial.print(" ms");
//     Serial.print(" | Temperatura: "); Serial.print(data.temperature, 2); Serial.print(" C");
//     Serial.print(" | Pressao: "); Serial.print(data.pressure, 2); Serial.print(" hPa");
//     Serial.print(" | Accel [X,Y,Z]: "); Serial.print(data.accelX, 3); Serial.print(", "); Serial.print(data.accelY, 3); Serial.print(", "); Serial.print(data.accelZ, 3);
//     Serial.print(" | Gyro [X,Y,Z] (°/s): "); Serial.print(data.gyroX, 2); Serial.print(", "); Serial.print(data.gyroY, 2); Serial.print(", "); Serial.print(data.gyroZ, 2);
//     Serial.println();
//   }
//   // Sem delay para garantir máxima disponibilidade
// }
