import time
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import customtkinter as ctk
import os
import Serial_lib as com 
from Serial_lib import Pump, Valve, Shutter, Mixer, Sensor, Vessel, Nano 
import cv2 
 
# UI styles 
LARGE_FONT= ("Consolas", 30)
styles = {"relief": "groove",
                "bd": 3, "bg": "#DDDDDD",
                "fg": "#073bb3", "font": ("Consolas", 15, "bold")}
entry_styles = {"relief": "groove", "width": 8,
                "bd": 5, "font": ("Arial", 12, "normal")}
button_styles = {"relief": "groove",
                "bd": 5, "font": ("Arial", 10, "normal")}
label_font = ("Consolas", 15, "normal")
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")
#init comms

buffer = com.Buffer()
def init_module():
    global arduinos, device, V, P, M, S, R, Comps
    Ports = com.ID_PORTS_AVAILABLE()
    arduinos = [0]*4
    V = [0]*5
    P = [0]*4
    S = 0
    M = 0
    R = [0]*8
    R[7] = Vessel(0, "main")
    for i in range(len(Ports)):
        print("\nSource: ", Ports[i])
        device = com.OPEN_SERIAL_PORT(Ports[i])
        print("\nDevice: ", device)
        while(device.inWaiting() == 0):
            time.sleep(0.1)

        message = com.READ(device)
        deviceID  = message[0][0:4]
        print("\narduino: ", deviceID)
        
        if deviceID=="1001":
            arduinos[0] = Nano(device, deviceID)
            arduinos[0].add_component("Pump 1")
            R[0] = Vessel()
            P[0] = Pump(device, deviceID, 1, buffer)
        if deviceID=="1002":
            arduinos[1] = Nano(device, deviceID)
            arduinos[1].add_component("Pump 2")
            R[1] = Vessel()
            P[1] = Pump(device, deviceID, 2, buffer)
        if deviceID=="1003":
            arduinos[2] = Nano(device, deviceID)
            arduinos[2].add_component("Pump 3")
            R[2] = Vessel()
            P[2] = Pump(device, deviceID, 3, buffer)
        if deviceID=="1004":
            arduinos[3] = Nano(device, deviceID)
            arduinos[3].add_component("Pump 4, V1-V5")
            V[0] = Valve(device, deviceID, 1, buffer)
            V[1] = Valve(device, deviceID, 2, buffer)
            V[2] = Valve(device, deviceID, 3, buffer)
            V[3] = Valve(device, deviceID, 4, buffer)
            V[4] = Valve(device, deviceID, 5, buffer)

            P[3] = Pump(device, deviceID, 4, buffer)
        if deviceID=="1005":
            M = Mixer(device, deviceID, 1, buffer)
            S = Shutter(device, deviceID, 1, buffer)
    
    for i in range(len(arduinos)):
        try:arduinos.remove(0)
        except:pass
    print("\n------------End initialisation--------------\n\n")
    Comps = com.Components()
    Comps.vessels = R
    Comps.valves = V
    Comps.pumps = P
    Comps.mixer = M
    Comps.shutter = S

    return

# UI functions

def update_label(label, new_text):
    label.configure(text = new_text)
    return label

def add_image(file_name, frame, relx, rely, size = (200,40), anchor='center'):
    photo = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images\\', file_name), "r"), size=size)
    label = ctk.CTkLabel(frame, image = photo, text="")
    label.image = photo
    label.place(relx = relx, rely = rely, anchor = anchor)

def btn(frame, text):
    btn = ctk.CTkButton(frame, 
                        text=text,
                        border_width=0,
                        border_color='black',
                        corner_radius=5, 
                        width=50, height=20, 
                        compound = 'left')
    return btn

def btn_img(frame, text, file_name, Xresize = 30, Yresize = 30):
    try:
        photo = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'images\\', file_name), "r"), size = (Xresize,Yresize))

    except:
        photo=None
    btn = ctk.CTkButton(frame, 
                        text=text, 
                        image = photo,
                        #fg_color='darkgrey',
                        #hover_color='darkblue', 
                        #border_width=1,
                        #border_color='black',
                        corner_radius=10, 
                        width=150, height=40,
                        compound = 'left')
    btn.image = photo
    return btn

def entry_block(text: str, frame, spin=False, from_ = 0, to = 10):
    """label followed by entry widget"""
    lbl = ctk.CTkLabel(frame, text = text)
    if (spin):
        entry = ttk.Spinbox(frame, from_=from_, to=to, width=2, wrap=True)
        entry.set(from_)
    else:
        entry = ctk.CTkEntry(frame,
                            width=50,
                            height=25,
                            border_width=0,
                            corner_radius=2)

    return lbl, entry

def place_entry_block(rely, lbl, entry):
    lbl.place(relx = 0.5, rely = rely, anchor = 'e')
    entry.place(relx = 0.55, rely = rely, anchor = 'w')
    return lbl, entry

def camera():
    #While loop in function = everything else stops = bad
    c = cv2.VideoCapture(0)
    while(1):
        _,f = c.read()
        cv2.imshow('e2',f)
        if cv2.waitKey(5)==27:
            break
    cv2.destroyAllWindows()

# UI classes
class Frame(ctk.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)
        self.label = ctk.CTkLabel(self, text=text)
        self.label.grid(row=0, column=0, padx=20)

class initialise(ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)

        main_frame = ctk.CTkFrame(self)  # this is the background
        main_frame.pack(fill="both", expand="true")

        self.geometry("600x400")  # 600w x 400h pixels
        #self.resizable(0, 0)  # This prevents any resizing of the screen
        self.title("Initialisation")

        title = ctk.CTkLabel(main_frame, text = "Initialise", font=LARGE_FONT)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')


        
        def update_devices():
            init_module()
            #refer to actual object returned if none= do not update label
            if len(arduinos):
                text = ""
                for arduino in arduinos:
                    text  += "arduino: '{}' : {}\n".format(arduino.get_id(), arduino.get_components())

                update_label(details, text)
        
        frame1 = Frame(main_frame, text = "Setup communcation")
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')
        
        btn1 = btn(frame1, text="Initialise")
        btn1.configure(command=lambda: update_devices())
        btn1.place(relx = 0.5, rely = 0.2, anchor = 'center') 

        ard_detail = "no arduino"
        details = ctk.CTkLabel(frame1, font=label_font, text=ard_detail,justify= 'left')
        details.place(relx = 0.5, rely = 0.5, anchor = 'center') 

        btn2 = btn(frame1, text="FINISH")
        btn2.configure(command=lambda: init.destroy())
        btn2.place(relx = 0.5, rely = 0.9, anchor = 'center') 
        
        update_devices()

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.configure(background= 'blue', fg='red')

        self.add_command(label="Home", command=lambda: parent.show_frame(P_Start))

        self.add_command(label="Manual", command=lambda: parent.show_frame(P_Test))

        menu_auto = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Auto", menu=menu_auto)
        menu_auto.add_command(label="Recipe",font=('Arial',11), command=lambda: parent.show_frame(P_Auto))
        menu_auto.add_separator()
        menu_auto.add_command(label="iterate",font=('Arial',11), command=lambda: parent.show_frame(P_Iter))

        menu_help = tk.Menu(self, tearoff=0)
        self.add_cascade(label="plots", menu=menu_help)
        menu_help.add_command(label="Open New Window",font=('Arial',11), command=lambda: parent.OpenNewWindow())

class Main(ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)

        ctk.CTk.wm_title(self, "ARCaDIUS")

        self.geometry("700x431") 
        self.minsize(500,300) 
        container = ctk.CTkFrame(self, height=600, width=1024)
        container.pack(side="top", fill = "both", expand = "true")
        container.grid_rowconfigure(0, weight= 1)
        container.grid_columnconfigure(0, weight= 1)
        self.frames = {}

        for F in (P_Start, P_Test, P_Auto, P_Iter, P_Hist):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(P_Start)
        menubar = MenuBar(self)
        ctk.CTk.config(self, menu=menubar)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
          
    def OpenNewWindow(self):
        OpenNewWindow()

    def Quit_application(self):
        self.destroy()

class P_Start(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        add_image("arcadius.png", self, relx=0.5, rely=0.05, size=(200,40), anchor = 'n')

        frame1 = Frame(self, fg_color="transparent")
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')

        btn1=btn_img(frame1, "Manual", "manual.png")
        btn1.configure(command=lambda: controller.show_frame(P_Test))
        btn1.place(relx = 0.45, rely = 0.2, anchor = 'e')
        
        btn2=btn_img(frame1, "Automate", "auto.png")
        btn2.configure(command=lambda: controller.show_frame(P_Auto))
        btn2.place(relx = 0.55, rely = 0.2,  anchor = 'w')

        btn3=btn_img(frame1, "History", "book.png")
        btn3.configure(command=lambda: controller.show_frame(P_Hist))
        btn3.place(relx = 0.45, rely = 0.4, anchor = 'e')

        btn4=btn_img(frame1, "Iterate", "iter.png")
        btn4.configure(command=lambda: controller.show_frame(P_Iter))
        btn4.place(relx = 0.55, rely = 0.4, anchor = 'w')

        btn4 = btn(frame1, text="Exit")
        btn4.configure(command=lambda: controller.Quit_application())
        btn4.place(relx = 0.5, rely = 0.9, anchor = 'center')

class P_Test(ctk.CTkFrame):

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)
        title = ctk.CTkLabel(self, text = "Manual Control", font=LARGE_FONT)
        title.place(relx = 0.5, rely = 0.05, anchor = 'center')
        
        frame1 = Frame(self, text = "Valve")
        frame1.place(relx=0.175, rely=0.15, relwidth=0.3, relheight=0.8, anchor = 'n')

        frame2 = Frame(self, text = "Pump")
        frame2.place(relx=0.5, rely=0.15, relwidth=0.3, relheight=0.8, anchor = 'n')

        frame3 = Frame(self, text = "Mixer")
        frame3.place(relx=0.825, rely=0.15, relwidth=0.3, relheight=0.38, anchor = 'n')

        frame4= Frame(self, text = "Sensors")
        frame4.place(relx=0.825, rely=0.55, relwidth=0.3, relheight=0.4, anchor = 'n')

        #box 1 Valve
        _, ent_valve = place_entry_block(0.2, *entry_block("select valve: ", frame1, True, 0, len(V)))

        btn1 = btn(frame1, text="close")
        btn1.configure(command=lambda: V[int(ent_valve.get())].close())
        btn1.place(relx = 0.48, rely = 0.3, anchor = 'e')
        btn2 = btn(frame1, text="open")
        btn2.configure(command=lambda: V[int(ent_valve.get())].open())
        btn2.place(relx = 0.52, rely = 0.3, anchor = 'w')
        btn3 = btn(frame1, text="mid")
        btn3.configure(command=lambda: V[int(ent_valve.get())].mid())
        btn3.place(relx = 0.5, rely = 0.4, anchor = 'center')

        #box 2 pump
        _, ent_pump = place_entry_block(0.2,*entry_block("select pump: ", frame2, True, 0, len(P)-1))
        _, ent_vol = place_entry_block(0.3, *entry_block("Volume (ml)", frame2))

        btn1 = btn(frame2, text="send")
        btn1.configure(command=lambda: P[int(ent_pump.get())].pump(float(ent_vol.get())))
        btn1.place(relx = 0.5, rely = 0.4, anchor = 'center')

        #box 3 mixer
        _, ent_mix = place_entry_block(0.2, *entry_block("speed : ", frame3))
        btn1 = btn(frame3, text="send")
        btn1.configure(command=lambda: print("mixing speed: ", ent_mix.get()))
        btn1.place(relx = 0.5, rely = 0.35, anchor = 'center')

class P_Auto(ctk.CTkFrame):

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)
        label = ctk.CTkLabel(self, text = "Recipe", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        btn1 = btn_img(self, "whatever", "frog.png")
        btn1.pack(pady=10,padx=10)

class P_Iter(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)

        title = ctk.CTkLabel(self, text = "Iterative experiment", font=LARGE_FONT)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')

        frames = [0]*5
        frames[0] = Frame(self, text = "Settings of experiments")
        frames[0].place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')
        frames[1] = Frame(frames[0], text = "volume", fg_color= "transparent")
        frames[1].place(relx= 0.75, rely = 0.05, relwidth=0.25, relheight=0.6, anchor = 'ne')
        frames[2] = Frame(frames[0], text = "steps", fg_color= "transparent")
        frames[2].place(relx= 0.75, rely = 0.05, relwidth=0.25, relheight=0.6, anchor = 'nw')
        frames[3] = Frame(frames[0], text = "Send", fg_color= "transparent")
        frames[3].place(relx= 0.75, rely = 0.65, relwidth=0.4, relheight=0.3, anchor = 'n')

        def on_click(checkbutton_var, widgets, pos: int):
            [lbl, ent_vol, lbls, ent_step] = widgets
            if checkbutton_var.get() == 1:
                place_entry_block(pos, lbl, ent_vol)
                place_entry_block(pos, lbls, ent_step)
            else:
                for widget in widgets:
                    widget.place_forget()

            
        lblA, ent_volA = entry_block("Liquid A:",frames[1])
        lblsA, ent_stepA = entry_block("step A:",frames[2])
        place_entry_block(0.2, lblA, ent_volA)
        place_entry_block(0.2, lblsA, ent_stepA)
        widgetsA = [lblA, ent_volA, lblsA, ent_stepA]

        lblB, ent_volB = entry_block("Liquid B:",frames[1])
        lblsB, ent_stepB = entry_block("step B:",frames[2])
        widgetsB = [lblB, ent_volB, lblsB, ent_stepB]
        
        lblcount, e_count = entry_block("iterations:",frames[3], spin=True, from_=1)
        place_entry_block(0.2, lblcount, e_count)
        btn1 = btn(frames[3], text="Start")
        btn1.configure(command=lambda: send_command())
        btn1.place(relx = 0.5, rely = 0.6, anchor='center') 

        checkbutton_var1 = tk.IntVar(value=1)
        checkbutton= tk.Checkbutton(frames[0], text="Reactant A", variable=checkbutton_var1, command=lambda: on_click(checkbutton_var1, widgetsA, 0.2))
        checkbutton.place(relx = 0.1, rely = 0.3, anchor='center') 
        checkbutton_var2 = tk.IntVar()
        checkbutton= tk.Checkbutton(frames[0], text="Reactant B", variable=checkbutton_var2, command=lambda: on_click(checkbutton_var2, widgetsB, 0.3))
        checkbutton.place(relx = 0.1, rely = 0.4, anchor='center') 

        def send_command():
            Ra_ml_init = ent_volA.get()
            Ra_step = ent_stepA.get()
            Rb_ml_init = ent_volB.get()
            Rb_step = ent_stepB.get()
            count = int(e_count.get())

            for i in range(count):
                if Ra_ml_init!="" and Ra_step!="":
                    Ra_ml = float(Ra_ml_init) + float(Ra_step)*i
                    P[0].pump(Ra_ml)
                if Rb_ml_init!="" and Rb_step!="":
                    Rb_ml = float(Rb_ml_init) + float(Rb_step)*i
                    P[1].pump(Rb_ml)

            return

class P_Hist(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)     

        title = ctk.CTkLabel(self, text = "History", font=LARGE_FONT)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center') 

        frame1 = Frame(self)
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')
        
        btn1 = btn(frame1, "Do NOT Click")
        btn1.configure(command=lambda: add_image("carap.png", frame1, relx=0.5, rely=0.5, size= (400,400)))
        btn1.place(relx = 0.5, rely = 0.5, anchor = 'center')

class OpenNewWindow(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.title("Here is the Title of the Window")
        self.geometry("500x200")
        self.resizable(0, 0)

        frame1 = Frame(main_frame, text="Results")
        frame1.pack(expand=True, fill="both")

        label1 = ctk.CTkLabel(frame1, font=("Verdana", 20), text="Plotting Page")
        label1.pack(side="top")

init = initialise()
init.mainloop()

def Event(MESSAGES):
    #MESSAGES can be a list or single element
    for MESSAGE in MESSAGES:
        match MESSAGE[5]:
            case "E":
                pass

            case "V":
                arduinos[0].busy()
                command = buffer.POP()
                com.DECODE_LINE(command, Comps)

            case "F":
                arduinos[0].free()
                    
            case _:
                pass
    return

def task():
    global device
    if len(arduinos):
        
        if (arduinos[0].get_state()==False) and (buffer.LENGTH()>0):
            buffer.OUT() 
            device,_ = buffer.READ()[0]
            arduinos[0].busy()
        
        if (device.inWaiting() > 0):
            Event(com.READ(device))
     
    gui.after(100, task)
    time.sleep(0.01)
#GUI
gui = Main()
gui.after(100,task)
gui.mainloop()