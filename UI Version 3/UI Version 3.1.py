import time
import tkinter as tk
from tkinter import ttk
import Serial_lib as com 
import cv2
import customtkinter
from PIL import Image, ImageTk

LARGE_FONT= ("Verdana", 20)
NORMAL_FONT= ("Verdana", 15)
SMALL_FONT= ("Verdana", 10)

frame_styles = {"relief": "groove", "white": "#fff", "black": "#000000",
                "bd": 3, "bg": "#f0a000",
                "fg": "#073bb3", "font": ("Arial", 9, "bold")}
                      
#global variables 
lastmessage = ""
messages = []
buffer = com.Buffer()
recipe_1 = [com.valve(1,0), com.pump(1, 5.2), com.valve(1,1)]

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

# Import images:
#add_NewExp_image = Image.Tk.PhotoImage(Image.open("UI_New_Exp_logo.png").resize(20,20), Image.ANTIALIAS)
#add_LoadExp_image = Image.Tk.PhotoImage(Image.open("UI_Load_Exp_logo.png").resize(20,20), Image.ANTIALIAS)

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

        for F in (StartPage, PageOne, PageTwo, PageThree, PageFour, PageFive, Page_New_Experiment, Page_Load_Data, Page_Load_Experiment, Page_See_History):
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
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])
        title = tk.Label(self, text = "Home", font=LARGE_FONT, bg = frame_styles["white"])
        title.place(x=156, y=20)

        #button_custom = customtkinter.CTkButton(master = self, image=add_NewExp_image, text="New Experiment", width=190, height=40, compound = "top")

        button1 = ttk.Button(self, text="New Experiment",
         command=lambda: controller.show_frame(Page_New_Experiment))
        button1.place(x=100, y=70) 

        button2 = ttk.Button(self, text="Load Experiment",
         command=lambda: controller.show_frame(Page_Load_Experiment))
        button2.place(x=203, y=70)

        button3 = ttk.Button(self, text="See History",
         command=lambda: controller.show_frame(Page_See_History))
        button3.place(x=120, y=110)

        button4 = ttk.Button(self, text="Load Data",
         command=lambda: controller.show_frame(Page_Load_Data))
        button4.place(x=203, y=110)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])
        label = tk.Label(self, text = "Valve Control", font=LARGE_FONT, bg = frame_styles["white"])
        label.grid(row=0, column= 2, columnspan=3)
        
        def entry_block(text, pos):
            row,col = pos
            T = tk.Label(self, text = text, font=SMALL_FONT, bg = frame_styles["white"])
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
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])
        label = tk.Label(self, text = "Pump Control", font=LARGE_FONT, bg = frame_styles["white"])
        label.pack(pady=10,padx=10)

class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])
        label = tk.Label(self, text = "Multi-Pump Control", font=LARGE_FONT)
        label.pack(pady=10,padx=10)


        MyText = "R A: Type in the number of ml"
        T1 = tk.Text(self, height = 1, width = 52)
        T1.insert(tk.END, MyText)
        T1.pack()

class PageFour(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])
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
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])
        
        label = tk.Label(self, text = "Iterative Sequence", font=LARGE_FONT, bg = frame_styles["white"])
        label.grid(row=0, column= 0, columnspan=3)

        def entry_block(text, pos):
            row,col = pos
            T = tk.Label(self, text = text, font=SMALL_FONT, bg = frame_styles["white"])
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
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])
        label = tk.Label(self, text = "Enter Recipe", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        buttonN = ttk.Button(self, text="Open Camera", command=lambda: camera())
        buttonN.pack(pady=100,padx=100)

class Page_Load_Experiment(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])

class Page_See_History(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])

class Page_Load_Data(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["white"])



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