# Import required Libraries
from tkinter import *
from PIL import Image, ImageTk
import cv2

import cv2
import numpy as np
c = cv2.VideoCapture(0)

a=0

if a==0:
    while(1):
        _,f = c.read()
        cv2.imshow('e2',f)
        if cv2.waitKey(5)==27:
            break
    cv2.destroyAllWindows()


if a==1:
    # Create an instance of TKinter Window or frame
    win = Tk()

    # Set the size of the window
    win.geometry("1000x1000")

    # Create a Label to capture the Video frames
    label =Label(win)
    label.grid(row=0, column=0)
    cap= cv2.VideoCapture(0)

    # Define function to show frame
    def show_frames():
        # Get the latest frame and convert into Image
        cv2image= cv2.cvtColor(cap.read()[1],cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        # Convert image to PhotoImage
        imgtk = ImageTk.PhotoImage(image = img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
        # Repeat after an interval to capture continiously
        label.after(20, show_frames)

    show_frames()
    win.mainloop()