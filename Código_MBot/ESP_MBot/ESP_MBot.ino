#include <Arduino.h>
#include <ctype.h>
#if defined(ESP32)
  #include <WiFi.h>
  #include <SD.h>
#elif defined(ESP8266)
#endif
#include <Firebase_ESP_Client.h>

//Provide the token generation process info.
#include "addons/TokenHelper.h"
//Provide the RTDB payload printing info and other helper functions.
#include "addons/RTDBHelper.h"

// Insert your network credentials
#define WIFI_SSID "----"
#define WIFI_PASSWORD "-----'"

//Firebase API Key
#define API_KEY "AIzaSyApifcKhHGhFe0OmXXGj-----"
#define DATABASE_URL "https://esp-mbot-default-rtdb.-----"

//Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config;
//Variables para Firebase
unsigned long sendDataPrevMillis = 0;
String movement;
String movement_tmp;
float floatValue;
bool signupOK = false;

String getMOVEMENT(){
  String stringValue;
  //Recibe string (movimiento MBot)
  if (Firebase.RTDB.getString(&fbdo, "/mover")) {
     if (fbdo.dataType() == "string") {
       stringValue = fbdo.stringData();
       return stringValue;
     }
  }
}

void setup(){
  Serial.begin(9600);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED){
    delay(100);
  }
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  if (Firebase.signUp(&config, &auth, "", "")){
    signupOK = true;
  }
  config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
}

void loop(){
  //Recibe datos de movimiento
  if (Firebase.ready() && signupOK && (millis() - sendDataPrevMillis > 200 || sendDataPrevMillis == 0)){
    sendDataPrevMillis = millis();
    movement = getMOVEMENT();
    if(movement != movement_tmp){
      //Funcion que recibe movimiento
      Serial.println(movement);
      movement_tmp=movement;
    }
  }
}
