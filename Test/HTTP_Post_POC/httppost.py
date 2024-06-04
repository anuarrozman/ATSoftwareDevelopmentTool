import tkinter as tk
from tkinter import messagebox
import requests
import json

def send_json():
    # Create JSON data
    data = {
        "key1": entry_key1.get(),
        "key2": entry_key2.get()
        # Add more keys as needed
    }
    
    try:
        # Send HTTP POST request with JSON data
        response = requests.post("http://localhost:4000/api/endpoint", json=data)
        
        # Display response message
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

# Create GUI window
root = tk.Tk()
root.title("JSON Sender")

# Create labels and entry fields for data input
label_key1 = tk.Label(root, text="Key 1:")
label_key1.grid(row=0, column=0)
entry_key1 = tk.Entry(root)
entry_key1.grid(row=0, column=1)

label_key2 = tk.Label(root, text="Key 2:")
label_key2.grid(row=1, column=0)
entry_key2 = tk.Entry(root)
entry_key2.grid(row=1, column=1)

# Create button to send JSON data
send_button = tk.Button(root, text="Send JSON", command=send_json)
send_button.grid(row=2, columnspan=2)

# Run the GUI application
root.mainloop()
