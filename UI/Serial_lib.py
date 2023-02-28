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

def OPEN_SERIAL_PORT(DEV):
    try:
        Dev = serial.Serial(port=DEV,baudrate=115200, timeout=.1)
        Dev.isOpen()
    except IOError:
        Dev.close()
        Dev = serial.Serial(port=DEV,baudrate=115200, timeout=.1)
        Dev.isOpen()
    except (OSError, serial.SerialException,ValueError):
        pass
    
    return Dev

def OPEN_SERIAL_PORTS(DEVS):
    DEVICES = []
    try:
        for i in range(len(DEVS)):
            try:
                Dev = serial.Serial(port=DEVS[i],baudrate=115200, timeout=.1)
                print(Dev)
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
        case "P":
            #[sID... rID... PK6 P1 V0 I0 M1 T1 B1 DeviceDesc]
            return senderID, pk_split
        case "E":
            out += " ERROR"
            match operator[3]:
                case "0":
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
            senderID = senderID

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

#components
class Pump:
    def __init__(self, device, ID, component_number: int, buffer):
        self.device = device
        self.ID = ID
        self.buffer = buffer
        self.num = component_number
        self.state = False
    
    def pump(self, volume: float, direction=1):
       self.buffer.IN([self.device, "[sID1000 rID{} PK3 P{} m{:.2f} D{}]".format(self.ID, self.num, volume, direction)])
    
    def set_state(self, state: bool):
        """Param bool state: set False->idle, True->used"""
        self.state = state
    
    def get_state(self):
        return self.state

class Valve:
    def __init__(self, device, ID, component_number: int, buffer):
        self.device = device
        self.ID = ID
        self.num = component_number
        self.buffer = buffer
        self.state = False
         
    def close(self):
        self.buffer.IN([self.device, "[sID1000 rID{} PK2 V{} S0]".format(self.ID, self.num)])

    def open(self):
        self.buffer.IN([self.device, "[sID1000 rID{} PK2 V{} S1]".format(self.ID, self.num)])

    def set_state(self, state: bool):
        """Param bool state: set False->closed, True->open"""
        self.state = state
    
    def get_state(self):
        return self.state

class Mixer:
    def __init__(self, deviceID, component_number):
        self.deviceID = deviceID
        self.num = component_number

    def mix(self, time):
        return "[sID1000 rID{} PK2 M{} S1]".format(self.deviceID, self.num)

class Sensor:
    pass

class Vessel: 
    def __init__(self, component_number: int, liquid_name: str, volume: float):
        self.num = component_number
        self.name = liquid_name
        self.vol = volume
    
    def sub(self, volume: float):
        self.vol = self.vol - volume

    def add(self, volume: float):
        self.vol = self.vol + volume
    
    def get_volume(self):
        return self.vol
    
    def set_volume(self, volume: float):
        self.vol = volume
    
    def set_name(self, name: str):
        self.name = name

    def get_name(self):
        return self.name
    
ves1 = Vessel(1,'H2', 2.3)
text = ves1.get_name
print(text)
    
#arduinos
class Nano:
    def __init__(self, device, ID):
        self.device = device
        self.ID = ID
        self.components = []
        self.state = False
        self.message = ""

    def get_id(self):
        #print(self.ID)
        return self.ID

    def get_device(self):
        return self.device

    def add_component(self, component):
        self.components.append(component)

    def toggle_state(self):
        self.state = not self.state
    
    def free(self):
        self.state = False

    def busy(self):
        self.state = True

    def get_state(self):
        # print("Device " + str(self.get_id) + "is " + str(self.state))
        return self.state
    
    def add_message(self, message):
        self.message = message
    
    def read_last(self):
        return self.message

# FIFO Buffer
class Buffer:
    def __init__(self, size=20):
        self.buffer = []
        self.size = size

    def IN(self, device_command: list):
        if len(self.buffer)<self.size:
            self.buffer.append(device_command)
        else: 
            print("buffer full")

    def OUT(self):
        if len(self.buffer):
            device, command = self.buffer[0]
            SERIAL_WRITE_LINE(device, command)

    def POP(self):
        if len(self.buffer):
            print("POP")
            self.buffer.pop(0)

    def READ(self) :
        # print("length: ", len(self.buffer))
        # print("\nBuffer Contents:\n", *[i[1] for i in self.buffer], sep = "\n")
        return self.buffer

    def LENGTH(self):
        #print("length of buffer:", len(self.buffer))
        return len(self.buffer)

    def RESET(self):
        self.buffer = []




