import tkinter as tk
import requests
import mysql.connector

# Function to create database table
def create_table():
    conn = mysql.connector.connect(
        host="localhost",
        user="anuarrozman2303",
        password="Matter2303!",
        database="device_mac_sn"
    )
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS devices
                 (id INT AUTO_INCREMENT PRIMARY KEY, mac_address VARCHAR(255), serial_number VARCHAR(255))''')
    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(data):
    conn = mysql.connector.connect(
        host="localhost",
        user="anuarrozman2303",
        password="Matter2303!",
        database="device_mac_sn"
    )
    cursor = conn.cursor()
    for device in data:
        mac_address = device.get("mac_address", "N/A")
        serial_number = device.get("serial_number", "N/A")
        cursor.execute("INSERT INTO devices (mac_address, serial_number) VALUES (%s, %s)", (mac_address, serial_number))
    conn.commit()
    conn.close()

# Function to download and display data
def download_data():
    url = "http://localhost:3000/serialnumber"
    try:
        response = requests.get(url)
        data = response.json()
        insert_data(data)
        display_data(data)
    except Exception as e:
        status_label.config(text="Error downloading data: " + str(e))

# Function to display data
def display_data(data):
    listbox.delete(0, tk.END)
    for device in data:
        mac_address = device.get("mac_address", "N/A")
        serial_number = device.get("serial_number", "N/A")
        listbox.insert(tk.END, f"MAC: {mac_address}, Serial: {serial_number}")
    status_label.config(text="Data downloaded successfully!")

# Create table when the script is run
create_table()

root = tk.Tk()
root.title("Device List")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

listbox = tk.Listbox(frame, width=50, height=10)
listbox.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

download_button = tk.Button(root, text="Download Data", command=download_data)
download_button.pack(pady=5)

status_label = tk.Label(root, text="", fg="green")
status_label.pack()

root.mainloop()
