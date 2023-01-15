
import asyncio
import time
import board
import digitalio
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import adafruit_bmp280
from adafruit_apds9960.apds9960 import APDS9960

temperature = 0
pressure = 0
altitutde = 0
proximity = 0

async def readSensorData():
    i2c = board.I2C()
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
    bmp280.sea_level_pressure = 1013.25
    time.sleep(1)
    global temperature 
    global pressure 
    global altitutde
    
    while True:
         temperature = bmp280.temperature
         pressure = bmp280.pressure
         altitutde = bmp280.altitude
         print("temperature:", bmp280.temperature)
         print("pressure:" , bmp280.pressure)
         print("altitude:" ,  bmp280.altitude)
         await asyncio.sleep(1)
         
async def proximitySensor():
    i2c = board.I2C()
    apds = APDS9960(i2c)
    apds.enable_proximity = True
    global proximity
    while True:
        proximity = apds.proximity
        print("proximity:", apds.proximity)
        await asyncio.sleep(1)

async def sendDataViaBle():
    ble = BLERadio()
    input = digitalio.DigitalInOut(board.D9)
    input.direction = digitalio.Direction.INPUT
    input.pull = digitalio.Pull.DOWN
    while True:
      while ble.connected and any(UARTService in connection for connection in ble.connections):
          for connection in ble.connections:
                if UARTService not in connection:
                    continue
                uart = connection[UARTService]
                inputSend = "I" + str(input.value)
                print(inputSend)
                uart.write(inputSend.encode('utf-8'))
                time.sleep(.5) 
                temperaatureData = "T" + str(temperature)
                print(temperaatureData)               
                uart.write(temperaatureData.encode('utf-8'))
                time.sleep(.5) 
                pressureData = "P" + str(pressure)
                print(pressureData)                
                uart.write(pressureData.encode('utf-8'))
                time.sleep(.5)
                altitutdeData = "A" + str(altitutde)
                print(altitutdeData)               
                uart.write(altitutdeData.encode('utf-8'))
                time.sleep(.5)
                proximityData = "R" + str(proximity)
                print(proximityData)               
                uart.write(proximityData.encode('utf-8'))
                time.sleep(.5)
          await asyncio.sleep(1)
      print("disconnected, scanning")
      for advertisement in ble.start_scan(ProvideServicesAdvertisement, timeout=1):
           if UARTService not in advertisement.services:
            continue
           ble.connect(advertisement)
           print("connected")
           break
      ble.stop_scan()
      await asyncio.sleep(1)
                

async def main():
    sendData = asyncio.create_task(sendDataViaBle())
    readData = asyncio.create_task(readSensorData())
    readProximitySensor = asyncio.create_task(proximitySensor())
    await asyncio.gather(sendData,readData,readProximitySensor)
    print("done")


asyncio.run(main())
