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
            "firmware": "adt_matter_project_"
        }

        # Define the directory to search in
        search_directory = "/usr/src/app/ATSoftwareDevelopmentTool/FlashingTool/firmware" # Update with your directory

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
        
        # After the process completes, update the flashing status
        self.get_flashing_status()

    def get_flashing_status(self):
        self.ch.flush()
        log_contents = self.log_capture_string.getvalue()
        if "Firmware Flashing Complete" in log_contents:
            self.status_label.config(text="Completed")
        else:
            self.status_label.config(text="Failed")
