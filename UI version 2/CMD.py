import Serial_lib as com 
import time

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

def Sensor_read():
    return "[sID1000 rID1001 PK1 R]"

#arduino output decoder
def decode_output(ard_out):
    #com standard -: return output
    if ard_out[0:-1]=="[]":
        if "ERR" in ard_out:
            return 

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
        command = CMD_BUFFER.pop(0)
        print("Send to arduino: ", command)
        response = com.WRITE(DEV, command)
        return CMD_BUFFER, response

def CLEAR_BUFFER(CMD_BUFFER):
    return

"""
buffer = []
recipe_1 = [valve(1,0), pump(1, 50.2), valve(1,1), valve(2,0), pump(1,21), shutter(0), shutter(1)]
for i in recipe_1:
    buffer = BUFFER_IN(buffer, i)
print(buffer)

while len(buffer)>0:
    buffer = BUFFER_OUT(buffer)
    time.sleep(2) 
"""