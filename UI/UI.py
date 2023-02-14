
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure


import tkinter as tk
from tkinter import ttk
import csv
import time
import datetime
import numpy as np

LARGE_FONT= ("Verdana", 15)
NORMAL_FONT= ("Verdana", 12)
SMALL_FONT = ("Verdana", 10)



class initialise(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        Start_frame = tk.Frame(self)
        Start_frame.pack(side="top", fill="both", expand = True)
        Start_frame.grid_rowconfigure(0, weight=1)
        Start_frame.grid_columnconfigure(0, weight=1)
        self.geometry("626x431")  # Sets window size to 626w x 431h pixels
        tk.Tk.wm_title(self, "Initialisation")
    
        menubar = tk.Menu(Start_frame)
        filemenu = tk.Menu(menubar, tearoff=0)
       
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)


        tk.Tk.config(self, menu=menubar)
        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree):

            frame = F(Start_frame, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise() 

  


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        button1 = ttk.Button(self, text=("visit page 1"), command= lambda: controller.show_frame(PageOne))
        button1.pack()



class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Page One", font=LARGE_FONT)
        label.grid(row=0, column= 0, columnspan=3)

        def entry_block(text, pos):
            row,col = pos
            T = tk.Label(self, text = text, font=NORMAL_FONT)
            entry = ttk.Entry(self, width=8)
            T.grid(row=row, column=col, sticky='E')
            entry.grid(row=row, column=col+1, sticky='W')
            return entry
        
        e_Ra_ml = entry_block("Ra:", [1,0])
        e_Ra_step = entry_block("step:",[1,2])
        e_Ra_flowrate = entry_block("Flow rate:",[1,4])
        e_Rb_ml = entry_block("Rb:",[2,0])
        e_Rb_step = entry_block("step:",[2,2])
        e_Rb_flowrate = entry_block("Flow rate:",[2,4])
        e_Ra_total = entry_block("Total Ra:", [3,2])
        e_Rb_total = entry_block("Total Rb:", [3,4])
        e_count = entry_block("iteration:",[3,0])

        label = tk.Label(self, text="", font=LARGE_FONT)
        label.grid(row=4, column= 0)
     

        button1 = ttk.Button(self, text=("Back to home"), command= lambda: controller.show_frame(StartPage))
        button1.grid(row=5, column=3)
        button2 = ttk.Button(self, text=("Plot Graph"), command= lambda: controller.show_frame(PageTwo))
        button2.grid(row=6, column=3)
        button3 = ttk.Button(self, text="Component Status", command=lambda: controller.show_frame(PageThree))
        button3.grid(row=7, column=3)
        button4 = ttk.Button(self, text="send", command=lambda: send_command())
        button4.grid(row=8, column=3)

        def send_command():
            
            Ra_ml = e_Ra_ml.get()
            Ra_step = e_Ra_step.get()
            Rb_ml = e_Rb_ml.get()
            Rb_step = e_Rb_step.get()
            count = int(e_count.get())
            Ra_flowrate = e_Ra_flowrate.get()
            Rb_flowrate = e_Rb_flowrate.get()
            Ra_total = e_Ra_total.get()
            Rb_total = e_Rb_total.get()
            nowTime = datetime.datetime.now()

            
            #data_list = [['' for j in range(10)] for i in range(count)]
            data_list= np.zeros((count,10))
            print(nowTime)

            for i in range(count):
                
                hour = nowTime.hour
                minute= nowTime.minute
                second= nowTime.second

                for j in range(10):
                    if j == 0:
                        data_list[i,j] = Ra_ml
                    elif j == 1:
                        data_list[i,j] = Rb_ml
                    elif j == 2:
                        data_list[i,j] = Ra_flowrate
                    elif j == 3:
                        data_list[i,j] = Rb_flowrate
                    elif j == 4:
                        data_list[i,j] = count
                    elif j == 5:
                        data_list[i,j] = Ra_total
                    elif j == 6:
                        data_list[i,j] = Rb_total
                    elif j == 7:
                        data_list[i,j] = hour
                    elif j == 8:
                        data_list[i,j] = minute
                    else:
                        data_list[i,j] = second
                
            
         
            
            with open("data.csv", mode ="w") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Ra_ml", "Rb_ml", "fRate_Ra", "fRate_Rb", "iteration", "Ra_total", "Rb_total", "hour", "minute", "second"])
                for row in range(count):
                    writer.writerow(data_list[row, :])
                    
                # for row in range(count):
                #     for col in range(10):
                #         out_string = ""
                #         out_string += str(data_list[row, col])
                #     out_string += "\n"
                



class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Graph Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        label1 = tk.Label(self, text="Toolbar", font=LARGE_FONT)
        label1.pack(side=tk.BOTTOM, fill=tk.X)
        button1 = ttk.Button(self, text=("Back to home"), command= lambda: controller.show_frame(StartPage))
        button1.pack()

        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        
       
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        #Frame2 = initialise.show_frame(PageTwo)
        toolbar = NavigationToolbar2Tk(canvas, label1, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
       # toolbar = NavigationToolbar2TkAgg(canvas, self)
       # toolbar.update() side=tk.TOP, fill=tk.X
        #canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class PageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Component Control", font=LARGE_FONT)
        label.grid(row=0, column= 0, columnspan=8 , pady = 10)
        label1 = tk.Label(self, text="Valves", font=NORMAL_FONT)
        label1.grid(row=1, column= 1, columnspan= 2, pady= 8)
        label2 = tk.Label(self, text="Mixer", font=NORMAL_FONT)
        label2.grid(row=1, column= 4, columnspan= 3, pady= 8)

        def component_control(n, component, state1, state2 ,pos):
            row,col = pos
            String = component + str(n) + str(":")
            label = tk.Label(self, text=String, font=SMALL_FONT)
            label.grid(row=row, column= col, sticky='E', padx = 5)
            button = ttk.Button(self, text=state1)
            button.grid(row=row, column=col+1, sticky='W', padx= 2, pady=3)
            button1 = ttk.Button(self, text=state2)
            button1.grid(row=row, column=col+2, sticky='W', padx= 2, pady=3)
            return label, button, button1


        valve1 = component_control(1, "Valve", "Pinch left","Pinch right", [3,0])
        valve2 = component_control(2,"Valve","Pinch left","Pinch right", [4,0])
        valve3 = component_control(3,"Valve","Pinch left","Pinch right", [5,0])

        separator = ttk.Separator(self, orient='vertical')
        separator.grid(column=3, row=2, rowspan=5, sticky='ns', padx = 5)

        mixer = component_control("", "Mixer", "Mix", "Stop", [3,4])

        separator1 = ttk.Separator(self, orient='vertical')
        separator1.grid(column=7, row=2, rowspan=5, sticky='ns', padx = 5)


        
        
        



app = initialise()
app.mainloop()
