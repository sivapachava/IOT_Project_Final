from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import asyncio
import board
import time
import digitalio
import adafruit_bmp280
from adafruit_apds9960.apds9960 import APDS9960


led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
 
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

recievedValue = "F"
async def readBleData():
  ble.start_advertising(advertisement)
  while not ble.connected:
        pass
  while ble.connected:
        receivedData = uart.read(1)
        print(receivedData.decode("utf-8"))
        global recievedValue
        print("intial",recievedValue)
        if recievedValue == 'T':
          print("tested")
          led.value  = True;
        if recievedValue == 'F':
          led.value  = False;
        if receivedData:
            recievedValue = receivedData.decode("utf-8")
            print("drf",recievedValue)
            uart.write(receivedData)
        await asyncio.sleep(1)
  print("rec", recievedValue)
  

async def blink(pin):
        led = digitalio.DigitalInOut(pin)
        led.direction = digitalio.Direction.OUTPUT
        while True:
             led.value = True
             await asyncio.sleep(1)
             led.value = False
             await asyncio.sleep(1)
             
async def readSensorData():
    i2c = board.I2C()
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
    bmp280.sea_level_pressure = 1013.25
    time.sleep(1)
    while True:
         print("temperature:", bmp280.temperature)
         print("pressure:" , bmp280.pressure)
         print("altitude:" ,  bmp280.altitude)
         await asyncio.sleep(1)
         
async def proximitySensor():
    i2c = board.I2C()
    apds = APDS9960(i2c)
    apds.enable_proximity = True
    while True:
        print(apds.proximity)
        await asyncio.sleep(1)
            
async def main():
    readBle = asyncio.create_task(readBleData())
    blinkLed = asyncio.create_task(blink(board.D6))
    readData = asyncio.create_task(readSensorData())
    readProximitySensor = asyncio.create_task(proximitySensor())
    await asyncio.gather(readBle,blinkLed,readData,readProximitySensor)
    print("done")
    

asyncio.run(main())