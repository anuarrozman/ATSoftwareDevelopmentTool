import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdateDB:
    def __init__(self, status_label):
        self.status_label = status_label

    def update_database(self, mac_address):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="anuarrozman2303",
                password="Matter2303!",
                database="device_mac_sn"
            )

            cursor = connection.cursor()

            # Check if the MAC address already exists in the database
            cursor.execute("SELECT * FROM device_info WHERE mac_address = %s", (mac_address,))
            result = cursor.fetchone()

            if result:
                logger.debug(f"MAC address already exists in the database: {mac_address}")
            else:
                # Insert the MAC address into the database if it doesn't exist
                sql_query = """
                            UPDATE device_info SET mac_address = %s, status = 1
                            WHERE status = 0;
                            """
                cursor.execute(sql_query, (mac_address,))
                connection.commit()
                logger.info(f"MAC address inserted into the database: {mac_address}")

        except mysql.connector.Error as error:
            logger.error(f"Failed to update database: {error}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                logger.info("MySQL connection closed.")

    def update_text_file(self, mac_address):
        try:
            # Open the text file for reading and writing
            with open('device_data.txt', 'r+') as file:
                lines = file.readlines()
                found = False
                updated_lines = []

                # Update the MAC address and status in the text file where status is 0
                for line in lines:
                    if 'MAC Address:' in line and 'Status: 0' in line:
                        line_parts = line.split(',')
                        line_parts[2] = f" MAC Address: {mac_address}"
                        line_parts[4] = " Status: 1\n"
                        updated_line = ','.join(line_parts)
                        updated_lines.append(updated_line)
                        found = True
                    else:
                        updated_lines.append(line)

                # If no lines with Status: 0 were found, raise IOError
                if not found:
                    raise IOError("No lines with Status: 0 found in the text file.")

                # Write the updated lines back to the text file
                file.seek(0)
                file.writelines(updated_lines)
                file.truncate()

                logger.info(f"MAC address and status updated in the text file where status was 0: {mac_address}")
                self.status_label.config(text="Success")

        except IOError as error:
            logger.error(f"Failed to update text file: {error}")
            self.status_label.config(text="Failed")

