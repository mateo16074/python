# Mateo Vaca, Matias Galarza, Alan Velastegui
from machine import Pin, ADC
from time import sleep, time
import dht
import urequests
import network


sensor = dht.DHT11(Pin(14))

THINGSPEAK_WRITE_API_KEY = 'xxxxxxx'
THINGSPEAK_URL = 'https://api.thingspeak.com/update'

ssid = 'xxxxxx'
password = 'xxxxxx'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print('Conexión exitosa')
print(station.ifconfig())

buzzer = Pin(13, Pin.OUT)
pir = Pin(22, Pin.IN, Pin.PULL_DOWN)

light_sensor = ADC(Pin(34))  
light_sensor.atten(ADC.ATTN_11DB)  

def send_to_thingspeak(temp, hum, motion, light):
    try:
        url = f"{THINGSPEAK_URL}?api_key={THINGSPEAK_WRITE_API_KEY}&field1={temp}&field2={hum}&field3={motion}&field4={light}"
        response = urequests.get(url)
        if response.status_code == 200:
            print('Datos enviados a ThingSpeak: ', response.text)
        else:
            print('Error en la respuesta de ThingSpeak:', response.status_code, response.text)
        response.close()
    except Exception as e:
        print('Error al enviar datos a ThingSpeak: ', e)

def read_sensor():
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        temp_f = temp * (9/5) + 32.0
        print('Temperature: %3.1f C' % temp)
        print('Temperature: %3.1f F' % temp_f)
        print('Humidity: %3.1f %%' % hum)

        return temp, hum
    except OSError as e:
        print('Failed to read sensor:', e)
    except Exception as e:
        print('Unexpected error:', e)
    return None, None

last_thingspeak_update = 0
thingspeak_interval = 15  
pir_check_interval = 1  

while True:
    current_time = time()

    if current_time - last_thingspeak_update >= thingspeak_interval:
        temp, hum = read_sensor()
        light_level = light_sensor.read()  
        if temp is not None and hum is not None:
            send_to_thingspeak(temp, hum, pir.value(), light_level)
        last_thingspeak_update = current_time

    if pir.value() == 1:
        print("Movimiento detectado")
        buzzer.value(1)
    else:
        print("Sin movimiento")
        buzzer.value(0)

    sleep(pir_check_interval)
