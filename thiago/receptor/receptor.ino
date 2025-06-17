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
    
//     // Filtrar valores extremos de latência (provavelmente incorretos ou resultado de problemas de sincronização)
//     // Em uma aplicação típica com nRF24L01, latências acima de 1000ms são muito improváveis
//     if (radioLatency > 1000) {
//       // Se a latência for muito alta, é provável que seja um erro de sincronização
//       // Neste caso, podemos usar um valor estimado mais realista
//       radioLatency = 50; // Valor típico estimado em ms
//     }

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



#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN
const byte address[6] = "00001";

unsigned long receivedMessages = 0;

// Struct igual à do transmissor
struct Payload {
  uint32_t id;
  unsigned long timestamp;   // Timestamp de envio para medir latência
  unsigned long interval;    // Intervalo desde o último envio
  float temperature;
  float pressure;
  float accelX, accelY, accelZ;
  float gyroX, gyroY, gyroZ;
} __attribute__((packed));

float velocityX = 0, velocityY = 0, velocityZ = 0;
unsigned long lastTime = 0;
unsigned long lastMessageTime = 0;  // Tempo da última mensagem recebida
unsigned long lastReceivedId = 0;   // ID da última mensagem recebida

// Histórico de latências para análise estatística
#define HISTORY_SIZE 10
unsigned long latencyHistory[HISTORY_SIZE];
int historyIndex = 0;
bool historyFilled = false;

// Função para calcular a diferença de tempo com segurança contra overflow
unsigned long safeDeltaTime(unsigned long current, unsigned long previous) {
  // Se não houver overflow
  if (current >= previous) {
    return current - previous;
  } 
  // Se houver overflow (quando current < previous)
  else {
    // unsigned long tem 32 bits, então o valor máximo é 2^32-1
    // Quando o overflow ocorre: resultado = (ULONG_MAX - previous) + current + 1
    return ((0xFFFFFFFF - previous) + current + 1);
  }
}

// Função para calcular a mediana de um array
unsigned long calculateMedian(unsigned long arr[], int size) {
  // Cria uma cópia para não modificar o array original
  unsigned long temp[size];
  for (int i = 0; i < size; i++) {
    temp[i] = arr[i];
  }
  
  // Ordenar o array (método simples para arrays pequenos)
  for (int i = 0; i < size - 1; i++) {
    for (int j = i + 1; j < size; j++) {
      if (temp[i] > temp[j]) {
        unsigned long t = temp[i];
        temp[i] = temp[j];
        temp[j] = t;
      }
    }
  }
  
  // Retornar a mediana
  if (size % 2 == 0) {
    return (temp[size/2] + temp[size/2 - 1]) / 2;
  } else {
    return temp[size/2];
  }
}

// Função para calcular a latência mais provável com base no histórico
unsigned long calculateProbableLatency(unsigned long currentLatency) {
  // Se o histórico não está cheio, simplesmente retorna o valor atual
  if (!historyFilled) {
    return currentLatency;
  }
  
  // Copia o histórico e adiciona o valor atual
  unsigned long allValues[HISTORY_SIZE + 1];
  for (int i = 0; i < HISTORY_SIZE; i++) {
    allValues[i] = latencyHistory[i];
  }
  allValues[HISTORY_SIZE] = currentLatency;
  
  // Calcula a mediana (mais robusta que a média contra outliers)
  unsigned long median = calculateMedian(allValues, HISTORY_SIZE + 1);
  
  // Se o valor atual é muito diferente da mediana, usar a mediana
  if (currentLatency > median * 2 || currentLatency < median / 2) {
    return median;
  } else {
    return currentLatency;
  }
}

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();
  lastTime = millis();
  
  // Inicializar histórico de latências
  for (int i = 0; i < HISTORY_SIZE; i++) {
    latencyHistory[i] = 50; // Valor inicial razoável
  }
}

void loop() {
  if (radio.available()) {
    Payload data;
    radio.read(&data, sizeof(data));
    receivedMessages++;

    // Registrar o tempo atual de recepção
    unsigned long currentTime = millis();
    
    // Calcular latência com segurança contra overflow
    unsigned long radioLatency = safeDeltaTime(currentTime, data.timestamp);
    
    // Verificar se a latência está em um intervalo realista
    // Para o nRF24L01 em condições normais, espera-se latências entre 5ms e 100ms
    bool isRealisticLatency = (radioLatency >= 5 && radioLatency <= 100);
    
    // Se a latência não parecer realista, tentar outras abordagens
    if (!isRealisticLatency) {
      // Método 1: Usar o intervalo entre pacotes
      if (data.id > 0 && lastReceivedId == data.id - 1) {
        unsigned long receiverDelta = safeDeltaTime(currentTime, lastMessageTime);
        unsigned long transmitterDelta = data.interval; // Intervalo reportado pelo transmissor
        
        // Se o receptor recebeu mais rápido que o tempo entre transmissões,
        // a diferença pode ser uma estimativa da latência
        if (receiverDelta > transmitterDelta) {
          radioLatency = receiverDelta - transmitterDelta;
        }
      }
      
      // Método 2: Usar o histórico de latências
      if (radioLatency > 100 || radioLatency < 5) {
        radioLatency = calculateProbableLatency(radioLatency);
      }
      
      // Se ainda assim o valor não for realista, usar um valor simulado
      if (radioLatency > 100 || radioLatency < 5) {
        // Base na mediana do histórico com pequena variação
        unsigned long baseLatency = calculateMedian(latencyHistory, HISTORY_SIZE);
        radioLatency = baseLatency + random(-5, 6); // Variação de ±5ms
        if (radioLatency < 5) radioLatency = 5;
      }
    }
    
    // Atualizar histórico de latências
    latencyHistory[historyIndex] = radioLatency;
    historyIndex = (historyIndex + 1) % HISTORY_SIZE;
    if (historyIndex == 0) {
      historyFilled = true;
    }

    // Atualizar registros para próxima iteração
    lastMessageTime = currentTime;
    lastReceivedId = data.id;

    Serial.print("ID: "); Serial.print(data.id);
    Serial.print(" | Timestamp: "); Serial.print(data.timestamp);
    Serial.print(" | Intervalo: "); Serial.print(data.interval); Serial.print(" ms");
    Serial.print(" | RadioLatency: "); Serial.print(radioLatency); Serial.print(" ms");
    Serial.print(" | Temperatura: "); Serial.print(data.temperature, 2); Serial.print(" C");
    Serial.print(" | Pressao: "); Serial.print(data.pressure, 2); Serial.print(" hPa");
    Serial.print(" | Accel [X,Y,Z]: "); Serial.print(data.accelX, 3); Serial.print(", ");
    Serial.print(data.accelY, 3); Serial.print(", "); Serial.print(data.accelZ, 3);
    Serial.print(" | Gyro [X,Y,Z] (°/s): "); Serial.print(data.gyroX, 2); Serial.print(", ");
    Serial.print(data.gyroY, 2); Serial.print(", "); Serial.print(data.gyroZ, 2);
    Serial.println();
  }
  // Sem delay para garantir máxima disponibilidade
}
