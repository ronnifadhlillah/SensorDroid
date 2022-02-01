import serial
import time

s=serial.Serial('Com Num',BaudRate)

def switch():
    v=input('LED ? ')
    if v == 'on':
        s.write(b'1')
        switch()
    elif v == 'off':
        s.write(b'0')
        switch()
    else:
        print('Input unknown. try using on or off')
        switch()

time.sleep(2)
print('Serial connection is ready')
switch()
