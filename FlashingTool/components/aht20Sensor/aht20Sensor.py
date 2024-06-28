import datetime
import time
from . import AHT20  # Assuming AHT20 is the name of the module where AHT20 class is defined

class SensorLogger:
    def __init__(self):
        # Instantiate the AHT20 class from the module
        self.aht20 = AHT20.AHT20()

    def log_sensor_data(self):
            # Fill a string with date, humidity and temperature
            data = str(datetime.datetime.now()) + ";" + "{:10.2f}".format(self.aht20.get_humidity()) + " %RH;" + "{:10.2f}".format(self.aht20.get_temperature()) + " °C"
            # Data with crc8 check
            data_crc8 = str(datetime.datetime.now()) + ";" + "{:10.2f}".format(self.aht20.get_humidity_crc8()) + " %RH;" + "{:10.2f}".format(self.aht20.get_temperature_crc8()) + " °C"

            # Print in the console
            print(data)
            print("data with crc check: {0}".format(data_crc8))

            # Append in a file
            with open("log.txt", "a") as log:
                log.write(data + "\n")

    def read_temp_sensor(self):
         data = self.aht20.get_temperature()
         print("Temperature: {0}".format(data))
