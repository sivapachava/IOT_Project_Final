
import asyncio
import board
import digitalio
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

async def sendDataViaBle(switch):
    ble = BLERadio()
    while True:
      while ble.connected and any(UARTService in connection for connection in ble.connections):
          for connection in ble.connections:
                if UARTService not in connection:
                    continue
                uart = connection[UARTService]
                data = str(switch.value)
                print(data)
                uart.write(data.encode('utf-8'))
                one_byte = uart.read()
                if one_byte:
                    print(one_byte)
                print()
      print("disconnected, scanning")
      for advertisement in ble.start_scan(ProvideServicesAdvertisement, timeout=1):
           if UARTService not in advertisement.services:
            continue
           ble.connect(advertisement)
           print("connected")
           break
      ble.stop_scan()
      await asyncio.sleep(1)
                
async def inputOutput(switch ,output):
    led = digitalio.DigitalInOut(output)
    led.direction = digitalio.Direction.OUTPUT    
    while True:
      if switch.value:
           led.value = True
      else:
           led.value = False
      await asyncio.sleep(1)

async def main():
    switch = digitalio.DigitalInOut(board.D9)
    switch.direction = digitalio.Direction.INPUT
    switch.pull = digitalio.Pull.DOWN
    sendData = asyncio.create_task(sendDataViaBle(switch))
    switchON = asyncio.create_task(inputOutput(switch ,board.LED))
    await asyncio.gather(switchON,sendData)
    print("done")


asyncio.run(main())
