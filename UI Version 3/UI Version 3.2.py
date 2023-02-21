import time
import tkinter as tk
from tkinter import ttk
import Serial_lib as com 
import cv2
import customtkinter
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
import numpy as np

LARGE_FONT= ("Verdana", 20)
NORMAL_FONT= ("Verdana", 15)
SMALL_FONT= ("Verdana", 10)

frame_styles = {"relief": "groove",
                "bd": 3, "bg": "#DDDDDD",
                "fg": "#073bb3", "font": ("Arial", 12, "bold")}
entry_styles = {"relief": "groove", "width": 8,
                "bd": 5, "font": ("Arial", 10, "normal")}
label_styles = {"relief": "flat", "bg": "#DDDDDD",
                "bd": 3, "font": ("Verdana", 10, "normal")}
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")


#global variables 
lastmessage = ""
messages = []
buffer = com.Buffer()
recipe_1 = [com.valve(1,0), com.pump(1, 5.2), com.valve(1,1)]
dataset= np.random.normal(25, 10, 500)

def BEGIN_SERIAL(arduinos):
    global arduino_servo
    arduinos = com.OPEN_SERIAL_PORTS(com.ID_PORTS_AVAILABLE())
    if len(arduinos)>0:
        arduino_servo = arduinos[0]
    else:
        arduino_servo = ""
    return arduinos
    
arduinos = BEGIN_SERIAL([])

def camera():
    c = cv2.VideoCapture(0)
    while(1):
        _,f = c.read()
        cv2.imshow('e2',f)
        if cv2.waitKey(5)==27:
            break
    cv2.destroyAllWindows()

def num_reactants(frame, number):
    n = int(number.get() or 0)
    
    lb_arr = [0 for i in range(n)]
    entry_arr = [0 for i in range(n)]
    pos = 0.4

    for x in range(n):
        text = str("Reactant ") + str(x+1) + str(":")
        lb_arr[x], entry_arr[x] = entry_block(text, frame)
        init_place_entry_block(lb_arr[x], entry_arr[x], pos)
        pos += 0.1
    return entry_arr, n

def show_plot(data):
    plt.hist(data, 50)
    plt.show()

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

        button2 = ttk.Button(self, text="ask Details",
         command=lambda: com.WRITE(arduino_servo, "[sID1000 rID1001 PK1 DETAIL]"))
        button2.pack()  

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
        self.add_cascade(label="Plots", menu=menu_help)
        menu_help.add_command(label="Open New Window", command=lambda: parent.OpenNewWindow(show_plot(dataset)))

class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Hardware control")

        container = tk.Frame(self, bg = "#BEB2A7", height=600, width=1024)
        container.pack(side="top", fill = "both", expand = "true")
        container.grid_rowconfigure(0, weight= 1)
        container.grid_columnconfigure(0, weight= 1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree, PageFour, PageFive, Page_New_Experiment, Page_Load_Data, Page_Load_Experiment, Page_See_History, Page_Testing, P_Test_Exp, P_Test_Comp):
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
        title = tk.Label(self, text = "Home", font=LARGE_FONT, bg = frame_styles["bg"])
        title.place(x=156, y=20)

        photo1 = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "New_Exp_2.png"), "r").resize((40,30), Image.ANTIALIAS))
        button1 = customtkinter.CTkButton(self, text="New Experiment", image=photo1, width=150, height=40, compound='left', 
                                          #fg_color="#D35858", hover_color="#C77C78", 
                                          command=lambda: controller.show_frame(Page_New_Experiment))
        button1.place(relx=0.05, rely=0.25)

        photo2 = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Load_Exp_2.png"), "r").resize((40,30), Image.ANTIALIAS))
        button2 = customtkinter.CTkButton(self, text="Load Experiment", image=photo2, width=150, height=40, compound='left', 
                                          #fg_color="#D35858", hover_color="#C77C78", 
                                          command=lambda: controller.show_frame(Page_New_Experiment))
        button2.place(relx=0.55, rely=0.25)


        photo3 = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "See_Hist.png"), "r").resize((30,30), Image.ANTIALIAS))
        button3 = customtkinter.CTkButton(self, text="See History", image=photo3, width=150, height=40, compound='left', 
                                          #fg_color="green", hover_color="light-green", 
                                          command=lambda: controller.show_frame(Page_New_Experiment))
        button3.place(relx=0.05, rely=0.45)

        photo4 = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Load_Data.png"), "r").resize((30,30), Image.ANTIALIAS))
        button4 = customtkinter.CTkButton(self, text="Load Data", image=photo4, width=150, height=40, compound='left', 
                                          #fg_color="green", hover_color="light-green", 
                                          command=lambda: controller.show_frame(Page_New_Experiment))
        button4.place(relx=0.55, rely=0.45)

        photo5 = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "arcadius.png"), "r"))
        button5 = customtkinter.CTkButton(self, text="Testing ARCaDUIS", image=photo5, width=150, height=40, compound='top', 
                                          #fg_color="green", hover_color="light-green", 
                                          command=lambda: controller.show_frame(Page_Testing))
        button5.place(relx=0.5, rely=0.75, anchor="center")

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Valve Control", font=LARGE_FONT, bg = frame_styles["bg"])
        label.grid(row=0, column= 2, columnspan=3)
        
        def entry_block(text, pos):
            row,col = pos
            T = tk.Label(self, text = text, font=SMALL_FONT, bg = frame_styles["bg"])
            entry = ttk.Entry(self, width=8)
            T.grid(row=row, column=col, sticky='E')
            entry.grid(row=row, column=col+1, sticky='W')
            return entry

        valve_number = entry_block("Valve number: ", [1,1])

        button2 = ttk.Button(self, text="close",
         command=lambda: buffer.IN(com.valve(int(valve_number.get()),0)))
        button2.grid(column=2, sticky='w')

        button3 = ttk.Button(self, text="open",
         command=lambda: buffer.IN(com.valve(int(valve_number.get()),1)))
        button3.grid(column=2, sticky='w')

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Pump Control", font=LARGE_FONT, bg = frame_styles["bg"])
        label.pack(pady=10,padx=10)

class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Multi-Pump Control", font=LARGE_FONT)
        label.pack(pady=10,padx=10)


        MyText = "R A: Type in the number of ml"
        T1 = tk.Text(self, height = 1, width = 52)
        T1.insert(tk.END, MyText)
        T1.pack()

class PageFour(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Recipe", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        MyText = str(recipe_1)
        T = tk.Text(self, height = 3, width = 52)
        T.insert(tk.END, MyText)
        T.pack()

        button2 = ttk.Button(self, text="send your recipe to Ard",
         command=lambda: buffer.IN(recipe_1))
        button2.pack()     

class PageFive(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        
        label = tk.Label(self, text = "Iterative Sequence", font=LARGE_FONT, bg = frame_styles["bg"])
        label.grid(row=0, column= 0, columnspan=3)

        def entry_block(text, pos):
            row,col = pos
            T = tk.Label(self, text = text, font=SMALL_FONT, bg = frame_styles["bg"])
            entry = ttk.Entry(self, width=8)
            T.grid(row=row, column=col, sticky='E')
            entry.grid(row=row, column=col+1, sticky='W')
            return entry

        e_Ra_ml = entry_block("Liquid A:", [1,0])
        e_Ra_step = entry_block("step A:",[1,2])

        e_Rb_ml = entry_block("Liquid B:",[2,0])
        e_Rb_step = entry_block("step B:",[2,2])
        e_count = entry_block("iterations:",[3,0])

        button1 = ttk.Button(self, text="Start", command=lambda: send_command())
        button1.grid(row=4, column=2) 

        def send_command():
            cmd_list = []
            Ra_ml_init = e_Ra_ml.get()
            Ra_step = e_Ra_step.get()
            Rb_ml_init = e_Rb_ml.get()
            Rb_step = e_Rb_step.get()
            count = int(e_count.get())

            for i in range(count):
                if Ra_ml_init!="" and Ra_step!="":
                    Ra_ml = float(Ra_ml_init) + float(Ra_step)*i
                    cmd_list.append(com.pump(1, Ra_ml))
                if Rb_ml_init!="" and Rb_step!="":
                    Rb_ml = float(Rb_ml_init) + float(Rb_step)*i
                    cmd_list.append(com.pump(1, float(Rb_ml)))

            buffer.IN(cmd_list)
            return

class Page_New_Experiment(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Enter Recipe", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        frame1 = tk.Frame(self, width=100, highlightbackground='grey', highlightthickness=3, bg = frame_styles["bg"])
        num_react = tk.Label(frame1, label_styles, text="NUmber of Reactants:")
        num_react.grid(column=0, row=0)
        entry_react = ttk.Entry(frame1, width=5)
        entry_react.place(relx = 0.62, rely = 0.15, anchor = 'center') 
        textbox1 = tk.Entry(frame1, textvariable=entry_react)
        textbox1.grid(row=0, column=1)
        button1 = tk.Button(frame1, command=num_reactants(frame1, entry_react), text="Ok")
        blank = tk.Label(frame1, text=" ")
        blank.grid(row=0, column=2)
        button1.grid(row=0, column=3)
        frame1.place(relx=0.1, rely=0.21, anchor='nw')

        entry_arr, n= num_reactants(frame1,entry_react) # This is empty

        buttonN = ttk.Button(self, text="Open Camera", command=lambda: camera())
        buttonN.pack(pady=100,padx=100)

class Page_Load_Experiment(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])

class Page_See_History(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])

class Page_Load_Data(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])

class Page_Testing(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])

        button1 = ttk.Button(self, text="Test Individual Components", command=lambda: controller.show_frame(P_Test_Comp))
        button1.pack(pady=100,padx=100)

        button2 = ttk.Button(self, text="Perform Test Experiment", command=lambda: controller.show_frame(P_Test_Exp) )
        button2.pack(pady=100,padx=100)
    

class P_Test_Comp(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Test Components", font=LARGE_FONT)
        label.place(relx=0.5,rely=0.15, anchor="center")

        def entry_block(text, pos):
            row,col = pos
            T = tk.Label(self, text = text, font=SMALL_FONT, bg = frame_styles["bg"])
            entry = ttk.Entry(self, width=8)
            T.grid(row=row, column=col, sticky='E')
            entry.grid(row=row, column=col+1, sticky='W')
            #entry.place(row=row, column=col+1, sticky='W')

            return entry

        valve_number = entry_block("Valve number: ", [1,1])

        button2 = ttk.Button(self, text="close",
         command=lambda: buffer.IN(com.valve(int(valve_number.get()),0)))
        button2.grid(column=2, sticky='w')

        button3 = ttk.Button(self, text="open",
         command=lambda: buffer.IN(com.valve(int(valve_number.get()),1)))
        button3.grid(column=2, sticky='w')
        








class P_Test_Exp(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])
        label = tk.Label(self, text = "Test Experiment", font=LARGE_FONT)
        label.pack(pady=10,padx=10)




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


def event_handler(MESSAGES):
    global lastmessage
    global buffer 
    for MESSAGE in MESSAGES:
        match MESSAGE[5]:
            case "E":
                print('REPEAT')

            case "V":
                buffer.POP()
                print("left in the buffer:", buffer.READ())

            case "F":
                if len(buffer.READ())>0:
                    lastmessage = buffer.OUT(arduino_servo)
                    
            case _:
                pass
    
    return 


def init_task():
    global lastmessage
    global messages
    if (arduino_servo.inWaiting() > 0):
        messages = com.SERIAL_READ_LINE(arduino_servo)
        lastmessage = messages[len(messages)-1]
        print("the last messge is: ", lastmessage)
        messages=[lastmessage]
    init.after(200, init_task)
    time.sleep(0.01)
#initialisation 
#init = initialise()
#init.after(200, init_task)
#init.mainloop()

def task():
    global lastmessage
    global messages
    global buffer

    
    if (arduino_servo.inWaiting() > 0):
        messages = com.SERIAL_READ_LINE(arduino_servo)
        lastmessage = messages[len(messages)-1]
        event_handler(messages)
        messages=[lastmessage]

     
    if len(messages)>0 and len(buffer.READ())>0:
        event_handler(messages)
        lastmessage = messages[len(messages)-1]
        messages=[]
    

    gui.after(100, task)
    time.sleep(0.01)
#GUI
gui = Main()
gui.after(100,task)
gui.mainloop()