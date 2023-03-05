import serial
import serial.tools.list_ports
import csv, datetime, os


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
    return [-1]

def DECODE_LINES(cmd_list):
    for i in range(0,len(cmd_list)):
        cmd_list[i] = cmd_list[i].decode('UTF-8').replace('\r\n','')
        cmd_list[i] = DECODE_LINE(cmd_list[i])
        print(cmd_list[i])
    return cmd_list

def DECODE_LINE(command, Comps = None):
    if command[0]!="[" or command[-1]!="]":
        return "- " + command 
    cmd_strip = command[1:-1]
    cmd_split = cmd_strip.split(" ", 2)
    senderID = cmd_split[0][3:]
    receiveID = cmd_split[1]
    PK = cmd_split[2]
    return DECODE_PACKAGE(senderID, PK, Comps)

class MyStr(str):
    def __eq__(self, other):
        return self.__contains__(other)

def DECODE_PACKAGE(senderID, PK, Comps):
    n_pk = int(PK[2:4])
    pk_split = PK.split(" ", n_pk)
    operator = MyStr(pk_split[1])
    out = str(senderID)
    if n_pk==1:
        # single package commands
        match operator:
            case "ERR":
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

            case "ACK":
                return (out + " Acknowledge")

            case "BUSY":
                return (out + " BUSY")

            case "VALID": 
                senderID = senderID
                return (out + " VALID")

            case "FREE":
                return (out + " FREE")
            
            case _:
                return out + " unrecognised package: " + PK
    else:
        #multi package commands 
        match operator[0]:
            case "P":
                #Pump: [sID... rID PK3 P1 m10.2 D1]
                num = int(pk_split[1][1])
                vol = float(pk_split[2][1:])
                dir = int(pk_split[3][1])
                if num==(1 or 2 or 3):
                    try: 
                        Comps.ves_in[num-1].sub(float(vol))
                        Comps.main.add(float(vol))
                    except:
                        pass
                if num==4:
                    try: 
                        Comps.main.sub(float(vol))
                        Comps.ves_out[Comps.valves.output_vessel].add(float(vol))
                    except:
                        pass
                print("Pump num {}, vol {}, dir {} ".format(num, vol, dir) )
                return num, vol
            
            case "V":
                #Valve: [sID... rID PK2 V1 S]
                num = pk_split[1][1]
                state = pk_split[2][1]
                print("Valve num {}, state {} ".format(num, state))
                return num,state
            
            case "I":
                #Shutter: [sID... rID PK2 V1 S]
                num = pk_split[1][1]
                state = pk_split[2][1]
                print("Shutter num {}, state {} ".format(num, state))
                return num,state
            
            case "M":
                #mixer
                num = pk_split[1][1]
                state = pk_split[2][1]
                print("Mixer num {}, state {} ".format(num, state))
                return num,state
            
            case "S":
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
                print("operator ",operator)
                return out + " unrecognised cmd package: " + PK

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
    return STATE

def READ(DEV):
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

def Log(command, file_name = "commands.csv"):
    nowTime = datetime.datetime.now()
    time = nowTime.strftime("%H:%M:%S")

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name), mode ="a", newline='') as csvfile:
        writer = csv.writer(csvfile) 
        writer.writerow([time, command])

def delete_file(file_name = "commands.csv"):
    try:os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name))
    except:pass

def save_detail(names: list, volumes: list, file_name = "details.csv"):
    try:os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name))
    except:pass

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name), mode ="a", newline='') as csvfile:
        for i in range(len(names)):
            writer = csv.writer(csvfile) 
            writer.writerow([names[i], volumes[i]])

def vessel_detail(ent_Rn, ent_Rv):
    names=[]
    volumes=[]
    for i in range(len(ent_Rn)):
        try:
            names.append(ent_Rn[i].get())
            volumes.append(ent_Rv[i].get())
        except:pass
    save_detail(names, volumes)
    return

def read_csv(filename:str):
    try:
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), filename), mode = 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter = ",")
            array = list(reader)
            n = len(array)
            first_col = [0 for i in range(n)]
            second_col = [0 for i in range(n)]
            for x in range(n):
                first_col[x]= array[x][0]
                second_col[x]= array[x][1]
        return first_col, second_col
    except:
        return ['']*3,['']*3
    

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
    output_vessel = 0
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

    def mid(self):
        self.buffer.IN([self.device, "[sID1000 rID{} PK2 V{} S2]".format(self.ID, self.num)])

    def set_state(self, state: int):
        """Param bool state: set False->closed, True->open"""
        self.state = state
    
    def get_state(self):
        return self.state
    
def valve_states(Valves, out: int):
    Valves[0].output_vessel = out
    match out:
        case 0: states = '02222'
        case 1: states = '10222'
        case 2: states = '11022'
        case 3: states = '11102'
        case 4: states = '11110'
        case 5: states = '11111'
        case _: 
            print("error unknown valve state")
            return
    for idx in range(0, len(states)):
        match int(states[idx]):
            case 0: Valves[idx].close()
            case 1: Valves[idx].open()
            case 2: Valves[idx].mid()
            case _: pass

class Shutter:
    def __init__(self, device, ID, component_number: int, buffer):
        self.device = device
        self.ID = ID
        self.num = component_number
        self.buffer = buffer
        self.state = 0
         
    def close(self):
        self.buffer.IN([self.device, "[sID1000 rID{} PK2 I{} S0]".format(self.ID, self.num)])

    def open(self):
        self.buffer.IN([self.device, "[sID1000 rID{} PK2 I{} S1]".format(self.ID, self.num)])

    def mid(self):
        self.buffer.IN([self.device, "[sID1000 rID{} PK2 I{} S2]".format(self.ID, self.num)])

    def set_state(self, state: int):
        self.state = state
    
    def get_state(self):
        return self.state

class Mixer:
    def __init__(self, device, ID, component_number: int, buffer):
        self.device = device
        self.ID = ID
        self.num = component_number
        self.buffer = buffer

    def mix(self, speed: int):
        return "[sID1000 rID{} PK2 M{} S{}]".format(self.ID, self.num, speed)

class Sensor:
    pass

class Vessel: 
    def __init__(self, volume = 10.0, liquid_name = 'none'):
        self.vol = volume
        self.name = liquid_name
        
    def sub(self, volume: float):
        self.vol = self.vol - volume

    def add(self, volume: float):
        self.vol = self.vol + volume
    
    def set_volume(self, volume: float):
        self.vol = volume

    def get_volume(self):
        return self.vol
    
    def set_name(self, name: str):
        self.name = name

    def get_name(self):
        return self.name

class Components:
    pass
    
class Nano:
    state = False
    def __init__(self, device, ID):
        self.device = device
        self.ID = ID
        self.components = ""
        self.message = ""

    def get_id(self):
        #print(self.ID)
        return self.ID

    def get_device(self):
        return self.device

    def add_component(self, components: str):
        self.components = components
    
    def get_components(self):
        return self.components
        
    def toggle_state(self):
        self.state = not self.state
    
    def free(self):
        self.state = False

    def busy(self):
        self.state = True
    
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
            # device, command = self.buffer[0]
            WRITE(*self.buffer[0])

    def POP(self):
        if len(self.buffer):
            print("POP")
            device, command = self.buffer.pop(0)
        return command
    def READ(self) :
        # print("\nBuffer Contents:\n", *[i[1] for i in self.buffer], sep = "\n")
        # reurns 2 outputs: device, command = self.buffer
        return self.buffer

    def LENGTH(self):
        #print("length of buffer:", len(self.buffer))
        return len(self.buffer)

    def RESET(self):
        self.buffer = []
