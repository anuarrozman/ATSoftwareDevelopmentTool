import subprocess
import os
import logging
import io

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlashFirmware:
    
    def __init__(self, status_label):
        self.status_label = status_label
        self.log_capture_string = io.StringIO()
        self.ch = logging.StreamHandler(self.log_capture_string)
        self.ch.setLevel(logging.INFO)
        self.ch.setFormatter(logging.Formatter('%(message)s'))
        # Clean up previous handlers if any to avoid duplicate logs
        if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
            logger.addHandler(self.ch)
    
    def find_bin_path(self, keyword, search_directory):
        for root, dirs, files in os.walk(search_directory):
            for file in files:
                if file.endswith(".bin") and keyword in file:
                    return os.path.join(root, file)
        return None

    def flash_firmware(self, port_var, baud_var):
        selected_port = port_var
        selected_baud = baud_var

        # Define keywords for each bin file
        keywords = {
            "boot_loader": "bootloader",
            "partition_table": "partition-table",
            "ota_data_initial": "ota_data_initial",
            # "firmware": "adt_matter_project_"
            "firmware": "v1_0_0-20240716-de5"
        }

        # Define the directory to search in
        search_directory = "/home/anuarrozman/FactoryApp_Dev/ATSoftwareDevelopmentTool/FlashingTool/firmware"

        # Find paths for each bin file using keywords
        bin_paths = {key: self.find_bin_path(keyword, search_directory) for key, keyword in keywords.items()}

        boot_loader_path = bin_paths["boot_loader"]
        partition_table_path = bin_paths["partition_table"]
        ota_data_initial_path = bin_paths["ota_data_initial"]
        fw_path = bin_paths["firmware"]

        # Check if all paths are valid
        if not all(bin_paths.values()):
            logger.error("Error: Unable to find one or more bin files")
            return

        # Run esptool.py command
        command = f"esptool.py -p {selected_port} -b {selected_baud} write_flash 0x0 {boot_loader_path} 0xc000 {partition_table_path} 0x1e000 {ota_data_initial_path} 0x200000 {fw_path}"

        try:
            # Open subprocess with stdout redirected to PIPE
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            # Read stdout line by line and log in real-time
            for line in iter(process.stdout.readline, ''):
                logger.info(line.strip())
                if "Hard resetting via RTS pin" in line:
                    logger.info("Firmware Flashing Complete")

            process.stdout.close()
            process.wait()  # Wait for the process to finish

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running esptool.py: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        
        # After the process completes, update the flashing status
        self.get_flashing_status()

    def get_flashing_status(self):
        self.ch.flush()
        log_contents = self.log_capture_string.getvalue()
        if "Firmware Flashing Complete" in log_contents:
            self.update_status_label("Completed", "green", ("Helvetica", 12, "bold"))
        else:
            self.update_status_label("Failed", "red", ("Helvetica", 12, "bold"))

    def update_status_label(self, message, fg, font):
        self.status_label.config(text=message, fg=fg, font=font)  # Update the status label with the message

