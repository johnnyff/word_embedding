import os 
import sys 
from selenium import webdriver
import time
if __name__ == '__start__':
    if sys.platform.startswith('linux'):
      print("argv[1] :"+sys.argv[1])
keyword = sys.argv[1:]
os.system("gnome-terminal -- sh -c 'sudo python open_chrome.py'")
time.sleep(5)

for key in keyword:
  os.system("gnome-terminal -- sh -c 'sudo python main.py {}'".format(key))
