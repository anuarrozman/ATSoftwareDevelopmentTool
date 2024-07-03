import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the .ini file
config.read('/home/anuarrozman/FactoryApp_Dev/ATSoftwareDevelopmentTool/FlashingTool/testscript.ini')

# Create an empty array to store the options and values
options_values = []

# Loop through the sections
for section in config.sections():
    print(f"Section: {section}")
    # Loop through the options in each section
    for option in config[section]:
        value = config[section][option]
        # Append the option and value as a tuple to the array
        options_values.append((option, value))
        print(f"Option: {option}, Value: {value}")
