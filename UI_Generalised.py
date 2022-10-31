import tkinter as tk
from tkinter import ttk
import serial
import time

# uncomment next line for arduino comm
try:
    arduino = serial.Serial(port='COM6', baudrate=9600, timeout=.1)
except:
    pass
arduino_servo = serial.Serial(port='COM7', baudrate=115200, timeout=.1)

# Send stuff to arduino through Serial
def write(x):
    # UNcomment 2 next lines for arduino comm
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    print(x)

def write_servo(x):
    # UNcomment 2 next lines for arduino comm
    arduino_servo.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    print(x)

LARGE_FONT= ("Verdana", 14)
BUTTON_FONT= ("Verdana", 10)




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

        for F in (StartPage, PageOne, PageTwo, PageThree):
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


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text = "control my valve", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 = ttk.Button(self, text="Home",
         command=lambda: controller.show_frame(StartPage))
        button1.pack()
        
        button2 = ttk.Button(self, text="close my valve :(",
         command=lambda: write_servo("0"))
        button2.pack()

        button3 = ttk.Button(self, text="open my valve :)",
         command=lambda: write_servo("1"))
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

        entry = ttk.Entry(self)
        entry.pack()

        button2 = ttk.Button(self, text="send your text to Ard",
         command=lambda: write(entry.get()))
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
         command=lambda: write_servo("1,"+entry0.get()))
        button2.pack() 

        MyText2 = "R B: Type in the number of ml"
        T2 = tk.Text(self, height = 1, width = 52)
        T2.insert(tk.END, MyText2)
        T2.pack()

        entry1 = ttk.Entry(self)
        entry1.pack()

        button3 = ttk.Button(self, text="send your text to Ard",
         command=lambda: [write(entry1.get()), write_servo("0,0")])
        button3.pack() 
gui=Main()
gui.mainloop()