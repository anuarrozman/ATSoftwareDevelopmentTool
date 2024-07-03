import logging
import sys
import io

# Configure logging to output to stdout
logging.basicConfig(level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)  # Output to stdout

# Example usage
def some_function():
    logging.debug('This is a debug message')
    logging.info('This is an info message')
    logging.warning('This is a warning message')
    logging.error('This is an error message')
    logging.critical('This is a critical message')

if __name__ == '__main__':
    some_function()
    
    # Read logs from stdout and filter for a keyword
    keyword = 'error'  # Change this to your desired keyword
    
    # Redirect logging output to a StringIO object to capture it
    output = io.StringIO()
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(handler)
    
    # Capture and filter logs
    logs = output.getvalue().strip().split('\n')
    for log in logs:
        if keyword in log.lower():
            print(log)
