import tkinter as tk
from servo import ServoController
import time

class ServoApp:
    def __init__(self, root):
        self.root = root
        self.servo_controller = ServoController()

        self.time_label = tk.Label(root, text="Enter pressing time:")
        self.time_label.pack()
        self.time_entry = tk.Entry(root)
        self.time_entry.pack()

        self.angle_label = tk.Label(root, text="Enter button angle:")
        self.angle_label.pack()
        self.angle_entry = tk.Entry(root)
        self.angle_entry.pack()

        self.duration_label = tk.Label(root, text="Enter pressing duration:")
        self.duration_label.pack()
        self.duration_entry = tk.Entry(root)
        self.duration_entry.pack()

        self.button = tk.Button(root, text="Press Button", command=self.press_button)
        self.button.pack()

    def press_button(self):
        pressing_time = int(self.time_entry.get())
        button_angle = float(self.angle_entry.get())
        pressing_duration = float(self.duration_entry.get())

        for i in range(pressing_time):
            print(f"Pressing button {i+1} time")
            self.servo_controller.set_angle(button_angle)
            time.sleep(pressing_duration)
            self.servo_controller.set_angle(0)
            time.sleep(0.5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServoApp(root)
    root.mainloop()
    app.servo_controller.stop()
