// Definovanie pinov pre LED diódy
const int ledPin1 = 9;  // cervena
const int ledPin2 = 10; // zlta
const int ledPin3 = 11; // zelena
const int ledPin4 = 8;  // LED pre ovládanie z webu

// Definovanie analógových vstupov
const int photoResistorPin = A0;

// Premenné na uloženie hodnôt analógových vstupov
int photoResistorValue = 0;
bool clientConnected = false;
bool ledState = false;

void setup() {
  // Nastavenie pinov LED ako výstupných
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  pinMode(ledPin4, OUTPUT); // LED pre ovládanie z webu

  // Nastavenie sériovej komunikácie pre monitorovanie (voliteľné)
  Serial.begin(9600);
}

void loop() {
  // Prečítanie hodnôt z analógových vstupov
  photoResistorValue = analogRead(photoResistorPin);

  // Vypísanie hodnoty fotorezistora do sériového monitoru (voliteľné)
  Serial.println(photoResistorValue);

  // Na základe hodnoty potenciometra nastavujeme intenzitu LED diód
  int pwmValue = map(photoResistorValue, 0, 1025, 255, 0);
  analogWrite(ledPin2, pwmValue);

  if (photoResistorValue > 900) {
    digitalWrite(ledPin1, HIGH);
  } else if (photoResistorValue < 150) {
    digitalWrite(ledPin1, HIGH);
  } else {
    digitalWrite(ledPin1, LOW);
  }

  // Ak je klient pripojený, rozsvieti sa LED na pine číslo 11, inak sa zhasne
  if (clientConnected) {
    digitalWrite(ledPin3, HIGH);
  } else {
    digitalWrite(ledPin3, LOW);
  }

  // Spracovanie seriových príkazov
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();
    if (receivedChar == 'O') {
      clientConnected = false;
    } else if (receivedChar == 'C') {
      clientConnected = true;
    } else if (receivedChar == 'T') {
      ledState = !ledState;  // Prepnúť stav LED
      digitalWrite(ledPin4, ledState ? HIGH : LOW);  // Nastavenie LED podľa nového stavu
    }
  }
  delay(1000);
}
