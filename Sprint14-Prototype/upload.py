from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfile 
import time

ws = Tk()
ws.title('PythonGuides')
ws.geometry('400x200') 


def open_file():
    file_path = askopenfile(mode='r', filetypes=[('Initialization File', '*jpeg')])
    if file_path is not None:
        pass


def uploadFiles():
    pb1 = Progressbar(
        ws, 
        orient=HORIZONTAL, 
        length=300, 
        mode='determinate'
        )
    pb1.grid(row=4, columnspan=3, pady=20)
    for i in range(5):
        ws.update_idletasks()
        pb1['value'] += 20
        time.sleep(1)
    pb1.destroy()
    Label(ws, text='File Uploaded Successfully!', foreground='green').grid(row=4, columnspan=3, pady=10)
        
    
adhar = Label(
    ws, 
    text='Upload configuration file:'
    )
adhar.grid(row=0, column=0, padx=10)

adharbtn = Button(
    ws, 
    text ='Choose File', 
    command = lambda:open_file()
    ) 
adharbtn.grid(row=0, column=1)

ws.mainloop()