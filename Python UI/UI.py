import tkinter as tk
from tkinter import ttk
from PIL import Image
import customtkinter as ctk
import Serial_lib as com 
from Serial_lib import Pump, Valve, Shutter, Mixer, Extract, Vessel, Nano
import os, cv2, time, multiprocessing, random, datetime
from flask import Flask, render_template, Response, request
from chump import Application
import logging, csv
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

#pyinstaller --onedir -w --add-data "c:\users\idan\appdata\local\programs\python\python310\lib\site-packages\customtkinter;customtkinter\" UI.py
# UI styles 
font_XS = ("Consolas", 15, "normal")
font_S = ("Consolas", 18, "normal")
font_M = ("Consolas", 25, "normal")
font_L = ("Consolas", 30, "normal")
def set_mode(i: int):
    if i==0: ctk.set_appearance_mode("light")
    if i==1: ctk.set_appearance_mode("dark")
set_mode(1)
ctk.set_default_color_theme("dark-blue")

class ProgressBar():
    def __init__(self, master, buffer):
        self.Pbar = ctk.CTkProgressBar(master, width= 300, height=25, corner_radius=5)
        self.buffer = buffer
    
    def SET(self, n_tasks: int):
        self.Pbar.place(relx=0.5, rely=0.4, anchor='center')
        self.Pbar.set(0)
        self.n_tasks = n_tasks
    
    def refresh(self):
        ratio = (self.n_tasks-self.buffer.Left())/self.n_tasks
        self.Pbar.set(ratio)
        if ratio==1:
            self.Pbar.place_forget()
            ratio=0.0

class MyTabView(ctk.CTkTabview):
    def __init__(self, master, pages = ["Module", "Vessels", "Phone"], **kwargs):
        super().__init__(master, **kwargs)

        for page in pages:
            self.add(page)

class MyLabel(ctk.CTkLabel):
    def __init__(self, master, text="NA", font=font_S, **kwargs):
        super().__init__(master,text=text, font=font, **kwargs)
        
    def update(self, new_text: str, **kwargs):
        self.configure(text = new_text, **kwargs)

# UI functions
def update_label(label, new_text):
    label.configure(text = new_text)
    return label

def add_image(frame, file_name, relx, rely, size = (200,40), anchor='center'):
    photo = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images\\', file_name), "r"), size=size)
    label = ctk.CTkLabel(frame, image = photo, text="")
    label.image = photo
    label.place(relx = relx, rely = rely, anchor = anchor)

def btn(frame, text: str, command=None, width=50, height=20, font=font_XS):
    btn = ctk.CTkButton(frame, 
                        text=text,
                        font=font,
                        border_width=0,
                        border_color='black',
                        corner_radius=5, 
                        width=width, height=height, 
                        compound = 'left',
                        command = command)
    return btn

def btn_img(frame, text: str,  file_name: str, command=None, Xresize = 30, Yresize = 30):
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
                        command = command,
                        compound = 'left')
    btn.image = photo
    return btn

def entry_block(frame, text: str, spin=False, from_ = 0, to = 10, drop_list=None, wrap=True, **kwargs):
    """label followed by entry widget"""
    lbl = ctk.CTkLabel(frame, font=font_XS, text = text)
    if (spin):
        entry = ttk.Spinbox(frame, from_=from_, to=to, width=5, font= font_XS, wrap=wrap, **kwargs)
        entry.set(from_)
    elif (type(drop_list) == list):
        entry = ctk.CTkOptionMenu(frame,
                        values=drop_list,
                        width= 100)
    else:
        entry = ctk.CTkEntry(frame,
                            width=50,
                            height=25,
                            font=font_XS,
                            border_width=0,
                            corner_radius=2)

    return lbl, entry

def place_2(rely, lbl, entry, relx = 0.5):
    lbl.place(relx = relx-0.05, rely = rely, anchor = 'e')
    entry.place(relx = relx, rely = rely, anchor = 'w')
    return lbl, entry

def popup(text):
    popup = tk.Tk()
    popup.wm_title("Warning!")
    w = 250
    h = 100

    # get screen width and height
    ws = popup.winfo_screenwidth() 
    hs = popup.winfo_screenheight()

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    popup.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    label = ttk.Label(popup, text=text, font=font_M)
    label.pack(side="top", fill="x", padx= 10, pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack(pady=10)
    popup.mainloop()

def check_isnumber(value, type = 'float'):
    if value != '':
        if type == 'float':
            try:
                float(value)
                value = float(value)
                return value
            except ValueError:
                popup('Please, insert a number')
        if type == 'int':
            try:
                int(value)
                value = int(value)
                return value
            except ValueError:
                popup('Please, insert an integer')
    else:
        pass
    
#init comms
com.delete_file()
phone = com.notif()
buffer = com.Buffer()
Comps = com.Components()
def init_module(label=None):
    global arduinos, device
    try: com.CLOSE_SERIAL_PORT(arduinos)
    except: pass
    Ports = com.ID_PORTS_AVAILABLE()
    arduinos = [0]*6
    valves = [0]*5
    pumps = [0]*5
    shutter = 0
    mixer = 0
    extract = 0
    ves_in = [0]*3
    ves_out = [0]*6
    ves_main = Vessel(0, "ves_main")

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
            arduinos[0] = Nano(device, deviceID, Ports[i])
            arduinos[0].add_component("Input Module 1, pump 1")
            
            ves_in[0] = Vessel()
            pumps[0] = Pump(device, deviceID, 1, buffer)
            pumps[1] = Pump(device, deviceID, 2, buffer)
            shutter = Shutter(device, deviceID, 1, buffer)
            mixer = Mixer(device, deviceID, 1, buffer)
        if deviceID=="1002":
            arduinos[1] = Nano(device, deviceID, Ports[i])
            arduinos[1].add_component("Input Module 2, pump 2")
            ves_in[1] = Vessel()
            pumps[1] = Pump(device, deviceID, 2, buffer)
        if deviceID=="1003":
            arduinos[2] = Nano(device, deviceID, Ports[i])
            arduinos[2].add_component("Input Module 3, pump 3")
            ves_in[2] = Vessel()
            pumps[2] = Pump(device, deviceID, 3, buffer)
        if deviceID=="1004":
            arduinos[3] = Nano(device, deviceID, Ports[i])
            arduinos[3].add_component("Ouput Module, pump 4, V1-V5")
            for i in range(5):
                valves[i] = Valve(device, deviceID, i+1, buffer)
            for i in range(6):
                ves_out[i] = Vessel(0, 'Product '+str(i))
            
            pumps[3] = Pump(device, deviceID, 4, buffer)
        if deviceID=="1005":
            arduinos[4] = Nano(device, deviceID, Ports[i])
            arduinos[4].add_component("Shutter Module")
            shutter = Shutter(device, deviceID, 1, buffer)
            mixer = Mixer(device, deviceID, 1, buffer)
        if deviceID=="1006":
            arduinos[5] = Nano(device, deviceID, Ports[i])
            arduinos[5].add_component("Extraction Module")
            extract = Extract(device, deviceID, 1, buffer, n_slots = 5)
            pumps[4] = Pump(device, deviceID, 5, buffer)
    for i in range(len(arduinos)):
        try:arduinos.remove(0)
        except:pass
    
    buffer.phone = phone
    buffer.arduinos = arduinos
    Comps.buffer = buffer
    Comps.arduinos = arduinos  #array
    Comps.ves_in = ves_in     #array
    Comps.ves_out = ves_out   #array
    Comps.ves_main = ves_main
    Comps.valves = valves        #array
    Comps.pumps = pumps         #array
    Comps.mixer = mixer
    Comps.shutter = shutter
    Comps.extract = extract
    Comps.Temp = [-1]
    Comps.Bubble = [-1]*3
    Comps.LDS = [-1]*4

    if len(arduinos):
        Comps.modules=[]
        for arduino in arduinos:
            Comps.modules.append("{}: {}\n".format(arduino.get_id(), arduino.get_components()))
    else:
        Comps.modules=['no modules found']

    try:update_label(label, '\n'.join(Comps.modules)) 
    except:pass
    print("\n------------ End initialisation --------------\n\n")


# UI classes
class Frame(ctk.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, **kwargs)
        self.label = ctk.CTkLabel(self, text=text)
        self.label.grid(row=0, column=0, padx=20)

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.configure(background= 'blue', fg='red')

        self.add_command(label="Home", command=lambda: parent.show_frame(P_Home))

        self.add_command(label="Manual", command=lambda: parent.show_frame(P_Test))

        menu_auto = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Auto", menu=menu_auto)
        menu_auto.add_command(label="MVP",font=('Arial',11), command=lambda: parent.show_frame(P_Auto))
        menu_auto.add_separator()
        menu_auto.add_command(label="iterate",font=('Arial',11), command=lambda: parent.show_frame(P_Iter))

        menu_help = tk.Menu(self, tearoff=0)
        self.add_cascade(label="More", menu=menu_help)
        menu_help.add_command(label="Parameter",font=('Arial',11), command=lambda: parent.show_frame(P_Param))
        menu_help.add_command(label="Open New Window",font=('Arial',11), command=lambda: parent.OpenNewWindow())
        menu_help.add_command(label="Camera",font=('Arial',11), command=lambda: parent.show_frame(P_Cam))

class Main(ctk.CTk):
    def __init__(self, *args, **kwargs):
        ctk.CTk.__init__(self, *args, **kwargs)
        ctk.CTk.wm_title(self, "ARCaDIUS")
        self.geometry("1200x700") 
        self.minsize(700,400) 
        container = ctk.CTkFrame(self, height=700, width=1200)
        container.pack(side="top", fill = "both", expand = "true")
        container.grid_rowconfigure(0, weight= 1)
        container.grid_columnconfigure(0, weight= 1)

        self.frames = {}

        for F in (P_Init, P_Home, P_Test, P_Auto, P_Iter, P_Hist, P_Param, P_Cam):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(P_Init)

        menubar = MenuBar(self)
        ctk.CTk.config(self, menu=menubar)
        self.connect_cam()

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        self.visible_frame = cont

    def connect_cam(self):
        global cam
        vid = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        if not vid.isOpened():
            vid = cv2.VideoCapture(0)
        
        self.vid_frame_size = (int(vid.get(3)),int(vid.get(4)))
        self.vid = vid
        cam = vid
    
    def get_cam_frame(self, label, resize=1.0):
        try:
            #only update camera if frame is raised.
            _, frame = self.vid.read()
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            captured_image = Image.fromarray(opencv_image) #.transpose(Image.FLIP_LEFT_RIGHT)
            photo_image = ctk.CTkImage(captured_image, size=(int(self.vid_frame_size[0]*resize),int(self.vid_frame_size[1]*resize)))
            label.cv_image = frame
            label.photo_image = photo_image
            label.configure(image=photo_image)
        except:
            pass

    def update_buffer_list(self, textbox):
        prev_text = textbox.get("0.0", "end").strip()
        commands = buffer.READ()
        text = '\n'.join(commands).strip()
        if (prev_text!=text):
            textbox.configure(state= 'normal')
            textbox.delete("0.0", "end")
            textbox.insert("0.0", text)
            textbox.configure(state= 'disabled')
    
    def OpenNewWindow(self):
        OpenNewWindow()

    def Quit_application(self):
        self.destroy()

class P_Init(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        title = ctk.CTkLabel(self, text = "SETUP", font=font_L)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')
        
        frame1 = Frame(self, text = "Setup communcation")
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.9, relheight=0.8, anchor = 'center')

        details = ctk.CTkLabel(frame1, font=font_XS, text='\n'.join(Comps.modules),justify= 'left')
        details.place(relx = 0.5, rely = 0.5, anchor = 'center') 

        btn2 = btn(frame1, text="Continue", command=lambda: controller.show_frame(P_Home), width = 100, height=30, font = font_S)
        btn2.place(relx = 0.5, rely = 0.9, anchor = 'center') 

        init_module(details)

class P_Home(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        add_image(self, "arcadius.png", relx=0.5, rely=0.05, size=(200,40), anchor = 'n')

        frame1 = Frame(self, fg_color="transparent")
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')

        btn1=btn_img(frame1, "Manual", "manual.png", command=lambda: controller.show_frame(P_Test))
        btn1.place(relx = 0.45, rely = 0.2, anchor = 'e')
        
        btn2=btn_img(frame1, "Automate", "auto.png", command=lambda: controller.show_frame(P_Auto))
        btn2.place(relx = 0.55, rely = 0.2,  anchor = 'w')

        btn3=btn_img(frame1, "Task", "book.png", command=lambda: controller.show_frame(P_Hist))
        btn3.place(relx = 0.45, rely = 0.4, anchor = 'e')

        btn4=btn_img(frame1, "Iterate", "iter.png", command=lambda: controller.show_frame(P_Iter))
        btn4.place(relx = 0.55, rely = 0.4, anchor = 'w')

        btn5=btn_img(frame1, "Parameters", "param.png", command=lambda: controller.show_frame(P_Param))
        btn5.place(relx = 0.45, rely = 0.6, anchor = 'e')

        btn4=btn_img(frame1, "Camera", "cam.png", command=lambda: controller.show_frame(P_Cam))
        btn4.place(relx = 0.55, rely = 0.6, anchor = 'w')

        btn6 = btn(frame1, text="Exit", command=lambda: controller.Quit_application())
        btn6.place(relx = 0.5, rely = 0.9, anchor = 'center')

class P_Param(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)
        title = ctk.CTkLabel(self, text = "Parameters", font=font_L)
        title.place(relx = 0.5, rely = 0.05, anchor = 'center')

        tabs = MyTabView(self, pages = ["Module", "Interface"])
        tabs.place(relx = 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')

        frame_vessel = Frame(tabs.tab("Module"), text="Vessel levels")
        frame_vessel.place(relx= 0.7, rely = 0.5, relwidth=0.3, relheight=0.4, anchor = 'center')

        frame_nano = Frame(tabs.tab("Module"), text="Arduinos")
        frame_nano.place(relx= 0.3, rely = 0.5, relwidth=0.3, relheight=0.4, anchor = 'center')
        
        frame_push = Frame(tabs.tab("Interface"), text="Push notification")
        frame_push.place(relx= 0.5, rely = 0.5, relwidth=0.4, relheight=0.3, anchor = 'center')
        #arduino
        
        details = ctk.CTkLabel(frame_nano, font=font_XS, text='\n'.join(Comps.modules),justify= 'left')
        details.place(relx = 0.5, rely = 0.5, anchor = 'center') 
        btn_flush = btn(frame_nano, text = 'reset', command=lambda: init_module(details))
        btn_flush.place(relx=0.5, rely=0.1, anchor='center')

        # interface
        mode_switch = ctk.CTkSwitch(master=tabs.tab("Interface"), text="Dark Mode", command=lambda: set_mode(mode_switch.get()), onvalue=1, offvalue=0)
        mode_switch.select()
        mode_switch.place(relx=0.5, rely=0.1, anchor='center')

        global rem_control
        rem_control = ctk.CTkSwitch(master=tabs.tab("Interface"), text="Remote control", onvalue=1, offvalue=0)
        rem_control.select()
        rem_control.place(relx=0.5, rely=0.3, anchor='center')

        _, ent_app = place_2(0.3, *entry_block(frame_push, text='app token'), relx=0.27)
        _, ent_user = place_2(0.6, *entry_block(frame_push, text='user key'), relx=0.27)
        btn_save = btn(frame_push, 'save', command=lambda: phone.set_token(ent_app.get(), ent_user.get()))
        btn_save.place(relx=0.5, rely= 0.9, anchor='center')
        ent_app.configure(width=200)
        ent_user.configure(width=200)
        ent_app.insert(0, phone.app_token)
        ent_user.insert(0, phone.user_key)

        # vessels
        n = 3
        ent_Rname = [0]*n
        ent_Rvol = [0]*n
        names, volumes =  com.read_detail('details.csv')
        for i in range(n):
            if i==0: text = 'A'
            elif i==1: text = 'B'
            elif i==2: text = 'C'
            _, ent_Rname[i] = place_2(0.2 + 0.2*i, *entry_block(frame_vessel, text=text), relx = 0.25)
            _, ent_Rvol[i]  = place_2(0.2 + 0.2*i, *entry_block(frame_vessel, text=(' Vol: ')), relx = 0.75)
           
            ent_Rname[i].insert(0,names[i])
            ent_Rvol[i].insert(0,volumes[i])

        btn1 = btn(frame_vessel, text ='save', command=lambda: com.vessel_detail(ent_Rname, ent_Rvol))
        btn1.place(relx = 0.5, rely = 0.8, anchor = 'center')

class P_Test(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)
        title = ctk.CTkLabel(self, text = "Manual Control", font=font_L)
        title.place(relx = 0.5, rely = 0.05, anchor = 'center')
        
        frame1 = Frame(self, text = "Valve")
        frame1.place(relx=0.175, rely=0.15, relwidth=0.3, relheight=0.8, anchor = 'n')
        frame12 = Frame(frame1, text = "shutter", fg_color = 'transparent')
        frame12.place(relx=0, rely=1, relwidth=1, relheight=0.5, anchor = 'sw')

        frame2 = Frame(self, text = "Pump")
        frame2.place(relx=0.5, rely=0.15, relwidth=0.3, relheight=0.8, anchor = 'n')

        frame3 = Frame(self, text = "Mixer")
        frame3.place(relx=0.825, rely=0.15, relwidth=0.3, relheight=0.38, anchor = 'n')

        frame4= Frame(self, text = "Extract")
        frame4.place(relx=0.825, rely=0.55, relwidth=0.3, relheight=0.4, anchor = 'n')

        #box 1 Valve
        _, ent_valve = place_2(0.2, *entry_block(frame1, "select valve: ", spin=True, from_=1, to=len(Comps.valves)))

        btn1 = btn(frame1, text="close", command=lambda: Comps.valves[int(ent_valve.get())-1].close())
        btn1.place(relx = 0.48, rely = 0.3, anchor = 'e')
        btn2 = btn(frame1, text="open", command=lambda: Comps.valves[int(ent_valve.get())-1].open())
        btn2.place(relx = 0.52, rely = 0.3, anchor = 'w')
        btn3 = btn(frame1, text="mid", command=lambda: Comps.valves[int(ent_valve.get())-1].mid())
        btn3.place(relx = 0.5, rely = 0.4, anchor = 'center')

        #box 1.2 Shutter
        
        btn1 = btn(frame12, text="close", command=lambda: Comps.shutter.close())
        btn1.place(relx = 0.48, rely = 0.3, anchor = 'e')
        btn2 = btn(frame12, text="open", command=lambda: Comps.shutter.open())
        btn2.place(relx = 0.52, rely = 0.3, anchor = 'w')
        btn3 = btn(frame12, text="mid", command=lambda: Comps.shutter.mid())
        btn3.place(relx = 0.5, rely = 0.5, anchor = 'center')


        #box 2 pump
        _, ent_pump = place_2(0.2,*entry_block(frame2, "select pump: ", spin=True, from_=1, to=len(Comps.pumps)))
        _, ent_vol = place_2(0.3, *entry_block(frame2, "Volume (ml)"))

        btn1 = btn(frame2, text="send", command=lambda: Comps.pumps[int(ent_pump.get())-1].pump(float(ent_vol.get())))
        btn1.place(relx = 0.5, rely = 0.4, anchor = 'center')

        #box 3 mixer
        _, ent_mix = place_2(0.2, *entry_block(frame3, "speed : "))
        btn1 = btn(frame3, text="send", command=lambda: Comps.mixer.mix(int(ent_mix.get())))
        btn1.place(relx = 0.5, rely = 0.35, anchor = 'center')

        #box 4 extract
        _, ent_ext = place_2(0.2,*entry_block(frame4, "select slot: ", spin=True, from_=1, to=5))
        ent_ext.config(command=lambda: Comps.extract.set_slot(int(ent_ext.get())))
        


class P_Auto(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)
        title = ctk.CTkLabel(self, text = "Automated MVP", font=font_L)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')

        frame1 = Frame(self)
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.45, relheight=0.8, anchor = 'e')
        frame2 = Frame(self, fg_color = 'transparent')
        frame2.place(relx= 0.5, rely = 0.55, relwidth=0.45, relheight=0.8, anchor = 'w')

        ent_P = [0]*3
        _, ent_P[0] = place_2(0.2, *entry_block(frame1, text="Input A (ml)"))
        _, ent_P[1] = place_2(0.3, *entry_block(frame1, text="Input B (ml)"))
        _, ent_P[2] = place_2(0.4, *entry_block(frame1, text="Input C (ml)"))
        _, ent_I = place_2(0.5, *entry_block(frame1, text="shutter time (s)"))
        
        out_list = ["Input A", "Input B", "Product", "Waste", "Recycle", "Recycle 2"]
        _, sel_output = place_2(0.6, *entry_block(frame1, text="Select Output", drop_list=out_list))

        btn1 = btn(frame1, text="Start", width = 100, height=35, command=lambda: experiment(), font=font_S)
        btn1.place(relx = 0.5, rely = 0.8, anchor = 'center')
        btn2 = btn(frame1, text="Wash", command=lambda: com.WASH(Comps)) 
        btn2.place(relx = 0.8, rely = 0.8, anchor = 'center')
        #progress bar
        Pbar = ProgressBar(frame2, buffer)
        def experiment():
            tot_vol=0.0
            for i in range(len(ent_P)):
                try:
                    vol=float(ent_P[i].get())
                    tot_vol+=vol
                    Comps.pumps[i].pump(vol)
                except:pass
            try:
                Comps.shutter.open()
                Comps.buffer.BLOCK(float(ent_I.get()))
                Comps.shutter.close()
            except:pass

            try:
                com.valve_states(Comps.valves, out_list.index(sel_output.get()))
                Comps.pumps[3].pump(tot_vol+10)
            except:pass
            buffer.NOTIFY('Experiment Over')
            Pbar.SET(buffer.Left())
       
        # buffer list
        textbox = ctk.CTkTextbox(frame2,width=300, height=200, state= 'normal')
        textbox.place(relx=0.5, rely=0, anchor="n")
        def update_buffer():
            try:
                if (controller.visible_frame==P_Auto):
                    controller.update_buffer_list(textbox)
                    Pbar.refresh()
            except:
                pass
            textbox.after(500, update_buffer)
        update_buffer()

        #camera
        label = ctk.CTkLabel(frame2, text="")
        label.place(relx = 0.5, rely = 1, anchor = 's')
        def update_cam():
            try:
                if (controller.visible_frame==P_Auto):
                    controller.get_cam_frame(label, resize = 0.6)
            except:
                pass
            label.after(50, update_cam)
        update_cam()

class P_Iter(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)

        title = ctk.CTkLabel(self, text = "Iterative experiment", font=font_L)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')

        frame1 = Frame(self, text= "setup experiment")
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.45, relheight=0.8, anchor = 'e')
        frame2 = Frame(self, fg_color = 'transparent')
        frame2.place(relx= 0.5, rely = 0.55, relwidth=0.45, relheight=0.8, anchor = 'w')    

        _, ent_volA = place_2(0.2, *entry_block(frame1, "A (ml):"), 0.4)
        _, ent_stepA = place_2(0.2, *entry_block(frame1, " + it x", spin=True, from_=-20, wrap=False, increment = 0.1), 0.7)
        ent_stepA.set(0)
        _, ent_volB = place_2(0.3, *entry_block(frame1, "B (ml):"), 0.4)
        _, ent_stepB = place_2(0.3, *entry_block(frame1, " + it x", spin=True, from_=-20, wrap=False, increment = 0.1), 0.7)
        ent_stepB.set(0)
        _, ent_volC = place_2(0.4, *entry_block(frame1, "C (ml):"), 0.4)
        _, ent_stepC = place_2(0.4, *entry_block(frame1, " + it x", spin=True, from_=-20, wrap=False, increment = 0.1), 0.7)
        ent_stepC.set(0)
        _, ent_Shut= place_2(0.5, *entry_block(frame1, "shutter time:"), 0.4)
        _, ent_step_Shut = place_2(0.5, *entry_block(frame1, " + it x", spin=True, wrap=False, from_=0), 0.7)

        _, ent_count = place_2(0.6, *entry_block(frame1, "number of iterations:", spin=True, from_=1, to=10))
        
        btn1 = btn(frame1, text="Start", width = 100, height=35, command=lambda: iterate(), font=font_S)
        btn1.place(relx = 0.5, rely = 0.8, anchor = 'center')

        #progress bar
        Pbar = ProgressBar(frame2, buffer)
       
        # buffer list
        textbox = ctk.CTkTextbox(frame2,width=300, height=200, state= 'normal')
        textbox.place(relx=0.5, rely=0, anchor="n")
        def update_buffer():
            try:
                if (controller.visible_frame==P_Iter):
                    controller.update_buffer_list(textbox)
                    Pbar.refresh()
            except:
                pass
            textbox.after(500, update_buffer)
        update_buffer()

        #camera
        label = ctk.CTkLabel(frame2, text="")
        label.place(relx = 0.5, rely = 1, anchor = 's')
        def update_cam():
            try:
                if (controller.visible_frame==P_Iter):
                    controller.get_cam_frame(label, resize = 0.6)
            except:
                pass
            label.after(50, update_cam)
        update_cam()

        def iterate():
            Ra = ent_volA.get()
            Ra_step = ent_stepA.get()
            Rb = ent_volB.get()
            Rb_step = ent_stepB.get()
            Rc = ent_volC.get()
            Rc_step = ent_stepC.get()
            time = ent_Shut.get()
            time_step = ent_step_Shut.get()
            count = int(ent_count.get())

            for i in range(count):
                if Ra!="" and Ra_step!="":
                    Comps.pumps[0].pump(float(Ra) + float(Ra_step)*i)
                if Rb!="" and Rb_step!="":
                    Comps.pumps[1].pump(float(Rb) + float(Rb_step)*i)
                if Rc!="" and Rc_step!="":
                    Comps.pumps[2].pump(float(Rc) + float(Rc_step)*i)
                if time!="" and time_step!="":
                    try:
                        Comps.shutter.open()
                        Comps.buffer.BLOCK(float(time)+float(time_step)*i)
                        Comps.shutter.close()
                    except:pass
                try:
                    com.valve_states(Comps.valves, 3)
                    Comps.pumps[3].pump(10)
                except:pass

            Pbar.SET(buffer.Left())
            buffer.NOTIFY('Iterations Over')
      
class P_Hist(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)     

        title = ctk.CTkLabel(self, text = "Task", font=font_L)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center') 

        sub = ctk.CTkLabel(self, text = "Queue", font=font_M)
        sub.place(relx = 0.2, rely = 0.1, anchor = 'center')

        sub1 = ctk.CTkLabel(self, text = "History", font=font_M)
        sub1.place(relx = 0.7, rely = 0.1, anchor = 'center')

        frame1 = Frame(self)
        frame1.place(relx= 0.95, rely = 0.55, relwidth=0.4, relheight=0.8, anchor = 'e')

        frame2 = Frame(self)
        frame2.place(relx= 0.05, rely = 0.55, relwidth=0.4, relheight=0.8, anchor = 'w')
        frame2.grid_rowconfigure(0, weight=1)  # configure grid system
        frame2.grid_columnconfigure(0, weight=1)

        scroll = ttk.Scrollbar(frame1, orient = "vertical")
        scroll.place(relx= 1, rely = 0.5, relwidth=0.03, relheight=1, anchor = 'e')

        list = tk.Listbox(frame1, bd= 3, relief = "groove", selectmode= "SINGLE", yscrollcommand = scroll.set )
        
        list.place(relx= 0, rely = 0.5, relwidth=0.97, relheight=1, anchor = 'w')
        scroll.config(command = list.yview )

        btn1 = btn(self, text="skip next", command=lambda: buffer.POP())
        btn1.place(relx = 0.5, rely = 0.4, anchor = 'center')
        btn2 = btn(self, text="skip last", command=lambda: buffer.POP_LAST())
        btn2.place(relx = 0.5, rely = 0.5, anchor = 'center')
        btn3 = btn(self, text="Clear Queue", command=lambda: buffer.RESET())
        btn3.place(relx = 0.5, rely = 0.6, anchor = 'center')

        textbox = ctk.CTkTextbox(frame2, state= 'normal')
        textbox.grid(row=0, column=0, sticky="nsew")
        def update_page():
            try:
                if (controller.visible_frame==P_Hist):
                    controller.update_buffer_list(textbox)                   
            except:
                pass
            # update history
            list.delete(0, 'end') #clear the list before updating
            time, command = com.read_detail("commands.csv")
            for x in range(len(time)):
                list.insert(0, time[x] + "   " + command[x])
            textbox.after(500, update_page)
        update_page()

class P_Cam(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)
        
        label = ctk.CTkLabel(self, text="")
        label.place(relx = 0.5, rely = 0.5, anchor = 'center')
    

        def update_cam():
            try: 
                if (controller.visible_frame==P_Cam):
                    controller.get_cam_frame(label)
            except:
                pass
            label.after(50, update_cam)
        update_cam()
 
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

def Event(MESSAGES):
    for MESSAGE in MESSAGES:
        match MESSAGE[5]:
            case "E":
                com.Log("ERROR: wrong command sent")

            case "V":
                # Command is Valid
                command = buffer.POP()
                com.Log(com.DECODE_LINE(command, Comps))

            case "F":
                arduinos[0].free()
                    
            case _:
                pass
    return

def task():
    global device
    # Handle multi-arduino two-way communication
    if len(arduinos):
        # Check if arduinos are not busy and the buffer is not empty
        if (arduinos[0].state==False) and (buffer.Left()>0):
            # Handle next command in buffer 
            # command is not removed from buffer yet except for notifications (immidiatly popped)
            buffer.OUT()
            # if buffer was not blocked and buffer is not empty => arduino command sent to serial 
            if not buffer.blocked and (buffer.Left()>0):
                # keep track of current device busy
                device = buffer.READ_DEVICE()
                # Set all arduinos to busy
                arduinos[0].busy()

        # wait for response from current device busy
        try:
            if (device.inWaiting() > 0):
                # handle response from device
                Event(com.READ(device))
        except:
            pass

    #To simulate getting commands this will be replaced with actual ones
    #------- start ----------#
    temp_list = buffer.READ()
    #for i in range(0,10):
    #    temp_list.append(random.randint(0,10))
    try:
        Current_cmd.put(temp_list[0], block=False)
    except:
        pass
    for i in range(1,5):
        try:
            Next_cmd.put(temp_list[i], block=False)
        except:
            pass
    #-------- end ----------#
    gui.after(200, task)
    time.sleep(0.01)

#---------- Webpage Commands ---------------#

#Global 
# Queues and pipes to share and communicate between threads
global web_frame, C_CMD, N_CMD, Kill_Conn, CMD_Conn

# Grabs the latest frame and puts it onto a Queue for the webpage to read and display
def GUI_Server_Comms():
    global cam
    _, frame = cam.read() # reusing GUI cam instance
    try:
        Frames.put(frame, block=False)# puts frame on queue, only stores the last 5 frames
    except:
        pass
    if Kill_rev.poll(timeout=0.1): # polls the kill pipeline for new commands
        if Kill_rev.recv() == "kill": # if the command is kill
            print("The system has been KILLED")
            gui.Quit_application() # Quits all applications
    if rem_control.get() and CMD_rev.poll(timeout=0.1): # polls the kill pipeline for new commands
        command = CMD_rev.recv()
        if command == "PUMP": # if the command is kill
            print("this is a Pump command")
            try:
                Comps.pumps[0].pump(5)
            except:
                pass
        if command == "Shutter":
            print("This is a shutter command")
            try:
                Comps.shutter.open()
            except:
                pass
    elif CMD_rev.poll(timeout=0.1):
        CMD_rev.recv()
    gui.after(200,GUI_Server_Comms) # executes it every 200ms 

app = Flask(__name__) #main web application

logged_in = list()
logged_in.append(['N/A','N/A'])

#main page of the website
@app.route("/", methods=['GET', 'POST']) # methods of interating and route address
def Main_page():
    global logged_in
    if any(request.remote_addr not in User for User in logged_in):
        if request.form.get('Login') == 'Login':
            Username = request.form.get('User')
            Password = request.form.get('Pass')
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static\\', 'credentials.csv'), newline='') as login:
                creds = list(csv.reader(login))
            for creds in creds:
                if creds[0] == Username:
                    if creds[1] == Password:
                        logged_in.append([request.remote_addr,creds[2]])
                                           
    if any(request.remote_addr in User for User in logged_in):    
        # Reads all the current commands in the buffer and addes N/A if blank
        Next =[] # list of next 4 commands
        for i in range(0, 4):
            try: 
                Next.append(N_CMD.get(block = False)) # reads queue and adds commands to the list.
            except: 
                Next.append("N/A") # N/A if it is not available
        try: 
            Current = C_CMD.get(block = False) #Reads current command 
        except: 
            Current = "N/A"

        #To edit the webpage HTML file with the python data
        template = {
            'title': 'Arcadius Monitoring Page',
            'Current' : Current,
            'N1' : Next[0], #the next 4 commands
            'N2' : Next[1],
            'N3' : Next[2],
            'N4' : Next[3]
        }
        
        # Gets the request form the webpage about button presses
        if request.method == 'POST':
                if request.form.get('Kill') == 'Kill': # if the form item called Kill is clicked it reads the value
                    Kill_Conn.send("kill") # Sends kill command on kill pipe
                elif request.form.get('Screenshot') == 'Screenshot':
                    frame = web_frame.get()
                    file_name = str(datetime.datetime.now()).replace('.','_').replace('-','_').replace(':','_') + ".jpg"
                    cv2.imwrite(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screenshots\\', file_name), frame)
                else:
                    pass
        elif request.method == 'GET':
            pass
        return render_template('Main.html', **template) #Renders webpage
                            
    else:
        template = {
            'address': '/',
        }
        return render_template('login.html', **template) #Renders webpage
        
# generates videofeed from frame queue
def gen_frames(): 
    while True:
        try:
            frame = web_frame.get(block=False) # gets the most recent frames
            try:   
                ret, buffer = cv2.imencode('.jpg', frame) # encodes the frame and stores it in a buffer
                frame = buffer.tobytes() # converts to bytes
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  #Concat frame one by one and show result
            except:
                pass
        except:
            pass
           
#Renders a webpage fro pure video streaming which is linked to on main page
@app.route('/video_feed')
def video_feed():
    global logged_in
    if any(request.remote_addr not in User for User in logged_in):
        if request.form.get('Login') == 'Login':
            Username = request.form.get('User')
            Password = request.form.get('Pass')
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static\\', 'login.csv'), newline='') as login:
                creds = list(csv.reader(login))
            for creds in creds:
                if creds[0] == Username:
                    if creds[1] == Password:
                        logged_in.append([request.remote_addr,creds[2]])
    if any(request.remote_addr in User for User in logged_in):
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')            
    else:
        print(0)
        template = {
            'address': '/',
        }
        return render_template('login.html', **template) #Renders webpage
        

#New control page
@app.route('/control', methods=['GET', 'POST'])
def control_page():
    global logged_in
    if any(request.remote_addr not in User for User in logged_in):
        if request.form.get('Login') == 'Login':
            Username = request.form.get('User')
            Password = request.form.get('Pass')
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static\\', 'credentials.csv'), newline='') as login:
                creds = list(csv.reader(login))
            for creds in creds:
                if creds[0] == Username:
                    if creds[1] == Password:
                        logged_in.append([request.remote_addr,creds[2]])

    if any(request.remote_addr in User for User in logged_in):
        if request.method == 'POST':
                if request.form.get('Kill') == 'Kill': # if the form item called Kill is clicked it reads the value
                    Kill_Conn.send("kill") # Sends kill command on kill pipe
                    return render_template('control.html')
                elif request.form.get('Screenshot') == 'Screenshot':
                    frame = web_frame.get() 
                    file_name = str(datetime.datetime.now()).replace('.','_').replace('-','_').replace(':','_')  + ".jpg"
                    cv2.imwrite(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screenshots\\', file_name), frame)
                elif  request.form.get('Pump') == 'Pump':
                    print("Pump")
                    CMD_Conn.send("PUMP")
                    return render_template('control.html')
                elif  request.form.get('Shutter') == 'Shutter':
                    print("Shutter")
                    CMD_Conn.send("Shutter")
                    return render_template('control.html')
                else:
                    pass
        elif request.method == 'GET':
            pass
        return render_template('control.html')          
    else:
        template = {
            'address': '/',
        }
        return render_template('login.html', **template) #Renders webpage

#---------- GUI Thread -------------#
def GUI():
    global gui
    gui = Main()
    gui.after(100,task)
    gui.after(200,GUI_Server_Comms)
    gui.mainloop()

#------- Webserver Thread ----------#
def Server(Q, L, N, K, P):
    global app, web_frame, C_CMD, N_CMD, Kill_Conn, CMD_Conn
    web_frame = Q
    C_CMD = L
    N_CMD = N
    Kill_Conn = K
    CMD_Conn = P
    if __name__ == '__mp_main__':
        app.run(host='0.0.0.0', port = 80)

#Starts all the threads and pages.
if __name__ == "__main__":
    Frames = multiprocessing.Queue(5)
    Current_cmd = multiprocessing.Queue(1)
    Next_cmd = multiprocessing.Queue(4)
    Kill_rev, Kill_send = multiprocessing.Pipe(duplex = False)
    CMD_rev, CMD_send = multiprocessing.Pipe(duplex = False)
    server = multiprocessing.Process(target = Server, args=(Frames, Current_cmd, Next_cmd, Kill_send, CMD_send))
    server.start()
    GUI()
    server.terminate()
    server.join()
    