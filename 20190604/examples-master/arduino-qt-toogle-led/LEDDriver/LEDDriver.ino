//// ****** THIS FILE IS AUTOGENERATED ******
////
////          >>>> DO NOT CHANGE <<<<
////
/// 
///  Filename; C:\Users\realm.DESKTOP-DQ0IJ8Q\Documents\GitHub\instrumentacion2\20190604\examples-master\arduino-qt-toogle-led\run.py
///  Source class: LEDDriver
///  Generation timestamp: 2019-06-04T14:53:50.939682
///  Class code hash: 8647375a3d456c77a25af7a8712a5951c71a1594
///
/////////////////////////////////////////////////////////////



// Import libraries
#include <Arduino.h>

#include "inodriver_bridge.h"
#include "inodriver_user.h"

#define BAUD_RATE 9600

void setup() {
  bridge_setup();
  
  user_setup();

  Serial.begin(BAUD_RATE);
}

void loop() {
  
  bridge_loop();
  
  user_loop();
}
