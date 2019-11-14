/*
Advanced_I2C.ino
Brian R Taylor
brian.taylor@bolderflight.com

Copyright (c) 2017 Bolder Flight Systems

Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or 
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

#include "MPU9250.h"

// an MPU9250 object with the MPU-9250 sensor on I2C bus 0 with address 0x68
MPU9250 IMU(Wire,0x68);
int status;

void setup() {
  // serial to display data
  Serial.begin(115200);
  while(!Serial) {}

  // start communication with IMU 
  status = IMU.begin();
  if (status < 0) {
    Serial.println("IMU initialization unsuccessful");
    Serial.println("Check IMU wiring or try cycling power");
    Serial.print("Status: ");
    Serial.println(status);
    while(1) {}
  }
  // setting the accelerometer full scale range to +/-8G 
  IMU.setAccelRange(MPU9250::ACCEL_RANGE_8G);
  // setting the gyroscope full scale range to +/-500 deg/s
  IMU.setGyroRange(MPU9250::GYRO_RANGE_500DPS);
  // setting DLPF bandwidth to 20 Hz
  IMU.setDlpfBandwidth(MPU9250::DLPF_BANDWIDTH_20HZ);
  // setting SRD to 19 for a 50 Hz update rate
  IMU.setSrd(99);
//  IMU.setGyroBiasX_rads(IMU.getGyroBiasX_rads());
//  IMU.setGyroBiasY_rads(IMU.getGyroBiasY_rads());
//  IMU.setGyroBiasZ_rads(IMU.getGyroBiasZ_rads());
//  IMU.setAccelCalX(0.3, 1);
//  IMU.setAccelCalY(0.15, 1);
//  IMU.setAccelCalZ(-0.4, 1);
  Serial.println("Calibrating!");
  calibrate();
  Serial.println("Ready!");
  Serial.print(IMU.getAccelBiasX_mss());
  Serial.print("           ");
  Serial.println(IMU.getAccelBiasY_mss());
}

void calibrate() {
  IMU.readSensor();
  float bx = IMU.getAccelX_mss();
  float by = IMU.getAccelY_mss();
  float bz = IMU.getAccelZ_mss();
  for (int i = 0; i < 49; i++) {
    IMU.readSensor();
    bx += IMU.getAccelX_mss();
    bx /= 2;
    
    by += IMU.getAccelY_mss();
    by /= 2;
    
    bz += IMU.getAccelZ_mss();
    bz /= 2;
    delay(100); 
  }
  IMU.setAccelCalX(bx, 1);
  IMU.setAccelCalY(by, 1);
  IMU.setAccelCalZ(bz + 9.8, 1);
  
}

void loop() {
  // read the sensor
  IMU.readSensor();

  // display the data
  Serial.print(IMU.getAccelX_mss(),6);
  Serial.print("x mss \t");
  Serial.print(IMU.getAccelY_mss(),6);
  Serial.print("y mss \t");
  Serial.print(IMU.getAccelZ_mss(),6);
  Serial.print("z mss \t");
  Serial.print(IMU.getGyroX_rads(),6);
  Serial.print("x rads \t");
  Serial.print(IMU.getGyroY_rads(),6);
  Serial.print("y rads \t");
  Serial.print(IMU.getGyroZ_rads(),6);
  Serial.print("z rads \t");
//  Serial.print(IMU.getMagX_uT(),6);
//  Serial.print("\t");
//  Serial.print(IMU.getMagY_uT(),6);
//  Serial.print("\t");
//  Serial.print(IMU.getMagZ_uT(),6);
//  Serial.print("\t");
//  Serial.println(IMU.getTemperature_C(),6);
  Serial.print("\n");
  delay(200);
}
