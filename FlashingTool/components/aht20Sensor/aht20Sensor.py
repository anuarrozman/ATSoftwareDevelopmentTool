import aht20Sensor
import datetime
import time
from AHT20 import AHT20

# Instantiate the AHT20 class correctly
aht20 = AHT20()

while True:
    # Fill a string with date, humidity and temperature
    data = str(datetime.datetime.now()) + ";" + "{:10.2f}".format(aht20.get_humidity()) + " %RH;" + "{:10.2f}".format(aht20.get_temperature()) + " °C"
    # Data with crc8 check
    data_crc8 = str(datetime.datetime.now()) + ";" + "{:10.2f}".format(aht20.get_humidity_crc8()) + " %RH;" + "{:10.2f}".format(aht20.get_temperature_crc8()) + " °C"

    # Print in the console
    print(data)
    print("data with crc check: {0}".format(data_crc8))

    # Append in a file
    with open("log.txt", "a") as log:
        log.write(data + "\n")

    # Wait
    time.sleep(2)
