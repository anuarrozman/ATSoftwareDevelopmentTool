from tkinter import Tk
from tkinter.filedialog import askopenfilename
import loadscript

# Create a Tkinter window
root = Tk()
root.withdraw()

# Prompt the user to select a .ini file
ini_file_path = askopenfilename(filetypes=[("INI Files", "*.ini")])

# Pass the file path to the load script function
loadscript.load_script(ini_file_path)
