import serial
import serial.tools.list_ports
import time

def ID_PORTS_AVAILABLE():
    devices = []
    for port in ['COM%s' % (i + 1) for i in range(256)]:
        try:
            s = serial.Serial(port)
            s.close()
            devices.append(port)
        except (OSError, serial.SerialException):
            pass
    
    return devices

def OPEN_SERIAL_PORTS(DEVS):
    DEVICES = []
    try:
        for i in range(len(DEVS)):
            try:
                Dev = serial.Serial(port=DEVS[i],baudrate=115200, timeout=.1)
                Dev.isOpen()
                DEVICES.append(Dev)
            except IOError:
                Dev.close()
                Dev = serial.Serial(port=DEVS[i],baudrate=115200, timeout=.1)
                Dev.isOpen()
                DEVICES.append(Dev)
            except (OSError, serial.SerialException,ValueError):
                pass
        
        return DEVICES
    except:
        return []

def SERIAL_READ_LINE(DEV):
    try:
        Incoming_Data = DEV.readlines()
        Incoming_Data = decode_lines(Incoming_Data)
        FLUSH_PORT(DEV) 
        return Incoming_Data
    except (NameError,IOError,ValueError):
            pass
    return -1

def decode_lines(cmd_list):
    for i in range(0,len(cmd_list)):
        cmd_list[i] = cmd_list[i].decode('UTF-8').replace('\r\n','')
        print(cmd_list[i])
    return cmd_list

def SERIAL_WRITE_LINE(DEV,COMMAND):
    try:
        DEV.write(COMMAND.encode('UTF-8'))
        return 1
    except:
        return -1

def WRITE(DEV,COMMAND):
    STATE = -1
    TRY = 0
    while(STATE == -1):
        STATE = SERIAL_WRITE_LINE(DEV,COMMAND)
        TRY = TRY + 1
        if(TRY>10):
            return -1
    STATE = -1
    TRY = 0
    while(STATE == -1):
        STATE = SERIAL_READ_LINE(DEV)
        TRY = TRY + 1
        if(TRY>10):
            return -1
    return STATE

def FLUSH_PORT(DEV):
    try:
        for i in range(len(DEV)):
            DEV[i].flushInput()
    except:
        pass



