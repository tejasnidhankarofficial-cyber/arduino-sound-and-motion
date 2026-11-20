
#include "Arduino_LED_Matrix.h"   // Include the LED_Matrix library

ArduinoLEDMatrix matrix;          // Create an instance of the ArduinoLEDMatrix class
const int SPEAKER_PIN = 8;
uint32_t frame[3] = {0, 0, 0};
uint32_t** anim;

void setup() {
  Serial.begin(9600);
  matrix.begin();
  pinMode(SPEAKER_PIN, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    //First we need to figure out the type of media
    String line = Serial.readStringUntil('\n');
    line.trim();
    int type = line.toInt();

    if(type == 1) //Image
    {
      line = Serial.readStringUntil('\n');
      line.trim();

      int c1 = line.indexOf(',');
      int c2 = line.indexOf(',', c1 + 1);
      if (c1 > 0 && c2 > c1) {
        frame[0] = strtoul(line.substring(0, c1).c_str(), NULL, 16);
        frame[1] = strtoul(line.substring(c1 + 1, c2).c_str(), NULL, 16);
        frame[2] = strtoul(line.substring(c2 + 1).c_str(), NULL, 16);
        matrix.loadFrame(frame);
      }
    }
    else if(type == 2) // Animation
    {
      line = Serial.readStringUntil('\n');
      line.trim();
      int numFrames = line.toInt();
      anim = new uint32_t*[numFrames];

      for(int i = 0; i < numFrames; i++)
      {
        anim[i] = new uint32_t[3];
        line = Serial.readStringUntil('\n');
        line.trim();

        int c1 = line.indexOf(',');
        int c2 = line.indexOf(',', c1 + 1);
        if (c1 > 0 && c2 > c1) 
        {
          anim[i][0] = strtoul(line.substring(0, c1).c_str(), NULL, 16);
          anim[i][1] = strtoul(line.substring(c1 + 1, c2).c_str(), NULL, 16);
          anim[i][2] = strtoul(line.substring(c2 + 1).c_str(), NULL, 16);
        }
      }
      while(!Serial.available())
      {
        for(int i = 0; i < numFrames; i++)
        {
          frame[0] = anim[i][0];
          frame[1] = anim[i][1];
          frame[2] = anim[i][2];
          matrix.loadFrame(frame);

          delay(250); //in milliseconds
        }
      }

      for(int i = 0; i < numFrames; i++)
      {
        delete[] anim[i];
      }
      delete[] anim;
    }
    else // Music
    {
      frame[0] = 0x0;
      frame[1] = 0x0;
      frame[2] = 0x0;
      matrix.loadFrame(frame);

      do
      {
        line = Serial.readStringUntil('\n');
        line.trim();

        int comma = line.indexOf(',');

        int pitch = line.substring(0,comma).toInt();
        int duration = line.substring(comma+1).toInt();  
        int noteMs = 1000 / duration;       // e.g. 4 -> 250 ms, 8 -> 125 ms
        
        tone(SPEAKER_PIN, pitch, noteMs);
        delay(noteMs * 1.30);               // brief gap between notes
        noTone(SPEAKER_PIN);
      }while(Serial.available());
    }

    
  }
}