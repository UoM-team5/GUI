import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
install("pyserial")

import time
import tkinter as tk
from tkinter import ttk
import serial
import Serial_lib as com 
import CMD as cmd


arduinos = com.OPEN_SERIAL_PORTS(com.ID_PORTS_AVAILABLE())
print(arduinos)
if len(arduinos)>0:
    arduino_servo = arduinos[0]


LARGE_FONT= ("Verdana", 14)
BUTTON_FONT= ("Verdana", 10)

#global variables 
lastmessage = ""
value = ''
buffer = []
recipe_1 = [cmd.valve(1,0), cmd.pump(1, 50.2), cmd.valve(1,1), cmd.valve(2,0)]

# UI 
class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Hardware control")

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight= 1)
        container.grid_columnconfigure(0, weight= 1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree, PageFour):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = "the Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="I want to control my valve",
         command=lambda: controller.show_frame(PageOne))
        button1.pack()

        button2 = ttk.Button(self, text="I want to control my stepper",
         command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="I want to control my System",
         command=lambda: controller.show_frame(PageThree))
        button3.pack()

        button4 = ttk.Button(self, text="Recipe!",
         command=lambda: controller.show_frame(PageFour))
        button4.pack()

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = "control my valve", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text="Home",
         command=lambda: controller.show_frame(StartPage))
        button1.pack()
        
        button2 = ttk.Button(self, text="close my valve :(",
         command=lambda: cmd.BUFFER_IN(buffer, cmd.valve(1,0)))
        button2.pack()

        button3 = ttk.Button(self, text="open my valve :)",
         command=lambda: com.WRITE(arduino_servo, cmd.valve(1,1)))
        button3.pack()

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = "Pump me", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Home",
         command=lambda: controller.show_frame(StartPage))
        button1.pack()

        MyText = "Type in the number of ml and press the button"
        T = tk.Text(self, height = 1, width = 52)
        T.insert(tk.END, MyText)
        T.pack()

        entry0 = ttk.Entry(self)
        entry0.pack()

        button2 = ttk.Button(self, text="send your text to Ard",
         command=lambda: com.WRITE(arduino_servo, cmd.pump(1, float(entry0.get()))))
        button2.pack()     

class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = "Pump from Ra or Rb", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Home",
         command=lambda: controller.show_frame(StartPage))
        button1.pack()

        MyText = "R A: Type in the number of ml"
        T1 = tk.Text(self, height = 1, width = 52)
        T1.insert(tk.END, MyText)
        T1.pack()

        entry0 = ttk.Entry(self)
        entry0.pack()

        button2 = ttk.Button(self, text="send your text to Ard",
         command=lambda: print(com.WRITE(arduino_servo, cmd.pump(1, float(entry0.get())))))
        button2.pack() 

        MyText2 = "R B: Type in the number of ml"
        T2 = tk.Text(self, height = 1, width = 52)
        T2.insert(tk.END, MyText2)
        T2.pack()

        entry1 = ttk.Entry(self)
        entry1.pack()

        button3 = ttk.Button(self, text="send your text to Ard",
         command=lambda: com.WRITE(arduino_servo, cmd.pump(1, float(entry1.get()))))
        button3.pack() 

        button4 = ttk.Button(self, text="Is there Liquid?")
        button4.pack() 

        my_string_var = tk.StringVar()

        def update_txt():
            my_string_var.set(value)

        my_label = tk.Label(self,
            textvariable = my_string_var, font=BUTTON_FONT)
        my_label.pack()

class PageFour(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = "Recipe", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Home",
         command=lambda: controller.show_frame(StartPage))
        button1.pack()

        MyText = "[cmd.valve(1,0), cmd.pump(1, 50.2), cmd.valve(1,1), cmd.valve(2,0)]"
        T = tk.Text(self, height = 3, width = 52)
        T.insert(tk.END, MyText)
        T.pack()

        button2 = ttk.Button(self, text="send your recipe to Ard",
         command=lambda: cmd.BUFFER_IN(buffer, recipe_1))
        button2.pack()     





# LoopEvent1 = if cmd waiting in Buffer => read lines; Frequency = 1/200ms 
# LoopEvent2: empty buffer: if receive FREE => BUFFER_OUT fifo = send next command
def task():
    global lastmessage
    global buffer
    if (arduino_servo.inWaiting() > 0):
        messages = com.SERIAL_READ_LINE(arduino_servo)
        lastmessage = messages[-1]
        lastmessage = lastmessage[-5:-1]
    if ("FREE" in lastmessage and len(buffer)>0):
        buffer,response = cmd.BUFFER_OUT(arduino_servo, buffer)
        lastmessage = response[-1]
        lastmessage = lastmessage[-5:-1]

    gui.after(100, task)
    time.sleep(0.01)

gui= Main()
gui.after(100,task)
gui.mainloop()