import tkinter as tk
from servo import ServoController
import configparser
import os
import time

class ServoApp:
    def __init__(self, root):
        self.root = root
        self.servo_controller = ServoController()

        # Get the absolute path to the servo.ini file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'servo.ini')

        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        settings = self.config['Settings']

        self.pressing_time = int(settings['pressing_time'])
        self.button_angle = float(settings['button_angle'])
        self.pressing_duration = float(settings['pressing_duration'])

        self.display_settings()

        self.button = tk.Button(root, text="Press Button", command=self.press_button)
        self.button.pack()

    def display_settings(self):
        settings_frame = tk.Frame(self.root)
        settings_frame.pack()

        time_label = tk.Label(settings_frame, text=f"Pressing time: {self.pressing_time}")
        time_label.pack()
        angle_label = tk.Label(settings_frame, text=f"Button angle: {self.button_angle}")
        angle_label.pack()
        duration_label = tk.Label(settings_frame, text=f"Pressing duration: {self.pressing_duration}")
        duration_label.pack()

    def press_button(self):
        for i in range(self.pressing_time):
            print(f"Pressing button {i+1} time")
            self.servo_controller.set_angle(self.button_angle)
            time.sleep(self.pressing_duration)
            self.servo_controller.set_angle(0)
            time.sleep(0.5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServoApp(root)
    root.mainloop()
    app.servo_controller.stop()
