import configparser

def load_script(ini_file_path):
    # Read the contents of the .ini file
    config = configparser.ConfigParser()
    config.read(ini_file_path)

    # Access the sections and options in the .ini file
    for section in config.sections():
        print(f"[{section}]")
        for option in config.options(section):
            value = config.get(section, option)
            print(f"{option} = {value}")
