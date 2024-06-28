from . import AHT20  # Assuming AHT20 is the name of the module where AHT20 class is defined
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SensorLogger:
    def __init__(self):
        # Instantiate the AHT20 class from the module
        self.aht20 = AHT20.AHT20()

    def read_temp_sensor(self):
        #  data = self.aht20.get_temperature()
         data_crc8 = "{:10.2f}".format(self.aht20.get_temperature()) + " °C"
         logger.debug("Temperature: {0}".format(data_crc8))
         return data_crc8

    def read_humid_sensor(self):
        #  data = self.aht20.get_humidity()
         data_crc8 = "{:10.2f}".format(self.aht20.get_humidity()) + " %RH"
         logger.debug("Humidity: {0}".format(data_crc8))

