import tkinter as tk
from tkinter import messagebox, filedialog
import configparser
import uploadReport

def upload_report():
    ini_file_path = filedialog.askopenfilename(title="Select .ini file", filetypes=[("INI files", "*.ini")])
    if not ini_file_path:
        return
    
    config = configparser.ConfigParser()
    config.read(ini_file_path)
    
    # Create a single dictionary from the INI file sections
    combined_data = {}
    for section in config.sections():
        combined_data.update(config[section])
    
    # Convert to the desired JSON format: a list of one dictionary
    data = [combined_data]

    # Debugging: Print the data dictionary to verify its contents
    print("Converted data:", data)
    
    api_url = "http://localhost:4000/api/endpoint"   # Replace with your actual API endpoint
    
    response = uploadReport.post_report(api_url, data)
    
    if response and response.status_code == 200:
        messagebox.showinfo("Success", "Report uploaded successfully!")
    else:
        messagebox.showerror("Error", "Failed to upload report.")

def create_gui():
    root = tk.Tk()
    root.title("Report Uploader")

    upload_button = tk.Button(root, text="Upload Report", command=upload_report)
    upload_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
