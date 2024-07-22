import tkinter as tk
from tkinter import ttk

# Function to read order numbers from the text file
def read_order_numbers(file_path):
    order_numbers = []
    with open(file_path, 'r') as file:
        for line in file:
            if 'order-no' in line:
                order_number = line.split('order-no: ')[1].split(',')[0].strip()
                if order_number not in order_numbers:
                    order_numbers.append(order_number)
    return order_numbers

# Function to handle selection from dropdown
def on_select(event):
    selected_order = event.widget.get()
    print(f"Selected Order Number: {selected_order}")

# Path to your text file
file_path = '/home/anuarrozman/FactoryApp_Dev/ATSoftwareDevelopmentTool/FlashingTool/device_data.txt'

# Read order numbers from the text file
order_numbers = read_order_numbers(file_path)

# Create a Tkinter window
root = tk.Tk()
root.title("Order Number Dropdown")

# Create a dropdown menu
selected_order = tk.StringVar(root)
dropdown = ttk.Combobox(root, textvariable=selected_order, values=order_numbers)
dropdown.pack(padx=20, pady=20)
dropdown.bind("<<ComboboxSelected>>", on_select)

root.mainloop()
