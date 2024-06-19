import mysql.connector
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdateDB:
    
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
