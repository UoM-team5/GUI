# GUI


This repo is for UI programs. 
For the first semester, only develop minimalist UI to control the hardware seperatly , and slowly moving to more exhaustive GUI

## UI_Generalised.py description 

Base template for UI with buttons and basic function calls for writing to arduino.

main source for the code: https://pythonprogramming.net/tkinter-depth-tutorial-making-actual-program/

### Python to arduino communication
Change the COM n° to fit

```
arduino = serial.Serial(port='COM7', baudrate=115200, timeout=.1)
def write(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
```



### Classes

#### class Main

The main class is the initialising all the frames, stacks them in a *container* and *raises* one by one if needed.

The functions in this class are actualy methods.

Do **NOT** touch this class unless adding a new page 
```
class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
         .
         .
         .
        for F in (StartPage, PageOne, PageTwo, **ADD MORE PAGE NAMES HERE** ):
          .
          .
          .

    def show_frame(self, cont):
        ...
```

#### class StartPage

This is the home page, can be modified to look however you like. including different widgets.

To call a function with argument when pressing a button: you must use ```command=lambda: FunctionName(args)```

(else the function is called once each time the frame is raised).

```
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
 ```
 
 
 Declare as many more frames as needed
 
 Once the code is ready, show all the frames using: 
```
gui=Main()
gui.mainloop()
```
