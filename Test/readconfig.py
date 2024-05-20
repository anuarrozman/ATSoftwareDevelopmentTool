import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the config.ini file
config.read('/home/anuar/ProdTools/ATSoftwareDevelopmentTool/config.ini')

# Accessing values from sections
value1 = config['Section1']['key1']
value2 = config['Section1']['key2']
value3 = config['Section2']['key3']
value4 = config['Section2']['key4']

# Print the values
print("Value 1:", value1)
print("Value 2:", value2)
print("Value 3:", value3)
print("Value 4:", value4)
