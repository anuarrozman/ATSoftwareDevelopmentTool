import tkinter as tk
import adminlogin

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Main Window")
        
        self.admin_login_button = tk.Button(master, text="Admin Login", command=self.open_admin_login)
        self.admin_login_button.pack()

        self.normal_button = tk.Button(master, text="Normal Button", state="disabled")
        self.normal_button.pack()

    def open_admin_login(self):
        admin_window = tk.Toplevel(self.master)
        adminlogin.AdminLoginWindow(admin_window, self.handle_admin_login)
        admin_window.wait_window(admin_window)

    def handle_admin_login(self, success):
        if success:
            self.normal_button.config(state="normal")

def main():
    root = tk.Tk()
    main_window = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
