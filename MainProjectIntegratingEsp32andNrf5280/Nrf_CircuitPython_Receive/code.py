from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import asyncio
import board
import time
import digitalio
import adafruit_bmp280
from adafruit_apds9960.apds9960 import APDS9960



 
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

recievedValue = "F"
async def readBleData():
  led = digitalio.DigitalInOut(board.LED)
  led.direction = digitalio.Direction.OUTPUT
  ble.start_advertising(advertisement)
  while not ble.connected:
        pass
  while ble.connected:
        receivedData = uart.read()
        print("dfdfd", receivedData.decode("utf-8"))
        global recievedValue
        print("intial",recievedValue)
        if receivedData.decode("utf-8")[:1] == "I":  
          recievedValue1 = receivedData.decode("utf-8")[1:]
          print("rec",recievedValue1[0])   
          if recievedValue1[0] == 'T':
             print("tested")
             led.value  = True
             print(led.value)
          if recievedValue1[0] == 'F':
             led.value  = False
        await asyncio.sleep(1)
  print("rec", recievedValue)
            
async def main():
    readBle = asyncio.create_task(readBleData())
    await asyncio.gather(readBle)
    print("done")
    

asyncio.run(main())