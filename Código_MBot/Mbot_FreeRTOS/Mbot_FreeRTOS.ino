#include <Arduino.h>
#include <Wire.h>
#include <SoftwareSerial.h>
#include "src/MeSingleLineFollower.h"
#include "src/MeCollisionSensor.h"
#include "src/MeBarrierSensor.h"
#include "src/MeNewRGBLed.h"
#include <MeMegaPi.h>
#include <avr/io.h>
#include <Arduino_FreeRTOS.h>
#include "semphr.h"
#include "queue.h"

#define F_CPU 16000000
#define USART_BAUDRATE 9600
#define UBRR_VALUE (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)

QueueHandle_t myQueue;
TaskHandle_t vMotoresHandle;

//buffer para el UART
unsigned char mybuffer[25];
unsigned int mybuffer_int[25];
unsigned char ch;

MeBarrierSensor barrier_60(60);
MeBarrierSensor barrier_61(61);
MeBarrierSensor barrier_62(62);
MeCollisionSensor collision_65(65);
MeCollisionSensor collision_66(66);
MeNewRGBLed rgbled_67(67,4);
MeNewRGBLed rgbled_68(68,4);

MeMegaPiDCMotor motor_1(1);
MeMegaPiDCMotor motor_9(9);
MeMegaPiDCMotor motor_2(2);
MeMegaPiDCMotor motor_10(10);
MeMegaPiDCMotor motor_3(3);
MeMegaPiDCMotor motor_11(11);
MeMegaPiDCMotor motor_4(4);
MeMegaPiDCMotor motor_12(12);

//Inicializacion UART
void usart_init(void){
  UCSR2B =(1<<RXEN2)|(1<<TXEN2);  //Enable receiver
  UCSR2C =(1<<UCSZ21)|(1<<UCSZ20);  //8 bits
  
  //Desire bps = (clk/16(X+1))
  UBRR2L =103; //Valor de X para 9600 bps
}

void forward(){
  PORTC  =  0b00010101; // Input1 e Input2 de M1, M2 y M4
  PORTG  =  0b00000001; // Input1 e Input2 de M3
}

void backward(){
  PORTC  =  0b00101010; // Input1 e Input2 de M1, M2 y M4
  PORTG  =  0b00000010; // Input1 e Input2 de M3
}

void right(){
  PORTC  =  0b00101001; // Input1 e Input2 de M1, M2 y M4
  PORTG  =  0b00000001; // Input1 e Input2 de M3
}

void left(){
  PORTC  =  0b00010110; // Input1 e Input2 de M1, M2 y M4
  PORTG  =  0b00000010; // Input1 e Input2 de M3
}

void stop_motor(){
  PORTC  =  0b00000000; // Input1 e Input2 de M1, M2 y M4
  PORTG  =  0b00000000; // Input1 e Input2 de M3
}

void setup(){
  
  // Inicializar puertos salida
  DDRC = 0xff;
  DDRG = 0xff;
  //Declaracion de salida (setup motores)
  DDRB = (1<<5)|(1<<6); 
  DDRH = (1<<4)|(1<<5);
  
  //Inicializa UART
  usart_init();

  xTaskCreate(vMotores, "MOTORS MOVEMENT", 100, NULL, 1, &vMotoresHandle);
  
  //Declaracion de motores
  TCCR1A = 0xA1; //PB5 y PB4 Y WGMn1 y WGMn0 (01)
  TCCR1B = 0x0C; //PH4 y PH5 y WGMn1 y WGMn0 (01)
  TCCR4A = 0x29; //WGMn3 y WGMn2 (01) Preescaler 1/255
  TCCR4B = 0x0C; //WGMn3 y WGMn2 (01) Preescaler 1/255
  
  //Se determina el valor del PWM
  OCR1A = 128;  
  OCR1B = 128;  
  OCR4B = 128;  
  OCR4C = 128;  

  //Interrupciones
  sei();
}

void vMotores(void * pvParameters){
  //Recibe datos por el UART para movimiento
  while(1){
     while(!(UCSR2A&(1<<RXC2))); //Wait until new data
      ch = UDR2;
      
    if(ch == 'f'){
      forward();
    }
    else if(ch == 'b'){
      backward();
    }
    else if(ch == 'r'){
      right();
    }
    else if(ch == 'l'){
      left();
    }
    else if(ch == 's'){
      stop_motor();
    } 
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}

void loop(){
  rgbled_68.setColor(0, 0, 100);
  rgbled_68.show();
  rgbled_67.setColor(0, 0, 100);
  rgbled_67.show();
  _delay_ms(200);
}
