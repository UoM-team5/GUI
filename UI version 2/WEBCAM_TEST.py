import time
import csv
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk
import cv2
import Serial_lib as com 
import CMD as cmd
import numpy as np
import random
from PIL import Image, ImageTk
from tkinter_webcam import webcam
import cv2

cap = cv2.VideoCapture(0)

LARGE_FONT= ("Verdana", 20)
NORMAL_FONT= ("Verdana", 15)
SMALL_FONT= ("Verdana", 10)

frame_styles = {"relief": "groove",
                "bd": 3, "bg": "#f0a000",
                "fg": "#073bb3", "font": ("Arial", 9, "bold")}


def camera2():
    win = Tk()

    # Set the size of the window
    win.geometry("700x350")

    # Create a Label to capture the Video frames
    label =Label(win)
    label.grid(row=0, column=0)
    #cap= cv2.VideoCapture(0)

    # Define function to show frame
    def show_frames1():
    # Get the latest frame and convert into Image
        cv2image= cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        # Convert image to PhotoImage
        imgtk = ImageTk.PhotoImage(image = img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
        # Repeat after an interval to capture continiously
        label.after(20, show_frames1)

    show_frames1()
    win.mainloop()


def camera3():
    #cap = cv2.VideoCapture(0)

    cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        success, image = cap.read()

        cv2.imshow("Image", image)

        if cv2.waitKey(1) & 0xFF == 27:
            break


def camera3():
    c = cv2.VideoCapture(0)
    while(1):
        _,f = c.read()
        cv2.imshow('e2',f)
        if cv2.waitKey(5)==27:
            break
    cv2.destroyAllWindows()


cv2.destroyAllWindows()
cap.release()


class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Hardware control")

        container = tk.Frame(self, bg = "#BEB2A7", height=600, width=1024)
        container.pack(side="top", fill = "both", expand = "true")
        container.grid_rowconfigure(0, weight= 1)
        container.grid_columnconfigure(0, weight= 1)

        self.frames = {}

        for F in (StartPage, PageSix):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

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
        title.pack(pady=100,padx=100)

        button = ttk.Button(self, text="Go to Webcam menu",
         command=lambda: controller.show_frame(PageSix))
        button.pack(pady=100,padx=100)


class PageSix(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, bg = frame_styles["bg"])

        buttonN = ttk.Button(self, text="Open Camera", command=lambda: camera3())
        buttonN.pack(pady=100,padx=100)


gui = Main()
gui.mainloop() 