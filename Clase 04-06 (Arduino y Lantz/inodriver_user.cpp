//// ****** THIS FILE IS AUTOGENERATED ******
////
////          >>>> PLEASE ADAPT IT TO YOUR NEEDS <<<<
////
/// 
///  Filename; C:\Users\Sabrina\PycharmProjects\Instrumentallantz\ARDUINO\examples-master\arduino-qt-toogle-led\run.py
///  Source class: LEDDriver
///  Generation timestamp: 2019-06-04T15:40:28.767055
///  Class code hash: 8647375a3d456c77a25af7a8712a5951c71a1594
///
/////////////////////////////////////////////////////////////

#include "arduino.h"
#include "inodriver_user.h"

int ledpin = 12;

void user_setup() {
   pinMode(ledpin, OUTPUT);
}

void user_loop() {
};
// COMMAND: LED, FEAT: led
int get_LED() {
  return 0;
};

int set_LED(int value) {
   if (value>0)
      digitalWrite(ledpin, HIGH);
   else
      digitalWrite(ledpin, LOW);
   return 0;
};
