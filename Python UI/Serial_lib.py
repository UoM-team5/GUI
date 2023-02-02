import serial
import serial.tools.list_ports


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
        Incoming_Data = DECODE_LINES(Incoming_Data)
        FLUSH_PORT(DEV) 
        return Incoming_Data
    except (NameError,IOError,ValueError):
            pass
    return -1

def DECODE_LINES(cmd_list):
    for i in range(0,len(cmd_list)):
        cmd_list[i] = cmd_list[i].decode('UTF-8').replace('\r\n','')
        cmd_list[i] = DECODE_LINE(cmd_list[i])
        print(cmd_list[i])
    return cmd_list

def DECODE_LINE(command):
    if command[0]!="[" or command[-1]!="]":
        return "1001 skip " + command #print("this is not valid: ", command)
    cmd_strip = command[1:-1]
    cmd_split = cmd_strip.split(" ", 2)
    senderID = cmd_split[0][3:]
    receiveID = cmd_split[1]
    PK = cmd_split[2]
    return DECODE_PACKAGE(senderID, PK)

def DECODE_PACKAGE(senderID, PK):
    n_pk = int(PK[2:4])
    pk_split = PK.split(" ", n_pk)
    operator = pk_split[1]
    out = str(senderID)
    match operator[0]:
        case "E":
            out += " ERROR"
            match operator[3]:
                case "0":
                    #try again 10 times
                    return (out + " 0: Incorrect packet format")
                case "1":
                    return (out + " 1: Packet missing items")
                case "2":
                    return (out + " 2: Incorrect Device ID")
                case "3":
                    return (out + " 3: Incorrect Sender ID")
                case "4":
                    return (out + " 4: System is in error state.")
                case _:
                    print("Unkown Error number {}".format(operator[3]))

        case "A":
            return (out + " Acknowledge")

        case "B":
            return (out + " BUSY")

        case "V":
            ## LOG DATA HERE!!!
            #buffer pop
            #get the command that you sent to arduino 
            senderID = senderID
            #log_valid_cmd()

            return (out + " VALID")

        case "F":
            return (out + " FREE")
        
        case "T":
            out += " sensors "
            sensor_amount = int((n_pk)/2)
            Temp=[0.0]*5
            bubb=[0]*5
            for i in range(sensor_amount):
                sensor_type = pk_split[2*i+1][0]
                sensor_num = int(pk_split[2*i+1][1:])
                sensor_val = float(pk_split[2*i+2][1:])
                #print(i, sensor_type, sensor_num, sensor_val)
                if sensor_type == "T":
                    Temp[sensor_num-1] = sensor_val
                elif sensor_type == "B":
                    bubb[sensor_num-1] = int(sensor_val)
                else:
                    print("unknown sensor")
            return out + " Temperature: " + str(Temp) + " bubble " + str(bubb)

        case _:
            return out + " unrecognised package: " + PK

def SERIAL_WRITE_LINE(DEV,COMMAND):
    try:
        print("\nSent to Serial ==>", COMMAND)
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


# Functions to Generate Commands
def valve(Valve_num, state):
    command = "[sID1000 rID1001 PK2 V{} S{}]".format(Valve_num, state)
    return command

def pump(Pump_num, amount, dir=1):
    # "[sID1000 rID1001 PK3 P2 m50.25 D1]"
    command = "[sID1000 rID1001 PK3 P{} m{:.2f} D{}]".format(Pump_num, amount, dir)
    return command

def shutter(state, shutter_num=1):
    # "[sID1000 rID1001 PK2 I1 S0]"
    command = "[sID1000 rID1001 PK2 I{} S{}]".format(shutter_num, state)
    return command

def mixer(speed, time):
    return

def Sensor_read():
    return "[sID1000 rID1001 PK1 R]"


# FIFO Buffer
class Buffer:
    def __init__(self):
        self.buffer = []

    def IN(self, COMMAND):
        if type(COMMAND) is str:
            if len(self.buffer)<15:
                self.buffer.append(COMMAND)
            else:
                print("BUFFER_FULL, try later")
        if type(COMMAND) is list:
            if len(self.buffer)<15:
                for element in COMMAND:
                    self.buffer.append(element)
            else:
                print("BUFFER_FULL, try later")

    def OUT(self, DEV):
        if len(self.buffer):
            command = self.buffer[0]
            messages = WRITE(DEV, command)
            last = messages[len(messages)-1]
            return last

    def POP(self):
        if len(self.buffer):
            print("POPING")
            self.buffer.pop(0)

    def READ(self):
        return self.buffer

