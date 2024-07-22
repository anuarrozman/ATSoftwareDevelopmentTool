import time
import wifi
from wifi import Cell

def scan_wifi():
    cells = wifi.Cell.all('wlan0')  # 'wlan0' might vary depending on your system
    return cells

def main():
    cells = scan_wifi()
    for cell in cells:
        print(f"SSID: {cell.ssid}, Signal: {cell.signal} dBm")

if __name__ == "__main__":
    main()
