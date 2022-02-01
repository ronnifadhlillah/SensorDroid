import serial
import time

s=serial.Serial('Com Num',BaudRate)

def led_switch():
    v=input('LED ? ')
    if v == 'on':
        s.write(b'1')
        led_switch()
    elif v == 'off':
        s.write(b'0')
        led_switch()
    else:
        print('Input unknown. try using on or off')
        led_switch()

time.sleep(2)
print('Serial connection is ready')
led_switch()
