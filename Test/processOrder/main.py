# main.py

import tkinter as tk
from tkinter import ttk
from components.processOrderNumber.processOrderNumber import get_order_numbers
from components.flashCert.flashCert import get_cert_ids_for_order, flash_certificate, get_remaining_cert_ids
from components.readOrderFile import parse_order_file

def main():
    file_path = '/home/anuarrozman/FactoryApp_Dev/ATSoftwareDevelopmentTool/FlashingTool/device_data.txt'  # Specify the correct path to your text file
    orders = parse_order_file(file_path)
    order_numbers = get_order_numbers(orders)

    def on_select_order_no(event):
        selected_order_no = order_no_var.get()
        cert_ids = get_cert_ids_for_order(orders, selected_order_no)
        remaining_cert_ids = get_remaining_cert_ids(cert_ids)
        
        if remaining_cert_ids:
            cert_id_dropdown['values'] = remaining_cert_ids
            cert_id_label.config(text="Select Cert ID:")
            cert_id_dropdown.pack(pady=10)
        else:
            cert_id_label.config(text="No Cert IDs available for the selected order.")
            cert_id_dropdown.pack_forget()  # Hide the dropdown if no cert IDs are available

        selected_order_no_label.config(text=f"Selected Order Number: {selected_order_no}")

    def on_select_cert_id(event):
        selected_cert_id = cert_id_var.get()
        if flash_certificate(selected_cert_id):
            remaining_cert_ids = get_remaining_cert_ids(get_cert_ids_for_order(orders, order_no_var.get()))
            cert_id_dropdown['values'] = remaining_cert_ids
            status_label.config(text=f"Cert ID {selected_cert_id} flashed successfully.")
        else:
            status_label.config(text=f"Cert ID {selected_cert_id} has already been used.")

    root = tk.Tk()
    root.title("Order Number Selector")

    # Create and place widgets
    order_no_var = tk.StringVar()
    cert_id_var = tk.StringVar()
    
    order_no_label = ttk.Label(root, text="Select Order Number:")
    order_no_label.pack(pady=10)

    order_no_dropdown = ttk.Combobox(root, textvariable=order_no_var, values=order_numbers)
    order_no_dropdown.pack(pady=10)
    order_no_dropdown.bind("<<ComboboxSelected>>", on_select_order_no)

    selected_order_no_label = ttk.Label(root, text="Selected Order Number: ")
    selected_order_no_label.pack(pady=10)

    cert_id_label = ttk.Label(root, text="Select Cert ID:")
    cert_id_label.pack(pady=10)

    cert_id_dropdown = ttk.Combobox(root, textvariable=cert_id_var)
    cert_id_dropdown.pack(pady=10)
    cert_id_dropdown.bind("<<ComboboxSelected>>", on_select_cert_id)

    status_label = ttk.Label(root, text="")
    status_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
