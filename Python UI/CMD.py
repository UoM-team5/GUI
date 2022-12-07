import Serial_lib as com 
import time

class Create_command():
    def __init__(self):
        pass


def get_component_device_id(component_type, component_num=1):
    return

# Command encoder
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
def BUFFER_IN(CMD_BUFFER, COMMAND):
    if type(COMMAND) is str:
        if len(CMD_BUFFER)<15:
            CMD_BUFFER.append(COMMAND)
        else:
            print("BUFFER_FULL, try later")
    if type(COMMAND) is list:
        if len(CMD_BUFFER)<15:
            for recipe_element in COMMAND:
                CMD_BUFFER.append(recipe_element)
        else:
            print("BUFFER_FULL, try later")

    return CMD_BUFFER
    
def BUFFER_OUT(DEV, CMD_BUFFER):
    if len(CMD_BUFFER)>0:
        command = CMD_BUFFER[0]
        response = com.WRITE(DEV, command)
        last_response = response[len(response)-1]

        i=3
        print("the last error response is here: ", last_response)
        if ("ERR" in last_response) and i!=0:
            response = com.WRITE(DEV, command)
            i=i-1
            print("I tried talking to him {i} times.\n enters one ear, exits the other")
        CMD_BUFFER.pop(0)
        return CMD_BUFFER, last_response


def CLEAR_BUFFER(CMD_BUFFER):
    CMD_BUFFER = []
    return CMD_BUFFER
