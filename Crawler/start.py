import os 
import sys 

if __name__ == '__start__':
    if sys.platform.startswith('linux'):
      print("argv[1] :"+sys.argv[1])
keyword = sys.argv[1:]
os.system("gnome-terminal -- sh -c 'python open_chrome.py'")
os.system("gnome-terminal -- sh -c 'sudo python test1.py {}'".format(keyword))
