import bluetooth
import ssd1306
import random
import struct
import _thread
import network
import urequests 
import dht
from machine import Pin, I2C, TouchPad
import time
from BLESimplePeripheral import BLESimplePeripheral
from micropython import const
from neopixel import NeoPixel

#paramter 
receivedTemperature = 0
receivedPressure = 0
receivedAltitude = 0
receivedProximity = 0
readHumidityData = 0.0
touchOuputSend = False 

#input/output details
i2c = I2C(sda=Pin(23), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 32, i2c)
switchPressureTempDisplayInput  = Pin(15, mode=Pin.IN)
switchAltitudeProximityInput = Pin(32, mode=Pin.IN)
touchOutputTrigger = Pin(13, mode=Pin.OUT)
touchInputCapacitanceValue = TouchPad(Pin(33))
neoPixel = Pin(12, Pin.OUT)
sensorHumudity = dht.DHT22(Pin(27))
   

display.fill(0)
display.text('Welcome', 30, 0, 1)
display.text('Weather',30, 12, 1)
display.text('Montioring',30, 24, 1)
display.show()

sta = network.WLAN(network.STA_IF)
if not sta.isconnected():
  print('connecting to network...')
  sta.active(True)
  sta.connect('Redmi 9 Prime', '123456780')
  while not sta.isconnected():
    pass
print('network config:', sta.ifconfig())

flag = False
delay = 0
def readSensorViaBLE(flag,delay):
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)

    def on_rx(receivedData):
        global receivedTemperature
        global receivedPressure
        global receivedAltitude
        global receivedProximity
        print("RVVVX", receivedData.decode('utf-8')[1:])
        if receivedData.decode('utf-8')[0] == "T":
            receivedTemperature = receivedData.decode('utf-8')[1:]
        if receivedData.decode('utf-8')[0] == "A":
            receivedAltitude = receivedData.decode('utf-8')[1:]
        if receivedData.decode('utf-8')[0] == "P":
            receivedPressure = receivedData.decode('utf-8')[1:]
        if receivedData.decode('utf-8')[0] == "R":
            receivedProximity = receivedData.decode('utf-8')[1:]
        print("receiveddata",receivedTemperature,receivedPressure,receivedAltitude,receivedProximity )
            
    p.on_write(on_rx)
    
def readHumidity(sensor,delay):
     while True:
          sensor.measure()
          global readHumidityData
          readHumidityData = sensor.humidity()
          temp = sensor.temperature()
          print("humidity:", readHumidityData)
    
    
def touchSensorRead(touchCapacitanceValue,touchOutput):
    while True:
       print("touch capacitance value:",touchCapacitanceValue.read() )
       global touchOuputSend
       if touchCapacitanceValue.read() <= 200:
           touchOutput.on()
           touchOuputSend = True
       else:
           touchOutput.off()
           touchOuputSend = False
           
    
def switchPressureTempDisplay(input,delay):
  while True:
     if input.value() == 0:
        display.fill(0)
        global receivedTemperature
        global receivedPressure
        global readHumidityData
        display.text("temp-" + str(receivedTemperature) + "degC", 0, 0, 1)
        display.text("pres-" + str(receivedPressure) + "hPa",0, 12, 1)
        display.text("hum-" + str(readHumidityData) + "%",0, 24, 1)
        display.show()
        
def switchAltitudeProximityDisplay(input,delay):
  while True:
     if input.value() == 0:
        display.fill(0)
        global receivedAltitude
        global receivedProximity
        display.text("alti-" + str(receivedAltitude), 0, 0, 1)
        display.text("proxi-" + str(receivedProximity),0, 12, 1)
        display.show()
        
def sendDataToThingSpeak(flag,delay):
    while True:
        apiKey = 'VS4J3BEBBESDBTVY' 
        timeInterval = 500
        global receivedTemperature
        global receivedPressure
        global receivedAltitude
        global receivedProximity
        global readHumidityData
        global touchOuputSend
        readings = {'field1':receivedTemperature, 'field2':receivedPressure,'field3':receivedAltitude,'field4':receivedProximity,'field4':readHumidityData,'field5':touchOuputSend} 
        request = urequests.post('http://api.thingspeak.com/update?api_key=' +
        apiKey,json = readings, headers = {'Content-Type': 'application/json'}  )      
        request.close() 
        print(readings) 
        
def changeNeopixelColorBasedOnProximitySensor(neoPixelInput,delay):
    np = NeoPixel(neoPixelInput, 8)   
    global receivedProximity
    while True:
        if receivedProximity>= 1 and receivedProximity<=100:
            np[0] = (100, 0, 0) 
            np.write() 
        if receivedProximity>= 100 and receivedProximity<=200:
            np[0] = (0, 100, 0) 
            np.write()
        if receivedProximity>= 200 and receivedProximity<=250:
            np[0] = (0, 0, 100) 
            np.write()
                



_thread.start_new_thread(readSensorViaBLE,(flag,delay))
_thread.start_new_thread(switchPressureTempDisplay,(switchPressureTempDisplayInput,delay))
_thread.start_new_thread(switchAltitudeProximityDisplay,(switchAltitudeProximityInput,delay))
_thread.start_new_thread(sendDataToThingSpeak,(flag,delay))
_thread.start_new_thread(touchSensorRead,(touchInputCapacitanceValue,touchOutputTrigger))
#_thread.start_new_thread(readHumidity,(sensorHumudity,delay))
_thread.start_new_thread(changeNeopixelColorBasedOnProximitySensor,(neoPixel,delay))
