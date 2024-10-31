#define LED_LARANJA 3  // LED laranja na porta 3
#define SENSOR_FLUXO 2  // Pino na porta 2

#define MUITO_FLUXO 7  // Fluxo alto

unsigned long pulsoAnterior = 0;
float taxaFluxo = 0;
volatile unsigned int pulsos = 0;  // Contagem de pulsos

void setup() {
  Serial.begin(9600);

  // Configura o LED laranja
  pinMode(LED_LARANJA, OUTPUT);
  digitalWrite(LED_LARANJA, LOW);  // LED começa apagado

  // Configura o sensor de fluxo como entrada
  pinMode(SENSOR_FLUXO, INPUT);
  attachInterrupt(digitalPinToInterrupt(SENSOR_FLUXO), contaPulso, RISING);
}

void loop() {
  unsigned long tempoAtual = millis();

  // Verifica se passou 1 segundo desde a última leitura
  if (tempoAtual - pulsoAnterior >= 1000) {
    taxaFluxo = calcularFluxo();

    // Acende o LED laranja se o fluxo for alto
    if (taxaFluxo >= MUITO_FLUXO) {
      digitalWrite(LED_LARANJA, HIGH);  // Liga o LED quando tá com fluxo alto
    } else {
      digitalWrite(LED_LARANJA, LOW);  // Apaga o LED quando o fluxo deixa de ser considerado alto
    }

    // Exibe a taxa de fluxo no Serial Monitor
    Serial.print("Taxa de fluxo: ");
    Serial.println(taxaFluxo);

    // Reinicia o contador para o próximo intervalo
    pulsoAnterior = tempoAtual;
  }
}

void contaPulso() {
  // Debounce para evitar leituras duplicadas
  static unsigned long ultimaInterrupcao = 0;
  unsigned long tempoAtual = millis();

  if (tempoAtual - ultimaInterrupcao > 10) {
    pulsos++;
    ultimaInterrupcao = tempoAtual;
  }
}

float calcularFluxo() {
  // Calcula a taxa de fluxo 
  float taxa = pulsos * 0.1; 
  pulsos = 0;  // Reseta a contagem para o próximo intervalo
  return taxa;
}
