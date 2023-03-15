import tkinter as tk
from tkinter import ttk
from PIL import Image
import customtkinter as ctk
import Serial_lib as com 
from Serial_lib import Pump, Valve, Shutter, Mixer, Vessel, Nano 
import os, cv2, time

# UI styles 
Title_font= ("Consolas", 30)
label_font = ("Consolas", 15, "normal")
btn_font = ("Arial", 13, "normal")
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")


# UI functions
def update_label(label, new_text):
    label.configure(text = new_text)
    return label

def add_image(frame, file_name, relx, rely, size = (200,40), anchor='center'):
    photo = ctk.CTkImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images\\', file_name), "r"), size=size)
    label = ctk.CTkLabel(frame, image = photo, text="")
    label.image = photo
    label.place(relx = relx, rely = rely, anchor = anchor)

def btn(frame, text: str, command=None, width=50, height=20, font=btn_font):
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

def entry_block(frame, text: str, spin=False, from_ = 0, to = 10, drop_list=None):
    """label followed by entry widget"""
    lbl = ctk.CTkLabel(frame, text = text)
    if (spin):
        entry = ttk.Spinbox(frame, from_=from_, to=to, width=2, wrap=True)
        entry.set(from_)
    elif (type(drop_list) == list):
        entry = ctk.CTkOptionMenu(frame,
                        values=drop_list,
                        width= 100)
    else:
        entry = ctk.CTkEntry(frame,
                            width=50,
                            height=25,
                            border_width=0,
                            corner_radius=2)

    return lbl, entry

def place_2(rely, lbl, entry, relx = 0.5):
    lbl.place(relx = relx-0.05, rely = rely, anchor = 'e')
    entry.place(relx = relx, rely = rely, anchor = 'w')
    return lbl, entry


#init comms
com.delete_file()
buffer = com.Buffer()
def init_module():
    global arduinos, device, Comps
    Ports = com.ID_PORTS_AVAILABLE()
    
    arduinos = [0]*5
    valves = [0]*5
    pumps = [0]*4
    shutter = 0
    mixer = 0
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
        if deviceID =='- st':
            deviceID=message[1][0:4]
        print("\narduino: ", deviceID)
        
        if deviceID=="1001":
            arduinos[0] = Nano(device, deviceID)
            arduinos[0].add_component("Pump 1")
            
            ves_in[0] = Vessel()
            pumps[0] = Pump(device, deviceID, 1, buffer)
        if deviceID=="1002":
            arduinos[1] = Nano(device, deviceID)
            arduinos[1].add_component("Pump 2")
            ves_in[1] = Vessel()
            pumps[1] = Pump(device, deviceID, 2, buffer)
        if deviceID=="1003":
            arduinos[2] = Nano(device, deviceID)
            arduinos[2].add_component("Pump 3")
            ves_in[2] = Vessel()
            pumps[2] = Pump(device, deviceID, 3, buffer)
        if deviceID=="1004":
            arduinos[3] = Nano(device, deviceID)
            arduinos[3].add_component("Pump 4, V1-V5")
            for i in range(5):
                valves[i] = Valve(device, deviceID, i+1, buffer)
            for i in range(6):
                ves_out[i] = Vessel(0, 'Product '+str(i))
            
            pumps[3] = Pump(device, deviceID, 4, buffer)
        if deviceID=="1005":
            arduinos[4] = Nano(device, deviceID)
            arduinos[4].add_component("shutter")
            shutter = Shutter(device, deviceID, 1, buffer)
            mixer = Mixer(device, deviceID, 1, buffer)
    
    for i in range(len(arduinos)):
        try:arduinos.remove(0)
        except:pass
    
    Comps = com.Components()
    Comps.buffer = buffer
    Comps.arduinos = arduinos  #array
    Comps.ves_in = ves_in     #array
    Comps.ves_out = ves_out   #array
    Comps.ves_main = ves_main
    Comps.valves = valves        #array
    Comps.pumps = pumps         #array
    Comps.mixer = mixer
    Comps.shutter = shutter
    Comps.Temp = [-1]
    Comps.Bubble = [-1]*3
    Comps.LDS = [-1]*4
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
        self.geometry("900x500") 
        self.minsize(700,400) 
        container = ctk.CTkFrame(self, height=600, width=1024)
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
        vid = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        if not vid.isOpened():
            vid = cv2.VideoCapture(0)
        self.vid_frame_size = (int(vid.get(3)),int(vid.get(4)))
        self.vid = vid

    def OpenNewWindow(self):
        OpenNewWindow()

    def Quit_application(self):
        self.destroy()

class P_Init(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)

        title = ctk.CTkLabel(self, text = "SETUP", font=Title_font)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')
        
        def update_devices():
            init_module()
            #refer to actual object returned if none= do not update label
            if len(arduinos):
                text = ""
                for arduino in arduinos:
                    text  += "arduino: '{}' : {}\n".format(arduino.get_id(), arduino.get_components())

                update_label(details, text)
        
        frame1 = Frame(self, text = "Setup communcation")
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.9, relheight=0.8, anchor = 'center')

        btn1 = btn(frame1, text="Initialise", command=lambda: update_devices(), width = 200, height=30, font = label_font)
        btn1.place(relx = 0.5, rely = 0.2, anchor = 'center') 

        ard_detail = "no arduino"
        details = ctk.CTkLabel(frame1, font=label_font, text=ard_detail,justify= 'left')
        details.place(relx = 0.5, rely = 0.5, anchor = 'center') 

        btn2 = btn(frame1, text="FINISH", command=lambda: controller.show_frame(P_Home), width = 100, height=30, font = label_font)
        btn2.place(relx = 0.5, rely = 0.9, anchor = 'center') 

        update_devices()

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

        btn3=btn_img(frame1, "History", "book.png", command=lambda: controller.show_frame(P_Hist))
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
        title = ctk.CTkLabel(self, text = "Parameters", font=Title_font)
        title.place(relx = 0.5, rely = 0.05, anchor = 'center')
        frame1 = Frame(self, fg_color="transparent")
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')
        
        frame2 = Frame(frame1, text = 'Vessels')
        frame2.place(relx= 0, rely = 0.5, relwidth=0.5, relheight=0.8, anchor = 'w')


        n = 3
        ent_Rname = [0]*n
        ent_Rvol = [0]*n
        names, volumes =  com.read_detail('details.csv')
        for i in range(n):
            _, ent_Rname[i] = place_2(0.2 + 0.2*i, *entry_block(frame2, text=(str(i+1) + ': Name ')), relx = 0.25)
            _, ent_Rvol[i]  = place_2(0.2 + 0.2*i, *entry_block(frame2, text=(' Vol: ')), relx = 0.75)
           
            ent_Rname[i].insert(0,names[i])
            ent_Rvol[i].insert(0,volumes[i])

        btn1 = btn(frame2, text ='save', command=lambda: com.vessel_detail(ent_Rname, ent_Rvol))
        btn1.place(relx = 0.5, rely = 0.8, anchor = 'center')

class P_Test(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)
        title = ctk.CTkLabel(self, text = "Manual Control", font=Title_font)
        title.place(relx = 0.5, rely = 0.05, anchor = 'center')
        
        frame1 = Frame(self, text = "Valve")
        frame1.place(relx=0.175, rely=0.15, relwidth=0.3, relheight=0.8, anchor = 'n')
        frame12 = Frame(frame1, text = "shutter", fg_color = 'transparent')
        frame12.place(relx=0, rely=1, relwidth=1, relheight=0.5, anchor = 'sw')

        frame2 = Frame(self, text = "Pump")
        frame2.place(relx=0.5, rely=0.15, relwidth=0.3, relheight=0.8, anchor = 'n')

        frame3 = Frame(self, text = "Mixer")
        frame3.place(relx=0.825, rely=0.15, relwidth=0.3, relheight=0.38, anchor = 'n')

        frame4= Frame(self, text = "Sensors")
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

class P_Auto(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)
        title = ctk.CTkLabel(self, text = "Automated MVP", font=Title_font)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')

        frame1 = Frame(self)
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')
        frame2 = Frame(frame1, text='inputs')
        frame2.place(relx= 0.25, rely = 0.55, relwidth=0.45, relheight=0.8, anchor = 'center')
        frame3 = Frame(frame1, text='output')
        frame3.place(relx= 0.75, rely = 0.55, relwidth=0.45, relheight=0.8, anchor = 'center')

        ent_P = [0]*3
        _, ent_P[0] = place_2(0.2, *entry_block(frame2, text="Reactant A"))
        _, ent_P[1] = place_2(0.3, *entry_block(frame2, text="Reactant B"))
        _, ent_P[2] = place_2(0.4, *entry_block(frame2, text="Reactant C"))

        _, ent_I = place_2(0.5, *entry_block(frame2, text="Shutter time"))
        
        out_list = ["Product","Product 2", "Waste", "2 A", "2 B", "2 C"]
        _, sel_output = place_2(0.2, *entry_block(frame3, text="Select", drop_list=out_list))

        btn1 = btn(frame3, text="Start", command=lambda: experiment())
        btn1.place(relx = 0.5, rely = 0.8, anchor = 'center')
        btn2 = btn(frame3, text="Wash", command=lambda: com.WASH(Comps)) 
        btn2.place(relx = 0.5, rely = 0.9, anchor = 'center')

        def experiment():
            tot_vol=0.0
            for i in range(len(ent_P)):
                try:
                    vol=float(ent_P[i].get())
                    tot_vol+=vol
                    Comps.pumps[i].pump(vol)
                except:pass
            try:
                Comps.mixer.mix(5)
                Comps.shutter.open()
                try:Comps.buffer.BLOCK(float(ent_I.get()))
                except: pass
                Comps.shutter.close()
                Comps.mixer.mix(0)
            except:pass

            try:
                com.valve_states(Comps.valves, out_list.index(sel_output.get()))
                Comps.pumps[3].pump(tot_vol)
            except:pass

class P_Iter(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)

        title = ctk.CTkLabel(self, text = "Iterative experiment", font=Title_font)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')

        frames = [0]*5
        frames[0] = Frame(self, text = "Settings of experiments")
        frames[0].place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')
        frames[1] = Frame(frames[0], text = "volume", fg_color= "transparent")
        frames[1].place(relx= 0.75, rely = 0.05, relwidth=0.25, relheight=0.6, anchor = 'ne')
        frames[2] = Frame(frames[0], text = "steps", fg_color= "transparent")
        frames[2].place(relx= 0.75, rely = 0.05, relwidth=0.25, relheight=0.6, anchor = 'nw')
        frames[3] = Frame(frames[0], text = "Send")
        frames[3].place(relx= 0.75, rely = 0.65, relwidth=0.4, relheight=0.3, anchor = 'n')

        def on_click(checkbutton_var, widgets, pos: int):
            [lbl, ent_vol, lbls, ent_step] = widgets
            if checkbutton_var.get() == 1:
                place_2(pos, lbl, ent_vol)
                place_2(pos, lbls, ent_step)
            else:
                for widget in widgets:
                    widget.place_forget()

            
        lblA, ent_volA = entry_block(frames[1], "Liquid A:")
        lblsA, ent_stepA = entry_block(frames[2], "step A:")
        place_2(0.2, lblA, ent_volA)
        place_2(0.2, lblsA, ent_stepA)
        widgetsA = [lblA, ent_volA, lblsA, ent_stepA]

        lblB, ent_volB = entry_block(frames[1],"Liquid B:")
        lblsB, ent_stepB = entry_block(frames[2],"step B:")
        widgetsB = [lblB, ent_volB, lblsB, ent_stepB]
        
        lblcount, e_count = entry_block(frames[3], "iterations:",spin=True, from_=1)
        place_2(0.2, lblcount, e_count)
        btn1 = btn(frames[3], text="Start", command=lambda: send_command())
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
                    Comps.pumps[0].pump(Ra_ml)
                if Rb_ml_init!="" and Rb_step!="":
                    Rb_ml = float(Rb_ml_init) + float(Rb_step)*i
                    Comps.pumps[1].pump(Rb_ml)

            return

class P_Hist(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)     

        title = ctk.CTkLabel(self, text = "History", font=Title_font)
        title.place(relx = 0.5, rely = 0.1, anchor = 'center') 

        frame1 = Frame(self)
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')

        scroll = ttk.Scrollbar(frame1, orient = "vertical")
        scroll.place(relx= 1, rely = 0.5, relwidth=0.03, relheight=1, anchor = 'e')

        list = tk.Listbox(frame1, bd= 3, relief = "groove", selectmode= "SINGLE", yscrollcommand = scroll.set )
        time, command = com.read_detail("commands.csv")
        for x in range(len(time)):
            list.insert(0, time[x] + " --- " + command[x])  # 0 for printing from last to first and 'end' for printing 1st to last

        list.place(relx= 0, rely = 0.5, relwidth=0.97, relheight=1, anchor = 'w')
        scroll.config( command = list.yview )

class P_Cam(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self,parent)
        
        label = ctk.CTkLabel(self, text="")
        label.place(relx = 0.5, rely = 0.5, anchor = 'center')

        def update_cam():
            try:
                if (controller.visible_frame==P_Cam):
                    #only update camera if frame is raised.
                    _, frame = controller.vid.read()
                    
                    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    captured_image = Image.fromarray(opencv_image).transpose(Image.FLIP_LEFT_RIGHT)
                    photo_image = ctk.CTkImage(captured_image, size=controller.vid_frame_size)
                    label.photo_image = photo_image
                    label.configure(image=photo_image)
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
    #MESSAGES can be a list or single element
    print("message received")
    for MESSAGE in MESSAGES:
        match MESSAGE[5]:
            case "E":
                pass

            case "V":
                arduinos[0].busy()
                command = buffer.POP()
                com.DECODE_LINE(command, Comps)
                com.Log(command)

            case "F":
                arduinos[0].free()
                    
            case _:
                pass
    return

def task():
    global device
    if len(arduinos):
        if (arduinos[0].state==False) and (buffer.LENGTH()>0):
            buffer.OUT() 
            device,_ = buffer.READ()[0]
            arduinos[0].busy()
        try:
            if (device.inWaiting() > 0):
                Event(com.READ(device))
        except:
            pass
    gui.after(100, task)
    time.sleep(0.01)

#GUI
gui = Main()
gui.after(100,task)
gui.mainloop()