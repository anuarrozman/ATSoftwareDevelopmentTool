import tkinter as tk

class AdminLoginWindow:
    def __init__(self, master, callback):
        self.master = master
        self.callback = callback
        self.master.title("Admin Login")
        
        self.label = tk.Label(master, text="Enter Admin Password:")
        self.label.pack()

        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(master, text="Login", command=self.check_password)
        self.login_button.pack()

    def check_password(self):
        entered_password = self.password_entry.get()
        # Replace 'admin123' with your actual admin password
        if entered_password == "admin123":
            self.callback(True)
            self.master.destroy()

def main():
    root = tk.Tk()
    admin_login_window = AdminLoginWindow(root, lambda x: None)
    root.mainloop()

if __name__ == "__main__":
    main()
