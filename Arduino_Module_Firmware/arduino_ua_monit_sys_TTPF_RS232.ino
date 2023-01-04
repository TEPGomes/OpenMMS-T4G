#include <stdio.h>
#include <Wire.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_I2CRegister.h>
#include "Adafruit_MCP9600.h"

#define I2C_ADDRESS (0x67)
#define I2C_ADDRESS_2 (0x60)

Adafruit_MCP9600 mcp;
Adafruit_MCP9600 mcp2;

int pwm_pin_P = 2;
int pwm_pin_F = 4;

float P = 0.0;
float F = 0.0;
int range_P = 1;
int range_F = 1;
float range_max_1_P = 20000;
float range_max_2_P = 5000;
float range_max_1_F = 53200;
float range_max_2_F = 10000;
float P_sens = 9.4;
float F_sens = 3.8;

String readstr;
String readstr1;

void setup() {
  bool start = false; //Variável que indica se a mensagem de inicio foi
                      //recebida (Verdadeiro) ou não (Falso).
  
  Serial.begin(115200); //Iniciar comunicação com o computador

  //Esperar até que a mensagem de inicio seja recebida
  while (!start) {
    if (Serial.available()>0) {
      //Se for recebido o caractére "s":
      if ( Serial.read() == *"s") {
        start = true;
        mcp.begin(I2C_ADDRESS); //Iniciar ligação a MCP9600 1.
        mcp2.begin(I2C_ADDRESS_2); //Iniciar ligação a MCP600 2.
        pinMode(pwm_pin_P, OUTPUT); 
        pinMode(pwm_pin_F, OUTPUT);} 
        }
    else {
        //Se nada é recebido, esperar e voltar a testar
        delay(10);}
      }
  mcp.setADCresolution(MCP9600_ADCRESOLUTION_12); //Definir resolução do ADC do MCP9600 1.
  mcp.setThermocoupleType(MCP9600_TYPE_J); //Definir tipo de termopar em utilização.
  mcp.setFilterCoefficient(3);
  mcp.enable(true);

  mcp2.setADCresolution(MCP9600_ADCRESOLUTION_12); //Definir resolução do ADC do MCP9600 2.
  mcp2.setThermocoupleType(MCP9600_TYPE_J); //Definir tipo de termopar em utilização.
  mcp2.setFilterCoefficient(3);
  mcp2.enable(true);

  analogWrite(pwm_pin_P, 255); //Amplificador de carga para pressão - Modo de operação.
  analogWrite(pwm_pin_F, 255); //Amplificador de carga para força - Modo de operação.
}

void loop() {
  bool pause = false; //Variável que indica se a mensagem de pausa foi
                      //recebida (Verdadeiro) ou não (Falso).
  bool serial1com = false; //Variável que indica se a mensagem para operar no modo de comunicação com o 
                           //amplificador de carga Kistler Type 5073A111 foi recebida (Verdadeiro) ou não (Falso).

  //Ler temperatura do termopar 1
  float T1 = mcp.readThermocouple();
  char T1str [6];
  dtostrf(T1,5,2,T1str); //Converter e armazenar valor lido num string

  //Ler temperatura do termopar 2
  float T2 = mcp2.readThermocouple();
  char T2str [6];
  dtostrf(T2,5,2,T2str); //Converter e armazenar valor lido num string

  float Vmax_sig = 5; 

  //Ler entrada analógica e calcular valor de pressão. Converter e armazenar num string.
  int P_Pin_read = analogRead(A0);
  float V_P = P_Pin_read * (Vmax_sig / 1023.0);
  if (range_P == 1){
    P = V_P * (range_max_1_P / P_sens ) / Vmax_sig; //Relative Pressure
    }
  else if (range_P == 2){
    P = V_P * (range_max_2_P / P_sens) / Vmax_sig;}
  char Pstr [8];
  dtostrf(P,5,2,Pstr);

  delay(5);

  //Ler entrada analógica e calcular valor de pressão. Converter e armazenar num string.
  int F_Pin_read = analogRead(A2);
  float V_F = F_Pin_read * (Vmax_sig / 1023.0);
  if (range_F == 1){
    F = V_F * (range_max_1_F / F_sens) / Vmax_sig;
    }
  else if (range_F == 2){
    F = V_F * (range_max_2_F / F_sens) / Vmax_sig;}
  char Fstr [8];
  dtostrf(F,5,2,Fstr);

  //Concatenar mensagem a enviar com os dados lidos.
  char serData[strlen(T1str) + strlen(T2str) + strlen(Pstr) + strlen(Fstr) + 4];
  sprintf(serData,"%s,%s,%s,%s",T1str,T2str,Pstr,Fstr);
  //Enviar dados.
  Serial.println(serData);

  if (Serial.available()>0) {
    //Caso o caractére "p" seja recebido, pausar a leitura
    if (Serial.read() == *"p") {
      pause = true;
      analogWrite(pwm_pin_P, 0); //Modo de operação do amplificador de carga para pressão - Reset
      analogWrite(pwm_pin_F, 0);} //Modo de operação do amplificador de carga para força - Reset
  }
  
  while (pause) {
    if (Serial.available()) {
      char command = Serial.read();

      //Se "s" for recebido, retomar a leitura e envio de dados.
      if ( command == 's') {
        pause = false;
        analogWrite(pwm_pin_P, 255);
        analogWrite(pwm_pin_F, 255);
      }
      //Se "c" for recebido, iniciar comunicação com o amplificador de carga Kistler Type 5073A111
      else if (command == 'c') {
        serial1com = true;
        Serial1.begin(115200);
        Serial.println(Serial1);
        Serial.println("Serial1 began");
          
        while (serial1com == true) {
          //Ler mensagens recebidas do computador:
          while (Serial.available() > 0) {
            char achar = Serial.read();
            readstr += achar;
            delay(3);}

          //Se "p" for recebido, parar comunicação com amplificador.
          if (readstr == "p") {
            Serial.println("End Serial1");
            Serial1.end();
            serial1com = false;}
          //Caso uma mensagem diferente seja lida, encaminhar para o amplificador.
          else if (readstr.length() > 0) {
            Serial1.println(readstr);}
          
          readstr = "";
          delay(3);

          //Ler mensagens provenienntes do amplificador.
          while (Serial1.available() > 0) {
            char achar1 = Serial1.read();
            readstr1 += achar1;
            delay(3);}

          //Caso uma mensagem tenha sido recebida do amplificador, encaminhar para o computador.
          if (readstr1.length() > 0) {
            Serial.println(readstr1);}
          
          readstr1 = "";
          }
        }
    else {
      delay(10);}
    }
  }
  //Esperar para que os dados sejam enviados a uma taxa de cerca de 10 Hz para o computador.
  delay(90);
}
