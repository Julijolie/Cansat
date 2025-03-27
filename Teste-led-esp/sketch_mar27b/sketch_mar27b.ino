#define LED_BUILTIN 2  // Pino do LED embutido (ESP32)

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);  // Configura o pino como saída
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);  // Liga o LED
  delay(1000);                      // Espera 1 segundo
  digitalWrite(LED_BUILTIN, LOW);   // Desliga o LED
  delay(1000);                      // Espera 1 segundo
}
