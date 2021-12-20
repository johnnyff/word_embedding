import sys
import multiprocessing
from datetime import datetime
from multi_processor import MultiCrawler
#include "user_header.h"
import os
import subprocess



if __name__ == '__main__' :
    if sys.platform.startswith('linux'):
      print("argv[1] :"+sys.argv[1])

      multiprocessing.freeze_support()
      multiprocessing.set_start_method("spawn")

      mc = MultiCrawler()


      keywords = sys.argv[1:]
      
      
    processes = [mc.multiCrawlingNavercafe]
    start = datetime.now()
    for keyword in keywords:
          community_start = datetime.now()
          print("Community "+keyword+" crawling start.")
          mc.distributeProcess(keyword, processes)
          sys.stdout.flush()
          print("Community "+keyword+" crawling finish. spend time : ",(datetime.now()-community_start))


    
# print("Community crawling finish. spend time :",(datetime.now()-start)) 