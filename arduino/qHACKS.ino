// Constants
#include <max6675.h>
#include <LiquidCrystal.h>
#include <Wire.h>
const int P1 = A0;       // A1 pin for the pressure sensor
const int P2 = A1;
const float Vref = 5.0;         // Reference voltage (5V for most Arduinos)
const float pressureMax = 10.0; // Maximum pressure in PSI
const float voltageMin = 0.0;   // Minimum sensor voltage (0V)
const float voltageMax = 5.0;   // Maximum sensor voltage (5V)
const float psiToPa = 6894.76;  // Conversion factor: 1 PSI = 6894.76 Pascals

const int thermoSO = 4; // Data Out (SO)
const int thermoSCK = 3; // Clock (SCK)
const int thermoCS = 2;  // Chip Select (CS)

const int thermoSO2 = 5; // Data Out (SO)
const int thermoSCK2 = 6; // Clock (SCK)
const int thermoCS2 = 7;  // Chip Select (CS)


float floatArray[] = {0, 0, 0, 0}; // Array of floats
int arraySize = sizeof(floatArray) / sizeof(floatArray[0]);


// Initialize the MAX6675 object
MAX6675 thermocouple(thermoSCK, thermoCS, thermoSO);
MAX6675 thermocouple2(thermoSCK2, thermoCS2, thermoSO2);
float desE = 0;
void setup() {
  Serial.begin(9600);
  while (!Serial); // Wait for Serial Monitor to open
  Serial.println("Starting...");
}

void loop() {
  // Read pressure values
  int p1 = pr1(); // Read ADC value for pressure sensor 1
  float voltage = (p1 / 1023.0) * Vref;
  float p1pa = (voltage - voltageMin) * (pressureMax / (voltageMax - voltageMin)) * psiToPa;

  int p2 = pr2(); // Read ADC value for pressure sensor 2
  float voltage2 = (p2 / 1023.0) * Vref;
  float p2pa = (voltage2 - voltageMin) * (pressureMax / (voltageMax - voltageMin)) * psiToPa;

  // Read temperature values
  int numSamples = 10;
  double temp1 = 0;
  double temp2 = 0;
  for (int i = 0; i < numSamples; i++) {
    temp1 += thermocouple.readCelsius();
    temp2 += thermocouple2.readCelsius();
    delay(10); // Small delay between samples
  }
  temp1 /= numSamples;
  temp2 /= numSamples;

  // Check for invalid temperature readings
  if (isnan(temp1)) {
    temp1 = -999; // Use -999 as a placeholder for error
  }
  if (isnan(temp2)) {
    temp2 = -999; // Use -999 as a placeholder for error
  }

  // Send all values as a comma-separated string
  Serial.print(p1pa*1100); // Pressure 1 in Pascals (scaled)
  Serial.print(",");
  Serial.print(p2pa/1.8); // Pressure 2 in Pascals (scaled)
  Serial.print(",");
  Serial.print(temp1+500); // Temperature 1 with offset
  Serial.print(",");
  Serial.println(temp2+260); // Temperature 2 with offset and newline

  delay(1000); // Adjust sampling rate as needed
}

const int numSamples = 10; // Number of readings to average
float pr1() {
   long sum = 0;
   for (int i = 0; i < numSamples; i++) {
     sum += analogRead(P1);
     delay(10); // Small delay between samples
   }
   return sum / (float)numSamples;
 }
float pr2() {
   long sum = 0;
   for (int i = 0; i < numSamples; i++) {
     sum += analogRead(P2);
     delay(10); // Small delay between samples
   }
   return sum / (float)numSamples;
 }

 void T1() {
  double temp1 = 0;
  for (int i = 0; i < numSamples; i++) {
     temp1 += thermocouple.readCelsius();
     delay(10); // Small delay between samples
   }
   temp1/=10;
  // Check if the reading is valid
  if (isnan(temp1)) {
    Serial.print("Error: No thermocouple detected");
    
  } else {
    Serial.print("Temperature 1: ");
    Serial.print(temp1+500);
    Serial.println(" °C");
  }
 }
 void T2() {
  double temp2 = 0;
  for (int i = 0; i < numSamples; i++) {
     temp2 += thermocouple2.readCelsius();
     delay(10); // Small delay between samples
   }
   temp2/=10;
  if (isnan(temp2)) {
    Serial.print("Error: No thermocouple 2 detected");
    
  } else {
    Serial.print("Temperature 2: ");
    Serial.print(temp2+100);
    Serial.println(" °C");
  }
 }
//need to include code lines for second pressure sensor still
//Temp: