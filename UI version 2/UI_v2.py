import time
import csv
import datetime
import tkinter as tk
from tkinter import ttk
import Serial_lib as com 
import CMD as cmd
import numpy as np

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

LARGE_FONT= ("Verdana", 20)
NORMAL_FONT= ("Verdana", 15)
SMALL_FONT= ("Verdana", 10)

frame_styles = {"relief": "groove",
                "bd": 3, "bg": "#f0a000",
                "fg": "#073bb3", "font": ("Arial", 9, "bold")}
                
                
#global variables 
lastmessage = ""
buffer = []
recipe_1 = [cmd.valve(1,0), cmd.pump(1, 50.2), cmd.valve(1,1), cmd.valve(2,0)]

def BEGIN_SERIAL(arduinos):
    global arduino_servo
    arduinos = com.OPEN_SERIAL_PORTS(com.ID_PORTS_AVAILABLE())
    if len(arduinos)>0:
        arduino_servo = arduinos[0]
    else:
        arduino_servo = ""
    return arduinos
    
arduinos = BEGIN_SERIAL([])

# UI 
def update_label(label, new_text):
    label.configure(text = new_text)
    return label

class initialise(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg="#708090", height=431, width=626)  # this is the background
        main_frame.pack(fill="both", expand="true")

        self.geometry("626x431")  # Sets window size to 626w x 431h pixels
        self.resizable(0, 0)  # This prevents any resizing of the screen
        self.title("Initialisation")

        title = tk.Label(main_frame, text = "Initialisation", font=LARGE_FONT)
        title.pack(pady=10,padx=10)
        

        
        def update_devices(label):
            global arduinos
            
            com.FLUSH_PORT(com.ID_PORTS_AVAILABLE())
            
            arduinos = BEGIN_SERIAL(arduinos)
            new_text = "there is {} arduinos connected".format(len(arduinos))
            label = update_label(label,new_text)
            print(arduinos)
            return
        
        button1 = ttk.Button(main_frame, text="Check connections",
         command=lambda: update_devices(label_arduino))
        button1.pack()

        label_arduino = tk.Label(main_frame, text ="there is {} arduinos connected".format(len(arduinos)), font=NORMAL_FONT)
        label_arduino.pack()
        
        button2 = ttk.Button(main_frame, text="CONTINUE",
         command=lambda: init.destroy())
        button2.pack()

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.add_command(label="Home", command=lambda: parent.show_frame(StartPage))

        manual_control = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Manual", menu=manual_control)
        manual_control.add_command(label="Valve", command=lambda: parent.show_frame(PageOne))
        manual_control.add_separator()
        manual_control.add_command(label="Pump", command=lambda: parent.show_frame(PageTwo))
        manual_control.add_command(label="Pumps", command=lambda: parent.show_frame(PageThree))

        menu_auto = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Auto", menu=menu_auto)
        menu_auto.add_command(label="Recipe", command=lambda: parent.show_frame(PageFour))
        menu_auto.add_separator()
        menu_auto.add_command(label="iterate", command=lambda: parent.show_frame(PageFive))

        menu_help = tk.Menu(self, tearoff=0)
        self.add_cascade(label="plots", menu=menu_help)
        menu_help.add_command(label="Open New Window", command=lambda: parent.OpenNewWindow())

class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Hardware control")

        container = tk.Frame(self, bg = "#BEB2A7", height=600, width=1024)
        container.pack(side="top", fill = "both", expand = "true")
        container.grid_rowconfigure(0, weight= 1)
        container.grid_columnconfigure(0, weight= 1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree, PageFour, PageFive):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)
        menubar = MenuBar(self)
        tk.Tk.config(self, menu=menubar)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
          
    def OpenNewWindow(self):
        OpenNewWindow()

    def Quit_application(self):
        self.destroy()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        title = tk.Label(self, text = "Home", font=LARGE_FONT)
        title.pack(pady=10,padx=10)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "control my valve", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        

        button2 = ttk.Button(self, text="close my valve :(",
         command=lambda: cmd.BUFFER_IN(buffer, cmd.valve(1,0)))
        button2.pack()

        button3 = ttk.Button(self, text="open my valve :)",
         command=lambda: cmd.BUFFER_IN(buffer, cmd.valve(1,1)))
        button3.pack()

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Pump me", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

    

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
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Pump from Ra or Rb", font=LARGE_FONT)
        label.pack(pady=10,padx=10)


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

        button4 = ttk.Button(self, text="Is there Liquid?",
            command=lambda: update_label(my_label, "yes"))
        button4.pack() 

        my_label = tk.Label(self, text = "no liquid", font=SMALL_FONT)
        my_label.pack()

class PageFour(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Recipe", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        MyText = "[cmd.valve(1,0), cmd.pump(1, 50.2), cmd.valve(1,1), cmd.valve(2,0)]"
        T = tk.Text(self, height = 3, width = 52)
        T.insert(tk.END, MyText)
        T.pack()

        button2 = ttk.Button(self, text="send your recipe to Ard",
         command=lambda: cmd.BUFFER_IN(buffer, recipe_1))
        button2.pack()     

class PageFive(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        
        label = tk.Label(self, text = "Run iterative loop", font=NORMAL_FONT, bg = frame_styles["bg"])
        label.grid(row=0, column= 0, columnspan=3)

        def entry_block(text, pos):
            row,col = pos
            T = tk.Label(self, text = text, font=SMALL_FONT, bg = frame_styles["bg"])
            entry = ttk.Entry(self, width=8)
            T.grid(row=row, column=col, sticky='E')
            entry.grid(row=row, column=col+1, sticky='W')
            return entry

        e_Ra_ml = entry_block("Ra:", [1,0])
        e_Ra_step = entry_block("step:",[1,2])

        e_Rb_ml = entry_block("Rb:",[2,0])
        e_Rb_step = entry_block("step:",[2,2])
        e_count = entry_block("loop count:",[3,0])

        button1 = ttk.Button(self, text="send", command=lambda: send_command())
        button1.grid(row=4, column=2) 

        def send_command():
            cmd_list = []
            Ra_ml = e_Ra_ml.get()
            Ra_step = e_Ra_step.get()
            Rb_ml = e_Rb_ml.get()
            Rb_step = e_Rb_step.get()
            count = int(e_count.get())

            for i in range(count):
                if Ra_ml!="" and Ra_step!="":
                    Ra_ml = float(Ra_ml) + float(Ra_step)*i
                    cmd_list.append(cmd.pump(1, Ra_ml))
                if Rb_ml!="" and Rb_step!="":
                    Ra_ml = float(Ra_ml) + float(Rb_step)*i
                    cmd_list.append(cmd.pump(1, float(Rb_ml)))

            cmd.BUFFER_IN(buffer, cmd_list)
            return
        
        
        

class OpenNewWindow(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.title("Here is the Title of the Window")
        self.geometry("500x200")
        self.resizable(0, 0)

        frame1 = ttk.LabelFrame(main_frame, text="Plotting the results")
        frame1.pack(expand=True, fill="both")

        label1 = tk.Label(frame1, font=("Verdana", 20), text="Plotting Page")
        label1.pack(side="top")

# LoopEvent1 = if cmd waiting in Buffer => read lines; Frequency = 1/200ms 
# LoopEvent2: empty buffer: if receive FREE => BUFFER_OUT fifo = send next command
def task():
    global lastmessage
    global buffer
    if (arduino_servo.inWaiting() > 0):
        messages = com.SERIAL_READ_LINE(arduino_servo)
        lastmessage = messages[-1]
        print("\nthe last message is ==>", lastmessage, "\n")
    if ("FREE" in lastmessage and len(buffer)>0):
        buffer,response = cmd.BUFFER_OUT(arduino_servo, buffer)
        lastmessage = response[len(response)-1]

    gui.after(100, task)
    time.sleep(0.01)

#initialisation 
init = initialise()
init.mainloop()

#GUI
gui = Main()
gui.after(100,task)
gui.mainloop()