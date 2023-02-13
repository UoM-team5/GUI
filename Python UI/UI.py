import time
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os
import Serial_lib as com 
import cv2 


#init comms

buffer = com.Buffer()
def init_module():
    global arduino, V, P
    arduino = []
    V = [0]
    P = [0]
    Ports = com.ID_PORTS_AVAILABLE()
    for i in range(len(Ports)):
        print("\nSource: ", Ports[i])
        device = com.OPEN_SERIAL_PORT(Ports[i])
        print("\nDevice: ", device)
        while(device.inWaiting() == 0):
            time.sleep(0.1)

        message = com.SERIAL_READ_LINE(device)
        deviceID  = message[0][0:4]
        print("\narduino: ", deviceID)
        arduino.append(com.Nano(device, deviceID))
        if deviceID=="1001":
            V1 = com.Valve(device, deviceID, 1, buffer)
            V2 = com.Valve(device, deviceID, 2, buffer)
            V3 = com.Valve(device, deviceID, 3, buffer)
            V = [V1,V2,V3]
            P1 = com.Pump(device, deviceID, 1, buffer)
            P2 = com.Pump(device, deviceID, 2, buffer)
            P = [P1, P2]
        #TO DO: Build CSV table and initialise components

    print("\n------------End initialisation--------------\n\n")
    return

# UI styles 
LARGE_FONT= ("Arial", 20)
styles = {"relief": "groove",
                "bd": 3, "bg": "#DDDDDD",
                "fg": "#073bb3", "font": ("Arial", 12, "bold")}
entry_styles = {"relief": "groove", "width": 8,
                "bd": 5, "font": ("Arial", 10, "normal")}
label_styles = {"relief": "flat", "bg": "#DDDDDD",
                "bd": 3, "font": ("Verdana", 10, "normal")}

# UI functions
def update_label(label, new_text):
    label.configure(text = new_text)
    return label

def add_image(file_name, frame, relx, rely, anchor='center'):
    carap = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name), "r"))
    label = tk.Label(frame, image = carap)
    label.image = carap
    label.place(relx = relx, rely = rely, anchor = anchor)

def bttn_image(frame, text, file_name):
    photo = ImageTk.PhotoImage(Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name), "r"))
    bttn1 = ttk.Button(frame, text=text, image = photo, compound = 'left')
    bttn1.image = photo
    return bttn1


def entry_block(text: str, frame, spin=False):
    """label followed by entry widget"""
    lbl_T = tk.Label(frame, label_styles, text = text)
    if (spin):
        entry = tk.Spinbox(frame, from_=0, to=10, width=2, wrap=True)
    else:
        entry = ttk.Entry(frame, width=5)
    return lbl_T, entry

def place_entry_block(lbl_T, entry, pos):
    lbl_T.place(relx = 0.6, rely = pos/6, anchor = 'e')
    entry.place(relx = 0.62, rely = pos/6, anchor = 'w')

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
class initialise(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg=styles["bg"])  # this is the background
        main_frame.pack(fill="both", expand="true")

        self.geometry("600x400")  # 600w x 400h pixels
        #self.resizable(0, 0)  # This prevents any resizing of the screen
        self.title("Initialisation")

        title = tk.Label(main_frame, text = "Initialise", font=LARGE_FONT, bg = styles["bg"])
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')
        
        def update_devices():
            init_module()
            #refer to actual object returned if none= do not update label
            if len(arduino):
                update_label(details, "arduino: '1001'\n2 Valve \n1 Pump")
        
        frame1 = tk.LabelFrame(main_frame, styles, text = "Setup communcation")
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')
        
        bttn1 = ttk.Button(frame1, text="Initialise",
         command=lambda: update_devices())
        bttn1.place(relx = 0.5, rely = 0.2, anchor = 'center') 

        ard_detail = "no arduino"
        details = tk.Label(frame1, label_styles, text=ard_detail,justify= 'left')
        details.place(relx = 0.5, rely = 0.5, anchor = 'center') 

        bttn2 = ttk.Button(frame1, text="FINISH",
         command=lambda: init.destroy())
        bttn2.place(relx = 0.5, rely = 0.9, anchor = 'center') 
        
        update_devices()

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.add_command(label="Home", command=lambda: parent.show_frame(StartPage))

        self.add_command(label="Manual", command=lambda: parent.show_frame(PageOne))

        menu_auto = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Auto", menu=menu_auto)
        menu_auto.add_command(label="Recipe", command=lambda: parent.show_frame(PageTwo))
        menu_auto.add_separator()
        menu_auto.add_command(label="iterate", command=lambda: parent.show_frame(PageThree))

        menu_help = tk.Menu(self, tearoff=0)
        self.add_cascade(label="plots", menu=menu_help)
        menu_help.add_command(label="Open New Window", command=lambda: parent.OpenNewWindow())

class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "ARCaDIUS")

        self.geometry("700x431") 
        self.minsize(500,300) 
        container = tk.Frame(self, bg = "#BEB2A7", height=600, width=1024)
        container.pack(side="top", fill = "both", expand = "true")
        container.grid_rowconfigure(0, weight= 1)
        container.grid_columnconfigure(0, weight= 1)
        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree):
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
        tk.Frame.__init__(self,parent, bg = styles["bg"])
        # title = tk.Label(self, text = "Home", font=LARGE_FONT, bg = styles["bg"])
        # title.place(relx = 0.5, rely = 0.1, anchor = 'center')
        add_image("arcadius.png", self, relx=0.5, rely=0.05, anchor = 'n')

        frame1 = tk.LabelFrame(self, styles, text = "Menu")
        frame1.place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')

        bttn1 = ttk.Button(frame1, text="Manual",
         command=lambda: controller.show_frame(PageOne))
        bttn1.place(relx = 0.48, rely = 0.2, anchor = 'e')

        bttn2 = ttk.Button(frame1, text="Auto",
         command=lambda: controller.show_frame(PageTwo))
        bttn2.place(relx = 0.52, rely = 0.2, anchor = 'w')

        bttn3 = ttk.Button(frame1, text="Details",
         command=lambda: controller.show_frame(PageTwo))
        bttn3.place(relx = 0.48, rely = 0.3, anchor = 'e')

        bttn4 = ttk.Button(frame1, text="iterate",
         command=lambda: controller.show_frame(PageThree))
        bttn4.place(relx = 0.52, rely = 0.3, anchor = 'w')

        
        # add_image("carap.png", frame1, relx=1, rely=1, anchor = 'se')
        # add_image("carap_flip.png", frame1, relx=0, rely=1, anchor = 'sw')
        bttn4 = ttk.Button(frame1, text="Exit",
         command=lambda: controller.Quit_application())
        bttn4.place(relx = 0.5, rely = 0.9, anchor = 'center')

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = styles["bg"])
        title = tk.Label(self, text = "Manual Control", font=LARGE_FONT, bg = styles["bg"])
        title.place(relx = 0.5, rely = 0.05, anchor = 'center')
        
        frame1 = tk.LabelFrame(self, styles, text = "Valve")
        frame1.place(relx=0.175, rely=0.15, relwidth=0.3, relheight=0.8, anchor = 'n')

        frame2 = tk.LabelFrame(self, styles, text = "Pump")
        frame2.place(relx=0.5, rely=0.15, relwidth=0.3, relheight=0.8, anchor = 'n')

        frame3 = tk.LabelFrame(self, styles, text = "Mixer")
        frame3.place(relx=0.825, rely=0.15, relwidth=0.3, relheight=0.38, anchor = 'n')

        frame4= tk.LabelFrame(self, styles, text = "Sensors")
        frame4.place(relx=0.825, rely=0.55, relwidth=0.3, relheight=0.4, anchor = 'n')

        #box 1 Valve
        lbl_valve = tk.Label(frame1, label_styles, text = "select valve: ")
        lbl_valve.place(relx=0.1, rely = 0.1, anchor = 'w')
        valve_num = tk.StringVar(value=0)
        valve_sel = tk.Spinbox(frame1, from_=0, to=len(V), width=2,  wrap=True, textvariable=valve_num)
        valve_sel.place(relx=0.6, rely = 0.1, anchor = 'w')

        bttn1 = ttk.Button(frame1, text="close",
         command=lambda: V[int(valve_num.get())].close())
        bttn1.place(relx = 0.48, rely = 0.2, anchor = 'e')
        bttn2 = ttk.Button(frame1, text="open",
         command=lambda: V[int(valve_num.get())].open())
        bttn2.place(relx = 0.52, rely = 0.2, anchor = 'w')

        #box 2 pump
        lbl_pump = tk.Label(frame2, label_styles, text = "select pump: ")
        lbl_pump.place(relx=0.1, rely = 0.1, anchor = 'w')
        pump_num=tk.StringVar(value=0)
        pump_sel = tk.Spinbox(frame2, from_=0, to=len(P), width=2, wrap=True, textvariable=pump_num)
        pump_sel.place(relx=0.6, rely = 0.1, anchor = 'w')

        lbl_pump = tk.Label(frame2, label_styles, text = "volume (ml): ")
        lbl_pump.place(relx=0.5, rely = 0.2, anchor = 'e')
        volume=tk.StringVar()
        vol_entry = tk.Entry(frame2, entry_styles, textvariable=volume)
        vol_entry.place(relx=0.5, rely = 0.2, anchor = 'w')
        bttn1 = ttk.Button(frame2, text="send",
         command=lambda: P[int(pump_num.get())].pump(float(volume.get())))
        bttn1.place(relx = 0.5, rely = 0.3, anchor = 'center')

        #box 3 mixer
        lbl_mix = tk.Label(frame3, label_styles, text = "time (s): ")
        lbl_mix.place(relx=0.5, rely = 0.1, anchor = 'e')
        time=tk.StringVar()
        t_entry = tk.Entry(frame3, entry_styles, textvariable= time)
        t_entry.place(relx=0.5, rely = 0.1, anchor = 'w')
        bttn1 = ttk.Button(frame3, text="send")
        bttn1.place(relx = 0.5, rely = 0.35, anchor = 'center')

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = styles["bg"])
        label = tk.Label(self, text = "Recipe", font=LARGE_FONT, bg = styles["bg"])
        label.pack(pady=10,padx=10)

        bttn1 = bttn_image(self, "whatever", "frog.png")
        bttn1.pack(pady=10,padx=10)

class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = styles["bg"])

        title = tk.Label(self, text = "Iterative experiment", font=LARGE_FONT, bg = styles["bg"])
        title.place(relx = 0.5, rely = 0.1, anchor = 'center')

        frames = [0]*5
        frames[0] = tk.LabelFrame(self, styles, text = "Settings of experiments")
        frames[0].place(relx= 0.5, rely = 0.55, relwidth=0.8, relheight=0.8, anchor = 'center')
        frames[1] = tk.LabelFrame(frames[0], styles, relief='flat', text = "volume")
        frames[1].place(relx= 0.75, rely = 0.05, relwidth=0.25, relheight=0.6, anchor = 'ne')
        frames[2] = tk.LabelFrame(frames[0], styles, relief='flat', text = "steps")
        frames[2].place(relx= 0.75, rely = 0.05, relwidth=0.25, relheight=0.6, anchor = 'nw')
        frames[3] = tk.LabelFrame(frames[0], styles, text = "Send")
        frames[3].place(relx= 0.75, rely = 0.65, relwidth=0.4, relheight=0.3, anchor = 'n')

        def on_click(checkbutton_var, widgets, pos: int):
            [lbl, ent_vol, lbls, ent_step] = widgets
            if checkbutton_var.get() == 1:
                place_entry_block(lbl, ent_vol, pos)
                place_entry_block(lbls, ent_step, pos)
            else:
                for widget in widgets:
                    widget.place_forget()

            
        lblA, ent_volA = entry_block("Liquid A:",frames[1])
        lblsA, ent_stepA = entry_block("step A:",frames[2])
        place_entry_block(lblA, ent_volA, 1)
        place_entry_block(lblsA, ent_stepA, 1)
        widgetsA = [lblA, ent_volA, lblsA, ent_stepA]

        lblB, ent_volB = entry_block("Liquid B:",frames[1])
        lblsB, ent_stepB = entry_block("step B:",frames[2])
        widgetsB = [lblB, ent_volB, lblsB, ent_stepB]
        
        lblcount, e_count = entry_block("iterations:",frames[3], spin=True)
        place_entry_block(lblcount, e_count, 1)
        bttn1 = ttk.Button(frames[3], text="Start", command=lambda: send_command())
        bttn1.place(relx = 0.5, rely = 0.6, anchor='center') 

        checkbutton_var1 = tk.IntVar(value=1)
        checkbutton= tk.Checkbutton(frames[0], text="Reactant A", variable=checkbutton_var1, command=lambda: on_click(checkbutton_var1, widgetsA, 1))
        checkbutton.place(relx = 0.1, rely = 0.3, anchor='center') 
        checkbutton_var2 = tk.IntVar()
        checkbutton= tk.Checkbutton(frames[0], text="Reactant B", variable=checkbutton_var2, command=lambda: on_click(checkbutton_var2, widgetsB, 2))
        checkbutton.place(relx = 0.1, rely = 0.4, anchor='center') 

        def send_command():
            cmd_list = []
            Ra_ml_init = ent_volA.get()
            Ra_step = ent_stepA.get()
            Rb_ml_init = ent_volB.get()
            Rb_step = ent_stepB.get()
            count = int(e_count.get())

            for i in range(count):
                if Ra_ml_init!="" and Ra_step!="":
                    Ra_ml = float(Ra_ml_init) + float(Ra_step)*i
                    cmd_list.append(P[0].pump(Ra_ml))
                if Rb_ml_init!="" and Rb_step!="":
                    Rb_ml = float(Rb_ml_init) + float(Rb_step)*i
                    cmd_list.append(P[1].pump(Rb_ml))

            buffer.IN(cmd_list)
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


init = initialise()
init.mainloop()

def Event(MESSAGES):
    for MESSAGE in MESSAGES:
        match MESSAGE[5]:
            case "E":
                print('REPEAT')

            case "V":
                arduino[0].busy()
                #create log function to save validated commands.
                All_commands = buffer.READ()
                
                buffer.POP()
                #print("left in the buffer:", buffer.READ())

            case "F":
                arduino[0].free()
                    
            case _:
                pass
    
    return 
def task():
    if len(arduino):

        if (arduino[0].get_device().inWaiting() > 0):
            messages = com.SERIAL_READ_LINE(arduino[0].get_device())
            Event(messages)
        
        if arduino[0].get_state()==False and buffer.LENGTH()>0:
            buffer.OUT() 

     
    gui.after(100, task)
    time.sleep(0.01)
#GUI
gui = Main()
gui.after(100,task)
gui.mainloop()