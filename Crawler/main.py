#-*- coding: utf-8 -*-

# Developer : Jeong Wooyoung, EGLAB, Hongik University
# Contact   : gunyoung20@naver.com

import sys
import multiprocessing
from datetime import datetime
from multi_processor import MultiCrawler
import os
#include "user_header.h"


if __name__ == '__main__' :
    if sys.platform.startswith('linux'):
      print("argv[1] :"+sys.argv[1])
      multiprocessing.freeze_support()
      multiprocessing.set_start_method("spawn")
      
      mc = MultiCrawler()
#        keywords = ['홈트']

      keywords = sys.argv[1:]
        
        #processes = [mc.multiCrawlingDaum]
        
        #processes = [mc.multiCrawlingFacebook,mc.multiCrawlingInsta,mc.multiCrawlingHygall, mc.multiCrawlingSlrclub,
        #       mc.multiCrawlingYgosu, mc.multiCrawlingHumoruniv, mc.multiCrawlingTheqoo, mc.multiCrawlingEtoland,
        #       mc.multiCrawlingFmkorea, mc.multiCrawlingPann, mc.multiCrawlingBobae, mc.multiCrawlingDcinside,
        #       mc.multiCrawlingRuliweb, mc.multiCrawlingMlbpark, mc.multiCrawlingInven, mc.multiCrawlingTodayhumor,
        #       mc.multiCrawlingPpomppu, mc.multiCrawlingClien, mc.multiCrawlingInstiz, mc.multiCrawlingCook82,mc.multiCrawlingNaver]
        
#        processes = [mc.multiCrawlingFacebook,mc.multiCrawlingInsta,mc.multiCrawlingHygall, mc.multiCrawlingSlrclub,mc.multiCrawlingNaver,
#               mc.multiCrawlingYgosu, mc.multiCrawlingHumoruniv, mc.multiCrawlingTheqoo, mc.multiCrawlingEtoland,
#               mc.multiCrawlingFmkorea, mc.multiCrawlingPann, mc.multiCrawlingBobae, mc.multiCrawlingDcinside,
#               mc.multiCrawlingRuliweb, mc.multiCrawlingMlbpark, mc.multiCrawlingInven, mc.multiCrawlingTodayhumor,
#               mc.multiCrawlingPpomppu, mc.multiCrawlingClien, mc.multiCrawlingInstiz, mc.multiCrawlingCook82]
      if keywords[0] == 'ranknews':
            processes = [mc.multiCrawlingRankingNews]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("Community "+keyword+" crawling finish. spend time :",(datetime.now()-community_start))

      else:
            # processes = [mc.multiCrawlingInstaDumper]
            # start = datetime.now()
            # for keyword in keywords:
            #       community_start = datetime.now()
            #       print("Community "+keyword+" crawling start.")
            #       mc.distributeProcess(keyword, processes)
            #       sys.stdout.flush()
            #       print("Community "+keyword+" crawling finish. spend time :",(datetime.now()-community_start))
            processes = [mc.multiCrawlingNaverblog]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("naverblog/ "+keyword+" crawling finish. spend time : ",(datetime.now()-community_start))

            processes = [mc.multiCrawlingSlrclub]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("slrclub/ "+keyword+" crawling finish. spend time : ",(datetime.now()-community_start))
      
            processes = [mc.multiCrawlingtistory]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("tstory/ "+keyword+" crawling finish. spend time : ",(datetime.now()-community_start))

            processes = [mc.multiCrawlingNaverNews, mc.multiCrawlingDaum, mc.multiCrawlingYgosu, mc.multiCrawlingHygall]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("Community "+keyword+" crawling finish. spend time : ",(datetime.now()-community_start))
            processes = [mc.multiCrawlingHumoruniv, mc.multiCrawlingTheqoo, mc.multiCrawlingEtoland]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("Community "+keyword+" crawling finish. spend time : ",(datetime.now()-community_start))

            processes = [mc.multiCrawlingNaver]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("Community "+keyword+" crawling finish. spend time : ",(datetime.now()-community_start))      
            
            processes = [mc.multiCrawlingDcinside, mc.multiCrawlingPann, mc.multiCrawlingBobae,  mc.multiCrawlingMlbpark]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("Community "+keyword+" crawling finish. spend time :",(datetime.now()-community_start))
                  
            processes = [mc.multiCrawlingInven, mc.multiCrawlingPpomppu, mc.multiCrawlingClien, mc.multiCrawlingInstiz, mc.multiCrawlingCook82, mc.multiCrawlingRuliweb ]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("Community "+keyword+" crawling finish. spend time :",(datetime.now()-community_start))

      
            # processes = []
            # start = datetime.now()
            # for keyword in keywords:
            #       community_start = datetime.now()
            #       print("Community "+keyword+" crawling start.")
            #       mc.distributeProcess(keyword, processes)
            #       sys.stdout.flush()
            #       print("Community "+keyword+"


            processes = [mc.multiCrawlingNavercafe]
            start = datetime.now()
            for keyword in keywords:
                  community_start = datetime.now()
                  print("Community "+keyword+" crawling start.")
                  mc.distributeProcess(keyword, processes)
                  sys.stdout.flush()
                  print("navercafe/ "+keyword+" crawling finish. spend time :",(datetime.now()-community_start))

            # processes = [mc.multiCrawlingInsta]
            # start = datetime.now()
            # for keyword in keywords:
            #       community_start = datetime.now()
            #       print("Community "+keyword+" crawling start.")
            #       mc.distributeProcess(keyword, processes)
            #       sys.stdout.flush()
            #       print("Community "+keyword+" crawling finish. spend time :",(datetime.now()-community_start))
            
      print("Community crawling finish. spend time :",(datetime.now()-start)) 