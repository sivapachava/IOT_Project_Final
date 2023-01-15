import ssd1306
import time
import _thread
import network
from machine import Pin, I2C
import urequests 
from machine import Pin
import dht
import ntptime


sensor = dht.DHT22(Pin(27))
switchWeatherData  = Pin(15, mode=Pin.IN)
currentDataTime  = Pin(32, mode=Pin.IN)

i2c = I2C(sda=Pin(23), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 32, i2c)
display.fill(0)
display.text('Welcome', 0, 0, 1)
display.text('Weather',0, 12, 1)
display.text('Montioring System',0, 24, 1)
display.show()

sta = network.WLAN(network.STA_IF)
if not sta.isconnected():
  print('connecting to network...')
  sta.active(True)
  sta.connect('Redmi 9 Prime', '123456780')
  while not sta.isconnected():
    pass
print('network config:', sta.ifconfig())

time.localtime()
ntptime.host = "1.fr.pool.ntp.org"

temp = 0
hum = 0

def readData(sensor,delay):
    while True:
        apiKey = 'VS4J3BEBBESDBTVY' 
        timeInterval = 500
        global temp
        global hum
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        readings = {'field1':temp, 'field2':hum} 
        request = urequests.post('http://api.thingspeak.com/update?api_key=' +
        apiKey,json = readings, headers = {'Content-Type': 'application/json'}  )      
        request.close() 
        print(readings) 

def switchDataDisplay(input,delay):
  while True:
     if input.value() == 0:
        display.fill(0)
        global temp
        global hum
        display.text("temp-" + str(temp) + "degC", 0, 0, 1)
        display.text("humid-" + str(hum) + "%",0, 12, 1)
        display.show()
        
def switchTimeDateDisplay(input,delay):
    while True:
        if  input.value() == 0:           
            time.localtime()
            ntptime.host = "1.fr.pool.ntp.org"
            ntptime.settime()
            offset = 60* 60
            year, month, day, hour, minute, second, ms, dayinyear = time.localtime(time.time() + offset )
            currentDate = str(year) + "-" + str(month) + "-" + str(day)
            currentTime = str(hour) + "-" + str(minute) + "-" + str(second)
            display.fill(0)
            display.text("date-" + currentDate,0,0,1)
            display.text("time-" + currentTime,0,12,1)
            display.show()
    
def dataLogger(input,delay):
  while True:
    global temp
    global hum
    apiKey = "fnIsHzZy0ti3rAKY7vYEJ8EsxQfVd60UZoUAY4YFcN8"
    readings = {'field1':temp, 'field2':hum}
    request = urequests.post('https://maker.ifttt.com/trigger/dht11/json/with/key/' +  apiKey,
    json=readings,
    headers={'Content-Type': 'application/json'})
    request.close()
    
    


delay=0

_thread.start_new_thread(switchDataDisplay,(switchWeatherData,delay))
_thread.start_new_thread(switchTimeDateDisplay,(currentDataTime,delay))
_thread.start_new_thread(readData,(sensor,delay))
    
   
        


 
